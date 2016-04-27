#define PY_SSIZE_T_CLEAN
#include "Python.h"

/* EVP is the preferred interface to hashing in OpenSSL */
#include <openssl/evp.h>
#include <openssl/hmac.h>
/* We use the object interface to discover what hashes OpenSSL supports. */
#include <openssl/objects.h>
#include "openssl/err.h"

static PyObject *
_setException(PyObject *exc)
{
    unsigned long errcode;
    const char *lib, *func, *reason;

    errcode = ERR_peek_last_error();
    if (!errcode) {
        PyErr_SetString(exc, "unknown reasons");
        return NULL;
    }
    ERR_clear_error();

    lib = ERR_lib_error_string(errcode);
    func = ERR_func_error_string(errcode);
    reason = ERR_reason_error_string(errcode);

    if (lib && func) {
        PyErr_Format(exc, "[%s: %s] %s", lib, func, reason);
    }
    else if (lib) {
        PyErr_Format(exc, "[%s] %s", lib, reason);
    }
    else {
        PyErr_SetString(exc, reason);
    }
    return NULL;
}

/* Improved implementation of PKCS5_PBKDF2_HMAC()
 *
 * PKCS5_PBKDF2_HMAC_fast() hashes the password exactly one time instead of
 * `iter` times. Today (2013) the iteration count is typically 100,000 or
 * more. The improved algorithm is not subject to a Denial-of-Service
 * vulnerability with overly large passwords.
 *
 * Also OpenSSL < 1.0 don't provide PKCS5_PBKDF2_HMAC(), only
 * PKCS5_PBKDF2_SHA1.
 */
int PKCS5_PBKDF2_HMAC_fast(const char *pass, int passlen,
                           const unsigned char *salt, int saltlen,
                           int iter, const EVP_MD *digest,
                           int keylen, unsigned char *out)
    {
    unsigned char digtmp[EVP_MAX_MD_SIZE], *p, itmp[4];
    int cplen, j, k, tkeylen, mdlen;
    unsigned long i = 1;
    HMAC_CTX hctx_tpl, hctx;

    mdlen = EVP_MD_size(digest);
    if (mdlen < 0)
        return 0;

    HMAC_CTX_init(&hctx_tpl);
    HMAC_CTX_init(&hctx);
    p = out;
    tkeylen = keylen;
    if(!pass)
        passlen = 0;
    else if(passlen == -1)
        passlen = strlen(pass);
    if (!HMAC_Init_ex(&hctx_tpl, pass, passlen, digest, NULL))
    {
        HMAC_CTX_cleanup(&hctx_tpl);
        return 0;
    }
    while(tkeylen)
        {
        if(tkeylen > mdlen)
            cplen = mdlen;
        else
            cplen = tkeylen;
        /* We are unlikely to ever use more than 256 blocks (5120 bits!)
         * but just in case...
         */
        itmp[0] = (unsigned char)((i >> 24) & 0xff);
        itmp[1] = (unsigned char)((i >> 16) & 0xff);
        itmp[2] = (unsigned char)((i >> 8) & 0xff);
        itmp[3] = (unsigned char)(i & 0xff);
        if (!HMAC_CTX_copy(&hctx, &hctx_tpl))
        {
            HMAC_CTX_cleanup(&hctx_tpl);
            return 0;
        }
        if (!HMAC_Update(&hctx, salt, saltlen)
                || !HMAC_Update(&hctx, itmp, 4)
                || !HMAC_Final(&hctx, digtmp, NULL))
            {
            HMAC_CTX_cleanup(&hctx_tpl);
            HMAC_CTX_cleanup(&hctx);
            return 0;
            }
        memcpy(p, digtmp, cplen);
        for(j = 1; j < iter; j++)
            {
            if (!HMAC_CTX_copy(&hctx, &hctx_tpl))
            {
                HMAC_CTX_cleanup(&hctx_tpl);
                return 0;
            }
            if (!HMAC_Update(&hctx, digtmp, mdlen)
                    || !HMAC_Final(&hctx, digtmp, NULL)) {
                HMAC_CTX_cleanup(&hctx_tpl);
                HMAC_CTX_cleanup(&hctx);
                return 0;
            }
            HMAC_CTX_cleanup(&hctx);
            for(k = 0; k < cplen; k++)
                p[k] ^= digtmp[k];
            }
        tkeylen-= cplen;
        i++;
        p+= cplen;
        }
    HMAC_CTX_cleanup(&hctx_tpl);
#ifdef DEBUG_PKCS5V2
    fprintf(stderr, "Password:\n");
    h__dump (pass, passlen);
    fprintf(stderr, "Salt:\n");
    h__dump (salt, saltlen);
    fprintf(stderr, "Iteration count %d\n", iter);
    fprintf(stderr, "Key:\n");
    h__dump (out, keylen);
#endif
    return 1;
    }


PyDoc_STRVAR(pbkdf2_hmac__doc__,
"pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None) -> key\n\
\n\
Password based key derivation function 2 (PKCS #5 v2.0) with HMAC as\n\
pseudorandom function.");

static PyObject *
pbkdf2_hmac(PyObject *self, PyObject *args, PyObject *kwdict)
{
    static char *kwlist[] = {"hash_name", "password", "salt", "iterations",
                             "dklen", NULL};
    PyObject *key_obj = NULL, *dklen_obj = Py_None;
    char *name, *key;
    Py_buffer password, salt;
    long iterations, dklen;
    int retval;
    const EVP_MD *digest;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict,
#if PY_MAJOR_VERSION >= 3
                                     "sy*y*l|O:pbkdf2_hmac",
#else
                                     "ss*s*l|O:pbkdf2_hmac",
#endif
                                     kwlist, &name, &password, &salt,
                                     &iterations, &dklen_obj)) {
        return NULL;
    }

    digest = EVP_get_digestbyname(name);
    if (digest == NULL) {
        PyErr_SetString(PyExc_ValueError, "unsupported hash type");
        goto end;
    }

    if (password.len > INT_MAX) {
        PyErr_SetString(PyExc_OverflowError,
                        "password is too long.");
        goto end;
    }

    if (salt.len > INT_MAX) {
        PyErr_SetString(PyExc_OverflowError,
                        "salt is too long.");
        goto end;
    }

    if (iterations < 1) {
        PyErr_SetString(PyExc_ValueError,
                        "iteration value must be greater than 0.");
        goto end;
    }
    if (iterations > INT_MAX) {
        PyErr_SetString(PyExc_OverflowError,
                        "iteration value is too great.");
        goto end;
    }

    if (dklen_obj == Py_None) {
        dklen = EVP_MD_size(digest);
    } else {
        dklen = PyLong_AsLong(dklen_obj);
        if ((dklen == -1) && PyErr_Occurred()) {
            goto end;
        }
    }
    if (dklen < 1) {
        PyErr_SetString(PyExc_ValueError,
                        "key length must be greater than 0.");
        goto end;
    }
    if (dklen > INT_MAX) {
        /* INT_MAX is always smaller than dkLen max (2^32 - 1) * hLen */
        PyErr_SetString(PyExc_OverflowError,
                        "key length is too great.");
        goto end;
    }

    key_obj = PyBytes_FromStringAndSize(NULL, dklen);
    if (key_obj == NULL) {
        goto end;
    }
    key = PyBytes_AS_STRING(key_obj);

    Py_BEGIN_ALLOW_THREADS
    retval = PKCS5_PBKDF2_HMAC_fast((char*)password.buf, password.len,
                                    (unsigned char *)salt.buf, salt.len,
                                    iterations, digest, dklen,
                                    (unsigned char *)key);
    Py_END_ALLOW_THREADS

    if (!retval) {
        Py_CLEAR(key_obj);
        _setException(PyExc_ValueError);
        goto end;
    }

  end:
    PyBuffer_Release(&password);
    PyBuffer_Release(&salt);
    return key_obj;
}


static struct PyMethodDef pbkdf2_functions[] = {
    {"pbkdf2_hmac", (PyCFunction)pbkdf2_hmac, METH_VARARGS|METH_KEYWORDS,
     pbkdf2_hmac__doc__},
    {NULL,      NULL}            /* Sentinel */
};


/* Initialize this module. */

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef pbkdf2_module = {
    PyModuleDef_HEAD_INIT,
    "_pbkdf2",
    NULL,
    -1,
    pbkdf2_functions,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit__pbkdf2(void)
#else
void
init_pbkdf2(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    return PyModule_Create(&pbkdf2_module);
#else
    Py_InitModule3("_pbkdf2", pbkdf2_functions, NULL);
#endif
}

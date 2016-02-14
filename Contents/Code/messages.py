class NewMessageContainer(object):
    def __init__(self, prefix, title):
        self.title = title
        Route.Connect(prefix + '/message', self.message_container)

    def message_container(self, header, message):
        """Setup MessageContainer depending on Platform"""

        if Client.Platform in ['Plex Home Theater', 'OpenPHT']:
            oc = ObjectContainer(
                title1=self.title, title2=header, no_cache=True,
                no_history=True, replace_parent=True
                )
            oc.add(PopupDirectoryObject(title=header, summary=message))
            return oc
        else:
            return MessageContainer(header, message)

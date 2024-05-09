import zope.interface


class ISerialDataListener(zope.interface.Interface):

    def on_new_line(self, line: str):
        pass

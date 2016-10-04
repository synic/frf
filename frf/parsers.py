class BaseParser(object):
    """Base parser.  Subclass this to create your own parser."""
    def parse(self, req, view, data):
        return data

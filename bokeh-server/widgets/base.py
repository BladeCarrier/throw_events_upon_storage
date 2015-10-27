__doc__="""an abstract widget interface"""


class _BaseWidget(object):
    """widget interface you gotta implement to create your own widget"""
    def __init__(self):
        """initialize the widget"""
        pass
    def get_updates(self):
        """return the list of bokeh data_sources to be updated on the bokeh server"""
        return []
__doc__= """An interface for dashboard drawer class"""

class Dashboard(object):
    """An interface for dashboard drawer class"""
    name = "yet another dashboard"
    def __init__(self):
        """An interface for dashboard drawer class."""
        pass
    def knit_html(self,es):
        """must return a valid HTML to display
        :es: - an elasticsearch client"""
        return "<p>Empty dashboard</p>"

dir_name = "dashboards"
from bokeh.plotting import figure
import os
def fetch_all():
    dashboards = {}
    for fname in filter(lambda fname:fname.endswith("py"),os.listdir(dir_name)):
        env = {}
        execfile(os.path.join(dir_name,fname),env)
        dashboard = env['dashboard']
        dashboards[dashboard.name] = dashboard
    return dashboards
    
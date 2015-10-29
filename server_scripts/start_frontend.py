# -*- coding: utf-8 -*-
__doc__="i start bokeh server"
import os
os.system("bokeh-server -m --ip 0.0.0.0 --port 7010 &")
os.system("cd bokeh-server && python dashboards/demo1_dashboard.py &")
os.system("cd presenter/dashing && python manage.py runserver 0.0.0.0:8000")
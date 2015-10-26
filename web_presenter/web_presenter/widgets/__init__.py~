#get relative file directory 
DIRNAME = __file__[:-__file__[::-1].index('/')]
IMPORTPATH = DIRNAME.replace("/",".")

import imp

names = set()
import os
def register_all(router):
    """imports all .widget.py widgets from module folder"""
    widget_modules = filter(lambda name: name.endswith("widget.py"), os.listdir(DIRNAME))
    
    urls = []
    for widget_module_name in widget_modules:
        #import widget using imp
        widget_path = os.path.join(DIRNAME,widget_module_name)
	mod = imp.load_source(widget_module_name[:-3],widget_path)

        #check if widget is a correct widget module
        if not hasattr(mod,"get_widget"):
            raise ImportError,"please define {}.get_widget()".format(widget_module_name) 
	if hasattr(mod,'NAME'):
            NAME = mod.NAME
        else:
            NAME = widget_module_name[:-3]

        #check that no two widgets have same NAMEs
        if NAME in names:
            print "cannot import {} from {}: there already is a widget with the same name".format(NAME,widget_module_name)

        #add urls (if any)
        if hasattr(mod,"get_urls"):
            print mod
            urls+=mod.get_urls()
        #register the widget
	router.register(mod.get_widget(),NAME)
        names.add(NAME)
	print "imported",widget_module_name,"as",NAME

    return urls

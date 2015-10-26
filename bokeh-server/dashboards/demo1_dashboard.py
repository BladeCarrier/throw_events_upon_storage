import time
import os

from bokeh.plotting import figure, hplot,vplot, output_server, cursession, show
    
from bokeh.session import Session

import sys

#killmepls
sys.path.append(sys.path[0][:-11])
#killmepls

from widgets.es_bokeh import *

dashboard_name = "dashboard1"
#django way
path_to_django_static = "/notebooks/web_presenter/web_presenter/static"
#flask way
path_to_flask_static = "/notebooks/throw_events_upon_storage/presenter/static"

bs_login = "bladeCarrier"
bs_password= "243414Aa"


#make up an ES client
import elasticsearch
es = elasticsearch.Elasticsearch(["localhost:9200"])


widgets= []
client = cursession()
whole_dashboard=0

def prepare_widgets():
    print "initializing..."
    # start bokeh-server session
    global client
    client = Session(root_url='http://0.0.0.0:7010/', load_from_config=False)
    try:
        client.register(bs_login,bs_password)
    except:pass

    client.login(bs_login,bs_password)

    ###CREATE WIDGETS
    print "preaparing widgets..."
    #hist1: hist with overlay
    import analysis.distfit as distfit
    import pandas as pd
    xname,xmin,xmax,xbins = "invariantMass",0,10,50


    bin_separators = np.histogram([],bins=xbins, range=[xmin,xmax])[1]
    bin_centers = np.array([0.5*(bin_separators[i]+bin_separators[i+1]) for i in range(len(bin_separators)-1)])
    bins = pd.DataFrame({"x":bin_centers})

    mix_model = distfit.DistributionsMixture(
        distributions={'sig': distfit.gauss, 'bck': distfit.exponential},
        weights_ranges={'sig': [1.,10.], 'bck': [1.,10.]},
        parameter_ranges={'mean': [xmin ,xmax], 'sigma': [0., xmax-xmin], 'slope': [0, 15.]},
        column_ranges={'x': [xmin, xmax]},
        sampling_strategy='grid',
    )


    mix_model.compile(bins,1000) #takes several seconds



    hist1_base = WhiskeredHistWidget(xname,xmin,xmax,xbins,es,
                       fig = figure(plot_width=600, plot_height=600,tools=['wheel_zoom','ywheel_zoom','pan','resize','reset']))
    hist1 = MLFitOverlayWidget(hist1_base,mix_model,n_pts=100)
    widgets.append(hist1)

    #hist2: just hist
    hist2 = ClassicHistWidget("muonHits",0,100,30,es,
                       fig = figure(plot_width=600, plot_height=600,tools=['wheel_zoom','ywheel_zoom','pan','reset']))
    widgets.append(hist2)


    #hist3: heatmap
    hist3 = HeatmapWidget("avgMass",0,35,50,
                          "muonHits",0,70,50,
                          es,fig = figure(plot_width=600, plot_height=600),)
    widgets.append(hist3)

    ###end CREATE PLOTS

    print "publishing plots..."
    #create a dashboard on bokeh_server
    output_server(dashboard_name,client)

    plots = [ hplot(widget.fig) for widget in widgets ]

    global whole_dashboard
    whole_dashboard = vplot(hplot(*plots[:2]),plots[2])
    plots.append(whole_dashboard)    

    for plot in plots:
        client.show(plot)


    client.publish()
 
    print "creating static links..."
    #publish the thing
    from bokeh.embed import autoload_server
    scripts = [autoload_server(plot,client,public=True) for plot in plots]


    print "saving widget scripts..."
    #remove previous widgets
    for path_to_static in path_to_django_static,path_to_flask_static:
        path_to_widgets = os.path.join(path_to_static,dashboard_name)

        os.system("rm -rf " + path_to_widgets)
        os.mkdir(path_to_widgets)

        for i, script in enumerate(scripts):
            with open("{}/widget{}.html".format(path_to_widgets,i),'w') as fscript:
                fscript.write(script)
    

    print "dashboard {} ready.".format(dashboard_name),
    


def start_updating(dt=0.5):
    print  "now updating..."
    while True:
        for widget in widgets:
            upd_sources = widget.get_updates()
            try:
                client.store_objects(*upd_sources)
            except:pass

        time.sleep(dt);

if __name__ == "__main__":
    prepare_widgets()
    start_updating()

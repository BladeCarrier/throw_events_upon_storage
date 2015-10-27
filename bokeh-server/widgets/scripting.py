
__doc__="""a module that contains a tool to transform bokeh-server plots into universal host-independent ones"""

def assemble_script(widget_name,source_html):
    """makes an html script for a widget
    widget_name must be a asting that uniquely indentifies the widget on the webpage
    source_html has to be an output of bokeh_server static publishing"""
    html_div = """    <div id="{}">
    </div>""".format(widget_name)


    html_first = """
    <script>
        function getPosition(str, m, i) {
           // get ith occurence of m in str
           return str.split(m, i).join(m).length;
        };

        var url = window.location.href;
        var hostname = url.substring(0,getPosition(url,":",2) );
    """

    html_create = """    
        var div = document.getElementById("{}")
        var bokeh_script = document.createElement("script");\n""".format(widget_name)


    #set the javascript parameters
    params = source_html[source_html.index("<script")+7:source_html.index("</script")-1]
    params = params.replace(" ","").split("\n") #remove spaces
    params = filter(len,params) #remove empty
    params = dict(map(lambda s: s.split("="),params)) #split key-value
    
    params["src"] = 'hostname+":' + "".join(params["src"].split(":")[2:])
    params["data-bokeh-root-url"] = 'hostname+":' + "".join(params["data-bokeh-root-url"].split(":")[2:])
    
    
    
    params = map(lambda (k,v): '        bokeh_script.setAttribute("{}",{});'.format(k,v), params.items())
    html_params = "\n".join(params)


    html_last="""
        div.appendChild(bokeh_script);
    </script>"""


    return html_div+html_first+html_create+html_params+html_last
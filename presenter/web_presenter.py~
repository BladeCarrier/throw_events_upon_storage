from flask import Flask, render_template, json, request
import json


from threading import Lock
lock = Lock()



#ElasticSearch part
import elasticsearch
es = elasticsearch.Elasticsearch(["localhost:9200"])
#/elasticSearch
#dashboards
import dashboard
#/dashboards


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/init', methods=['POST'])
def show_dashboards():
    html = ""
    for name in dashboards:
        html+='<input type="radio" name="dashboard" value="{}" >{}</input>\n<br/>'.format(name,name)
    return html

@app.route('/show_dashboard', methods=['POST'])
def show_dashboard():
    data = json.loads(request.data)
    if "dashboard" not in data:
        return "<p>Please select dashboard</p>"
    name = data["dashboard"]
    with lock:
        return dashboards[name].knit_html(es)


if __name__ == '__main__':
    dashboards = dashboard.fetch_all()
    print "all dashboards ready"

    app.run(debug=True, host='localhost')

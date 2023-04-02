from flask import Flask, render_template, request, redirect, url_for

import pygal
from pygal.style import Style
import pandas as pd
import requests
import json
from app.config import Config
from app.module.dal import Dal 
from app.module.visual import Visual

import gzip
from io import BytesIO

allcharts = Dal.get_all_visuals()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    allcharts = Dal.get_all_visuals()

    @app.route('/')
    def home():
        

        return render_template('index.html')
        #return app.config['DATA_API_TOKEN']
    
    def get_chart_by_url_name(url_name):
        allcharts = Dal.get_all_visuals() #This will need to be removed from final code somehow 
        matching_charts = [chart for chart in allcharts if chart.chart_url_name == url_name]
        return matching_charts[0] if matching_charts else None
    def get_chart_by_chart_id(charts,chart_id):
        print(chart_id)
        matching_charts = [chart for chart in charts if chart.chart_id == chart_id]
        return matching_charts[0] if matching_charts else None
    
    @app.route("/charts/<string:chartname>")
    def get_charts_for(chartname):
        visual =  get_chart_by_url_name(f'/{chartname}')
        if (visual == None):
            return 'Visual not yet supported !!!'
        
        charttype = request.args.get('ct')
        
        token = app.config['DATA_API_TOKEN'] 
        chart_pygal = visual.get_chart(request.args, token, charttype) 
        response  = chart_pygal.render_response()
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if 'gzip' not in accept_encoding:
            return response

        response.headers['Content-Encoding'] = 'gzip'
        buffer = BytesIO()
        gzip_obj = gzip.GzipFile(mode='wb', fileobj=buffer)
        gzip_obj.write(response.data)
        gzip_obj.close()
        response.data = buffer.getvalue()
        response.headers['Content-Length'] = len(response.data)
        return response
    
    @app.route("/charts-management")
    def charts_management():
        selected = request.args.get("modify")
        charts = Dal.get_all_visuals()
        data = {
                'chart_id': 0,
                'chart_name': 'Bar Chart',
                'chart_url_name': 'bar_chart',
                'chart_styles': '{"background":"transparent"}',
                'chart_configs': '{"title": "My Bar Chart"}',
                'chart_data_source': '{"datasource":"url"}'
            }
        modify = Visual.from_dict(data)
        if not selected is None :
            modify = get_chart_by_chart_id(charts, int(selected))
        print(modify)
        return render_template('charts.html', data=charts, modify=modify)

    @app.route("/charts-management", methods=['POST'])
    def configure_chart():
        data = {
                'chart_id': request.form['chart_id'],
                'chart_name':  request.form['chart_name'],
                'chart_url_name': request.form['chart_url_name'],
                'chart_styles': request.form['chart_styles'],
                'chart_configs': request.form['chart_configs'],
                'chart_data_source': request.form['chart_data_source']
            }
         
        visual = Visual.from_dict(data)
        Dal.save_update_visual(visual)
        allcharts = None
        allcharts = Dal.get_all_visuals()
        # Redirect the user back to the home page
         

        return redirect(url_for('charts_management'))
    return app
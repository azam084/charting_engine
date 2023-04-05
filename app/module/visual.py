from flask import request
import requests
import json
import pandas as pd
from app.config import Config as config
import pygal
from pygal.style import Style

import plotly
import plotly.graph_objs as go
import plotly.io as pio

class Visual:
    @classmethod
    def from_dict(cls, data_dict):
        return cls(
            data_dict['chart_id'],
            data_dict['chart_name'],
            data_dict['chart_url_name'],
            data_dict['chart_styles'],
            data_dict['chart_configs'],
            data_dict['chart_data_source'],
            data_dict['custom_css']
        )
    def __init__(self, chart_id, chart_name, chart_url_name, chart_styles, chart_configs, chart_data_source, custom_css):
        self.chart_id = chart_id
        self.chart_name = chart_name
        self.chart_url_name = chart_url_name
        self.chart_styles = chart_styles
        self.chart_configs = chart_configs
        self.chart_data_source = chart_data_source
        self.custom_css = custom_css
    @classmethod
    def get_style(self,chartstyle):
        style_dict = json.loads(chartstyle)
        styleobj = pygal.style.Style(**style_dict)
        # for key, value in stylejson.items():
        #     setattr(styleobj, key, value) 
        return  styleobj


    @classmethod
    def from_row(cls, row):
        return cls(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6])

    def get_data(self, args, token):
        _datasource = json.loads(self.chart_data_source)
       
        arguments = str(_datasource['arguments']).split(',')
        _apiurl = str(_datasource["url"])
        print(_apiurl)
        for arg in arguments:
            _apiurl = _apiurl.replace(arg, args.get(arg))
        _apiurl = _apiurl.replace('{','').replace('}','')
        print(_apiurl)
        try:
            uResponse = requests.get(_apiurl, headers={'Authorization': f'Bearer {token}'}) 
        except requests.exceptions.RequestException as e: 
            return str(e)
        Jresponse = uResponse.text 
        data = json.loads(Jresponse)
        
        return data 

    def get_chart(self, args, token, charttype):
        data  = self.get_data(args, token)
        df = pd.DataFrame(data)
        index = 0
        values = df.values[index][4:].tolist()
        labels = df.columns[4:].tolist()
        title = df.values[index][:1][0]  
        chart_style = self.get_style(self.chart_styles)  

        
        config_dict = json.loads(self.chart_configs)
        chart_config = pygal.Config(**config_dict) 
 
        bar_chart = pygal.Bar()
        if (charttype == 'line'):
            bar_chart = pygal.Line(x_labels_major_count = 6)
        if (charttype == 'stackedline'):
            bar_chart  = pygal.StackedLine(fill=True)
        bar_chart.style = chart_style 
        bar_chart.config = chart_config
        bar_chart.config.css.append(self.custom_css)
        # bar_chart.show_legend  = False 
        # bar_chart.pretty_print = True
        # #bar_chart.human_readable = True
        # #bar_chart.title = title
        #bar_chart.truncate_label  = None
        bar_chart.x_labels = map(str, labels) 
        # bar_chart.x_labels_major_count = 6 
        bar_chart.add(title, values) 
        # bar_chart.x_labels_major_count = 6 
        # bar_chart.x_labels_major_every = 4
        # bar_chart.truncate_label = -1
        # bar_chart.show_minor_x_labels = False
        return bar_chart

    def get_chart_plotly(self, args, token, charttype):
        data  = self.get_data(args, token)
        df = pd.DataFrame(data)
        index = 0
        values = df.values[index][4:].tolist()
        labels = df.columns[4:].tolist()
        title = df.values[index][:1][0]  
        trace = go.Scatter(x=labels, y=values)
        chart_data = [trace]

        config_dict = json.loads(self.chart_configs)
        del config_dict['use_plotly']
        layout = go.Layout(title='My Plot', **config_dict)
        fig = go.Figure(data=chart_data, layout=layout)
        plot_div = plotly.offline.plot(fig, output_type='div')
        return plot_div
        # svg_image = pio.to_svg(fig)
        # return svg_image

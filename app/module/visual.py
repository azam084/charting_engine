 
import datetime
from flask import request
import requests
import json
import pandas as pd
from app.config import Config as config
import pygal
from pygal.style import Style
import math
import plotly
import plotly.graph_objs as go
import plotly.io as pio

from app.module.LineBar import LineBar
from app.module.ArgaamBar import ArgaamBar

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
        
        for arg in arguments:
            _apiurl = _apiurl.replace(arg, args.get(arg))
        _apiurl = _apiurl.replace('{','').replace('}','')
        
        try:
            uResponse = requests.get(_apiurl, headers={'Authorization': f'Bearer {token}'}) 
        except requests.exceptions.RequestException as e: 
            return str(e)
        Jresponse = uResponse.text 
        data = json.loads(Jresponse)
        
        return data 

    def get_chart(self, args, token, charttype):
        try:
            data = self.get_data(args, token)
            df = pd.DataFrame(data)
        except:
           df = pd.DataFrame(columns=["EntityID", "EntityName", "Labels", "ForYear", "FiscalPeriodValue", "ForDate"])

        if df.empty:
            df = pd.DataFrame(columns=["EntityID", "EntityName", "Labels", "ForYear", "FiscalPeriodValue", "ForDate"])
       
       
        fixed_cols = ["EntityID", "EntityName", "Labels", "ForYear", "FiscalPeriodValue", "ForDate"]
        variable_cols = list(set(df.columns) - set(fixed_cols))

        chart_style = self.get_style(self.chart_styles)  
        
        
        config_dict = json.loads(self.chart_configs)

        chart_config = pygal.Config(**config_dict) 
        
        entities =  df['EntityID'].unique() 
        entities_names = df['EntityName'].unique()
        bar_chart = ArgaamBar()
        if (charttype == 'line'):
            bar_chart = pygal.Line()
        # if (charttype == 'stackedline'):
        #     bar_chart  = pygal.StackedLine()
        if (charttype == 'dateline'):
            bar_chart  = pygal.DateLine()
        if (charttype == 'pie'):
            bar_chart  = pygal.Pie()     
        
        bar_chart.config = chart_config

        if entities.shape[0] > 1: 
            bar_chart  = LineBar(chart_config)

        bar_chart.style = chart_style 
        bar_chart.config = chart_config
        bar_chart.config.css.append(self.custom_css)
        data_length = len(df["ForDate"])
        if charttype == "line" or charttype == "stackedline":
            bar_chart.x_labels = list([int(df.loc[i]["ForYear"]) if i % 240 == 0 else '' for i in range(df.shape[0])])
            bar_chart.config.x_labels_major_count = 4
            bar_chart.config.x_labels_major_every = 240
        else:
            labels = df['Labels']
            bar_chart.x_labels =  list(map(str, labels.unique()))
            bar_chart.x_labels = list([str(df.loc[i]["Labels"]) if int(data_length / 4) != 0 and i % int(data_length / 4) == 0 else '' for i in range(df.shape[0])])            
            bar_chart.config.x_labels_major_count = 4
            bar_chart.config.x_labels_major_every = data_length
        
        bar_max_value = 0
        bar_min_value = -20000000

        if charttype == 'bar':
            bar_chart.config.defs.append('''
            <linearGradient id="gradient-0" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="#F08823" />
                <stop offset="40%" stop-color="#FFB347" />
                <stop offset="60%" stop-color="#FFE4C4" />
                <stop offset="80%" stop-color="#FFFFFF" />
                <stop offset="100%" stop-color="#FFFFFF" />
            </linearGradient>
            ''')
            bar_chart.config.css.append('''inline:
            .color-0 {
                fill: url(#gradient-0) !important;
                stroke: url(#gradient-0) !important;
            }''')
        
        for col in variable_cols:
            if charttype == 'stackedline' or charttype == "line":
                values = df[[col, 'ForDate']].rename(columns={col: 'value', 'ForDate': 'label'}).to_dict(orient='records')
                for record in values:
                    record['value'] = round(record['value'], 2)
                bar_chart.add('', values)
            else:
                #values =  df.loc[df['EntityID'] == entities[0], col].round(2)
                values = df[[col, 'Labels']].rename(columns={col: 'value', 'Labels': 'label'}).to_dict(orient='records')
                title =  entities_names[0] + '-' + col if len(entities_names) > 1 else col
                i = 0
                for record in values:
                    record['value'] = round(record['value'], 2)
                    record['label'] = '' if int(data_length / 4) and i % int(data_length / 4) == 0 else record['label']
                    i = i + 1
                bar_chart.add(" ", values)  
                # bar_max_value = values.max() if bar_max_value < values.max() else bar_max_value
                # bar_min_value = values.min() if bar_min_value < values.min() else bar_min_value

        if entities.shape[0] > 1:
            line_max_value = 0
            line_min_value = -20000000
            bar_chart.x_labels.append("")  # without this the final bars overlap the secondary axis
            for index, entity in enumerate(entities[1:]):
                for col in variable_cols:
                    values =  df.loc[df['EntityID'] == entity, col].round(2)
                    title = entities_names[index+1] + '-' + col
                    bar_chart.add(title, values,  plotas='line', secondary=True)   
                    line_max_value = values.max() if line_max_value < values.max() else line_max_value
                    line_min_value = values.min() if line_min_value < values.min() else line_min_value

            bar_chart.secondary_range = (-0.003,line_max_value) 

            # bar_min_value = math.floor(bar_min_value)
            # bar_min_value = (bar_min_value if bar_min_value < 0 else 0)
            # print(math.floor(bar_min_value))
            bar_chart.range = (-1.002, math.ceil(bar_max_value)) 
        
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
    
    def get_pie_chart(self, args, token, charttype):
        try:
            data = self.get_data(args, token) 
            df = pd.DataFrame(data) 
        except: 
            df = pd.DataFrame(columns=["EntityID", "EntityName", "Labels", "ForYear", "FiscalPeriodValue", "ForDate", "Percentage"])

        if df.empty: 
            df = pd.DataFrame(columns=["EntityID", "EntityName", "Labels", "ForYear", "FiscalPeriodValue", "ForDate", "Percentage"])
         
        fixed_cols = ["EntityID", "EntityName", "Labels", "ForYear", "FiscalPeriodValue", "ForDate"]

        variable_cols = list(set(df.columns) - set(fixed_cols))
        
        labels = df['Labels']

        chart_style = self.get_style(self.chart_styles)        
        
        config_dict = json.loads(self.chart_configs)
        chart_config = pygal.Config(**config_dict)
        
        entities =  df['EntityID'].unique() 
        entities_names = df['EntityName'].unique()
        pie_chart = pygal.Pie()             
        
        pie_chart.config = chart_config
        pie_chart.style = chart_style
        pie_chart.config.css.append(self.custom_css)

        namesOfLabels=df['Labels']
        valuesForLabels=df['Percentage'] 
         
        for i in range (len(namesOfLabels)):
            pie_chart.add(namesOfLabels[i],valuesForLabels[i])

        return pie_chart
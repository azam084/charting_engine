 
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
        
        fiscalperiodtype=request.args.get('fiscalperiodtype')

        df=df.dropna(subset=variable_cols, how='any')

        
        def x_lbl_count(n):
            return (NumberOfBars // 2)+1 if NumberOfBars % 2 == 1 else (math.ceil(NumberOfBars / 2))
        

        NumberOfBars=df['Labels'].nunique()
 

        def calculateNumberOfMajors():
            if fiscalperiodtype ==4:
                numberOfMajors=NumberOfBars if (NumberOfBars<13) else x_lbl_count(NumberOfBars/2) if (NumberOfBars>=13 and NumberOfBars<= 25) else 5  #display number of years 
                return numberOfMajors
            else:
                numberOfMajors=NumberOfBars if (NumberOfBars<8) else x_lbl_count(NumberOfBars) if (NumberOfBars>=8 and NumberOfBars<=13) else 5  #display number of qtrs 
                return numberOfMajors                

        
        chart_style = self.get_style(self.chart_styles)          
        config_dict = json.loads(self.chart_configs)

        #needs to get improve: we have to remove under properties and add them to init
        config_dict['precision'] = 2 if 'precision' not in config_dict else config_dict['precision']
        config_dict['max_scale'] = 11 if 'max_scale' not in config_dict else config_dict['max_scale']
        precesion_val='{{:.{}f}}'.format(config_dict['precision'])    
        config_dict['legend_at_bottom_columns']=3 if 'legend_at_bottom_columns' not in config_dict else config_dict['legend_at_bottom_columns']
        config_dict['width'] = 384 
        config_dict['height'] = 160
        config_dict['margin'] = 0
        config_dict['legend_at_bottom'] = True if 'legend_at_bottom' not in config_dict else config_dict['legend_at_bottom']
        config_dict['show_legend'] = False if 'show_legend' not in config_dict else config_dict['show_legend']
        config_dict['legend_box_size'] = 6 if 'legend_box_size' not in config_dict else config_dict['legend_box_size']
 

        entities =  df['EntityID'].unique() # extract unique entities into an array
        entities_names = df['EntityName'].unique()
        
        bar_chart = ArgaamBar()
        if entities.shape[0] > 1:
            config_dict['print_values']=False
            
            


        chart_config = pygal.Config(**config_dict) 

        if (charttype == 'line'):

            bar_chart = pygal.Line()
        # if (charttype == 'stackedline'):
        #     bar_chart  = pygal.StackedLine()
        if (charttype == 'dateline'):

            bar_chart  = pygal.DateLine()
        if (charttype == 'pie'):
           
            bar_chart  = pygal.Pie()     
        

        if entities.shape[0] > 1:
                       
            bar_chart  = pygal.Line(chart_config)


           

        bar_chart.style = chart_style 
        bar_chart.config = chart_config
        bar_chart.config.css.append(self.custom_css)
        print_values_every=math.ceil(NumberOfBars/8)
        css_selector = "[text-anchor='middle']:nth-of-type({}n)".format(print_values_every)
        css_code = "{} {{ display: initial !important; }}".format(css_selector)

        
        
        if entities.shape[0]==1:          
            bar_chart.config.css.append('''inline: 
            [text-anchor='middle']:nth-of-type(n) { display: none !Important;}
            ''')
            bar_chart.config.css.append("inline: {} {{ display: initial !important; }}".format(css_selector))
        # if entities.shape[0]==1 and fiscalperiodtype is not 4:
        # else :
            # print('dont print value at top of bar on qtrs')
            # bar_chart.config.css.append('''inline: 
            # [text-anchor='middle']:nth-of-type(n) { display: none !Important;}
            # ''')


       

        data_length = len(df["ForDate"]) 
        
        if charttype == "line" or charttype == "stackedline":
            bar_chart.config.margin=0
            data_count = len(df["ForYear"])
            data_count = 240 if data_count < 1500 else 480
            bar_chart.x_labels = list([int(df.loc[i]["ForYear"]) if i % data_count == 0 else '' for i in range(df.shape[0])])
            bar_chart.config.x_labels_major_count = 4
            bar_chart.config.x_labels_major_every = 240
        else:
            labels = df['Labels']
            bar_chart.x_labels =  list(map(str, labels.unique()))
            
            bar_chart.config.x_labels_major_count = calculateNumberOfMajors()
            
            
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
            

        bar_max_value=0
        bar_min_value=0
        valuesAry=[]
        
        
        for en_index, entity in enumerate(entities):
           
            for col in variable_cols:
                if charttype == 'stackedline' or charttype == "line":
                    
                    values = df[[col, 'ForDate']].rename(columns={col: 'value', 'ForDate': 'label'}).to_dict(orient='records')
                    
                    for record in values:
                        
                        record['value'] = round(record['value'], 2)
                    bar_chart.add('', values)
                else:
                    
                    df_filtered = df.loc[df['EntityID'] == entity, [col, 'Labels']]
                    values = df_filtered.rename(columns={col: 'value', 'Labels': 'label'}).to_dict(orient='records')

                    title =  entities_names[en_index] if len(entities_names) > 1 else col
                    if (len(entities)==1):
                        bar_chart.config.show_legend=False
                    else:
                        bar_chart.config.show_legend=True
                        bar_chart.config.margin=12
                        num_rows_legend=math.ceil((len(entities))/bar_chart.config.legend_at_bottom_columns)
                        bar_chart.config.width = 384 +(120*num_rows_legend) 
                        bar_chart.config.height = 160+(50*num_rows_legend)
                        
                

                    bar_chart.add(title, values,formatter=lambda x: precesion_val.format(x) if x is not None else None)  

        
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






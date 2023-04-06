
import pygal
from pygal.graph.graph import Graph
from pygal.graph.bar import Bar
from pygal.graph.line import Line

from pygal.util import alter, decorate, ident, swap

class LineBar(pygal.Line, pygal.Bar):
    def __init__(self, config=None, **kwargs):
        super(LineBar, self).__init__(config=config, **kwargs)
        self.y_title_secondary = kwargs.get('y_title_secondary')
        self.plotas = kwargs.get('plotas', 'line')

    def _make_y_title(self):
        super(LineBar, self)._make_y_title()
        
        # Add secondary title
        if self.y_title_secondary:
            yc = self.margin_box.top + self.view.height / 2
            xc = self.width - 10
            text2 = self.svg.node(
                self.nodes['title'], 'text', class_='title',
                x=xc,
                y=yc
            )
            text2.attrib['transform'] = "rotate(%d %f %f)" % (
                -90, xc, yc)
            text2.text = self.y_title_secondary

    def _plot(self):
        for i, serie in enumerate(self.series, 1):
            plottype = self.plotas

            raw_series_params = self.svg.graph.raw_series[serie.index][1]
            if 'plotas' in raw_series_params:
                plottype = raw_series_params['plotas']
                
            if plottype == 'bar':
                self.bar(serie)
            elif plottype == 'line':
                self.line(serie)
            else:
                raise ValueError('Unknown plottype for %s: %s'%(serie.title, plottype))

        for i, serie in enumerate(self.secondary_series, 1):
            plottype = self.plotas

            raw_series_params = self.svg.graph.raw_series[serie.index][1]
            if 'plotas' in raw_series_params:
                plottype = raw_series_params['plotas']

            if plottype == 'bar':
                self.bar(serie, True)
            elif plottype == 'line':
                self.line(serie, True)
            else:
                raise ValueError('Unknown plottype for %s: %s'%(serie.title, plottype))
    def _tooltip_and_print_values(
        self, serie_node, serie, parent, i, val, metadata, x, y, width, height
    ):
        transpose = swap if self.horizontal else ident
        x_center, y_center = transpose((x + width/2 , (y - height/4)))
        x_top, y_top = transpose((x + width, y + height))
        x_bottom, y_bottom = transpose((x, y))
        if self._dual:
            v = serie.values[i][0]
        else:
            v = serie.values[i]
        sign = -1 if v < self.zero else 1
        self._tooltip_data(
            parent, val, x_center, y_center, "centered", self._get_x_label(i)
        )

        if self.print_values_position == 'top':
            if self.horizontal:
                x = x_bottom + sign * self.style.value_font_size / 2
                y = y_center
            else:
                x = x_center
                y = y_bottom - sign * self.style.value_font_size / 2
        elif self.print_values_position == 'bottom':
            if self.horizontal:
                x = x_top + sign * self.style.value_font_size / 2
                y = y_center
            else:
                x = x_center
                y = y_top - sign * self.style.value_font_size / 2
        else:
            x = x_center
            y = y_center
        self._static_value(serie_node, val, x, y, metadata, "middle")
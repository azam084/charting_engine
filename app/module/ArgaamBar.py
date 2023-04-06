import pygal
from pygal.style import Style
from pygal.util import alter, decorate, ident, swap

class ArgaamBar(pygal.Bar):
    lang= 1

    def _init_(self, *args, **kwargs):
        super(ArgaamBar, self)._init_(*args, **kwargs)

    def _make_title(self):
        """Make the title"""
        if self._title:
            for i, title_line in enumerate(self._title, 1):
                self.svg.node(
                    self.nodes['title'],
                    'text',
                    class_='title plot_title',
                    x=self.margin_box.left if lang == 2 else self.width - self.margin_box.right,
                    y=i * (self.style.title_font_size + self.spacing)
                ).text = title_line

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

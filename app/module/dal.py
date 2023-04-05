import sqlite3

from app.config import Config 
from app.module.visual import Visual
class Dal :
    def get_all_visuals():
        conn = sqlite3.connect(Config.DB_FILE)
        c = conn.cursor()
        c.execute("SELECT chart_id, chart_name, chart_url_name, chart_styles, chart_configs, chart_data_source, custom_css FROM ChartConfigs")
        all_charts = [Visual.from_row(row) for row in c.fetchall()]
        conn.close()
        return all_charts
    
    def save_update_visual(visual):
        conn = sqlite3.connect(Config.DB_FILE)
        c = conn.cursor()

        if not visual.chart_id or int(visual.chart_id) == 0:
            c.execute("INSERT INTO ChartConfigs (chart_name, chart_url_name, chart_styles, chart_configs, chart_data_source, custom_css) VALUES (?, ?, ?, ?, ?)",
                        (visual.chart_name, visual.chart_url_name, visual.chart_styles, visual.chart_configs, visual.chart_data_source, visual.custom_css))
        else:
            c.execute("UPDATE ChartConfigs SET chart_name = ?, chart_url_name = ?, chart_styles = ?, chart_configs = ?, chart_data_source = ?, custom_css = ? WHERE chart_id = ?",
                        (visual.chart_name, visual.chart_url_name, visual.chart_styles, visual.chart_configs, visual.chart_data_source,visual.custom_css, visual.chart_id))

        conn.commit()
        conn.close()
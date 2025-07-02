import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import geopandas as gpd
from typing import List, Optional, Tuple, Any

class ChartVisualizations:
    """Handle all chart visualizations including bar charts, trends, and scatterplots"""
    
    # Constants extracted to top for easy maintenance
    PINK_PURPLE_SCALE = ['#fce4ec', '#f8bbd9', '#e91e63', '#ad1457', '#7b1fa2', '#4a148c']
    
    HARMONIZED_COLORS = [
        '#1f77b4', '#17becf', '#2ca02c', '#ff7f0e', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#d62728'
    ]
    
    PROVINCE_COLORS = {
        "Kigali City": "#D62828", "Northern": "#3A0CA3", "Southern": "#2A9D8F",
        "Eastern": "#F4A261", "Western": "#577590", "Western Province": "#577590",
        "East": "#F4A261", "North": "#3A0CA3", "South": "#2A9D8F", "West": "#577590"
    }
    
    MONTH_NAMES = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }
    
    # Chart configuration templates
    CHART_CONFIGS = {
        'districts': {
            'all cases': ('All Cases', 'All Cases Trends Over Time'),
            'Severe cases/Deaths': ('Severe Cases & Deaths', 'Severe Cases & Deaths Trends Over Time'),
            'all cases incidence': ('All Cases Incidence', 'All Cases Incidence Trends Over Time'),
            'Severe cases/Deaths incidence': ('Severe Cases & Deaths Incidence', 'Severe Cases & Deaths Incidence Trends Over Time')
        },
        'sectors': {
            'Simple malaria cases': ('Simple Malaria Cases', 'Simple Malaria Cases Trends Over Time'),
            'incidence': ('Incidence', 'Incidence Trends Over Time')
        }
    }
    
    def __init__(self, dashboard_type: str, metrics_calculator):
        self.dashboard_type = dashboard_type
        self.metrics_calculator = metrics_calculator
    
    def create_top_entities_chart(self, data: gpd.GeoDataFrame, year: int, month: int, metric: str, top_n: int = 10) -> Any:
        """Create top entities bar chart with improved ranking (highest at top)"""
        filtered_data = data[(data['year'] == year) & (data['month'] == month)].copy()
        
        # Get top entities - FIXED: Now shows highest values at TOP
        sorted_data = filtered_data.nlargest(top_n, metric)
        
        # Reverse the order so highest appears at top of chart
        sorted_data = sorted_data.iloc[::-1]
        
        # Get configuration using helper
        y_title, title, y_column = self._get_chart_config('bar', year, month, metric, top_n)
        
        # Get yearly maximum for consistent color scaling
        yearly_max = data[data['year'] == year][metric].max()
        yearly_min = data[data['year'] == year][metric].min()
        
        fig = px.bar(
            sorted_data, x=metric, y=y_column, orientation='h', color=metric,
            color_continuous_scale=self.PINK_PURPLE_SCALE, 
            range_color=[yearly_min, yearly_max],  # FIXED: Use yearly range, not monthly
            title=title,
            labels={metric: y_title, y_column: self._get_entity_label()},
            hover_data=self._get_hover_data('bar')
        )
        
        # Update colorbar with better labels
        fig.update_layout(
            coloraxis_colorbar=dict(
                title=dict(
                    text=f"{y_title}<br><span style='font-size:10px'>Max {year}: {yearly_max:,.0f}</span>",
                    font=dict(size=12)
                ),
                tickformat=":,.0f",
                tickfont=dict(size=10),
                len=0.7,
                thickness=15
            )
        )
        
        # Apply common dark theme styling
        self._apply_dark_theme(fig, height=520, title_size=14)
        return fig
    
    def create_trend_chart(self, data: gpd.GeoDataFrame, selected_entities: List[str], metric: str) -> Optional[Any]:
        """Create trend line chart for selected entities showing monthly trends"""
        if not selected_entities:
            return None
        
        # Filter and prepare data
        filtered_data = self._filter_trend_data(data, selected_entities)
        if filtered_data.empty:
            return None
        
        # Create date column and sort
        filtered_data = filtered_data.copy()
        filtered_data['date'] = pd.to_datetime(filtered_data[['year', 'month']].assign(day=1))
        filtered_data = filtered_data.sort_values('date')
        
        # Get configuration
        y_column, y_title, title = self._get_chart_config('trend', metric=metric)
        color_column = 'sector_display' if self.dashboard_type == "Sectors" else self.metrics_calculator.get_display_column()
        
        # Create color mapping
        color_map = {entity: self.HARMONIZED_COLORS[i % len(self.HARMONIZED_COLORS)] 
                     for i, entity in enumerate(selected_entities)}
        
        fig = px.line(
            filtered_data, x='date', y=y_column, color=color_column, title=title,
            labels={y_column: y_title, 'date': 'Time Period', color_column: self._get_entity_label()},
            color_discrete_map=color_map, hover_data=self._get_hover_data('trend')
        )
        
        # Apply styling with spline smoothing
        fig.update_traces(line=dict(width=3, shape='spline', smoothing=0.3), marker=dict(size=6), mode='lines+markers')
        fig.update_layout(xaxis=dict(tickformat='%b %Y'))
        self._apply_dark_theme(fig, height=450, title_size=16)
        
        return fig
    
    def create_scatterplot(self, data: gpd.GeoDataFrame, year: int, month: int) -> Tuple[Optional[Any], Optional[float], Optional[float]]:
        """Create scatterplot with quadrant analysis and star/triangle highlights for selected month/year"""
        filtered_data = data[(data['year'] == year) & (data['month'] == month)].copy()
        
        if filtered_data.empty:
            return None, None, None
        
        if self.dashboard_type == "Districts":
            return self._create_district_scatterplot(filtered_data, year, month)
        else:
            return self._create_sector_scatterplot(filtered_data, year, month)
    
    # === PRIVATE HELPER METHODS ===
    
    def _get_chart_config(self, chart_type: str, year: int = None, month: int = None, metric: str = None, top_n: int = 10) -> Tuple[str, str, str]:
        """Universal configuration method for all chart types"""
        dashboard_key = 'districts' if self.dashboard_type == "Districts" else 'sectors'
        
        if chart_type == 'bar':
            month_name = self.MONTH_NAMES.get(month, str(month))
            entity_label = "Districts" if self.dashboard_type == "Districts" else "Sectors"
            y_column = 'District' if self.dashboard_type == "Districts" else 'Sector'
            
            if metric in self.CHART_CONFIGS[dashboard_key]:
                y_title = self.CHART_CONFIGS[dashboard_key][metric][0]
                title = f'Top {top_n} {entity_label}: {y_title} ({month_name} {year})'
            else:
                y_title, title = 'Value', f'Top {top_n} {entity_label} ({month_name} {year})'
            
            return y_title, title, y_column
        
        elif chart_type == 'trend':
            if metric in self.CHART_CONFIGS[dashboard_key]:
                y_title, title = self.CHART_CONFIGS[dashboard_key][metric]
                return metric, y_title, title
            else:
                return metric, 'Value', 'Trends Over Time'
    
    def _get_hover_data(self, chart_type: str) -> dict:
        """Get hover data configuration based on dashboard type and chart type"""
        base_data = {'Population': ':,.0f'}
        
        if self.dashboard_type == "Districts":
            specific_data = {
                'all cases': ':,.0f', 'Severe cases/Deaths': ':,.0f',
                'all cases incidence': ':.2f', 'Severe cases/Deaths incidence': ':.2f'
            }
        else:
            specific_data = {
                'District': True, 'Simple malaria cases': ':,.0f', 'incidence': ':.2f'
            }
        
        return {**base_data, **specific_data} if chart_type == 'bar' else specific_data
    
    def _filter_trend_data(self, data: gpd.GeoDataFrame, selected_entities: List[str]) -> gpd.GeoDataFrame:
        """Filter data for trend charts based on dashboard type"""
        if self.dashboard_type == "Districts":
            return data[data[self.metrics_calculator.get_display_column()].isin(selected_entities)]
        else:
            if 'sector_display' in data.columns:
                return data[data['sector_display'].isin(selected_entities)]
            else:
                return data[data['Sector'].isin(selected_entities)]
    
    def _apply_dark_theme(self, fig, height: int = 450, title_size: int = 16):
        """Apply consistent dark theme styling to all charts"""
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', height=height, margin=dict(l=0, r=0, t=40, b=0),
            title_font_size=title_size, title=dict(font=dict(color='white')),
            legend=dict(font=dict(color='white', size=10), bgcolor='rgba(30,30,30,0.9)', 
                       bordercolor='white', borderwidth=1),
            xaxis=dict(showgrid=False, color='white'),
            yaxis=dict(showgrid=False, color='white'),
            coloraxis_colorbar=dict(title_font_color='white', tickfont_color='white')
        )
    
    def _create_district_scatterplot(self, filtered_data: gpd.GeoDataFrame, year: int, month: int) -> Tuple[Optional[Any], Optional[float], Optional[float]]:
        """Create district scatterplot: Total vs Severe Cases"""
        # Prepare data
        filtered_data['Total Malaria Cases'] = filtered_data['all cases']
        filtered_data['Severe Cases & Deaths'] = filtered_data['Severe cases/Deaths']
        
        filtered_data = filtered_data[(filtered_data['Total Malaria Cases'] >= 0) & 
                                      (filtered_data['Severe Cases & Deaths'] >= 0)].copy()
        if filtered_data.empty:
            return None, None, None
        
        # Calculate thresholds and bounds
        thresholds = self._calculate_scatterplot_bounds(filtered_data, 'Total Malaria Cases', 'Severe Cases & Deaths')
        
        # Create scatterplot
        month_name = self.MONTH_NAMES.get(month, str(month))
        fig = px.scatter(
            filtered_data, x='Total Malaria Cases', y='Severe Cases & Deaths', color='Province',
            color_discrete_map=self.PROVINCE_COLORS, hover_name='District',
            hover_data={'Province': False, 'all cases': ':,.1f', 'Severe cases/Deaths': ':,.1f', 'Population': ':,.0f'},
            title=f'District Performance: Total vs Severe Cases ({month_name} {year})',
            labels={'Total Malaria Cases': 'Total Malaria Cases', 'Severe Cases & Deaths': 'Severe Cases & Deaths'},
            opacity=0.85
        )
        
        # Add styling and highlights
        self._style_scatterplot(fig, thresholds, 'district')
        self._add_highlights(fig, filtered_data, 'district')
        
        return fig, thresholds['x_threshold'], thresholds['y_threshold']
    
    def _create_sector_scatterplot(self, filtered_data: gpd.GeoDataFrame, year: int, month: int) -> Tuple[Optional[Any], Optional[float], Optional[float]]:
        """Create sector scatterplot: Population vs Incidence"""
        # Clean province names and filter data
        filtered_data['Province'] = filtered_data['Province'].replace('Iburengerazuba', 'Western Province')
        filtered_data = filtered_data[(filtered_data['Population'] >= 0) & (filtered_data['incidence'] >= 0)].copy()
        
        if filtered_data.empty:
            return None, None, None
        
        # Calculate thresholds with custom x bounds
        thresholds = self._calculate_scatterplot_bounds(filtered_data, 'Population', 'incidence', x_lower=-100)
        
        # Create scatterplot
        month_name = self.MONTH_NAMES.get(month, str(month))
        hover_name_col = 'sector_display' if 'sector_display' in filtered_data.columns else 'Sector'
        
        fig = px.scatter(
            filtered_data, x='Population', y='incidence', color='Province',
            color_discrete_map=self.PROVINCE_COLORS, hover_name=hover_name_col,
            hover_data={'Province': False, 'District': True, 'Simple malaria cases': ':,.0f', 'Population': ':,.0f', 'incidence': ':.2f'},
            title=f'<br><br>',
            labels={'Population': 'Population', 'incidence': 'Incidence (per 1,000 people)'},
            opacity=0.85
        )
        
        # Add styling and highlights
        self._style_scatterplot(fig, thresholds, 'sector')
        self._add_highlights(fig, filtered_data, 'sector')
        
        return fig, thresholds['x_threshold'], thresholds['y_threshold']
    
    def _calculate_scatterplot_bounds(self, data, x_col: str, y_col: str, x_lower: int = 0) -> dict:
        """Calculate thresholds and bounds for scatterplot"""
        x_threshold = np.percentile(data[x_col], 75)
        y_threshold = np.percentile(data[y_col], 75)
        x_upper = max(data[x_col].max() * 1.2, x_threshold * 1.5)
        y_upper = max(data[y_col].max() * 1.2, y_threshold * 1.5)
        
        return {
            'x_threshold': x_threshold, 'y_threshold': y_threshold,
            'x_upper': x_upper, 'y_upper': y_upper, 'x_lower': x_lower
        }
    
    def _style_scatterplot(self, fig, thresholds: dict, plot_type: str):
        """Apply consistent styling to scatterplots"""
        # Add quadrant lines
        fig.add_shape(type="line", x0=thresholds['x_threshold'], y0=0, 
                      x1=thresholds['x_threshold'], y1=thresholds['y_upper'],
                      line=dict(color="white", width=1.5, dash="dot"))
        fig.add_shape(type="line", x0=thresholds['x_lower'], y0=thresholds['y_threshold'], 
                      x1=thresholds['x_upper'], y1=thresholds['y_threshold'],
                      line=dict(color="white", width=1.5, dash="dot"))
        
        # Apply dark theme with custom ranges
        self._apply_dark_theme(fig, height=450, title_size=16)
        fig.update_layout(
            xaxis=dict(range=[thresholds['x_lower'], thresholds['x_upper']], 
                      showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
            yaxis=dict(range=[0, thresholds['y_upper']], 
                      showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
            legend=dict(title='Province')
        )
        
        # Add quadrant labels
        self._add_quadrant_labels(fig, thresholds, plot_type)
        
        # Style markers
        fig.update_traces(marker=dict(size=8, line=dict(width=1, color='white')), selector=dict(mode='markers'))
    
    def _add_quadrant_labels(self, fig, thresholds: dict, plot_type: str):
        """Add quadrant labels based on plot type"""
        if plot_type == 'district':
            labels = [
                ("Low Cases<br>Low Severity", 0.05, -0.101, "left", "top"),
                ("High Cases<br>Low Severity", 0.775, -0.101, "left", "top"),
                ("Low Cases<br>High Severity", 0.05, 0.75, "left", "bottom"),
                ("High Cases<br>High Severity", 0.75, 0.75, "left", "bottom")
            ]
            x_range = thresholds['x_upper']
        else:  # sector
            labels = [
                ("Low pop<br>Low Incidence", 0.05, -0.101, "left", "top"),
                ("High pop<br>Low Incidence", 0.755, -0.101, "left", "top"),
                ("Low Pop<br>High Incidence", 0.05, 0.75, "left", "bottom"),
                ("High Pop<br>High Incidence", 0.75, 0.75, "left", "bottom")
            ]
            x_range = thresholds['x_upper'] - thresholds['x_lower']
        
        for text, x_frac, y_frac, x_anchor, y_anchor in labels:
            x_pos = thresholds['x_lower'] + x_frac * x_range if plot_type == 'sector' else x_frac * x_range
            y_pos = thresholds['y_threshold'] + y_frac * thresholds['y_upper'] if y_frac < 0 else y_frac * thresholds['y_upper']
            
            fig.add_annotation(x=x_pos, y=y_pos, text=text, showarrow=False,
                              font=dict(color="lightgray", size=11), xanchor=x_anchor, yanchor=y_anchor)
    
    def _add_highlights(self, fig, data, plot_type: str):
        """Add star and triangle highlights"""
        if plot_type == 'district':
            max_case_row = data.loc[data['Total Malaria Cases'].idxmax()]
            max_severe_row = data.loc[data['Severe Cases & Deaths'].idxmax()]
            
            self._add_highlight_marker(fig, max_case_row, 'Total Malaria Cases', 'Severe Cases & Deaths', 
                                     'District', 'Province', 'star', 'Highest Total')
            
            if max_severe_row['District'] != max_case_row['District']:
                self._add_highlight_marker(fig, max_severe_row, 'Total Malaria Cases', 'Severe Cases & Deaths', 
                                         'District', 'Province', 'triangle-up', 'Highest Severe')
        else:  # sector
            max_pop_row = data.loc[data['Population'].idxmax()]
            max_inc_row = data.loc[data['incidence'].idxmax()]
            
            name_col = 'sector_display' if 'sector_display' in data.columns else 'Sector'
            pop_name = max_pop_row.get(name_col, 'Unknown')
            inc_name = max_inc_row.get(name_col, 'Unknown')
            
            self._add_highlight_marker(fig, max_pop_row, 'Population', 'incidence', 
                                     name_col, 'Province', 'star', 'Highest Population')
            
            if inc_name != pop_name:
                self._add_highlight_marker(fig, max_inc_row, 'Population', 'incidence', 
                                         name_col, 'Province', 'triangle-up', 'Highest Incidence')
    
    def _add_highlight_marker(self, fig, row, x_col: str, y_col: str, name_col: str, color_col: str, symbol: str, name: str):
        """Add a single highlight marker"""
        fig.add_trace(go.Scatter(
            x=[row[x_col]], y=[row[y_col]], mode='markers+text',
            marker=dict(symbol=symbol, size=16, 
                       color=self.PROVINCE_COLORS.get(row[color_col], 'white'),
                       line=dict(width=2, color='white')),
            text=[row[name_col]], textposition='top center',
            name=name, hoverinfo='skip', showlegend=False
        ))
    
    def _get_entity_label(self) -> str:
        """Get entity label for charts"""
        return "District" if self.dashboard_type == "Districts" else "Sector"
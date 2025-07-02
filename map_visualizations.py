import plotly.express as px
import streamlit as st
from typing import Dict, Any
import geopandas as gpd

class MapVisualizations:
    """Handle choropleth map visualizations for both districts and sectors"""
    
    def __init__(self, dashboard_type: str, metrics_calculator):
        self.dashboard_type = dashboard_type
        self.metrics_calculator = metrics_calculator
        
        # Pink to purple color scale
        self.pink_purple_scale = [
            [0.0, '#fce4ec'],    # Very light pink
            [0.2, '#f8bbd9'],    # Light pink
            [0.4, '#e91e63'],    # Medium pink
            [0.6, '#ad1457'],    # Dark pink
            [0.8, '#7b1fa2'],    # Light purple
            [1.0, '#4a148c']     # Deep purple
        ]
    
    def create_choropleth_map(self, data: gpd.GeoDataFrame, year: int, month: int, metric: str) -> Any:
        """Create choropleth map with completely clean styling"""
        filtered_data = data[(data['year'] == year) & (data['month'] == month)].copy()
        
        # Get yearly range for consistent coloring
        yearly_data = data[data['year'] == year]
        vmin = yearly_data[metric].min()
        vmax = yearly_data[metric].max()
        
        # Get simple colorbar title
        if self.dashboard_type == "Districts":
            if metric == 'all cases':
                colorbar_title = 'All Cases'
            elif metric == 'Severe cases/Deaths':
                colorbar_title = 'Severe Cases'
            elif metric == 'all cases incidence':
                colorbar_title = 'Incidence'
            else:
                colorbar_title = 'Cases'
        else:
            if metric == 'Simple malaria cases':
                colorbar_title = 'Cases'
            elif metric == 'incidence':
                colorbar_title = 'Incidence'
            else:
                colorbar_title = 'Cases'
        
        # Get hover data and display column
        hover_data = self._get_hover_data()
        display_col = self.metrics_calculator.get_display_column()
        
        if display_col not in filtered_data.columns:
            if self.dashboard_type == "Districts":
                display_col = 'District'
            else:
                display_col = 'Sector' if 'Sector' in filtered_data.columns else 'District'
        
        # Create the map with NO title
        fig = px.choropleth_mapbox(
            filtered_data,
            geojson=filtered_data.geometry.__geo_interface__,
            locations=filtered_data.index,
            color=metric,
            hover_name=display_col,
            hover_data=hover_data,
            color_continuous_scale=self.pink_purple_scale,
            range_color=[vmin, vmax],
            mapbox_style='carto-darkmatter',
            zoom=6.8,
            center={'lat': -1.9, 'lon': 29.9},
            labels=self._get_map_labels()
        )
        
        # Update layout with CLEAN colorbar - no extra text
        fig.update_layout(
            plot_bgcolor='rgba(20,20,20,0.9)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=580,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            coloraxis_colorbar=dict(
                title_font_color='white',
                tickfont_color='white',
                title=dict(
                    text=colorbar_title,  # Just the metric name
                    font=dict(size=12)
                ),
                tickformat=":,.0f",
                len=0.8,
                thickness=20,
                x=1.02
            )
        )
        
        return fig
    
    def _get_map_titles(self, year: int, month: int, metric: str) -> tuple:
        """Get appropriate titles based on dashboard type and metric"""
        month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        month_name = month_names.get(month, str(month))
        
        if self.dashboard_type == "Districts":
            return self._get_district_titles(year, month_name, metric)
        else:
            return self._get_sector_titles(year, month_name, metric)
    
    def _get_district_titles(self, year: int, month_name: str, metric: str) -> tuple:
        """Get titles for district maps"""
        title_map = {
            'all cases': (f'All Malaria Cases by District ({month_name} {year})', 'All Cases'),
            'Severe cases/Deaths': (f'Severe Cases & Deaths by District ({month_name} {year})', 'Severe Cases & Deaths'),
            'all cases incidence': (f'All Cases Incidence by District ({month_name} {year})', 'All Cases Incidence'),
            'Severe cases/Deaths incidence': (f'Severe Cases & Deaths Incidence by District ({month_name} {year})', 'Severe Cases & Deaths Incidence')
        }
        return title_map.get(metric, (f'District Analysis ({month_name} {year})', 'Value'))
    
    def _get_sector_titles(self, year: int, month_name: str, metric: str) -> tuple:
        """Get titles for sector maps"""
        title_map = {
            'Simple malaria cases': (f'Simple Malaria Cases Distribution ({month_name} {year})', 'Simple Malaria Cases'),
            'incidence': (f'Simple Malaria Incidence ({month_name} {year})', 'Incidence')
        }
        return title_map.get(metric, (f'Sector Analysis ({month_name} {year})', 'Value'))
    
    def _get_hover_data(self) -> Dict[str, Any]:
        """Get hover data configuration based on dashboard type"""
        if self.dashboard_type == "Districts":
            return {
                'all cases': ':,.0f',
                'Severe cases/Deaths': ':,.0f',
                'all cases incidence': ':.2f',
                'Severe cases/Deaths incidence': ':.2f',
                'Population': ':,.0f'
            }
        else:
            return {
                'District': True,
                'Simple malaria cases': ':,.0f',
                'incidence': ':.2f',
                'Population': ':,.0f'
            }
    
    def _get_map_labels(self) -> Dict[str, str]:
        """Get labels for map based on dashboard type"""
        if self.dashboard_type == "Districts":
            return {
                'all cases': 'All Cases',
                'Severe cases/Deaths': 'Severe Cases & Deaths',
                'all cases incidence': 'All Cases Incidence',
                'Severe cases/Deaths incidence': 'Severe Cases & Deaths Incidence',
                'District': 'District',
                'Population': 'Population'
            }
        else:
            return {
                'Simple malaria cases': 'Simple Malaria Cases',
                'incidence': 'Incidence',
                'District': 'District',
                'Sector': 'Sector',
                'Population': 'Population'
            }
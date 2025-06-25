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
        """Create choropleth map using Plotly with pink-purple color scheme"""
        filtered_data = data[(data['year'] == year) & (data['month'] == month)].copy()
        
        # Get global range for consistent coloring across all time periods
        vmin, vmax = self.metrics_calculator.get_color_scale_range(data, metric)
        
        # Get titles and labels based on dashboard type and metric
        title, colorbar_title = self._get_map_titles(year, month, metric)
        
        # Get hover data based on dashboard type
        hover_data = self._get_hover_data()
        
        # Get display column for hover name
        display_col = self.metrics_calculator.get_display_column()
        
        # Check if display column exists, use fallback if not
        if display_col not in filtered_data.columns:
            if self.dashboard_type == "Districts":
                display_col = 'District'
            else:
                display_col = 'Sector' if 'Sector' in filtered_data.columns else 'District'
        
        # Create the map
        fig = px.choropleth_mapbox(
            filtered_data,
            geojson=filtered_data.geometry.__geo_interface__,
            locations=filtered_data.index,
            color=metric,
            hover_name=display_col,
            hover_data=hover_data,
            color_continuous_scale=self.pink_purple_scale,
            range_color=[vmin, vmax],  # Set consistent color range
            mapbox_style='carto-darkmatter',
            zoom=6.8,
            center={'lat': -1.9, 'lon': 29.9},
            title=title,
            labels=self._get_map_labels()
        )
        
        # Update layout for dark mode
        fig.update_layout(
            plot_bgcolor='rgba(20,20,20,0.9)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16,
            height=520,
            margin=dict(l=0, r=0, t=40, b=0),
            title=dict(font=dict(color='white')),
            coloraxis_colorbar=dict(
                title_font_color='white',
                tickfont_color='white',
                title=dict(text=colorbar_title)
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
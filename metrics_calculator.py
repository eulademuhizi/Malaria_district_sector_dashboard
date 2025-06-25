import streamlit as st
import pandas as pd
from typing import Tuple, Optional

class MetricsCalculator:
    """Calculate key metrics for both district and sector dashboards"""
    
    def __init__(self, dashboard_type: str):
        self.dashboard_type = dashboard_type
        # Updated district metrics - removed "Severe cases/Deaths incidence"
        self.district_metrics = {
            '📊 All Cases': 'all cases',
            '📈 All Cases Incidence': 'all cases incidence',
            '⚠️ Severe Cases & Deaths': 'Severe cases/Deaths'
        }
        self.sector_metrics = {
            '🦟 Simple Malaria Cases': 'Simple malaria cases',
            '📊 Incidence': 'incidence'
        }
    
    def get_available_metrics(self) -> dict:
        """Get available metrics based on dashboard type"""
        if self.dashboard_type == "Districts":
            return self.district_metrics
        elif self.dashboard_type == "Sectors":
            return self.sector_metrics
        else:
            # Fallback
            return self.district_metrics
    
    @st.cache_data
    def calculate_metrics(_self, _data, selected_year: int, selected_metric: str, 
                         previous_year: Optional[int] = None) -> Tuple[float, float, Optional[float]]:
        """Calculate key metrics for the dashboard - cached for performance"""
        # Use all data for the selected year (not filtered by month) for proper totals
        current_data = _data[_data['year'] == selected_year]
        
        if _self.dashboard_type == "Districts":
            return _self._calculate_district_metrics(current_data, _data, selected_metric, 
                                                   selected_year, previous_year)
        else:
            return _self._calculate_sector_metrics(current_data, _data, selected_metric, 
                                                 selected_year, previous_year)
    
    def _calculate_district_metrics(self, current_data, all_data, selected_metric: str, 
                                  selected_year: int, previous_year: Optional[int]) -> Tuple[float, float, Optional[float]]:
        """Calculate metrics for district dashboard"""
        if selected_metric in ['all cases', 'Severe cases/Deaths']:
            total_cases = current_data[selected_metric].sum()
            total_population = current_data['Population'].sum()
            # Calculate overall incidence: (total cases / total population) * 1000
            overall_incidence = (total_cases / total_population * 1000) if total_population > 0 else 0
        else:
            # For incidence metrics, take the mean of district-level incidences
            overall_incidence = current_data[selected_metric].mean()
            if selected_metric == 'all cases incidence':
                total_cases = current_data['all cases'].sum()
            else:
                total_cases = 0
        
        change_percent = None
        if previous_year and previous_year in all_data['year'].values:
            prev_data = all_data[all_data['year'] == previous_year]
            if selected_metric in ['all cases', 'Severe cases/Deaths']:
                prev_total_cases = prev_data[selected_metric].sum()
                prev_total_pop = prev_data['Population'].sum()
                prev_incidence = (prev_total_cases / prev_total_pop * 1000) if prev_total_pop > 0 else 0
            else:
                prev_incidence = prev_data[selected_metric].mean()
            
            if prev_incidence > 0:
                change_percent = ((overall_incidence - prev_incidence) / prev_incidence) * 100
        
        return total_cases, overall_incidence, change_percent
    
    def _calculate_sector_metrics(self, current_data, all_data, selected_metric: str, 
                                selected_year: int, previous_year: Optional[int]) -> Tuple[float, float, Optional[float]]:
        """Calculate metrics for sector dashboard"""
        if selected_metric == 'Simple malaria cases':
            total_cases = current_data[selected_metric].sum()
            total_population = current_data['Population'].sum()
            # Calculate overall incidence: (total cases / total population) * 1000
            overall_incidence = (total_cases / total_population * 1000) if total_population > 0 else 0
        else:  # incidence
            # For incidence metric, take the mean of sector-level incidences
            overall_incidence = current_data[selected_metric].mean()
            total_cases = current_data['Simple malaria cases'].sum()
        
        change_percent = None
        if previous_year and previous_year in all_data['year'].values:
            prev_data = all_data[all_data['year'] == previous_year]
            if selected_metric == 'Simple malaria cases':
                prev_total_cases = prev_data[selected_metric].sum()
                prev_total_pop = prev_data['Population'].sum()
                prev_incidence = (prev_total_cases / prev_total_pop * 1000) if prev_total_pop > 0 else 0
            else:  # incidence
                prev_incidence = prev_data[selected_metric].mean()
            
            if prev_incidence > 0:
                change_percent = ((overall_incidence - prev_incidence) / prev_incidence) * 100
        
        return total_cases, overall_incidence, change_percent
    
    @st.cache_data
    def get_color_scale_range(_self, _data, metric: str) -> Tuple[float, float]:
        """Get the global min and max for consistent color scaling across years - cached"""
        return _data[metric].min(), _data[metric].max()
    
    def get_entity_column(self) -> str:
        """Get the column name for entities (districts/sectors)"""
        if self.dashboard_type == "Districts":
            return 'District'
        else:
            return 'Sector'
    
    def get_display_column(self) -> str:
        """Get the column name for display purposes"""
        if self.dashboard_type == "Districts":
            return 'District'
        else:
            return 'sector_display'
    
    def get_province_column(self) -> str:
        """Get the province column name"""
        return 'Province'  # Both districts and sectors use 'Province'
    
    def prepare_sector_display_names(self, data):
        """This method is no longer needed as sector display names are created in the data loader"""
        return data
import streamlit as st
import geopandas as gpd
import pandas as pd
from typing import List, Optional, Tuple
import numpy as np

# Import custom classes
from data_loader import MalariaDataLoader, SectorDataLoader
from metrics_calculator import MetricsCalculator
from map_visualizations import MapVisualizations
from chart_visualizations import ChartVisualizations

class DashboardConfig:
    """Handle page configuration and styling"""
    
    @staticmethod
    def setup_page():
        """Set up page configuration"""
        st.set_page_config(
            page_title="Rwanda Malaria Dashboard",
            page_icon="🦟",
            layout="wide",
            initial_sidebar_state="collapsed"  # Collapse sidebar since we're not using it
        )
    
    @staticmethod
    def apply_custom_css():
        """Apply custom CSS for dark mode and color-coded sections"""
        st.markdown("""
        <style>
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 0.5rem;
                max-width: 100%;
            }
            .stMetric {
                background-color: #2b2b2b;
                border: 1px solid #444;
                padding: 0.5rem;
                border-radius: 0.25rem;
                margin: 0;
                color: white;
            }
            .stMetric > div {
                color: white;
            }
            .stMetric label {
                color: white !important;
            }
            .stMetric [data-testid="metric-container"] > div {
                color: white !important;
            }
            h1, h2, h3 {
                margin-top: 0.5rem;
                margin-bottom: 0.25rem;
                color: white;
            }
            .element-container {
                margin: 0 !important;
            }
            .stPlotlyChart {
                margin: 0 !important;
            }
            [data-testid="metric-container"] {
                background-color: #2b2b2b;
                border: 1px solid #444;
                padding: 0.5rem;
                border-radius: 0.25rem;
                color: white;
            }
            [data-testid="metric-container"] > div {
                color: white !important;
            }
            [data-testid="metric-container"] label {
                color: white !important;
            }
            /* Style for control area */
            .control-container {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 1rem;
                margin-bottom: 1rem;
                border: 1px solid #444;
            }
        </style>
        """, unsafe_allow_html=True)

class DashboardUI:
    """Handle Streamlit UI components and layout - Controls in Main Area Version"""
    
    # Constants for consistent styling and configuration
    MONTH_NAMES = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
    
    # Reusable HTML templates
    SECTION_TEMPLATE = """
    <div style="background: linear-gradient(135deg, {bg_start} 0%, {bg_end} 100%); 
                border: 2px solid {border_color}; border-radius: 12px; padding: 1.2rem; color: white;">
        <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0.8rem; 
                   text-align: center; text-transform: uppercase; letter-spacing: 1px;">
            {header}
        </div>
        {content}
    </div>
    """
    
    METRIC_ITEM_TEMPLATE = """
    <div style="display: flex; justify-content: space-between; padding: 0.4rem 0; 
               {border_style} color: white;">
        <span>{icon} {label}</span>
        <div style="text-align: right;">
            <div style="font-size: 1.1rem; font-weight: bold;">{value}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">{delta}</div>
        </div>
    </div>
    """
    
    PERFORMANCE_ITEM_TEMPLATE = """
    <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; 
               font-size: 0.95rem; color: white;">
        <span style="font-weight: 500;">{arrow} {entity}</span>
        <span style="font-weight: bold;">{change}</span>
    </div>
    """
    
    # Color schemes for sections
    SECTION_COLORS = {
        'status': {'bg_start': '#1e3a8a', 'bg_end': '#1e40af', 'border_color': '#3b82f6'},
        'improvements': {'bg_start': '#166534', 'bg_end': '#15803d', 'border_color': '#22c55e'},
        'concerns': {'bg_start': '#991b1b', 'bg_end': '#dc2626', 'border_color': '#ef4444'}
    }
    
    def __init__(self, dashboard_type: str, metrics_calculator, map_viz, chart_viz):
        self.dashboard_type = dashboard_type
        self.metrics_calculator = metrics_calculator
        self.map_viz = map_viz
        self.chart_viz = chart_viz
    
    def render_header(self):
        """Render dashboard header"""
        if self.dashboard_type == "Districts":
            st.title("🏥 Rwanda Malaria Districts Dashboard")
            st.markdown("*Monitor malaria cases and trends across Rwanda's districts*")
        else:
            st.title("🏥 Rwanda Malaria Sectors Dashboard")
            st.markdown("*Track malaria cases, incidence, and trends across Rwanda's sectors*")
    
    def render_controls_in_main_area(self, data: gpd.GeoDataFrame, entity_options: List[str]) -> Tuple[int, int, str, List[str]]:
        """Render controls in main content area instead of sidebar"""
        
        # Create a styled container for controls
        st.markdown('<div class="control-container">', unsafe_allow_html=True)
        st.markdown("### 🛠️ Dashboard Controls")
        
        # Create columns for different control groups
        col1, col2, col3, col4 = st.columns([2, 2, 3, 3])
        
        with col1:
            st.markdown("**📅 Time Filters**")
            selected_year, selected_month = self._render_time_controls_main(data)
        
        with col2:
            st.markdown("**📈 Primary Metric**")
            selected_metric = self._render_metric_selection_main()
        
        with col3:
            st.markdown("**🔍 Entity Comparison**")
            selected_entities = self._render_entity_selection_main(entity_options)
        
        with col4:
            st.markdown("**📊 Current Selection**")
            self._render_selection_summary(selected_year, selected_month, selected_metric, len(selected_entities))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add some spacing
        st.markdown("---")
        
        return selected_year, selected_month, selected_metric, selected_entities
    
    def _render_time_controls_main(self, data: gpd.GeoDataFrame) -> Tuple[int, int]:
        """Render time controls in main area (not sidebar)"""
        key_prefix = "district" if self.dashboard_type == "Districts" else "sector"
        
        # Initialize session state
        years = sorted(data['year'].unique())
        if f'{key_prefix}_year' not in st.session_state:
            st.session_state[f'{key_prefix}_year'] = max(years)
        if f'{key_prefix}_month' not in st.session_state:
            st.session_state[f'{key_prefix}_month'] = 12
        
        # Sync between tabs
        self._sync_time_between_tabs(key_prefix)
        
        # Year selection
        selected_year = st.slider(
            "Year", min_value=min(years), max_value=max(years), 
            value=st.session_state[f'{key_prefix}_year'], step=1,
            key=f"{key_prefix}_year_slider_main", 
            help="Choose which year's data to display"
        )
        st.session_state[f'{key_prefix}_year'] = selected_year
        
        # Month selection with validation
        selected_month = self._render_month_control_main(data, selected_year, key_prefix)
        
        return selected_year, selected_month
    
    def _render_month_control_main(self, data: gpd.GeoDataFrame, selected_year: int, key_prefix: str) -> int:
        """Render month control in main area with validation"""
        available_months = sorted(data[data['year'] == selected_year]['month'].unique())
        if available_months:
            current_month = st.session_state[f'{key_prefix}_month']
            if current_month not in available_months:
                current_month = max(available_months)
                st.session_state[f'{key_prefix}_month'] = current_month
            
            selected_month = st.slider(
                "Month", min_value=min(available_months), max_value=max(available_months),
                value=current_month, step=1, format="%d", 
                key=f"{key_prefix}_month_slider_main",
                help="Choose which month's data to display"
            )
            st.session_state[f'{key_prefix}_month'] = selected_month
            return selected_month
        else:
            st.error("No data available for selected year")
            return 1
    
    def _render_metric_selection_main(self) -> str:
        """Render metric selection in main area"""
        key_prefix = "district" if self.dashboard_type == "Districts" else "sector"
        
        metric_options = self.metrics_calculator.get_available_metrics()
        selected_metric_display = st.selectbox(
            "Choose Metric", list(metric_options.keys()),
            key=f"{key_prefix}_metric_selector_main",
            help="Select the main metric to show on the map and charts"
        )
        return metric_options[selected_metric_display]
    
    def _render_entity_selection_main(self, entity_options: List[str]) -> List[str]:
        """Render entity selection in main area"""
        key_prefix = "district" if self.dashboard_type == "Districts" else "sector"
        entity_label = "Districts" if self.dashboard_type == "Districts" else "Sectors"
        
        return st.multiselect(
            f"Choose {entity_label} to Compare", entity_options, default=[],
            key=f"{key_prefix}_entity_selector_main", max_selections=10,
            help=f"Select up to 10 {entity_label.lower()} to see their trends over time"
        )
    
    def _render_selection_summary(self, year: int, month: int, metric: str, num_entities: int):
        """Render a summary of current selections"""
        month_name = self.MONTH_NAMES.get(month, str(month))
        entity_type = "districts" if self.dashboard_type == "Districts" else "sectors"
        
        # Get metric display name
        metric_options = self.metrics_calculator.get_available_metrics()
        metric_display = next((k for k, v in metric_options.items() if v == metric), metric)
        
        st.info(f"""
        **Period:** {month_name} {year}  
        **Metric:** {metric_display}  
        **Comparing:** {num_entities} {entity_type}
        """)
    
    def _sync_time_between_tabs(self, key_prefix: str):
        """Synchronize time selection between tabs"""
        other_prefix = "sector" if key_prefix == "district" else "district"
        
        if f'{other_prefix}_year' in st.session_state:
            st.session_state[f'{key_prefix}_year'] = st.session_state[f'{other_prefix}_year']
        if f'{other_prefix}_month' in st.session_state:
            st.session_state[f'{key_prefix}_month'] = st.session_state[f'{other_prefix}_month']
    
    def render_color_coded_overview(self, current_data, previous_data, selected_year: int, selected_month: int, selected_metric: str):
        """Render color-coded sections: Current Status | Improvements | Concerns"""
        st.markdown(f"### {self.MONTH_NAMES.get(selected_month)} {selected_year} Overview")
        
        # Three equal columns for color-coded sections
        status_col, improvements_col, concerns_col = st.columns(3)
        
        with status_col:
            self._render_section('status', current_data, previous_data, selected_metric)
        
        with improvements_col:
            self._render_section('improvements', current_data, previous_data, selected_metric)
        
        with concerns_col:
            self._render_section('concerns', current_data, previous_data, selected_metric)
    
    def render_map_and_top_entities(self, data: gpd.GeoDataFrame, selected_year: int, selected_month: int, selected_metric: str):
        """Render map and top entities charts with maximized map size"""
        map_col, chart_col = st.columns([7, 3])
        
        with map_col:
            map_fig = self.map_viz.create_choropleth_map(data, selected_year, selected_month, selected_metric)
            st.plotly_chart(map_fig, use_container_width=True)
        
        with chart_col:
            top_entities_fig = self.chart_viz.create_top_entities_chart(data, selected_year, selected_month, selected_metric)
            st.plotly_chart(top_entities_fig, use_container_width=True)
    
    def render_detailed_analysis(self, data: gpd.GeoDataFrame, selected_entities: List[str], selected_metric: str, selected_year: int, selected_month: int):
        """Render detailed analysis section without headers"""
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            self._render_trends_section(data, selected_entities, selected_metric)
        
        with col_right:
            self._render_priority_analysis(data, selected_year, selected_month)
    
    # === PRIVATE HELPER METHODS ===
    
    def _calculate_overview_metrics(self, data) -> dict:
        """Calculate overview metrics for current dashboard type"""
        if data is None or data.empty:
            return {}
        
        if self.dashboard_type == "Districts":
            total_cases = data['all cases'].sum()
            total_population = data['Population'].sum()
            incidence = (total_cases / total_population * 1000) if total_population > 0 else 0
            severe_cases = data['Severe cases/Deaths'].sum()
            return {'total_cases': total_cases, 'incidence': incidence, 'severe_cases': severe_cases}
        else:
            simple_cases = data['Simple malaria cases'].sum()
            total_population = data['Population'].sum()
            incidence = (simple_cases / total_population * 1000) if total_population > 0 else 0
            return {'simple_cases': simple_cases, 'incidence': incidence}
    
    def _calculate_delta(self, current_metrics: dict, previous_metrics: dict, key: str, fmt: str) -> str:
        """Calculate delta between current and previous metrics"""
        if not previous_metrics:
            return ""
        
        current_val = current_metrics.get(key, 0)
        previous_val = previous_metrics.get(key, 0)
        change = current_val - previous_val
        
        # Fix the formatting logic
        if fmt == ":,.0f":
            return f"Δ {'+' if change >= 0 else ''}{change:,.0f}"
        elif fmt == ":.1f":
            return f"Δ {'+' if change >= 0 else ''}{change:.1f}"
        else:
            return f"Δ {'+' if change >= 0 else ''}{change:.1f}"
    
    def _render_section(self, section_type: str, current_data, previous_data, selected_metric: str):
        """Universal method to render any color-coded section"""
        colors = self.SECTION_COLORS[section_type]
        
        if section_type == 'status':
            header = "🔵 CURRENT STATUS"
            content = self._build_status_content(current_data, previous_data)
        elif section_type == 'improvements':
            header = "🟢 TOP 3 IMPROVEMENTS" 
            content = self._build_performance_content(current_data, previous_data, selected_metric, 'improvements')
        else:  # concerns
            header = "🔴 TOP 3 CONCERNS"
            content = self._build_performance_content(current_data, previous_data, selected_metric, 'concerns')
        
        section_html = self.SECTION_TEMPLATE.format(
            bg_start=colors['bg_start'], bg_end=colors['bg_end'], 
            border_color=colors['border_color'], header=header, content=content
        )
        
        st.markdown(section_html, unsafe_allow_html=True)
    
    def _build_status_content(self, current_data, previous_data) -> str:
        """Build content for status section"""
        current_metrics = self._calculate_overview_metrics(current_data)
        previous_metrics = self._calculate_overview_metrics(previous_data)
        
        content = ""
        
        if self.dashboard_type == "Districts":
            metrics_config = [
                ("🦟", "Total Cases", "total_cases", ":,.0f"),
                ("📈", "Incidence", "incidence", ":.1f"),
                ("⚠️", "Severe Cases", "severe_cases", ":,.0f")
            ]
        else:
            metrics_config = [
                ("🦟", "Simple Cases", "simple_cases", ":,.0f"),
                ("📊", "Incidence", "incidence", ":.1f")
            ]
        
        for i, (icon, label, key, fmt) in enumerate(metrics_config):
            current_val = current_metrics.get(key, 0) if current_metrics else 0
            delta = self._calculate_delta(current_metrics, previous_metrics, key, fmt)
            
            border_style = "border-bottom: 1px solid rgba(255,255,255,0.2);" if i < len(metrics_config) - 1 else ""
            
            # Fix the formatting issue
            if fmt == ":,.0f":
                formatted_value = f"{current_val:,.0f}"
            elif fmt == ":.1f":
                formatted_value = f"{current_val:.1f}"
            else:
                formatted_value = str(current_val)
            
            content += self.METRIC_ITEM_TEMPLATE.format(
                icon=icon, label=label, value=formatted_value,
                delta=delta, border_style=border_style
            )
        
        return content
    
    def _build_performance_content(self, current_data, previous_data, selected_metric: str, performance_type: str) -> str:
        """Build content for performance sections"""
        if previous_data is None or previous_data.empty or current_data.empty:
            return '<div style="text-align: center; opacity: 0.7; color: white;">No comparison data</div>'
        
        performance_data = self._get_performance_data(current_data, previous_data, selected_metric, performance_type)
        
        if performance_data.empty:
            message = "No improvements detected" if performance_type == 'improvements' else "No concerns detected"
            return f'<div style="text-align: center; opacity: 0.7; color: white;">{message}</div>'
        
        content = ""
        arrow = "↓" if performance_type == 'improvements' else "↑"
        sign = "-" if performance_type == 'improvements' else "+"
        
        for _, row in performance_data.iterrows():
            change = abs(row['absolute_change']) if performance_type == 'improvements' else row['absolute_change']
            entity_name = row['entity'][:17] + "..." if len(row['entity']) > 20 else row['entity']
            
            content += self.PERFORMANCE_ITEM_TEMPLATE.format(
                arrow=arrow, entity=entity_name, change=f"{sign}{change:.0f}"
            )
        
        return content
    
    def _get_performance_data(self, current_data, previous_data, selected_metric: str, performance_type: str):
        """Get performance data for improvements or concerns"""
        entity_col = 'District' if self.dashboard_type == "Districts" else 'Sector'
        
        # Prepare data based on dashboard type
        if self.dashboard_type == "Sectors" and 'sector_display' in current_data.columns:
            current_summary = current_data.groupby('sector_display')[selected_metric].sum().reset_index()
            previous_summary = previous_data.groupby('sector_display')[selected_metric].sum().reset_index()
        else:
            current_summary = current_data.groupby(entity_col)[selected_metric].sum().reset_index()
            previous_summary = previous_data.groupby(entity_col)[selected_metric].sum().reset_index()
        
        current_summary.columns = ['entity', 'current_value']
        previous_summary.columns = ['entity', 'previous_value']
        
        # Calculate changes
        comparison = current_summary.merge(previous_summary, on='entity', how='inner')
        comparison['absolute_change'] = comparison['current_value'] - comparison['previous_value']
        comparison = comparison[comparison['absolute_change'] != 0]
        
        # Return top 3 based on performance type
        if performance_type == 'improvements':
            return comparison.nsmallest(3, 'absolute_change')
        else:
            return comparison.nlargest(3, 'absolute_change')
    
    def _render_trends_section(self, data: gpd.GeoDataFrame, selected_entities: List[str], selected_metric: str):
        """Render trends over time section without header"""
        if selected_entities:
            trend_fig = self.chart_viz.create_trend_chart(data, selected_entities, selected_metric)
            if trend_fig:
                st.plotly_chart(trend_fig, use_container_width=True)
        else:
            entity_type = "districts" if self.dashboard_type == "Districts" else "sectors"
            st.info(f"👈 Select {entity_type} from the controls above to view trends over time")
    
    def _render_priority_analysis(self, data: gpd.GeoDataFrame, selected_year: int, selected_month: int):
        """Render priority analysis section without header"""
        scatterplot_fig, threshold1, threshold2 = self.chart_viz.create_scatterplot(data, selected_year, selected_month)
        if scatterplot_fig:
            st.plotly_chart(scatterplot_fig, use_container_width=True)
            self._render_interpretation_guide()
    
    def _render_interpretation_guide(self):
        """Render interpretation guide based on dashboard type"""
        if self.dashboard_type == "Districts":
            st.markdown("""
            **🧭 Quadrant Interpretation Guide:**
            | Color | Quadrant | Policy |
            |-------|----------|--------|
            | 🟥 Red | **High cases & High severity** | Intensify control and emergency response |
            | 🟧 Orange | **Low cases & High severity** | Improve treatment and case detection |
            | 🟨 Yellow | **High cases & Low severity** | Boost prevention and community outreach |
            | 🟩 Green | **Low cases & Low severity** | Maintain measures and routine monitoring |
            """)
        else:
            st.markdown("""
            **🧭 Action Plan Based on Zones:**
            | Color | Quadrant | Recommended Intervention Strategy |
            |-------|----------|-----------------------------------|
            | 🟥 Red | **High Population & High Cases** | Scale-up full response: mass testing, bed nets, active case management |
            | 🟧 Orange | **Low Population & High Cases** | Targeted interventions: hotspot investigation, focused spraying |
            | 🟨 Yellow | **High Population & Low Cases** | Sustain preventive efforts: routine testing, community education |
            | 🟩 Green | **Low Population & Low Cases** | Low-risk zones: periodic monitoring and minimal resource input |
            """)

class MainDashboard:
    """Main dashboard orchestrator"""
    
    def __init__(self):
        self.config = DashboardConfig()
        self.district_loader = MalariaDataLoader()
        self.sector_loader = SectorDataLoader()
        self.current_dashboard_type = "Districts"
        self.current_data = None
        self.current_entity_options = None
        
    def initialize(self):
        """Initialize the dashboard"""
        self.config.setup_page()
        self.config.apply_custom_css()
    
    def load_data(self, dashboard_type: str):
        """Load data based on dashboard type"""
        if dashboard_type == "Districts":
            data, entity_options = self.district_loader.load_data()
        else:
            data, entity_options = self.sector_loader.load_data()
        
        if data is None:
            st.error("Failed to load data. Please check your data files.")
            st.stop()
        
        return data, entity_options
    
    def setup_components(self, dashboard_type: str, data: gpd.GeoDataFrame):
        """Setup dashboard components"""
        metrics_calculator = MetricsCalculator(dashboard_type)
        
        # Debug: Print dashboard type to verify
        print(f"Setting up components for: {dashboard_type}")
        print(f"Available metrics: {metrics_calculator.get_available_metrics()}")
        
        map_viz = MapVisualizations(dashboard_type, metrics_calculator)
        chart_viz = ChartVisualizations(dashboard_type, metrics_calculator)
        ui = DashboardUI(dashboard_type, metrics_calculator, map_viz, chart_viz)
        
        return metrics_calculator, map_viz, chart_viz, ui, data
    
    def run(self):
        """Main dashboard execution"""
        self.initialize()
        
        # Create tabs for Districts and Sectors
        tab1, tab2 = st.tabs(["🏘️ Districts", "🏭 Sectors"])
        
        with tab1:
            self._run_dashboard_tab("Districts")
        
        with tab2:
            self._run_dashboard_tab("Sectors")
    
    def _run_dashboard_tab(self, dashboard_type: str):
        """Run dashboard for specific tab with main area controls"""
        # Load data
        data, entity_options = self.load_data(dashboard_type)
        
        # Setup components
        metrics_calculator, map_viz, chart_viz, ui, data = self.setup_components(dashboard_type, data)
        
        # Render header
        ui.render_header()
        
        # Render controls in MAIN AREA instead of sidebar
        selected_year, selected_month, selected_metric, selected_entities = ui.render_controls_in_main_area(data, entity_options)
        
        # Filter data by year and month for maps and top charts
        filtered_data = data[(data['year'] == selected_year) & (data['month'] == selected_month)]
        
        # Get previous month data for comparison
        if selected_month == 1:
            # If January, compare with December of previous year
            prev_month = 12
            prev_year = selected_year - 1
        else:
            # Otherwise, compare with previous month of same year
            prev_month = selected_month - 1
            prev_year = selected_year
        
        previous_data = data[(data['year'] == prev_year) & (data['month'] == prev_month)]
        
        # Debug: Check if filtered data is empty
        if filtered_data.empty:
            st.warning(f"No data found for {selected_year}-{selected_month:02d}. Please select a different time period.")
            return
        
        # First Row: Color-coded overview with all key information
        ui.render_color_coded_overview(filtered_data, previous_data, selected_year, selected_month, selected_metric)
        
        # Second Row: Map and top entities (using filtered data) - Map maximized
        ui.render_map_and_top_entities(filtered_data, selected_year, selected_month, selected_metric)
        
        # Third Row: Detailed analysis (using all data for trends, current month for scatterplot)
        ui.render_detailed_analysis(data, selected_entities, selected_metric, selected_year, selected_month)

# Main execution
def main():
    """Main function to run the dashboard"""
    dashboard = MainDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
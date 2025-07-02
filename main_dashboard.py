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
            initial_sidebar_state="expanded"
        )
    
    @staticmethod
    def apply_custom_css():
        """Apply custom CSS for dark mode and professional styling"""
        st.markdown("""
        <style>
            /* Dark theme for main app */
            .stApp {
                background-color: #1E1E1E !important;
                color: #FFFFFF !important;
            }
            
            /* Main content area */
            .main .block-container {
                background-color: #1E1E1E !important;
                color: #FFFFFF !important;
            }
            
            /* Content blocks */
            .element-container {
                background-color: transparent !important;
            }
            
            /* Dark sidebar */
            .css-1d391kg {
                background-color: #2D2D2D !important;
            }
            
            /* Main header */
            .main-header {
                text-align: center;
                padding: 1.5rem 0;
                margin-bottom: 2rem;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
                color: white;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                border: 1px solid #333333;
            }
            
            .dashboard-title {
                font-size: 2.2rem;
                font-weight: 600;
                color: #FFFFFF;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
                letter-spacing: 0.5px;
            }
            
            /* Dark theme cards */
            .metric-card {
                background: #2D2D2D !important;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                margin-bottom: 1rem;
                border: 1px solid #404040;
                color: #FFFFFF !important;
            }
            
            /* Status borders for dark theme */
            .status-improved { border-left: 4px solid #4CAF50; }
            .status-concern { border-left: 4px solid #F44336; }
            .status-current { border-left: 4px solid #2196F3; }
            
            /* Dark theme for sidebar */
            .css-1d391kg, .css-1lcbmhc, .css-17eq0hr {
                background-color: #2D2D2D !important;
                color: #FFFFFF !important;
            }
            
            /* Dark theme for selectbox and other inputs */
            .stSelectbox > div > div {
                background-color: #404040 !important;
                color: #FFFFFF !important;
                border: 1px solid #666666 !important;
            }
            
            /* Dark theme for radio buttons */
            .stRadio > div {
                background-color: #2D2D2D !important;
                color: #FFFFFF !important;
            }
            
            /* Dark theme for text elements */
            .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, div {
                color: #FFFFFF !important;
            }
            
            /* Sidebar buttons */
            .stButton > button {
                width: 100%;
                text-align: left;
                background-color: transparent;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin-bottom: 0.25rem;
                transition: all 0.2s ease;
                color: white;
            }
            
            .stButton > button:hover {
                background-color: #FF6B6B;
                color: white;
                border-color: #FF6B6B;
            }
            
            /* Filter container styling */
            .filter-container {
                background: #2a2a2a;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 2rem;
                border: 1px solid #444;
            }
            
            /* Text areas and inputs */
            .stTextArea > div > div > textarea {
                background-color: #404040 !important;
                color: #FFFFFF !important;
                border: 1px solid #666666 !important;
            }
            
            /* Metrics containers */
            [data-testid="metric-container"] {
                background-color: #2D2D2D !important;
                border: 1px solid #404040 !important;
                padding: 0.5rem;
                border-radius: 0.25rem;
                color: white !important;
            }
            
            /* Info boxes */
            .stInfo {
                background-color: #e3f2fd !important;
                border-left: 4px solid #2196f3 !important;
            }
            
            /* Success boxes */
            .stSuccess {
                background-color: #e8f5e8 !important;
                border-left: 4px solid #4caf50 !important;
            }
            
            /* Warning boxes */
            .stWarning {
                background-color: #fff3e0 !important;
                border-left: 4px solid #ff9800 !important;
            }
            
            /* Error boxes */
            .stError {
                background-color: #ffebee !important;
                border-left: 4px solid #f44336 !important;
            }
        </style>
        """, unsafe_allow_html=True)

class MainDashboard:
    """Main dashboard orchestrator"""
    
    def __init__(self):
        self.config = DashboardConfig()
        self.district_loader = MalariaDataLoader()
        self.sector_loader = SectorDataLoader()
        
        # Initialize session state
        if 'admin_level' not in st.session_state:
            st.session_state.admin_level = 'districts'
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
    
    def initialize(self):
        """Initialize the dashboard"""
        self.config.setup_page()
        self.config.apply_custom_css()
    
    def get_available_metrics_for_data(self, data):
        """Automatically detect available metrics based on data columns"""
        columns = data.columns.tolist()
        
        if 'all cases' in columns and 'Severe cases/Deaths' in columns:
            # District data
            return {
                "all cases": "Total Cases",
                "Severe cases/Deaths": "Severe Cases/Deaths", 
                "all cases incidence": "Cases Incidence Rate"
            }
        elif 'Simple malaria cases' in columns and 'incidence' in columns:
            # Sector data
            return {
                "Simple malaria cases": "Simple Malaria Cases",
                "incidence": "Incidence Rate"
            }
        else:
            # Fallback - return what's available
            available_metrics = {}
            if 'all cases' in columns:
                available_metrics['all cases'] = 'All Cases'
            if 'Simple malaria cases' in columns:
                available_metrics['Simple malaria cases'] = 'Simple Malaria Cases'
            if 'incidence' in columns:
                available_metrics['incidence'] = 'Incidence'
            return available_metrics or {"Population": "Population"}  # Ultimate fallback
    
    def get_default_metric_for_data(self, data):
        """Get the best default metric for the current data"""
        columns = data.columns.tolist()
        
        if 'all cases' in columns:
            return 'all cases'
        elif 'Simple malaria cases' in columns:
            return 'Simple malaria cases'
        elif 'incidence' in columns:
            return 'incidence'
        else:
            return 'Population'  # Ultimate fallback
    
    def render_header(self):
        """Render the professional header with centered logo"""
        logo_base64 = self.get_logo_base64()
        
        if logo_base64:
            # Header with logo - simple and clean
            header_html = f"""
            <div class="main-header">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <img src="data:image/png;base64,{logo_base64}" alt="Health Intelligence Center - Rwanda Ministry of Health" 
                         style="height: 100px; width: auto; margin-bottom: 1rem;">
                </div>
                <div class="dashboard-title">Rwanda Malaria Surveillance Dashboard</div>
            </div>
            """
        else:
            # Header without logo (fallback)
            header_html = """
            <div class="main-header">
                <div class="dashboard-title">Rwanda Malaria Surveillance Dashboard</div>
            </div>
            """
        
        st.markdown(header_html, unsafe_allow_html=True)
    
    def get_logo_base64(self):
        """Get logo as base64 string - loads your HIC_logo.png"""
        import base64
        import os
        
        # Your actual logo file path
        logo_path = "assets/HIC_logo.png"
        
        try:
            if os.path.exists(logo_path):
                print(f"✅ Loading logo from: {logo_path}")
                with open(logo_path, "rb") as f:
                    logo_data = f.read()
                return base64.b64encode(logo_data).decode()
            else:
                print(f"❌ Logo not found at: {logo_path}")
                return ""
        except Exception as e:
            print(f"❌ Error loading logo: {e}")
            return ""
    
    def render_sidebar_navigation(self):
        """Render sidebar navigation"""
        st.sidebar.markdown("## Administrative Level")
        
        # Administrative level selection
        admin_level = st.sidebar.radio(
            "Select Administrative Level",
            ['districts', 'sectors'],
            format_func=lambda x: '📍 Districts' if x == 'districts' else '🏘️ Sectors',
            key='admin_level_radio'
        )
        st.session_state.admin_level = admin_level
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"## {admin_level.title()} Analysis")
        
        # Navigation menu
        page_options = {
            'dashboard': 'Dashboard & Analytics',
            'trends': 'Trends & Insights',
            'assistant': 'AI Assistant'
        }
        
        # Navigation buttons
        for page_key, page_label in page_options.items():
            if st.sidebar.button(page_label, key=f"{page_key}_{admin_level}"):
                st.session_state.current_page = page_key
                st.rerun()
    
    def load_data(self, dashboard_type: str):
        """Load data based on dashboard type"""
        if dashboard_type == "districts":
            data, entity_options = self.district_loader.load_data()
            display_type = "Districts"
        else:
            data, entity_options = self.sector_loader.load_data()
            display_type = "Sectors"
        
        if data is None:
            st.error("Failed to load data. Please check your data files.")
            st.stop()
        
        return data, entity_options, display_type
    
    def setup_components(self, dashboard_type: str, data: gpd.GeoDataFrame):
        """Setup dashboard components"""
        display_type = "Districts" if dashboard_type == "districts" else "Sectors"
        metrics_calculator = MetricsCalculator(display_type)
        map_viz = MapVisualizations(display_type, metrics_calculator)
        chart_viz = ChartVisualizations(display_type, metrics_calculator)
        
        return metrics_calculator, map_viz, chart_viz, display_type
    
    def render_global_filters(self, data: gpd.GeoDataFrame, admin_level: str) -> Tuple[int, int, str, dict]:
        """Render global filters with dynamic metric detection"""
        st.markdown("## Filters")
        
        with st.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                available_years = sorted(data['year'].unique(), reverse=True)
                selected_year = st.selectbox(
                    "Year",
                    available_years,
                    key=f"year_{admin_level}_{st.session_state.current_page}"
                )
            
            with col2:
                available_months = sorted(data[data['year'] == selected_year]['month'].unique())
                month_names = {
                    1: "January", 2: "February", 3: "March", 4: "April", 
                    5: "May", 6: "June", 7: "July", 8: "August",
                    9: "September", 10: "October", 11: "November", 12: "December"
                }
                
                if available_months:
                    selected_month = st.selectbox(
                        "Month",
                        available_months,
                        format_func=lambda x: month_names.get(x, str(x)),
                        index=len(available_months)-1,  # Default to last available month
                        key=f"month_{admin_level}_{st.session_state.current_page}"
                    )
                else:
                    selected_month = 1
            
            with col3:
                # DYNAMIC METRIC DETECTION
                metric_options = self.get_available_metrics_for_data(data)
                
                selected_metric = st.selectbox(
                    "Primary Metric",
                    list(metric_options.keys()),
                    format_func=lambda x: metric_options[x],
                    key=f"metric_{admin_level}_{st.session_state.current_page}"
                )
        
        st.markdown("---")
        
        return selected_year, selected_month, selected_metric, metric_options
    
    def render_compact_overview_cards(self, current_data, prev_data, admin_level, selected_year, selected_month):
        """Render 3 compact overview cards"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self.render_current_status_card(current_data, prev_data, admin_level, selected_year, selected_month)
        
        with col2:
            self.render_top_improved_card(current_data, prev_data, admin_level)
        
        with col3:
            self.render_top_concerns_card(current_data, prev_data, admin_level)
    
    def render_current_status_card(self, current_data, prev_data, admin_level, selected_year, selected_month):
        """Render current status card with big numbers and centered period"""
        # Get month name
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April", 
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        month_name = month_names.get(selected_month, str(selected_month))
        
        # Centered period header
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h3 style="color: #2196F3; font-size: 1.5rem; margin: 0;">{month_name} {selected_year}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if admin_level == "districts":
            total_cases = current_data['all cases'].sum() if not current_data.empty else 0
            avg_incidence = current_data['all cases incidence'].mean() if not current_data.empty else 0
        else:
            total_cases = current_data['Simple malaria cases'].sum() if not current_data.empty else 0
            avg_incidence = current_data['incidence'].mean() if not current_data.empty else 0
        
        # Big numbers using Streamlit columns for better rendering
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Total Cases
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 3.5rem; font-weight: bold; color: #2196F3; margin-bottom: 0.2rem; line-height: 1;">
                    {int(total_cases):,}
                </div>
                <div style="font-size: 0.9rem; color: #888;">
                    {"Total Cases" if admin_level == "districts" else "Simple Cases"}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Incidence
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="font-size: 3.5rem; font-weight: bold; color: #FF9800; margin-bottom: 0.2rem; line-height: 1;">
                    {avg_incidence:.1f}
                </div>
                <div style="font-size: 0.9rem; color: #888;">
                    Incidence
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_top_improved_card(self, current_data, prev_data, admin_level):
        """Render top improved areas card"""
        st.markdown("### Top 3 Most Improved")
        
        if prev_data.empty or current_data.empty:
            st.info("No comparison data")
            return
        
        entity_col = 'District' if admin_level == 'districts' else 'Sector'
        metric_col = 'all cases' if admin_level == 'districts' else 'Simple malaria cases'
        
        # Calculate improvements
        improvements = self.calculate_entity_changes(current_data, prev_data, entity_col, metric_col)
        top_improved = improvements.nsmallest(3, 'change')  # Smallest change (most improved)
        
        for i, (_, row) in enumerate(top_improved.iterrows()):
            change_val = row['change']
            entity_name = row[entity_col][:15] + "..." if len(row[entity_col]) > 18 else row[entity_col]
            
            if change_val < 0:
                st.success(f"**{i+1}. {entity_name}** {change_val:.0f}")
            else:
                st.info(f"**{i+1}. {entity_name}** {change_val:+.0f}")
    
    def render_top_concerns_card(self, current_data, prev_data, admin_level):
        """Render top concerns card"""
        st.markdown("### Top 3 Concerns")
        
        if prev_data.empty or current_data.empty:
            st.info("No comparison data")
            return
        
        entity_col = 'District' if admin_level == 'districts' else 'Sector'
        metric_col = 'all cases' if admin_level == 'districts' else 'Simple malaria cases'
        
        # Calculate concerns
        concerns = self.calculate_entity_changes(current_data, prev_data, entity_col, metric_col)
        top_concerns = concerns.nlargest(3, 'change')  # Largest change (most concerning)
        
        for i, (_, row) in enumerate(top_concerns.iterrows()):
            change_val = row['change']
            entity_name = row[entity_col][:15] + "..." if len(row[entity_col]) > 18 else row[entity_col]
            
            if change_val > 0:
                st.error(f"**{i+1}. {entity_name}** +{change_val:.0f}")
            else:
                st.success(f"**{i+1}. {entity_name}** {change_val:.0f}")
    
    def calculate_entity_changes(self, current_data, prev_data, entity_col, metric_col):
        """Calculate changes between current and previous data"""
        current_summary = current_data.groupby(entity_col)[metric_col].sum().reset_index()
        prev_summary = prev_data.groupby(entity_col)[metric_col].sum().reset_index()
        
        current_summary.columns = ['entity', 'current_value']
        prev_summary.columns = ['entity', 'previous_value']
        
        merged = current_summary.merge(prev_summary, on='entity', how='inner')
        merged['change'] = merged['current_value'] - merged['previous_value']
        merged[entity_col] = merged['entity']
        
        return merged[merged['change'] != 0]
    
    def render_dashboard_page(self, data, entity_options, display_type, components):
        """Render Dashboard & Geographic Analysis page"""
        metrics_calculator, map_viz, chart_viz, _ = components
        
        st.markdown(f"# {st.session_state.admin_level.title()} Dashboard & Geographic Analysis")
        st.markdown(f"Comprehensive overview with spatial analysis across Rwanda's {st.session_state.admin_level}")
        
        # Global filters - ONLY ON DASHBOARD PAGE
        selected_year, selected_month, selected_metric, metric_options = self.render_global_filters(data, st.session_state.admin_level)
        
        # Filter current and previous data
        current_data = data[(data['year'] == selected_year) & (data['month'] == selected_month)]
        
        # Get previous month data
        if selected_month == 1:
            prev_month, prev_year = 12, selected_year - 1
        else:
            prev_month, prev_year = selected_month - 1, selected_year
        
        prev_data = data[(data['year'] == prev_year) & (data['month'] == prev_month)]
        
        if current_data.empty:
            st.error(f"No data available for the selected period.")
            return
        
        # Store selections in session state for other pages
        st.session_state.dashboard_year = selected_year
        st.session_state.dashboard_month = selected_month
        st.session_state.dashboard_metric = selected_metric
        st.session_state.dashboard_metric_options = metric_options
        
        # Compact overview cards
        self.render_compact_overview_cards(current_data, prev_data, st.session_state.admin_level, selected_year, selected_month)
        
        st.markdown("---")
        
        # Map and top entities layout
        col1, col2 = st.columns([7, 3])
        
        with col1:
            st.markdown(f"### Geographic Distribution - {metric_options[selected_metric]}")
            map_fig = map_viz.create_choropleth_map(data, selected_year, selected_month, selected_metric)
            st.plotly_chart(map_fig, use_container_width=True)
        
        with col2:
            st.markdown(f"### Top 10 {display_type}")
            top_entities_fig = chart_viz.create_top_entities_chart(data, selected_year, selected_month, selected_metric)
            st.plotly_chart(top_entities_fig, use_container_width=True)
    
    def render_trends_page(self, data, entity_options, display_type, components):
        """Render Trends & Insights page"""
        metrics_calculator, map_viz, chart_viz, _ = components
        
        st.markdown(f"# Trends & Insights")
        st.markdown(f"Historical trends and strategic priority assessment for {st.session_state.admin_level}")
        
        # Use dashboard filters if available, otherwise use defaults
        if hasattr(st.session_state, 'dashboard_year'):
            selected_year = st.session_state.dashboard_year
            selected_month = st.session_state.dashboard_month
            selected_metric = st.session_state.dashboard_metric
            metric_options = st.session_state.dashboard_metric_options
        else:
            # FLEXIBLE DEFAULT VALUES - auto-detect based on actual data
            selected_year = data['year'].max()
            selected_month = data[data['year'] == selected_year]['month'].max()
            metric_options = self.get_available_metrics_for_data(data)
            selected_metric = self.get_default_metric_for_data(data)
        
        # Two-column layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Historical Trends")
            
            # Get default entities (top 3 by latest data)
            default_entities = []
            if not data.empty and entity_options:
                latest_data = data[data['year'] == data['year'].max()]
                if not latest_data.empty:
                    latest_month_data = latest_data[latest_data['month'] == latest_data['month'].max()]
                    
                    if st.session_state.admin_level == "districts":
                        entity_col = 'District'
                        metric_for_default = self.get_default_metric_for_data(data)
                    else:
                        entity_col = 'Sector'
                        metric_for_default = self.get_default_metric_for_data(data)
                    
                    if entity_col in latest_month_data.columns and metric_for_default in latest_month_data.columns:
                        # Get top 3 entities as default, but ensure they exist in entity_options
                        top_entities = latest_month_data.nlargest(3, metric_for_default)[entity_col].tolist()
                        default_entities = [entity for entity in top_entities if entity in entity_options][:3]
                
                # If no valid defaults found, use first 3 from entity_options
                if not default_entities and entity_options:
                    default_entities = entity_options[:3]
            
            # Entity selection
            selected_entities = st.multiselect(
                f"Select {display_type} (max 5)",
                entity_options,
                default=default_entities,
                max_selections=5,
                key=f"trend_entities_{st.session_state.admin_level}"
            )
            
            if selected_entities:
                trend_fig = chart_viz.create_trend_chart(data, selected_entities, selected_metric)
                if trend_fig:
                    st.plotly_chart(trend_fig, use_container_width=True)
            else:
                st.info(f"Please select {display_type.lower()} to view trends")
        
        with col2:
            st.markdown("### Priority Analysis")
            
            # Get current month data for scatterplot
            current_data = data[(data['year'] == selected_year) & (data['month'] == selected_month)]
            
            if not current_data.empty:
                scatterplot_fig, threshold1, threshold2 = chart_viz.create_scatterplot(data, selected_year, selected_month)
                if scatterplot_fig:
                    st.plotly_chart(scatterplot_fig, use_container_width=True)
                    
                    # Interpretation guide
                    self.render_interpretation_guide(st.session_state.admin_level)
    
    def render_interpretation_guide(self, admin_level):
        """Render interpretation guide"""
        if admin_level == "districts":
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
    
    def render_assistant_page(self, data, selected_year, selected_month):
        """Enhanced AI Assistant with RAG + Local AI"""
        
        # Use dashboard filters if available
        if hasattr(st.session_state, 'dashboard_year'):
            year = st.session_state.dashboard_year
            month = st.session_state.dashboard_month
        else:
            year = data['year'].max()
            month = data[data['year'] == year]['month'].max()
        
        try:
            # Use your enhanced malaria_bot.py
            from malaria_bot import render_ai_assistant_page
            render_ai_assistant_page(data, st.session_state.admin_level, year, month)
            
        except ImportError as e:
            st.error(f"AI Assistant module not found: {e}")
            st.info("Please ensure malaria_bot.py is in the same directory")
    
    def run(self):
        """Main dashboard execution"""
        self.initialize()
        self.render_header()
        self.render_sidebar_navigation()
        
        # Load data based on current selection
        data, entity_options, display_type = self.load_data(st.session_state.admin_level)
        components = self.setup_components(st.session_state.admin_level, data)
        
        # Render selected page
        if st.session_state.current_page == 'dashboard':
            self.render_dashboard_page(data, entity_options, display_type, components)
        elif st.session_state.current_page == 'trends':
            self.render_trends_page(data, entity_options, display_type, components)
        elif st.session_state.current_page == 'assistant':
            self.render_assistant_page(data, None, None)  # Will use dashboard filters internally

# Main execution
def main():
    """Main function to run the dashboard"""
    dashboard = MainDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
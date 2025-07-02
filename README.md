# 🦟 Rwanda Malaria Dashboard

A comprehensive interactive dashboard for monitoring malaria cases and trends across Rwanda's districts and sectors.

## 🌟 Features

### 🏘️ Districts Dashboard
- **Interactive Maps**: Choropleth visualizations of malaria cases and incidence
- **Time Series Analysis**: Track trends over months and years
- **Top Performers**: Identify districts with highest case loads
- **Quadrant Analysis**: Population vs severity scatter plots for priority setting

### 🏭 Sectors Dashboard  
- **Sector-Level Monitoring**: Detailed analysis at the sector level
- **Population-Based Metrics**: Incidence calculations per 1,000 people
- **Comparative Analysis**: Multi-sector trend comparisons
- **Hotspot Identification**: Geographic concentration of cases

### 🎛️ Interactive Controls
- **Collapsible Side Panels**: Independent controls for districts (left) and sectors (right)
- **Time Period Selection**: Year and month sliders
- **Metric Selection**: Multiple malaria indicators
- **Entity Comparison**: Multi-select for trend analysis

## 🗂️ Data Sources

The dashboard analyzes:
- **District-level malaria data**: Cases, severity, incidence rates
- **Sector-level malaria data**: Simple cases and population-based incidence
- **Geographic boundaries**: GeoJSON files for mapping
- **Time series**: Monthly data across multiple years

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, GeoPandas
- **Visualizations**: Plotly
- **Geospatial**: Fiona, Shapely, PyProj
- **Deployment**: Streamlit Cloud

## 🚀 Live Demo

[**View Live Dashboard**](https://eulademuhizi-malaria-district-sector-dashboard-main-dashboard.streamlit.app/) *(Coming Soon)*

## 💻 Local Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/eulademuhizi/Malaria_district_sector_dashboard.git
   cd Malaria_district_sector_dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run main_dashboard.py
   ```

4. **Open your browser** to `http://localhost:8501`

## 📊 How to Use

### Getting Started
1. **Open Control Panels**: Click "🏘️ Districts Panel" or "🏭 Sectors Panel" buttons
2. **Select Time Period**: Use year and month sliders
3. **Choose Metrics**: Select from available malaria indicators
4. **Compare Entities**: Multi-select districts or sectors for trend analysis
5. **Analyze Results**: View maps, charts, and performance quadrants

### Dashboard Navigation
- **Overview Sections**: Current status, improvements, and concerns
- **Interactive Maps**: Click and hover for detailed information
- **Trend Charts**: Compare multiple entities over time
- **Scatter Plots**: Identify priority areas using quadrant analysis

## 📁 Project Structure

```
├── main_dashboard.py           # Main application entry point
├── data_loader.py             # Data loading and preprocessing
├── metrics_calculator.py      # Metric calculations and caching
├── map_visualizations.py      # Choropleth map components
├── chart_visualizations.py    # Chart and graph components
├── requirements.txt           # Python dependencies
├── data/                      # Data directory
│   ├── district_malaria_data.csv
│   ├── sector_malaria_data.csv
│   ├── district_geometries.geojson
│   └── sector_geometries.geojson
└── README.md                  # This file
```

## 🎯 Key Insights

### Districts Analysis
- **Quadrant Interpretation**: 
  - 🟥 High cases & severity → Intensive response needed
  - 🟧 Low cases & severity → Improve treatment quality
  - 🟨 High cases & low severity → Boost prevention
  - 🟩 Low cases & severity → Maintain measures

### Sectors Analysis
- **Action Zones**:
  - 🟥 High population & cases → Scale-up response
  - 🟧 Low population & cases → Targeted interventions
  - 🟨 High population & low cases → Sustain prevention
  - 🟩 Low population & cases → Routine monitoring

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


- **Project Maintainer**: Eulade muhizi
- **Email**: eulademuhizi@andrew.cmu.edu
- **GitHub**: [@eulademuhizi](https://github.com/eulademuhizi)

## 🙏 Acknowledgments

- Rwanda Ministry of Health for data standards
- Health Intelligence Center for project coordination
- Carnegie Mellon University for academic support

---

**Built with ❤️ for public health in Rwanda**
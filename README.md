# Geospatial Analytics Dashboard

A professional geospatial dashboard with interactive maps, data visualizations, and tables built with Streamlit.

## Features

- Interactive map views with Folium and Plotly
- Data analysis charts and visualizations
- Interactive data tables with filtering options
- Support for various geospatial file formats (GeoJSON, Shapefiles, CSV)
- Sample datasets for exploration
- Filtering and data analysis tools

## Installation

### 1. Set up environment

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install dependencies

Install all required packages:

```bash
pip install streamlit>=1.44.1 folium>=0.19.5 geopandas>=1.0.1 streamlit-folium>=0.25.0 plotly>=6.0.1 pyogrio>=0.10.0
```

## Running the Application

```bash
streamlit run app.py
```

The application will start and open in your default web browser at http://localhost:8501.

## Project Structure

- `app.py`: Main application entry point
- `components/`: UI components
  - `sidebar.py`: Dashboard sidebar with data selection and filters
  - `map_view.py`: Interactive map visualization
  - `charts.py`: Data analysis charts
  - `data_table.py`: Interactive data tables
- `utils/`: Utility functions
  - `data_loader.py`: Functions for loading and processing data
  - `map_utils.py`: Map creation utilities
  - `chart_utils.py`: Chart creation utilities

## Supported File Formats

- GeoJSON (.geojson, .json)
- Shapefiles (.shp, requires supporting files)
- CSV files with latitude/longitude columns
- ZIP files containing shapefiles

## Notes for Shapefile Usage

Shapefiles require multiple files (.shp, .shx, .dbf) to work properly. For best results:
1. Upload a ZIP file containing all related shapefile components
2. Or ensure all required files are uploaded together

## Troubleshooting

If you encounter issues with geospatial dependencies (particularly on Windows):
1. Consider using conda to install geopandas and its dependencies
2. GDAL and other GIS libraries may require specific installation steps for your OS
3. Check the console for detailed error messages

## License

Open source, free to use and modify.

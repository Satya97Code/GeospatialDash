import streamlit as st
import pandas as pd
import geopandas as gpd
import os
from urllib.request import urlopen
import json
import tempfile
import io

def get_sample_datasets():
    """
    Return a list of sample geospatial datasets that users can choose from.
    Each dataset includes metadata and a URL to load from.
    """
    return [
        {
            "name": "US States",
            "description": "US States boundaries with population data",
            "path": "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
            "type": "geojson"
        },
        {
            "name": "World Countries",
            "description": "World countries with socioeconomic indicators",
            "path": "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json",
            "type": "geojson"
        },
        {
            "name": "NYC Boroughs",
            "description": "New York City boroughs with demographic data",
            "path": "https://raw.githubusercontent.com/nychealth/coronavirus-data/master/Geography-resources/MODZCTA_2010_WGS1984.geo.json",
            "type": "geojson"
        },
        {
            "name": "Global Earthquakes",
            "description": "Recent earthquake data from around the world",
            "path": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson",
            "type": "geojson"
        }
    ]

def load_data(path=None):
    """
    Load geospatial data from various sources:
    - URL for remote GeoJSON/Shapefile
    - User uploaded file
    - Local file path
    
    Returns GeoDataFrame or None if data can't be loaded
    """
    try:
        if path is not None:
            if path.startswith(('http://', 'https://')):
                # Handle remote data
                if path.endswith('.json') or path.endswith('.geojson'):
                    with urlopen(path) as response:
                        data = json.load(response)
                        gdf = gpd.GeoDataFrame.from_features(data["features"])
                        
                        # Generate random data if needed for visualization
                        if 'value' not in gdf.columns and len(gdf) > 0:
                            gdf['value'] = range(len(gdf))
                        
                        return gdf
                else:
                    # Other remote file types
                    temp_dir = tempfile.mkdtemp()
                    temp_file = os.path.join(temp_dir, "temp_data")
                    
                    with urlopen(path) as response, open(temp_file, 'wb') as out_file:
                        out_file.write(response.read())
                    
                    if path.endswith('.csv'):
                        df = pd.read_csv(temp_file)
                        # Try to convert to GeoDataFrame if it has coordinates
                        if all(col in df.columns for col in ['latitude', 'longitude']):
                            gdf = gpd.GeoDataFrame(
                                df, 
                                geometry=gpd.points_from_xy(df.longitude, df.latitude),
                                crs="EPSG:4326"
                            )
                            return gdf
                        return df
                    elif path.endswith('.shp'):
                        return gpd.read_file(temp_file)
            else:
                # Local file path
                if path.endswith(('.json', '.geojson')):
                    return gpd.read_file(path)
                elif path.endswith('.csv'):
                    df = pd.read_csv(path)
                    # Try to convert to GeoDataFrame if it has coordinates
                    if all(col in df.columns for col in ['latitude', 'longitude']):
                        gdf = gpd.GeoDataFrame(
                            df, 
                            geometry=gpd.points_from_xy(df.longitude, df.latitude),
                            crs="EPSG:4326"
                        )
                        return gdf
                    return df
                elif path.endswith('.shp'):
                    return gpd.read_file(path)
        
        # Default to returning None
        return None
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def handle_uploaded_file(uploaded_file):
    """
    Process uploaded geospatial data file
    """
    try:
        # Set GDAL configuration to restore .shx files if missing
        os.environ['SHAPE_RESTORE_SHX'] = 'YES'
        
        if uploaded_file.name.endswith(('.json', '.geojson')):
            # Parse GeoJSON
            content = uploaded_file.getvalue().decode()
            data = json.loads(content)
            gdf = gpd.GeoDataFrame.from_features(data["features"])
            return gdf
        
        elif uploaded_file.name.endswith('.csv'):
            # Parse CSV
            df = pd.read_csv(uploaded_file)
            
            # Check if it has coordinate columns
            if all(col in df.columns for col in ['latitude', 'longitude']):
                gdf = gpd.GeoDataFrame(
                    df, 
                    geometry=gpd.points_from_xy(df.longitude, df.latitude),
                    crs="EPSG:4326"
                )
                return gdf
            
            return df
        
        elif uploaded_file.name.endswith('.shp'):
            # For shapefiles, need to handle the related files (.dbf, .shx, etc.)
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    with open(os.path.join(tmpdir, uploaded_file.name), 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Apply extra options for shapefile reading
                    return gpd.read_file(
                        os.path.join(tmpdir, uploaded_file.name),
                        engine='pyogrio'  # Use the pyogrio engine which is more flexible
                    )
            except Exception as shape_error:
                st.error(f"Error loading shapefile: {str(shape_error)}")
                st.info("Shapefiles require multiple files (.shp, .shx, .dbf) to work properly. Make sure to upload all required files.")
                return None
        
        elif uploaded_file.name.endswith('.zip'):
            # Handle zip files containing shapefiles
            with tempfile.TemporaryDirectory() as tmpdir:
                # Save zip file
                zip_path = os.path.join(tmpdir, 'data.zip')
                with open(zip_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Extract zip file
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                
                # Find .shp files in the extracted directory
                shp_files = []
                for root, dirs, files in os.walk(tmpdir):
                    for file in files:
                        if file.endswith('.shp'):
                            shp_files.append(os.path.join(root, file))
                
                if shp_files:
                    # Use the first shapefile found
                    return gpd.read_file(shp_files[0])
                else:
                    st.error("No shapefile found in the uploaded zip file.")
                    return None
        
        else:
            st.error("Unsupported file format. Please upload a GeoJSON, Shapefile, CSV, or ZIP file containing shapefiles.")
            return None
    
    except Exception as e:
        st.error(f"Error processing the uploaded file: {str(e)}")
        return None

def filter_data(data, filters):
    """
    Apply filters to the dataset
    
    Parameters:
    - data: DataFrame or GeoDataFrame
    - filters: dict of column names and filter values
    
    Returns filtered data
    """
    if data is None or not filters:
        return data
    
    filtered_data = data.copy()
    for col, filter_val in filters.items():
        if col in filtered_data.columns:
            if isinstance(filter_val, tuple) and len(filter_val) == 2:
                # Range filter
                min_val, max_val = filter_val
                filtered_data = filtered_data[(filtered_data[col] >= min_val) & 
                                             (filtered_data[col] <= max_val)]
            elif isinstance(filter_val, list):
                # Multiple selection filter
                filtered_data = filtered_data[filtered_data[col].isin(filter_val)]
            else:
                # Single value filter
                filtered_data = filtered_data[filtered_data[col] == filter_val]
    
    return filtered_data

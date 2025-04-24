import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
from utils.map_utils import create_folium_map, create_plotly_map
from utils.data_loader import filter_data

def create_map_view(data):
    """
    Create an interactive map view based on data
    
    Parameters:
    - data: DataFrame or GeoDataFrame
    """
    # Apply any filters
    filtered_data = filter_data(data, st.session_state.filters) if hasattr(st.session_state, 'filters') else data
    
    # Check if we have valid data
    if filtered_data is None or len(filtered_data) == 0:
        st.warning("No data available to display on the map.")
        return
    
    # Convert to GeoDataFrame if it's not already
    if not isinstance(filtered_data, gpd.GeoDataFrame):
        if all(col in filtered_data.columns for col in ['latitude', 'longitude']):
            try:
                filtered_data = gpd.GeoDataFrame(
                    filtered_data, 
                    geometry=gpd.points_from_xy(filtered_data.longitude, filtered_data.latitude),
                    crs="EPSG:4326"
                )
            except Exception as e:
                st.error(f"Error converting data to GeoDataFrame: {str(e)}")
                return
        else:
            st.error("Data must contain geometry or latitude/longitude columns.")
            return
    
    # Map view selection
    map_type = st.radio("Select Map Type", ["Folium", "Plotly"], horizontal=True)
    
    # Display column selector for choropleth/bubble maps
    numeric_cols = filtered_data.select_dtypes(include=['number']).columns.tolist()
    if 'geometry' in numeric_cols:
        numeric_cols.remove('geometry')
    
    # Select column for color coding
    if numeric_cols:
        selected_column = st.selectbox(
            "Select a column for color coding",
            options=['None'] + numeric_cols,
            index=0
        )
        
        color_column = None if selected_column == 'None' else selected_column
    else:
        color_column = None
        st.info("No numeric columns available for color coding.")
    
    # Create map
    if map_type == "Folium":
        # Create Folium map
        m = create_folium_map(
            filtered_data,
            column=color_column,
            popup_columns=filtered_data.columns[:5].tolist() if len(filtered_data.columns) > 5 else filtered_data.columns.tolist()
        )
        
        if m:
            st.subheader("Interactive Map")
            folium_static(m, width=800, height=500)
            
            # Map instructions
            st.info("👉 Use the controls on the left to zoom, draw shapes, and measure distances. Click on features for more information.")
        else:
            st.error("Could not create map with the provided data.")
    else:
        # Create Plotly map
        fig = create_plotly_map(
            filtered_data,
            column=color_column,
            popup_columns=filtered_data.columns[:5].tolist() if len(filtered_data.columns) > 5 else filtered_data.columns.tolist()
        )
        
        if fig:
            st.subheader("Interactive Map")
            st.plotly_chart(fig, use_container_width=True)
            
            # Map instructions
            st.info("👉 Hover over features to see details. Use the toolbar on the right to zoom, pan, and download the map.")
        else:
            st.error("Could not create map with the provided data.")
    
    # Display data statistics
    st.subheader("Data Overview")
    row_count = len(filtered_data)
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", f"{row_count:,}")
    
    if color_column:
        with col2:
            st.metric(f"Avg {color_column}", f"{filtered_data[color_column].mean():.2f}")
        
        with col3:
            st.metric(f"Max {color_column}", f"{filtered_data[color_column].max():.2f}")

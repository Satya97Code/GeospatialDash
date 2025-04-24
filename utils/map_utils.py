import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import numpy as np
from branca.colormap import linear

def create_folium_map(gdf, column=None, popup_columns=None, zoom_start=2):
    """
    Create a Folium map from a GeoDataFrame
    
    Parameters:
    - gdf: GeoDataFrame with geometry
    - column: column to use for color mapping
    - popup_columns: list of columns to show in popup
    - zoom_start: initial zoom level
    
    Returns a folium map
    """
    # Ensure we have a valid GeoDataFrame
    if not isinstance(gdf, gpd.GeoDataFrame):
        st.error("Invalid geographic data provided")
        return None
    
    # Set default center of map
    if not gdf.empty:
        try:
            # Get centroid of all geometries
            gdf_centroid = gdf.geometry.unary_union.centroid
            center = [gdf_centroid.y, gdf_centroid.x]
        except:
            # Default center (world view)
            center = [0, 0]
    else:
        center = [0, 0]
    
    # Create base map
    m = folium.Map(location=center, zoom_start=zoom_start, 
                   tiles="CartoDB positron", control_scale=True)
    
    # Add fullscreen button
    folium.plugins.Fullscreen().add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add search functionality if we have a column called 'name'
    if 'name' in gdf.columns:
        from folium.plugins import Search
        search = Search(
            layer=None,
            geom_type='Point',
            placeholder='Search for a place',
            collapsed=True,
            search_label='name'
        )
        m.add_child(search)
    
    # Determine if we're dealing with points or polygons
    if all(gdf.geometry.type == 'Point'):
        # Point data
        if column and column in gdf.columns:
            # Use column values for coloring and sizing points
            min_val = gdf[column].min()
            max_val = gdf[column].max()
            
            # Create colormap
            colormap = linear.viridis.scale(min_val, max_val)
            
            # Add points to map
            for idx, row in gdf.iterrows():
                # Create popup HTML
                popup_html = "<div style='width: 200px'>"
                if popup_columns:
                    for col in popup_columns:
                        if col in row and pd.notna(row[col]):
                            popup_html += f"<b>{col}:</b> {row[col]}<br>"
                else:
                    for col in gdf.columns:
                        if col != 'geometry' and pd.notna(row[col]):
                            popup_html += f"<b>{col}:</b> {row[col]}<br>"
                popup_html += "</div>"
                
                # Determine marker size based on value
                marker_size = 8
                if column in row and pd.notna(row[column]):
                    # Scale size between 5 and 15
                    normalized_size = (row[column] - min_val) / (max_val - min_val) if max_val > min_val else 0.5
                    marker_size = 5 + normalized_size * 10
                
                # Add marker
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=marker_size,
                    color=colormap(row[column]) if column in row and pd.notna(row[column]) else 'blue',
                    fill=True,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)
                
            # Add colormap legend
            colormap.caption = column
            colormap.add_to(m)
        else:
            # Simple point map without color coding
            for idx, row in gdf.iterrows():
                # Create popup HTML
                popup_html = "<div style='width: 200px'>"
                for col in gdf.columns:
                    if col != 'geometry' and pd.notna(row[col]):
                        popup_html += f"<b>{col}:</b> {row[col]}<br>"
                popup_html += "</div>"
                
                # Add marker
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=8,
                    color='blue',
                    fill=True,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)
    else:
        # Polygon data - create choropleth
        if column and column in gdf.columns:
            # Add choropleth layer
            choropleth = folium.Choropleth(
                geo_data=gdf.__geo_interface__,
                name='Choropleth',
                data=gdf,
                columns=[gdf.index, column],
                key_on='feature.id',
                fill_color='YlGnBu',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name=column
            ).add_to(m)
            
            # Add tooltips
            choropleth.geojson.add_child(
                folium.features.GeoJsonTooltip(
                    fields=popup_columns if popup_columns else [col for col in gdf.columns if col != 'geometry'],
                    aliases=popup_columns if popup_columns else [col for col in gdf.columns if col != 'geometry'],
                    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                )
            )
        else:
            # Simple polygon map without color coding
            folium.GeoJson(
                gdf,
                name='geojson',
                style_function=lambda x: {'fillColor': '#ffff00', 'color': 'black', 'weight': 1, 'fillOpacity': 0.5},
                tooltip=folium.features.GeoJsonTooltip(
                    fields=popup_columns if popup_columns else [col for col in gdf.columns if col != 'geometry'],
                    aliases=popup_columns if popup_columns else [col for col in gdf.columns if col != 'geometry'],
                    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                )
            ).add_to(m)
    
    # Add draw tools
    folium.plugins.Draw(
        export=True,
        filename='data.geojson',
        position='topleft',
        draw_options={'polyline': True, 'polygon': True, 'rectangle': True, 'circle': True, 'marker': True},
        edit_options={'poly': {'allowIntersection': False}}
    ).add_to(m)
    
    # Add measure tool
    folium.plugins.MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)
    
    return m

def create_plotly_map(gdf, column=None, popup_columns=None):
    """
    Create a Plotly map from a GeoDataFrame
    
    Parameters:
    - gdf: GeoDataFrame with geometry
    - column: column to use for color mapping
    - popup_columns: list of columns to show in hover info
    
    Returns a Plotly figure
    """
    # Ensure we have a valid GeoDataFrame
    if not isinstance(gdf, gpd.GeoDataFrame):
        st.error("Invalid geographic data provided")
        return None
    
    # Check if we're dealing with points
    if all(gdf.geometry.type == 'Point'):
        # Extract coordinates for scatter plot
        gdf['lon'] = gdf.geometry.x
        gdf['lat'] = gdf.geometry.y
        
        # Create hover text
        hover_data = {}
        if popup_columns:
            for col in popup_columns:
                if col in gdf.columns:
                    hover_data[col] = True
        else:
            for col in gdf.columns:
                if col not in ['geometry', 'lon', 'lat']:
                    hover_data[col] = True
        
        # Create scatter map
        if column and column in gdf.columns:
            fig = px.scatter_mapbox(
                gdf, 
                lat='lat', 
                lon='lon', 
                color=column,
                size=column if gdf[column].dtype in [np.float64, np.int64] else None,
                hover_name=gdf.index.astype(str),
                hover_data=hover_data,
                zoom=1,
                height=600,
                color_continuous_scale=px.colors.sequential.Viridis
            )
        else:
            fig = px.scatter_mapbox(
                gdf, 
                lat='lat', 
                lon='lon',
                hover_name=gdf.index.astype(str),
                hover_data=hover_data,
                zoom=1,
                height=600
            )
        
        # Use open-street-map as base map
        fig.update_layout(mapbox_style="open-street-map")
        
    else:
        # For polygons, convert to GeoJSON for choropleth
        fig = go.Figure()
        
        if column and column in gdf.columns:
            # Create choropleth map
            fig = px.choropleth_mapbox(
                gdf,
                geojson=gdf.__geo_interface__,
                locations=gdf.index,
                color=column,
                color_continuous_scale="Viridis",
                zoom=1,
                height=600,
                center={"lat": 0, "lon": 0},
                opacity=0.5,
                labels={column: column}
            )
        else:
            # Create simple map without color coding
            fig = px.choropleth_mapbox(
                gdf,
                geojson=gdf.__geo_interface__,
                locations=gdf.index,
                zoom=1,
                height=600,
                center={"lat": 0, "lon": 0},
                opacity=0.5
            )
            
        # Use open-street-map as base map
        fig.update_layout(mapbox_style="open-street-map")
    
    # Update layout
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        autosize=True
    )
    
    return fig

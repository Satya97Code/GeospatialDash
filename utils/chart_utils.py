import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def get_numeric_columns(df):
    """Get list of numeric columns from DataFrame"""
    return df.select_dtypes(include=['number']).columns.tolist()

def get_categorical_columns(df):
    """Get list of categorical columns from DataFrame"""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def get_datetime_columns(df):
    """Get list of datetime columns from DataFrame"""
    return df.select_dtypes(include=['datetime']).columns.tolist()

def create_correlation_heatmap(df):
    """Create correlation heatmap for numeric columns"""
    numeric_cols = get_numeric_columns(df)
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns to create a correlation heatmap.")
        return None
    
    # Calculate correlation matrix
    corr = df[numeric_cols].corr()
    
    # Create heatmap
    fig = px.imshow(
        corr.values,
        x=corr.columns,
        y=corr.columns,
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        title="Correlation Heatmap"
    )
    
    return fig

def create_bar_chart(df, x_col, y_col, title=None, color=None):
    """Create a bar chart"""
    if x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Columns {x_col} or {y_col} not found in the data.")
        return None
    
    fig = px.bar(
        df, x=x_col, y=y_col, 
        title=title if title else f"{y_col} by {x_col}",
        color=color if color and color in df.columns else None
    )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        autosize=True
    )
    
    return fig

def create_line_chart(df, x_col, y_col, title=None, color=None):
    """Create a line chart"""
    if x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Columns {x_col} or {y_col} not found in the data.")
        return None
    
    fig = px.line(
        df, x=x_col, y=y_col, 
        title=title if title else f"{y_col} over {x_col}",
        color=color if color and color in df.columns else None
    )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        autosize=True
    )
    
    return fig

def create_scatter_plot(df, x_col, y_col, title=None, color=None, size=None):
    """Create a scatter plot"""
    if x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Columns {x_col} or {y_col} not found in the data.")
        return None
    
    fig = px.scatter(
        df, x=x_col, y=y_col, 
        title=title if title else f"{y_col} vs {x_col}",
        color=color if color and color in df.columns else None,
        size=size if size and size in df.columns else None,
        opacity=0.7
    )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        autosize=True
    )
    
    return fig

def create_histogram(df, column, bins=None, title=None, color=None):
    """Create a histogram"""
    if column not in df.columns:
        st.warning(f"Column {column} not found in the data.")
        return None
    
    fig = px.histogram(
        df, x=column, 
        nbins=bins if bins else 20,
        title=title if title else f"Distribution of {column}",
        color=color if color and color in df.columns else None
    )
    
    fig.update_layout(
        xaxis_title=column,
        yaxis_title="Count",
        autosize=True
    )
    
    return fig

def create_pie_chart(df, column, title=None):
    """Create a pie chart"""
    if column not in df.columns:
        st.warning(f"Column {column} not found in the data.")
        return None
    
    # Count values for categorical variables
    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, 'count']
    
    fig = px.pie(
        value_counts, 
        values='count', 
        names=column,
        title=title if title else f"Distribution of {column}"
    )
    
    fig.update_layout(autosize=True)
    
    return fig

def create_box_plot(df, x_col, y_col, title=None, color=None):
    """Create a box plot"""
    if y_col not in df.columns:
        st.warning(f"Column {y_col} not found in the data.")
        return None
    
    if x_col and x_col not in df.columns:
        st.warning(f"Column {x_col} not found in the data.")
        return None
    
    fig = px.box(
        df, 
        x=x_col if x_col else None, 
        y=y_col,
        title=title if title else f"Box Plot of {y_col}" + (f" by {x_col}" if x_col else ""),
        color=color if color and color in df.columns else None
    )
    
    fig.update_layout(
        xaxis_title=x_col if x_col else "",
        yaxis_title=y_col,
        autosize=True
    )
    
    return fig

def create_summary_stats(df):
    """Create a table of summary statistics"""
    numeric_cols = get_numeric_columns(df)
    if not numeric_cols:
        st.warning("No numeric columns found for summary statistics.")
        return None
    
    summary = df[numeric_cols].describe().T
    
    # Add more statistics
    summary['median'] = df[numeric_cols].median()
    summary['mode'] = df[numeric_cols].mode().iloc[0] if not df[numeric_cols].mode().empty else None
    summary['missing'] = df[numeric_cols].isna().sum()
    summary['missing_pct'] = (df[numeric_cols].isna().sum() / len(df)) * 100
    
    # Create a plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Statistic'] + list(summary.columns),
            fill_color='#4287f5',
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[summary.index] + [summary[col] for col in summary.columns],
            fill_color='#f0f2f6',
            align='left',
            font=dict(color='#262730', size=11)
        )
    )])
    
    fig.update_layout(
        title="Summary Statistics",
        margin=dict(l=0, r=0, t=40, b=0),
        height=400
    )
    
    return fig

def create_choropleth(gdf, column):
    """Create a choropleth map"""
    if column not in gdf.columns:
        st.warning(f"Column {column} not found in the data.")
        return None
    
    # Check if the column is numeric
    if gdf[column].dtype not in [np.int64, np.float64]:
        st.warning(f"Column {column} must be numeric for a choropleth map.")
        return None
    
    fig = px.choropleth(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color=column,
        projection="mercator"
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    
    fig.update_layout(
        title=f"Choropleth Map of {column}",
        autosize=True,
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )
    
    return fig

def create_bubble_map(gdf, size_col, color_col=None, title=None):
    """Create a bubble map"""
    if not isinstance(gdf, gpd.GeoDataFrame):
        st.warning("Data must be a GeoDataFrame for mapping.")
        return None
    
    if size_col not in gdf.columns:
        st.warning(f"Column {size_col} not found in the data.")
        return None
    
    if color_col and color_col not in gdf.columns:
        st.warning(f"Column {color_col} not found in the data.")
        return None
    
    # Extract point coordinates
    if all(gdf.geometry.type == 'Point'):
        gdf['lon'] = gdf.geometry.x
        gdf['lat'] = gdf.geometry.y
        
        fig = px.scatter_mapbox(
            gdf,
            lat='lat',
            lon='lon',
            size=size_col,
            color=color_col if color_col else None,
            mapbox_style="open-street-map",
            zoom=1,
            title=title if title else f"Bubble Map of {size_col}" + (f" colored by {color_col}" if color_col else "")
        )
        
        fig.update_layout(
            autosize=True,
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        
        return fig
    else:
        st.warning("Bubble maps require point geometries.")
        return None

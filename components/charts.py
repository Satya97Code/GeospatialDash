import streamlit as st
import pandas as pd
import numpy as np
from utils.chart_utils import (
    get_numeric_columns, get_categorical_columns, get_datetime_columns,
    create_correlation_heatmap, create_bar_chart, create_line_chart, 
    create_scatter_plot, create_histogram, create_pie_chart, 
    create_box_plot, create_summary_stats
)
from utils.data_loader import filter_data

def create_charts(data, chart_type="analysis"):
    """
    Create data visualization charts based on the provided data
    
    Parameters:
    - data: DataFrame or GeoDataFrame
    - chart_type: Type of charts to display ("analysis" or "summary")
    """
    # Apply any filters
    filtered_data = filter_data(data, st.session_state.filters) if hasattr(st.session_state, 'filters') else data
    
    # Check if we have valid data
    if filtered_data is None or len(filtered_data) == 0:
        st.warning("No data available for visualization.")
        return
    
    # Get column types
    numeric_cols = get_numeric_columns(filtered_data)
    categorical_cols = get_categorical_columns(filtered_data)
    datetime_cols = get_datetime_columns(filtered_data)
    
    # Remove geometry column from analysis
    if 'geometry' in numeric_cols:
        numeric_cols.remove('geometry')
    if 'geometry' in categorical_cols:
        categorical_cols.remove('geometry')
    
    # For summary view - show key insights
    if chart_type == "summary":
        # Show key statistics card
        if numeric_cols:
            # Display summary statistics
            summary_stats = filtered_data[numeric_cols].describe().T
            
            # Pick a few key columns for display
            display_cols = numeric_cols[:3] if len(numeric_cols) > 3 else numeric_cols
            
            for col in display_cols:
                st.metric(
                    label=col,
                    value=f"{filtered_data[col].mean():.2f}",
                    delta=f"{filtered_data[col].max() - filtered_data[col].mean():.2f} from avg to max"
                )
            
            # Show a quick visualization
            if len(numeric_cols) >= 2:
                st.subheader("Quick Correlation")
                x_col, y_col = numeric_cols[0], numeric_cols[1]
                fig = create_scatter_plot(filtered_data, x_col, y_col, 
                                         title=f"Relationship between {x_col} and {y_col}")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # Show distribution of main column
            if numeric_cols:
                st.subheader("Value Distribution")
                main_col = numeric_cols[0]
                fig = create_histogram(filtered_data, main_col, title=f"Distribution of {main_col}")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
        # Show categorical breakdown if available
        if categorical_cols:
            st.subheader("Category Breakdown")
            cat_col = categorical_cols[0]
            fig = create_pie_chart(filtered_data, cat_col, title=f"Distribution of {cat_col}")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    # For analysis view - show detailed charts with options
    else:
        # Chart selection
        chart_options = [
            "Summary Statistics", 
            "Correlation Heatmap", 
            "Bar Chart", 
            "Line Chart", 
            "Scatter Plot", 
            "Histogram", 
            "Box Plot", 
            "Pie Chart"
        ]
        
        selected_chart = st.selectbox("Select Chart Type", chart_options)
        
        if selected_chart == "Summary Statistics":
            st.subheader("Summary Statistics")
            fig = create_summary_stats(filtered_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No numeric data available for summary statistics.")
        
        elif selected_chart == "Correlation Heatmap":
            st.subheader("Correlation Heatmap")
            fig = create_correlation_heatmap(filtered_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Unable to create correlation heatmap. Need at least 2 numeric columns.")
        
        elif selected_chart == "Bar Chart":
            st.subheader("Bar Chart")
            
            # Get x and y selections
            col1, col2 = st.columns(2)
            
            with col1:
                x_options = categorical_cols + datetime_cols
                x_col = st.selectbox("Select X-axis (Category)", options=x_options if x_options else ["No categorical columns"])
            
            with col2:
                y_col = st.selectbox("Select Y-axis (Value)", options=numeric_cols if numeric_cols else ["No numeric columns"])
            
            # Optional color by
            color_col = st.selectbox("Color by (optional)", options=["None"] + categorical_cols)
            color = None if color_col == "None" else color_col
            
            # Create chart if valid selections
            if x_options and numeric_cols and x_col in filtered_data.columns and y_col in filtered_data.columns:
                fig = create_bar_chart(filtered_data, x_col, y_col, color=color)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Cannot create bar chart with the selected columns.")
        
        elif selected_chart == "Line Chart":
            st.subheader("Line Chart")
            
            # Get x and y selections
            col1, col2 = st.columns(2)
            
            with col1:
                x_options = numeric_cols + datetime_cols
                x_col = st.selectbox("Select X-axis", options=x_options if x_options else ["No suitable columns"])
            
            with col2:
                y_col = st.selectbox("Select Y-axis", options=numeric_cols if numeric_cols else ["No numeric columns"])
            
            # Optional color by
            color_col = st.selectbox("Group by (optional)", options=["None"] + categorical_cols)
            color = None if color_col == "None" else color_col
            
            # Create chart if valid selections
            if x_options and numeric_cols and x_col in filtered_data.columns and y_col in filtered_data.columns:
                fig = create_line_chart(filtered_data, x_col, y_col, color=color)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Cannot create line chart with the selected columns.")
        
        elif selected_chart == "Scatter Plot":
            st.subheader("Scatter Plot")
            
            # Get x and y selections
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("Select X-axis", options=numeric_cols if numeric_cols else ["No numeric columns"])
            
            with col2:
                y_options = [col for col in numeric_cols if col != x_col]
                y_col = st.selectbox("Select Y-axis", options=y_options if y_options else ["No other numeric columns"])
            
            # Optional parameters
            color_col = st.selectbox("Color by (optional)", options=["None"] + categorical_cols + numeric_cols)
            color = None if color_col == "None" else color_col
            
            size_col = st.selectbox("Size by (optional)", options=["None"] + numeric_cols)
            size = None if size_col == "None" else size_col
            
            # Create chart if valid selections
            if numeric_cols and len(numeric_cols) > 1 and x_col in filtered_data.columns and y_col in filtered_data.columns:
                fig = create_scatter_plot(filtered_data, x_col, y_col, color=color, size=size)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Cannot create scatter plot with the selected columns.")
        
        elif selected_chart == "Histogram":
            st.subheader("Histogram")
            
            # Select column for histogram
            column = st.selectbox("Select Column", options=numeric_cols if numeric_cols else ["No numeric columns"])
            
            # Optional parameters
            bins = st.slider("Number of Bins", min_value=5, max_value=100, value=20)
            
            color_col = st.selectbox("Group by (optional)", options=["None"] + categorical_cols)
            color = None if color_col == "None" else color_col
            
            # Create chart if valid selection
            if numeric_cols and column in filtered_data.columns:
                fig = create_histogram(filtered_data, column, bins=bins, color=color)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Cannot create histogram with the selected column.")
        
        elif selected_chart == "Box Plot":
            st.subheader("Box Plot")
            
            # Get y selection (required)
            y_col = st.selectbox("Select Value Column", options=numeric_cols if numeric_cols else ["No numeric columns"])
            
            # Get x selection (optional)
            x_col = st.selectbox("Group by (optional)", options=["None"] + categorical_cols)
            x = None if x_col == "None" else x_col
            
            # Optional color
            color_col = st.selectbox("Color by (optional)", options=["None"] + categorical_cols)
            color = None if color_col == "None" else color_col
            
            # Create chart if valid selection
            if numeric_cols and y_col in filtered_data.columns:
                fig = create_box_plot(filtered_data, x, y_col, color=color)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Cannot create box plot with the selected columns.")
        
        elif selected_chart == "Pie Chart":
            st.subheader("Pie Chart")
            
            # Select categorical column
            column = st.selectbox("Select Category Column", options=categorical_cols if categorical_cols else ["No categorical columns"])
            
            # Create chart if valid selection
            if categorical_cols and column in filtered_data.columns:
                fig = create_pie_chart(filtered_data, column)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Cannot create pie chart with the selected column.")

import streamlit as st
import pandas as pd
from utils.data_loader import load_data, handle_uploaded_file, get_sample_datasets

def create_sidebar():
    """
    Create the sidebar with dataset selection and filtering options
    """
    with st.sidebar:
        st.title("Controls")
        
        # Dataset selection
        st.header("Dataset")
        
        # Upload data option
        upload_tab, sample_tab = st.tabs(["Upload Data", "Sample Data"])
        
        with upload_tab:
            st.markdown("""
            ### Upload a file
            You can upload GeoJSON, CSV files with coordinates, or shapefiles.
            
            **Note for shapefiles:** Shapefiles require multiple files (.shp, .shx, .dbf) to work properly. 
            For best results, upload the .shp file with its supporting files.
            """)
            
            uploaded_file = st.file_uploader(
                "Upload a GeoJSON, Shapefile, or CSV file",
                type=["geojson", "json", "csv", "shp", "zip"]
            )
            
            if uploaded_file is not None:
                if st.button("Load Uploaded Data"):
                    with st.spinner("Loading data..."):
                        data = handle_uploaded_file(uploaded_file)
                        if data is not None:
                            st.session_state.data = data
                            st.session_state.selected_dataset = uploaded_file.name
                            st.success(f"Successfully loaded {uploaded_file.name}")
                            st.rerun()
                        else:
                            st.error("Failed to load the file")
        
        with sample_tab:
            sample_datasets = get_sample_datasets()
            selected_sample = st.selectbox(
                "Select a sample dataset",
                options=[dataset["name"] for dataset in sample_datasets],
                index=0 if sample_datasets else None
            )
            
            if selected_sample:
                selected_dataset = next((dataset for dataset in sample_datasets if dataset["name"] == selected_sample), None)
                if selected_dataset and st.button("Load Sample Data"):
                    with st.spinner(f"Loading {selected_sample}..."):
                        data = load_data(selected_dataset["path"])
                        if data is not None:
                            st.session_state.data = data
                            st.session_state.selected_dataset = selected_sample
                            st.success(f"Successfully loaded {selected_sample}")
                            st.rerun()
                        else:
                            st.error("Failed to load the sample dataset")
        
        # Display current dataset
        if st.session_state.selected_dataset:
            st.info(f"Current dataset: {st.session_state.selected_dataset}")
        
        # Only show filters if data is loaded
        if st.session_state.data is not None:
            data = st.session_state.data
            
            st.header("Filters")
            
            # Get data columns for filtering
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Remove geometry column from filtering
            if 'geometry' in categorical_cols:
                categorical_cols.remove('geometry')
            
            # Create filters based on column types
            if numeric_cols:
                st.subheader("Numeric Filters")
                for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                    min_val = float(data[col].min())
                    max_val = float(data[col].max())
                    
                    # Create a range slider for numeric columns
                    filter_val = st.slider(
                        f"Filter by {col}",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        step=(max_val - min_val) / 100 if max_val > min_val else 0.01
                    )
                    
                    # Update filters in session state
                    if filter_val != (min_val, max_val):
                        st.session_state.filters[col] = filter_val
                    elif col in st.session_state.filters:
                        del st.session_state.filters[col]
            
            if categorical_cols:
                st.subheader("Categorical Filters")
                for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
                    # Get unique values
                    unique_vals = data[col].dropna().unique().tolist()
                    
                    # If too many unique values, use a text input instead
                    if len(unique_vals) > 10:
                        filter_val = st.text_input(f"Filter by {col} (comma-separated values)")
                        if filter_val:
                            values = [val.strip() for val in filter_val.split(',')]
                            st.session_state.filters[col] = values
                        elif col in st.session_state.filters:
                            del st.session_state.filters[col]
                    else:
                        # Create a multiselect for categorical columns
                        filter_val = st.multiselect(
                            f"Filter by {col}",
                            options=unique_vals,
                            default=[]
                        )
                        
                        # Update filters in session state
                        if filter_val:
                            st.session_state.filters[col] = filter_val
                        elif col in st.session_state.filters:
                            del st.session_state.filters[col]
            
            # Reset filters button
            if st.session_state.filters and st.button("Reset All Filters"):
                st.session_state.filters = {}
                st.rerun()
            
            # Display current filters
            if st.session_state.filters:
                st.subheader("Applied Filters")
                for col, filter_val in st.session_state.filters.items():
                    if isinstance(filter_val, tuple):
                        st.write(f"{col}: {filter_val[0]} to {filter_val[1]}")
                    elif isinstance(filter_val, list):
                        st.write(f"{col}: {', '.join(str(v) for v in filter_val)}")
                    else:
                        st.write(f"{col}: {filter_val}")
        
        # Home button in sidebar
        st.sidebar.markdown("---")
        if st.sidebar.button("🏠 Return to Home", use_container_width=True):
            # Reset data to return to default screen
            st.session_state.data = None
            st.session_state.selected_dataset = None
            st.session_state.filters = {}
            st.rerun()
            
        # About section
        st.sidebar.markdown("---")
        st.sidebar.subheader("About")
        st.sidebar.info(
            "This dashboard provides interactive visualization tools for geospatial data analysis. "
            "Upload your own data or use sample datasets to explore geographic patterns and insights."
        )

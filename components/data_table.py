import streamlit as st
import pandas as pd
from utils.data_loader import filter_data

def create_data_table(data):
    """
    Create an interactive data table with filtering and sorting
    
    Parameters:
    - data: DataFrame or GeoDataFrame to display
    """
    # Apply any filters
    filtered_data = filter_data(data, st.session_state.filters) if hasattr(st.session_state, 'filters') else data
    
    # Check if we have valid data
    if filtered_data is None or len(filtered_data) == 0:
        st.warning("No data available to display.")
        return
    
    # Create a copy of the data without the geometry column for display
    if 'geometry' in filtered_data.columns:
        display_data = filtered_data.drop(columns=['geometry'])
    else:
        display_data = filtered_data.copy()
    
    # Table options
    st.subheader("Data Table Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Option to select columns
        all_columns = display_data.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to display",
            options=all_columns,
            default=all_columns[:5] if len(all_columns) > 5 else all_columns
        )
    
    with col2:
        # Search functionality
        search_term = st.text_input("Search in data", "")
    
    with col3:
        # Number of rows to display
        n_rows = st.number_input("Rows to display", min_value=5, max_value=100, value=10, step=5)
    
    # Apply column selection
    if selected_columns:
        display_data = display_data[selected_columns]
    
    # Apply search if provided
    if search_term:
        # Search in all columns
        mask = pd.Series(False, index=display_data.index)
        for column in display_data.columns:
            # Convert column to string for searching
            mask = mask | display_data[column].astype(str).str.contains(search_term, case=False, na=False)
        display_data = display_data[mask]
    
    # Display row count
    st.write(f"Showing {min(len(display_data), n_rows)} of {len(display_data)} rows")
    
    # Display the data table
    st.dataframe(display_data.head(n_rows), use_container_width=True)
    
    # Download button
    csv = display_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
    )
    
    # Display summary statistics
    with st.expander("View Summary Statistics"):
        # Display basic statistics for numeric columns
        numeric_data = display_data.select_dtypes(include=['number'])
        if not numeric_data.empty:
            st.write("Numeric Columns Summary:")
            st.dataframe(numeric_data.describe(), use_container_width=True)
        
        # Display value counts for categorical columns (first 3)
        categorical_data = display_data.select_dtypes(include=['object', 'category'])
        if not categorical_data.empty:
            st.write("Categorical Columns Summary (Top 5 values):")
            
            for col in categorical_data.columns[:3]:  # Limit to first 3 categorical columns
                st.write(f"Column: {col}")
                value_counts = categorical_data[col].value_counts().head(5)
                st.bar_chart(value_counts)

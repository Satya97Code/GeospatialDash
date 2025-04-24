import streamlit as st
from components.sidebar import create_sidebar
from components.map_view import create_map_view
from components.charts import create_charts
from components.data_table import create_data_table
from utils.data_loader import load_data, get_sample_datasets

# Page configuration
st.set_page_config(
    page_title="Geospatial Analytics Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header with Home button
col1, col2 = st.columns([6, 1])
with col1:
    st.title("🌍 Geospatial Analytics Dashboard")
with col2:
    # Add Home button in the header
    if st.button("🏠 Home", use_container_width=True):
        # Reset data to return to default screen
        st.session_state.data = None
        st.session_state.selected_dataset = None
        st.session_state.filters = {}
        st.rerun()

st.markdown("""
    <div style="border-bottom: 1px solid #e6e6e6; margin-bottom: 16px;"></div>
""", unsafe_allow_html=True)

# Main function
def main():
    # Initialize session state for filters and data
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'selected_dataset' not in st.session_state:
        st.session_state.selected_dataset = None
    if 'filters' not in st.session_state:
        st.session_state.filters = {}
    
    # Create sidebar with filters and dataset selection
    create_sidebar()
    
    # Check if data is available
    if st.session_state.data is None:
        st.info("👈 Please select a dataset from the sidebar or upload your own data.")
        
        # Display dataset options
        st.header("Available Sample Datasets")
        sample_datasets = get_sample_datasets()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Spatial Analysis")
            for dataset in sample_datasets[:len(sample_datasets)//2]:
                if st.button(f"Load {dataset['name']}", key=f"btn_{dataset['name']}"):
                    with st.spinner(f"Loading {dataset['name']}..."):
                        st.session_state.data = load_data(dataset['path'])
                        st.session_state.selected_dataset = dataset['name']
                        st.rerun()
        
        with col2:
            st.subheader("Geographic Insights")
            for dataset in sample_datasets[len(sample_datasets)//2:]:
                if st.button(f"Load {dataset['name']}", key=f"btn_{dataset['name']}"):
                    with st.spinner(f"Loading {dataset['name']}..."):
                        st.session_state.data = load_data(dataset['path'])
                        st.session_state.selected_dataset = dataset['name']
                        st.rerun()
        
        return
    
    # Create main layout with tabs
    tab1, tab2, tab3 = st.tabs(["Map View", "Data Analysis", "Data Table"])
    
    with tab1:
        # Map and charts layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            create_map_view(st.session_state.data)
        
        with col2:
            st.subheader("Key Insights")
            create_charts(st.session_state.data, chart_type="summary")
    
    with tab2:
        st.header("Data Analysis")
        create_charts(st.session_state.data, chart_type="analysis")
    
    with tab3:
        st.header("Data Table")
        create_data_table(st.session_state.data)
    
    # Footer
    st.markdown("""
        <div style="border-top: 1px solid #e6e6e6; margin-top: 20px; padding-top: 10px; text-align: center; font-size: 0.8em;">
            Geospatial Analytics Dashboard | Built with Streamlit
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import numpy as np
import math
from datetime import datetime, timedelta, date

# Set page configuration
st.set_page_config(
    page_title="Production Visualization Dashboard",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better tile layout
st.markdown("""
<style>
    .tile-chart {
        border: 1px solid #f0f0f0;
        border-radius: 5px;
        padding: 10px;
        margin: 5px;
        background-color: white;
    }
    .stPlotlyChart {
        margin-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Production Volume Visualization Dashboard")
# st.markdown("### Analyze production volumes across delivery networks")

# Function to load data from SQLite database
@st.cache_data
def load_data():
    # Connect to SQLite database
    # Replace with your actual database path
    conn = sqlite3.connect('petro-wellprod-06042025.db')
    
    # Query for delivery network data with well counts
    delivery_network_df = pd.read_sql_query("""
        SELECT 
            "Process Platform/CTF" AS "Delivery Network Group",
            SUM("Allocated Oil ProductionMT") AS "Oil (MT)",
            SUM("Allocated Gas ProductionKCM") AS "Gas (KCM)",
            SUM("Allocated Condensate ProductionMT") AS "Condensate (MT)",
            SUM("Allocated Water ProductionBB6") AS "Water (BB6)",
            COUNT(CASE WHEN "Hrs Flown" > 0 THEN 1 END) as "Flowing Wells",
            COUNT(CASE WHEN "Hrs Flown" = 0 THEN 1 END) as "Non-Flowing Wells",
            COUNT(*) as "Total Wells"
        FROM production
        WHERE "Process Platform/CTF" IS NOT NULL
        GROUP BY "Process Platform/CTF"
        ORDER BY "Gas (KCM)" DESC
    """, conn)
    
    # Query for all production data (to get full details)
    production_df = pd.read_sql_query("""
        SELECT * FROM production
    """, conn)
    
    conn.close()
    
    return delivery_network_df, production_df

# Function to generate time series data for simulation
def generate_time_series_data(delivery_network_df, start_date=None, end_date=None):
    networks = delivery_network_df['Delivery Network Group'].tolist()
    
    # Create a dictionary of base values for each network
    base_values = {}
    for _, row in delivery_network_df.iterrows():
        network = row['Delivery Network Group']
        base_values[network] = {
            'gas': row['Gas (KCM)'],
            'oil': row['Oil (MT)'],
            'condensate': row['Condensate (MT)'],
            'water': row['Water (BB6)']
        }
    
    # Generate 24 months of data starting from 24 months ago (to allow for date range selection)
    today = datetime.now()
    if start_date is None:
        default_start_date = datetime(today.year - 2, today.month, 1)
    else:
        default_start_date = start_date
        
    if end_date is None:
        default_end_date = today
    else:
        default_end_date = end_date
    
    time_series_data = []
    
    # Generate data for each month in the 24-month period
    current_date = datetime(today.year - 2, today.month, 1)
    i = 0
    
    while current_date <= today:
        month_name = current_date.strftime('%b %Y')
        date_obj = current_date.date()
        
        month_data = {
            'month': month_name, 
            'month_num': i,
            'date': date_obj
        }
        
        for network in networks:
            # Add some random variation and seasonal pattern
            variation_factor = 0.8 + np.random.random() * 0.4  # Random between 0.8 and 1.2
            seasonal_factor = 1 + math.sin(i / 12 * 2 * math.pi) * 0.15  # Seasonal pattern
            
            for product in ['gas', 'oil', 'condensate', 'water']:
                base_value = base_values[network][product]
                adjusted_value = base_value * variation_factor * seasonal_factor
                month_data[f"{network}_{product}"] = round(adjusted_value, 2)
        
        time_series_data.append(month_data)
        current_date = current_date + timedelta(days=30)
        i += 1
    
    df = pd.DataFrame(time_series_data)
    
    # Filter by date range if provided
    if start_date is not None and end_date is not None:
        start_date_obj = start_date if isinstance(start_date, date) else start_date.date()
        end_date_obj = end_date if isinstance(end_date, date) else end_date.date()
        df = df[(df['date'] >= start_date_obj) & (df['date'] <= end_date_obj)]
    
    return df

# Function to create a small chart for the tiled view
def create_small_chart(data, network, volume_type, volume_key, height=250):
    y_values = [row[f"{network}_{volume_key}"] for _, row in data.iterrows()]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['month'],
        y=y_values,
        mode='lines+markers',
        name=network
    ))
    
    fig.update_layout(
        title=f"{network}: {volume_type}",
        xaxis_title=None,
        yaxis_title=volume_type,
        height=height,
        margin=dict(l=10, r=10, t=40, b=20),
        hovermode="x unified"
    )
    
    return fig

# Load the data
try:
    delivery_network_df, production_df = load_data()
    
    delivery_network_df['Total Wells'] = delivery_network_df['Flowing Wells'] + delivery_network_df['Non-Flowing Wells']
    delivery_network_df = delivery_network_df.fillna(0)

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select View", 
        ["Standard Volume by Delivery Network", "Standard Volume over Time", "Tiled Charts", "Well Status Analysis", "Well Status Map", "Well Production Trends", "Measurement Point Radar"]
    )
    
    # Date range selector in sidebar (for time series views)
    if page in ["Standard Volume over Time", "Tiled Charts"]:
        st.sidebar.title("Date Range")
        
        # Calculate default date range (last 12 months)
        today = datetime.now()
        default_start = datetime(today.year - 1, today.month, 1)
        default_end = today
        
        start_date = st.sidebar.date_input(
            "Select Start Date",
            value=default_start,
            min_value=datetime(today.year - 2, 1, 1),
            max_value=today,
            help="Choose the start date for the data range"
        )

        end_date = st.sidebar.date_input(
            "Select End Date",
            value=default_end,
            min_value=start_date,
            max_value=today,
            help="Choose the end date for the data range"
        )
        
        # Create time series data with date filtering
        time_series_df = generate_time_series_data(delivery_network_df, start_date, end_date)
    else:
        # Create time series data without date filtering for other views
        time_series_df = generate_time_series_data(delivery_network_df)
    
    if page == "Standard Volume by Delivery Network":
        st.header("Standard Volume by Delivery Network Group")
        
        # Volume type selection
        volume_type = st.selectbox(
            "Select Volume Type",
            ["Gas (KCM)", "Oil (MT)", "Condensate (MT)", "Water (BB6)", "All Volumes"],
            index=0
        )
        
        # Prepare data based on selection
        if volume_type == "All Volumes":
            # Create a melted dataframe for all volume types
            melted_df = pd.melt(
                delivery_network_df,
                id_vars=['Delivery Network Group'],
                value_vars=['Gas (KCM)', 'Oil (MT)', 'Condensate (MT)', 'Water (BB6)'],
                var_name='Volume Type',
                value_name='Volume'
            )
            
            # Separate chart for water if "All Volumes" is selected (due to scale difference)
            fig1 = px.bar(
                melted_df[melted_df['Volume Type'] != 'Water (BB6)'],
                x='Delivery Network Group',
                y='Volume',
                color='Volume Type',
                title='Standard Volume by Delivery Network Group (Excluding Water)',
                labels={'Delivery Network Group': 'Delivery Network', 'Volume': 'Volume'},
                height=500
            )
            
            fig2 = px.bar(
                melted_df[melted_df['Volume Type'] == 'Water (BB6)'],
                x='Delivery Network Group',
                y='Volume',
                title='Water Volume (BB6) by Delivery Network Group',
                labels={'Delivery Network Group': 'Delivery Network', 'Volume': 'Volume (BB6)'},
                height=400,
                color_discrete_sequence=['#FF7300']
            )
            
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)
            
        else:
            # Single volume type
            column_name = volume_type
            sorted_df = delivery_network_df.sort_values(by=column_name, ascending=False)
            
            # Create two column layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(
                    sorted_df,
                    x='Delivery Network Group',
                    y=column_name,
                    title=f'{volume_type} by Delivery Network Group',
                    labels={'Delivery Network Group': 'Delivery Network'},
                    height=600,
                    color=column_name,
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Create a well count summary chart
                well_counts = pd.melt(
                    sorted_df,
                    id_vars=['Delivery Network Group'],
                    value_vars=['Flowing Wells', 'Non-Flowing Wells'],
                    var_name='Well Status',
                    value_name='Count'
                )
                
                fig_wells = px.bar(
                    well_counts,
                    x='Delivery Network Group',
                    y='Count',
                    color='Well Status',
                    title='Well Status by Delivery Network',
                    labels={'Delivery Network Group': 'Delivery Network'},
                    height=600,
                    barmode='stack'
                )
                fig_wells.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig_wells, use_container_width=True)
        
        # Display the data table
        st.subheader("Data Table")
        st.dataframe(delivery_network_df.style.highlight_max(axis=0, color='lightgreen'))
        
    elif page == "Standard Volume over Time":
        st.header(f"Standard Volume over Time ({start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')})")
            
        # Volume type selection
        volume_type_mapping = {
            "Gas (KCM)": "gas",
            "Oil (MT)": "oil", 
            "Condensate (MT)": "condensate",
            "Water (BB6)": "water"
        }
            
        volume_type = st.selectbox(
            "Select Volume Type",
            ["Gas (KCM)", "Oil (MT)", "Condensate (MT)", "Water (BB6)"],
            index=0
        )
        
        volume_key = volume_type_mapping[volume_type]
        
        # Network selection (multi-select)
        all_networks = delivery_network_df['Delivery Network Group'].tolist()
        default_networks = all_networks[:3]  # Top 3 by default
        
        selected_networks = st.multiselect(
            "Select Delivery Networks to Compare",
            all_networks,
            default=default_networks
        )
            
        if not selected_networks:
            st.warning("Please select at least one delivery network.")
        else:
            # Prepare data for the selected networks
            fig = go.Figure()
                
            for network in selected_networks:
                y_values = [row[f"{network}_{volume_key}"] for _, row in time_series_df.iterrows()]
                fig.add_trace(go.Scatter(
                    x=time_series_df['month'],
                    y=y_values,
                    mode='lines+markers',
                    name=network
                ))
            
            fig.update_layout(
                title=f"{volume_type} over Time by Delivery Network",
                xaxis_title="Month",
                yaxis_title=volume_type,
                hovermode="x unified",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Information about the simulated data
            st.info("""
                **Note**: This chart displays simulated time series data based on actual production values.
                The simulation includes seasonal patterns and random variations to illustrate potential volume changes over time.
            """)
            
            # Show the aggregated data for selected networks
            st.subheader("Data for Selected Networks")
            selected_data = delivery_network_df[delivery_network_df['Delivery Network Group'].isin(selected_networks)]
            st.dataframe(selected_data)

            # Add download button for time series data
            st.subheader("Download Time Series Data")
            csv = time_series_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"production_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
    elif page == "Tiled Charts":
        st.header(f"Tiled Charts View ({start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')})")
        
        # Volume type selection for tiled view
        volume_type_mapping = {
            "Gas (KCM)": "gas",
            "Oil (MT)": "oil", 
            "Condensate (MT)": "condensate",
            "Water (BB6)": "water"
        }
            
        # Allow selecting multiple volume types for tiled view
        selected_volume_types = st.multiselect(
            "Select Volume Types to Display",
            ["Gas (KCM)", "Oil (MT)", "Condensate (MT)", "Water (BB6)"],
            default=["Gas (KCM)", "Oil (MT)"]
        )
        
        # Network selection for tiled view
        all_networks = delivery_network_df['Delivery Network Group'].tolist()
        
        # Sort networks by total volume for better selection
        network_totals = {}
        for network in all_networks:
            total = sum(delivery_network_df[delivery_network_df['Delivery Network Group'] == network][['Gas (KCM)', 'Oil (MT)', 'Condensate (MT)']].values[0])
            network_totals[network] = total
        
        sorted_networks = sorted(all_networks, key=lambda x: network_totals[x], reverse=True)
        default_networks = sorted_networks[:4]  # Top 4 by default
        
        selected_networks = st.multiselect(
            "Select Delivery Networks to Display",
            sorted_networks,
            default=default_networks
        )
            
        if not selected_volume_types:
            st.warning("Please select at least one volume type.")
        elif not selected_networks:
            st.warning("Please select at least one delivery network.")
        else:
            # Create tiled layout
            st.subheader("Production Metrics by Network")
                
            # Determine grid layout based on selections
            if len(selected_networks) == 1:
                # Single network, multiple volume types
                network = selected_networks[0]
                
                # Create a row of charts for each volume type
                for i, volume_type in enumerate(selected_volume_types):
                    volume_key = volume_type_mapping[volume_type]
                    
                    # Create chart
                    fig = create_small_chart(time_series_df, network, volume_type, volume_key, height=300)
                    
                    # Display chart
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Multiple networks
                # For each volume type, create a row of charts
                for volume_type in selected_volume_types:
                    st.write(f"### {volume_type}")
                    volume_key = volume_type_mapping[volume_type]
                    
                    # Calculate number of columns based on network count
                    num_networks = len(selected_networks)
                    if num_networks <= 2:
                        cols = st.columns(num_networks)
                    else:
                        cols = st.columns(min(3, num_networks))  # Max 3 columns
                    
                    # Create charts for each network
                    for i, network in enumerate(selected_networks):
                        col_idx = i % len(cols)
                        with cols[col_idx]:
                            fig = create_small_chart(time_series_df, network, volume_type, volume_key)
                            st.plotly_chart(fig, use_container_width=True)
            
        # Information about the simulated data
        st.info("""
            **Note**: These charts display simulated time series data based on actual production values.
            The simulation includes seasonal patterns and random variations to illustrate potential volume changes over time.
        """)
        
        # Show the aggregated data for selected networks
        st.subheader("Data Summary for Selected Networks")
        selected_data = delivery_network_df[delivery_network_df['Delivery Network Group'].isin(selected_networks)]
        st.dataframe(selected_data.style.highlight_max(axis=0, color='lightgreen'))

    elif page == "Well Status Analysis":
        st.header("Well Status Analysis by Network")
        
        # Create metrics for total wells
        total_flowing = delivery_network_df["Flowing Wells"].sum()
        total_non_flowing = delivery_network_df["Non-Flowing Wells"].sum()
        total_wells = delivery_network_df["Total Wells"].sum()

        print(f"Total Flowing Wells: {total_flowing}")
        print(f"Total Non-Flowing Wells: {total_non_flowing}")
        print(f"Total Wells: {total_wells}")
        
        # Display overall metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Flowing Wells", f"{total_flowing:,}")
        with col2:
            st.metric("Total Non-Flowing Wells", f"{total_non_flowing:,}")
        with col3:
            st.metric("Total Wells", f"{total_wells:,}")
        
        # Create well status percentage chart
        well_status_pct = pd.DataFrame({
            'Delivery Network': delivery_network_df['Delivery Network Group'],
            'Flowing %': (delivery_network_df['Flowing Wells'] / delivery_network_df['Total Wells'] * 100).round(1),
            'Non-Flowing %': (delivery_network_df['Non-Flowing Wells'] / delivery_network_df['Total Wells'] * 100).round(1)
        }).sort_values('Flowing %', ascending=False)

        # Create two columns for charts
        col1, col2 = st.columns(2)
    
        with col1:
            # Stacked bar chart showing absolute numbers
            well_counts = pd.melt(
                delivery_network_df,
                id_vars=['Delivery Network Group'],
                value_vars=['Flowing Wells', 'Non-Flowing Wells'],
                var_name='Well Status',
                value_name='Count'
            )
            
            fig_counts = px.bar(
                well_counts,
                x='Delivery Network Group',
                y='Count',
                color='Well Status',
                title='Well Count by Status and Network',
                labels={'Delivery Network Group': 'Delivery Network'},
                height=400,
                barmode='stack'
            )
            fig_counts.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_counts, use_container_width=True)

        with col2:
            # Percentage stacked bar chart
            well_pct = pd.melt(
                well_status_pct,
                id_vars=['Delivery Network'],
                value_vars=['Flowing %', 'Non-Flowing %'],
                var_name='Status',
                value_name='Percentage'
            )
            
            fig_pct = px.bar(
                well_pct,
                x='Delivery Network',
                y='Percentage',
                color='Status',
                title='Well Status Distribution by Network (%)',
                labels={'Delivery Network': 'Network'},
                height=400,
                barmode='stack'
            )
            fig_pct.update_layout(xaxis_tickangle=45, yaxis_title='Percentage (%)')
            st.plotly_chart(fig_pct, use_container_width=True)

        # Display detailed data table
        st.subheader("Detailed Well Status Data")
        detailed_df = delivery_network_df[['Delivery Network Group', 'Flowing Wells', 'Non-Flowing Wells', 'Total Wells']].copy()
        detailed_df['Flowing %'] = (detailed_df['Flowing Wells'] / detailed_df['Total Wells'] * 100).round(1)
        detailed_df['Non-Flowing %'] = (detailed_df['Non-Flowing Wells'] / detailed_df['Total Wells'] * 100).round(1)
        st.dataframe(detailed_df.style.highlight_max(axis=0, color='lightgreen'))

    elif page == "Measurement Point Radar":
        st.header("Measurement Point Radar (Spider Chart)")

        # Metrics to compare
        metrics = [
            ("Standard Volume", "Allocated Oil ProductionMT"),
            ("Density", "Density"),
            ("Mass", "Mass"),
            ("Temp", "Temp"),
            ("BSW", "BSW")
        ]

        # Check which columns exist, simulate if missing
        available_cols = production_df.columns
        radar_metrics = []
        for label, col in metrics:
            if col in available_cols:
                radar_metrics.append((label, col, False))
            else:
                radar_metrics.append((label, col, True))  # True = simulate

        # Get unique measurement points
        point_col = "Process Platform/CTF"
        points = production_df[point_col].dropna().unique()
        selected_points = st.multiselect(
            "Select Measurement Points",
            points,
            default=points[:2] if len(points) > 1 else points
        )

        if not selected_points:
            st.warning("Please select at least one measurement point.")
        else:
            fig = go.Figure()
            np.random.seed(42)
            for idx, point in enumerate(selected_points):
                row = production_df[production_df[point_col] == point]
                values = []
                for label, col, simulate in radar_metrics:
                    if simulate:
                        # Simulate plausible value
                        if label == "Standard Volume":
                            val = np.random.uniform(100, 1000)
                        elif label == "Density":
                            val = np.random.uniform(0.7, 1.1)
                        elif label == "Mass":
                            val = np.random.uniform(100, 1000)
                        elif label == "Temp":
                            val = np.random.uniform(20, 80)
                        elif label == "BSW":
                            val = np.random.uniform(0, 10)
                        else:
                            val = 0
                    else:
                        val = row[col].mean()
                    values.append(val)
                # Close the loop for radar
                values += [values[0]]
                labels = [m[0] for m in radar_metrics] + [radar_metrics[0][0]]
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    name=str(point)
                ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True)
                ),
                showlegend=True,
                title="Radar/Spider Chart per Measurement Point",
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info("This radar chart profiles each measurement point across key metrics. Outlier sites can be identified at a glance.")

    elif page == "Well Production Trends":
        st.header("Well Production Trends (Heatmap)")

        # Use production_df to get well and volume info
        # If no date column, simulate 12 months of data per well
        if "Well Id" in production_df.columns:
            well_col = "Well Id"
        elif "Well String" in production_df.columns:
            well_col = "Well String"
        else:
            well_col = production_df.columns[0]  # fallback

        # Use "Allocated Oil ProductionMT" as standard volume
        if "Allocated Oil ProductionMT" in production_df.columns:
            vol_col = "Allocated Oil ProductionMT"
        else:
            vol_col = production_df.columns[-1]  # fallback

        # Simulate 12 months of data per well
        months = pd.date_range(end=datetime.now(), periods=12, freq="M")
        wells = production_df[well_col].dropna().unique()
        heatmap_data = []
        np.random.seed(42)
        for well in wells:
            base_vol = production_df[production_df[well_col] == well][vol_col].mean()
            for month in months:
                # Simulate volume with some random variation
                vol = max(0, base_vol * (0.7 + 0.6 * np.random.rand()))
                heatmap_data.append({
                    "Production Date": month.strftime("%Y-%m"),
                    "Well": well,
                    "Volume": vol
                })
        heatmap_df = pd.DataFrame(heatmap_data)

        # Pivot for heatmap
        heatmap_pivot = heatmap_df.pivot(index="Well", columns="Production Date", values="Volume")

        fig = go.Figure(
            data=go.Heatmap(
                z=heatmap_pivot.values,
                x=heatmap_pivot.columns,
                y=heatmap_pivot.index,
                colorscale="YlGnBu",
                colorbar=dict(title="Volume"),
                hoverongaps=False
            )
        )
        fig.update_layout(
            title="Production Volume per Well Over Time",
            xaxis_title="Production Date",
            yaxis_title="Well",
            height=700
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info("This heatmap shows which wells are producing most (or least) volume across time. Useful for identifying production dips, maintenance needs, or anomalies.")

    elif page == "Well Status Map":
        st.header("Well Status Map")

        # Generate mock well data
        np.random.seed(42)
        num_wells = 20
        # Example: random lat/lon within a plausible oilfield region (e.g., Mumbai Offshore)
        latitudes = np.random.uniform(18.5, 19.5, num_wells)
        longitudes = np.random.uniform(71.0, 73.0, num_wells)
        statuses = np.random.choice(["Active", "Inactive", "Shut-in"], num_wells, p=[0.6, 0.3, 0.1])
        well_ids = [f"WELL-{i+1:03d}" for i in range(num_wells)]
        # Simulate volume (1-10)
        volumes = np.random.randint(1, 11, num_wells)

        well_df = pd.DataFrame({
            "Well Id": well_ids,
            "Latitude": latitudes,
            "Longitude": longitudes,
            "Status": statuses,
            "Volume": volumes
        })

        # For each well, create multiple dots according to volume (with jitter)
        emoji = "🛢️"
        expanded_rows = []
        for _, row in well_df.iterrows():
            for i in range(row["Volume"]):
                jitter_lat = row["Latitude"] + i*0.03
                jitter_lon = row["Longitude"] #+ np.random.uniform(-0.01, 0.01)
                expanded_rows.append({
                    "Well Id": row["Well Id"],
                    "Latitude": jitter_lat,
                    "Longitude": jitter_lon,
                    "Status": row["Status"],
                    "Volume": row["Volume"],
                    "Emoji": emoji
                })
        plot_df = pd.DataFrame(expanded_rows)

        # Map color for status
        status_color_map = {
            "Active": "green",
            "Inactive": "red",
            "Shut-in": "orange"
        }
        plot_df["Color"] = plot_df["Status"].map(status_color_map)

        # Plotly scatter_mapbox with bigger dots and emoji as text
        fig_map = px.scatter_mapbox(
            plot_df,
            lat="Latitude",
            lon="Longitude",
            color="Status",
            hover_name="Well Id",
            hover_data={"Latitude": True, "Longitude": True, "Status": True, "Volume": True},
            zoom=7,
            height=700,
            color_discrete_map=status_color_map,
            title="Well Status Map",
            text="Emoji",
            size_max=30
        )
        fig_map.update_traces(marker=dict(size=7, sizemode="diameter"), textfont_size=24)
        fig_map.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":40,"l":0,"b":0}
        )

        st.plotly_chart(fig_map, use_container_width=True)

        st.info("This map displays well locations and status. Each 🛢️ represents a well, and more dots indicate higher volume. Replace with actual well coordinates, status, and volume for real data.")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("""
        Please ensure that the database file 'production.db' is available in the same directory as this script.
        The database should contain a table named 'production' with the expected columns.
    """)

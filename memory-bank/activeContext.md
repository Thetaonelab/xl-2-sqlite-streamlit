# Active Context: Excel to SQLite Production Dashboard

## Current Work Focus

The project is currently in a functional state with core features implemented:

1. **Data Import**: Excel to SQLite conversion is working for both well production and MPVL data
2. **Dashboard Visualization**: Streamlit dashboard with interactive charts is operational
3. **Data Analysis**: Basic aggregation and filtering capabilities are implemented
4. **Time Series Simulation**: Simulated historical data generation is functional

The system currently handles two primary data types:
- **Well Production Data**: From `wellprod 06.04.25 mt.XLSX`
- **MPVL Data**: From `mpvl _01 to 06.04.25.XLSX`

## Recent Changes

1. **Database Creation**: Successfully created SQLite databases from Excel files
   - `petro-wellprod-06042025.db`: Contains well production data
   - `petro-mpvl.db`: Contains MPVL data

2. **Dashboard Implementation**: Created interactive Streamlit dashboard with:
   - Volume by delivery network visualization
   - Time series analysis with simulated historical data
   - Interactive filtering by volume type and delivery network
   - Data tables with highlighted maximum values

3. **Data Processing**: Implemented data aggregation and transformation:
   - Grouping by delivery network/platform
   - Calculation of total production volumes by type
   - Sorting and ranking of delivery networks

## Active Decisions

1. **Data Simulation Approach**:
   - Currently using simulated time series data based on actual production values
   - Adding random variations and seasonal patterns for realistic visualization
   - This is a temporary solution until historical data is available

2. **Chart Selection**:
   - Bar charts for comparing delivery networks
   - Line charts for time series analysis
   - Separate charts for water due to scale differences

3. **Database Structure**:
   - Using separate database files for different data types
   - Direct table mapping from Excel structure
   - No normalization applied yet

## Current Challenges

1. **Hardcoded File Paths**:
   - Excel and database paths are currently hardcoded
   - Need to implement configuration for flexible file locations

2. **Data Validation**:
   - Limited validation of Excel data during import
   - Need to add error handling for malformed data

3. **Historical Data**:
   - Currently using simulated historical data
   - Need to implement actual historical data storage

4. **Performance Optimization**:
   - Large Excel files may cause performance issues
   - Need to optimize SQL queries for better performance

## Next Steps

### Immediate Tasks

1. **Configuration System**:
   - Create configuration file for paths and settings
   - Implement command-line arguments for flexible execution

2. **Data Validation**:
   - Add validation for Excel data during import
   - Implement error handling for malformed data

3. **Code Refactoring**:
   - Modularize code into proper package structure
   - Separate data processing from visualization logic

### Short-term Goals

1. **Historical Data Storage**:
   - Implement actual historical data storage
   - Replace simulated time series with real data

2. **Additional Visualizations**:
   - Add well-level detailed analysis
   - Implement geographic visualization if coordinates available
   - Create production forecasting capabilities

3. **Export Functionality**:
   - Add ability to export filtered data
   - Implement report generation features

### Long-term Vision

1. **Automated Data Pipeline**:
   - Schedule regular data imports
   - Implement data change detection

2. **Multi-user Deployment**:
   - Deploy as internal web service
   - Implement user authentication if needed

3. **Advanced Analytics**:
   - Add statistical analysis tools
   - Implement anomaly detection
   - Create production optimization recommendations

## Current Focus Areas

The primary focus areas for current development are:

1. **Usability Improvements**:
   - Enhance UI/UX for non-technical users
   - Add help text and tooltips for complex features

2. **Data Quality**:
   - Improve data validation and error handling
   - Add data quality metrics and warnings

3. **Performance Optimization**:
   - Optimize database queries
   - Improve caching strategy
   - Enhance chart rendering performance

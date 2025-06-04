# Project Brief: Excel to SQLite Production Dashboard

## Overview
A data visualization system that converts petro (Petro Corporation) production data from Excel files to SQLite databases and provides an interactive dashboard for analysis. The system handles well production data and MPVL (Multi-Phase Volume Loss) data, offering insights through various visualizations.

## Core Requirements

### Data Processing
- Convert Excel files (.XLSX) to SQLite databases
- Handle multiple data types:
  - Oil Production (MT)
  - Gas Production (KCM)
  - Condensate Production (MT)
  - Water Production (BB6)
- Support automatic database updates with new Excel files
- Maintain data integrity during conversion

### Visualization Dashboard
- Interactive web interface using Streamlit
- Multiple visualization types:
  - Volume by Delivery Network
  - Time series analysis
  - Comparative analysis between networks
- Flexible data filtering and selection
- Real-time data updates
- Responsive design for various screen sizes

### Data Analysis
- Group data by delivery network/platform
- Calculate aggregated production volumes
- Generate simulated time series data for trend analysis
- Support comparative analysis between different networks
- Highlight maximum values in data tables

## Technical Goals
- Efficient data storage and retrieval
- Clean separation between data processing and visualization
- Maintainable and extensible codebase
- Optimized performance for large datasets
- Intuitive user interface for non-technical users

## Success Criteria
- Successful conversion of Excel data to SQLite
- Accurate visualization of production data
- Interactive dashboard with responsive controls
- Support for both current and historical data analysis
- Ability to handle updates with new Excel files

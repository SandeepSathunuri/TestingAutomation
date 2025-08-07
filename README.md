# Swift Insights Dashboard Automation

A comprehensive Selenium-based automation framework for testing and validating dashboard data in Swift Insights web application.

## 🎯 Project Overview

This automation framework performs end-to-end testing of the Swift Insights dashboard by:

1. **Login Authentication** - Automated login to the web application
2. **Dashboard Navigation** - Selects and navigates to Sales Summary dashboard
3. **KPI Validation** - Extracts KPI data and compares with database values
4. **Widget Testing** - Tests widget functionality (tooltips, expand, download)
5. **Data Comparison** - Compares extracted data with database stored procedures
6. **Drillthrough Testing** - Performs drillthrough operations on each widget
7. **Comprehensive Reporting** - Generates Excel reports for all comparisons

## 📁 Project Structure

```
├── newmain.py                     # Main automation script
├── setup_project.py               # Project setup and validation script
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (credentials)
├── .gitignore                    # Git ignore rules
│
├── Core Modules/
│   ├── login.py                  # Authentication handler
│   ├── dashboardSelection.py     # Dashboard navigation
│   ├── kpisdataextraction.py     # KPI data extraction
│   ├── widgetsdataextract.py     # Widget data extraction
│   ├── filters.py                # Filter automation
│   └── dataBase.py               # Database connection
│
├── Data Processing/
│   ├── kpistoreprocedures.py     # KPI database comparison
│   ├── widgetstoreprocedures.py  # Widget database comparison
│   ├── drillthrough_db_handler.py # Drillthrough database handling
│   └── excel_merger.py           # Excel file operations
│
├── Widget Components/
│   ├── widget_loader.py          # Widget loading utilities
│   ├── tooltip_handler.py        # Tooltip testing
│   ├── widget_menu.py            # Widget menu interactions
│   ├── drillthrough_handler.py   # Drillthrough operations
│   └── widget_utils.py           # Widget utility functions
│
├── Error Handling/
│   └── error_handler.py          # Centralized error handling
│
└── Output Directories/
    ├── download/
    │   ├── kpis/                 # KPI Excel files and reports
    │   └── widgets/              # Widget Excel files and reports
    ├── errors/                   # Error screenshots and logs
    └── logs/                     # Application logs
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd swift-insights-automation

# Run setup script
python setup_project.py
```

### 2. Configure Environment Variables

Create a `.env` file with your credentials:

```env
# Database Configuration
DB_SERVER=your_database_server
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name

# Application Configuration
LOGIN_URL=http://qaapp.swiftinsights.ai/#/login-page
EMAIL=your_email@domain.com
PASSWORD=your_password
```

### 3. Run Automation

```bash
python newmain.py
```

## 📊 Workflow Details

### Phase 1: Landing Page Processing

1. **Login & Navigation**
   - Authenticates using provided credentials
   - Navigates to Sales Summary dashboard
   - Applies necessary filters

2. **KPI Processing**
   - Extracts all KPI values from dashboard
   - Tests KPI tooltip functionality
   - Compares with database using stored procedures
   - Generates `landing_kpi_comparison_report.xlsx`

3. **Widget Processing**
   - For each widget:
     - Tests tooltip functionality
     - Tests expand functionality  
     - Downloads widget data
   - Combines all widget files into `Combined_Widgets_Landing.xlsx`
   - Compares with database using stored procedures
   - Generates `landing_widgets_comparison.xlsx`

### Phase 2: Drillthrough Processing

4. **Drillthrough Operations**
   - For each widget on landing page:
     - Performs drillthrough operation
     - Extracts KPIs from drillthrough page
     - Processes all widgets in drillthrough view
     - Downloads and combines drillthrough widget data
     - Compares with drillthrough stored procedures
     - Returns to landing page for next widget

## 🗄️ Database Integration

### KPI Stored Procedures

**Landing Page:**
- `N_GetFilteredSalesData` - Total Sales
- `SP_TotalUnitsSoldkpi` - Total Units Sold
- `SP_TotalBillsKPI` - Total No. of Bills
- `SP_AvgBillValue` - Avg. Bill Value
- `TotalCustomersKPI` - Total Customers
- `SalesPerSqftKPI` - Sales per Sqft

**Drillthrough:**
- `DR_TotalSalesKPI` - Drillthrough Total Sales
- `DR_TotalUnitsSoldKPI` - Drillthrough Total Units Sold
- (Additional drillthrough procedures...)

### Widget Stored Procedures

**Landing Page:**
- `SP_TopStoresbySales` - Top Stores by Sales
- `SP_TopBrandsBySales` - Top Brands by Sales
- `SP_TopCategoriesBySaleswidget` - Top Categories by Sales
- `SP_TopSubCategoriesBySales` - Top Sub Categories by Sales
- `SP_TopProductsBySaleswidget` - Top Products by Sales
- `SP_WeeklyTrendswidget` - Weekly Trends
- `SP_StorewiseActualVsTarget_Vertical_SortedByActual` - Store Sales with Targets

## 📈 Reports Generated

### KPI Reports
- `landing_kpi_comparison_report.xlsx` - Landing page KPI vs Database comparison
- `{widget}_drillthrough_kpi_comparison.xlsx` - Drillthrough KPI comparisons

### Widget Reports
- `Combined_Widgets_Landing.xlsx` - All landing page widget data
- `landing_widgets_comparison.xlsx` - Landing page widget vs Database comparison
- `{widget}_{submenu}_drillthrough_widgets.xlsx` - Drillthrough widget data
- `{widget}_{submenu}_widget_comparison.xlsx` - Drillthrough widget comparisons

### Error Reports
- `error_report.xlsx` - Comprehensive error and warning report
- Screenshots saved in `errors/` directory for debugging

## 🛠️ Error Handling

The framework includes comprehensive error handling:

- **Centralized Error Logging** - All errors logged with context
- **Screenshot Capture** - Automatic screenshots on errors
- **Graceful Continuation** - Process continues even if individual components fail
- **Detailed Reporting** - Error summary and detailed reports generated

## ⚙️ Configuration

### Chrome Driver Options
- Automatic download handling
- Security settings for testing
- Performance optimizations

### Database Parameters
```python
params = (year, month, store, state, channel, fromdate, todate)
# Example: (2024, None, None, None, None, None, None)
```

### Drillthrough Mapping
```python
DRILLTHROUGH_MAP = {
    "Top Stores by Sales": "Love Library",
    "Top Brands by Sales": "Routledge Publications",
    "Top Categories by Sales": "E-Books",
    # ... additional mappings
}
```

## 🔧 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - Ensure Chrome browser is installed
   - Check Chrome driver compatibility

2. **Database Connection**
   - Verify database credentials in `.env`
   - Check network connectivity to database server

3. **Element Not Found**
   - Check if website structure has changed
   - Verify selectors in component files

4. **Download Issues**
   - Ensure download directory permissions
   - Check Chrome download settings

### Debug Mode

Enable detailed logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Dependencies

- **selenium** - Web automation
- **openpyxl** - Excel file operations
- **python-dotenv** - Environment variable management
- **pandas** - Data processing
- **undetected-chromedriver** - Chrome driver management

## 🤝 Contributing

1. Follow the existing code structure
2. Add comprehensive error handling
3. Update documentation for new features
4. Test thoroughly before submitting

## 📄 License

This project is for internal use and testing purposes.

---

**Note:** This automation framework is designed specifically for the Swift Insights dashboard. Ensure you have proper authorization before running automated tests on any web application.
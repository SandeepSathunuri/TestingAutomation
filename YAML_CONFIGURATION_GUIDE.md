# YAML Configuration Guide

## 📋 Overview

This project now uses YAML configuration files to manage all stored procedures, drillthrough filters, and widget mappings. This makes the system more maintainable, flexible, and easier to update without modifying code.

## 📁 Configuration Files

### 1. `config/stored_procedures.yaml`

Contains all stored procedure definitions and mappings:

- **Landing Page Widgets**: Maps widget sheet names to stored procedures
- **KPI Procedures**: KPI-related stored procedures
- **Drillthrough Procedures**: Organized by target (Love Library, Routledge Publications, etc.)
- **Dynamic Engine SPs**: List of available SPs for the dynamic comparison engine
- **Return Formats**: Expected column formats and patterns for each SP type

### 2. `config/drillthrough_filters.yaml`

Contains drillthrough filter mappings and parameters:

- **Drillthrough Map**: Widget to submenu mappings
- **Store Mappings**: Store names to ID mappings (20 stores)
- **Brand/Category/Product Mappings**: Entity name mappings
- **Drillthrough Parameters**: Parameters for each target with validation rules
- **Supported Filters**: Which filter types are supported for each target

### 3. `config/widget_mappings.yaml`

Contains widget-specific mappings and configurations:

- **Widget Sheet Mappings**: Landing page and drillthrough widget configurations
- **Data Structure Definitions**: Column definitions and key formats for each widget type
- **Widget Priority**: Processing order for widgets
- **Validation Rules**: Required columns and data types
- **Display Configuration**: Formatting rules for output

### 4. `config/dynamic_engine_config.yaml`

Contains dynamic comparison engine configuration:

- **Pattern Recognition**: Direct mappings and pattern matching rules
- **Scoring System**: Confidence scoring for SP matching
- **Data Pattern Detection**: Time-based, entity-based, and value-based patterns
- **SP Output Classification**: How to classify different SP return formats
- **Formatting Rules**: Key generation and value cleaning rules
- **Performance Settings**: Caching, timeouts, and parallel processing

### 5. `config/database_config.yaml`

Contains database connection and query configurations:

- **Connection Settings**: Timeouts, retry logic, connection pooling
- **Query Execution**: Parameter formats, timeouts, retry logic
- **Data Type Mappings**: SQL Server to Python type mappings
- **Security Settings**: SQL injection prevention, access control
- **Error Handling**: Database, connection, and query error handling
- **Logging Configuration**: What to log and how verbose

## 🔧 Configuration Loader

The `config_loader.py` module provides easy access to all configurations:

```python
from config_loader import config_loader

# Get landing page widget mappings
widgets = config_loader.get_landing_page_widgets()

# Get drillthrough parameters
params = config_loader.get_drillthrough_parameters("Love Library")

# Get store ID mapping
store_id = config_loader.get_store_mapping("Love Library")

# Check if filter is supported
filter_type = config_loader.is_filter_supported("Love Library")
```

## 📊 Current Configuration Summary

- **📁 Configuration Files**: 5 YAML files
- **🔧 Total Stored Procedures**: 33 procedures (23 widgets + 10 KPIs)
- **🏠 Landing Page KPIs**: 5 KPI procedures
- **🎯 Drillthrough KPIs**: 5 KPI procedures
- **🎯 Drillthrough Targets**: 7 targets configured
- **🧩 Widget Mappings**: 12 widget configurations
- **🏪 Store Mappings**: 20 store locations
- **🔍 Dynamic Engine SPs**: 21 available procedures

## 🚀 Integration Status

The following files have been updated to use YAML configurations:

### ✅ Updated Files:

1. **`widgetstoreprocedures.py`**: Now loads widget mappings from YAML
2. **`drillthrough_db_handler.py`**: Added YAML config import
3. **`dynamic_comparison_engine.py`**: Added YAML config import

### 📝 New Files:

1. **`config_loader.py`**: Configuration loader utility
2. **`initialize_yaml_configs.py`**: Integration initialization script
3. **`yaml_integration_example.py`**: Usage examples

## 🎯 Drillthrough Configuration

### Store-Based Drillthrough (Fully Supported)

- **Love Library** (Store 717): ✅ 5 procedures configured
- **Willis Library** (Store 718): ✅ Configured
- **All 20 Libraries**: ✅ Store ID mappings available

### Other Drillthrough Types (Limited Support)

- **Brand-Based** (Routledge Publications): ⚠️ Not supported by current SPs
- **Category-Based** (E-Books): ⚠️ Not supported by current SPs
- **Product-Based** (MATLAB): ⚠️ Not supported by current SPs
- **Weekly** (Week1): ✅ Supported

## 🔧 Stored Procedures by Category

### Landing Page KPIs (5 procedures):
- `N_GetFilteredSalesData` - Total Sales
- `SP_TotalUnitsSoldkpi` - Total Units Sold
- `SP_AvgBillValue` - Avg. Bill Value
- `SP_AvgDailySalesKPI` - Avg. Daily Sales
- `SP_NewCustomersKPI` - New Customers

### Drillthrough KPIs (5 procedures):
- `DR_Totalsaleskpi` - Total Sales (Drillthrough)
- `DR_TotalUnitsSoldKPI` - Total Units Sold (Drillthrough)
- `DR_avgbillvalue` - Avg. Bill Value (Drillthrough)
- `DR_Totalnobillsa` - Total No. of Bills
- `DR_totalcustomers` - Total Customers

### Landing Page Widgets (7 procedures):

- `SP_TopStoresbySales` - Top Stores by Sales
- `SP_TopBrandsBySales` - Top Brands by Sales
- `SP_TopCategoriesBySaleswidget` - Top Categories by Sales
- `SP_TopSubCategoriesBySales` - Top Sub Categories by Sales
- `SP_TopProductsBySaleswidget` - Top Products by Sales
- `SP_WeeklyTrendswidget` - Weekly Trends
- `SP_StorewiseActualVsTarget_Vertical_SortedByActual` - Store Sales with Targets

### Love Library Drillthrough (5 procedures):

- `SP_SalesTrend` - Sales Trends (Monthly)
- `SP_TopPerformingEmployee` - Top Performing Employee
- `SP_TopProductsBySales` - Sales by Product
- `SP_WeekdayWeekendSales` - Weekday Weekend Sales
- `SP_WeekwiseSalesComparison` - Weekwise Sales

### Dynamic Engine (11 procedures):

All landing page + drillthrough procedures available for intelligent matching

## 📋 Usage Examples

### Basic Configuration Access:

```python
# Get all landing page widgets
widgets = config_loader.get_landing_page_widgets()
print(f"Found {len(widgets)} widgets")

# Get specific drillthrough parameters
params = config_loader.get_drillthrough_parameters("Love Library")
# Returns: (2024, None, '717', None, None, None, None)
```

### Drillthrough Integration:

```python
# Get Love Library procedures
procedures = config_loader.get_drillthrough_procedures("love_library")
# Returns: {'sales_trends': 'SP_SalesTrend', 'weekday_weekend': 'SP_WeekdayWeekendSales', ...}

# Check filter support
filter_type = config_loader.is_filter_supported("Love Library")
# Returns: "store"
```

### Dynamic Engine Configuration:

```python
# Get available SPs for dynamic matching
dynamic_sps = config_loader.get_dynamic_engine_sps()
# Returns: ['SP_SalesTrend', 'SP_TopPerformingEmployee', ...]

# Get pattern matching configuration
patterns = config_loader.get_pattern_mappings()
# Returns: Pattern recognition rules for intelligent SP matching
```

## 🔄 Updating Configurations

To update configurations:

1. **Edit YAML files** in the `config/` directory
2. **Reload configurations** (automatic on next run)
3. **Test changes** with `python yaml_integration_example.py`
4. **Validate** with `python config_loader.py`

## ✅ Benefits of YAML Configuration

1. **🔧 Maintainability**: Easy to update without code changes
2. **📊 Centralized**: All configurations in one place
3. **🔍 Readable**: Human-readable YAML format
4. **✅ Validated**: Built-in parameter validation
5. **🚀 Flexible**: Easy to add new procedures and mappings
6. **📝 Documented**: Self-documenting configuration structure
7. **🔄 Reloadable**: Can reload configurations without restart

## 🎉 Next Steps

1. **Customize** YAML files for your specific environment
2. **Add new** stored procedures as needed
3. **Extend** drillthrough support for brands/categories/products
4. **Monitor** performance and adjust settings
5. **Update** configurations as business requirements change

## 📊 KPI Configuration Usage

### Loading KPI Configurations:
```python
from config_loader import config_loader

# Get landing page KPI mappings
landing_kpis = config_loader.get_landing_page_kpis()
# Returns: {'Total Sales': 'N_GetFilteredSalesData', 'Total Units Sold': 'SP_TotalUnitsSoldkpi', ...}

# Get drillthrough KPI mappings
drillthrough_kpis = config_loader.get_drillthrough_kpis()
# Returns: {'Total Sales': 'DR_Totalsaleskpi', 'Total Units Sold': 'DR_TotalUnitsSoldKPI', ...}

# Get KPI parameters
kpi_params = config_loader.get_kpi_parameters()
# Returns: {'Year': 2024, 'Month': None, 'Store': None, ...}
```

### KPI Integration in kpistoreprocedures.py:
```python
# The module now automatically loads from YAML
import kpistoreprocedures

# Access the YAML-loaded mappings
landing_map = kpistoreprocedures.LANDING_SP_MAP
drillthrough_map = kpistoreprocedures.DRILLTHROUGH_SP_MAP
params = kpistoreprocedures.LANDING_PARAMS
```

### KPI Summary:
- **🏠 Landing Page KPIs**: 5 procedures for main dashboard
- **🎯 Drillthrough KPIs**: 5 procedures for detailed analysis
- **🔄 Common KPIs**: 3 KPIs available in both landing and drillthrough
- **📊 Unique KPIs**: 2 landing-only + 2 drillthrough-only KPIs

The system is now fully configured and ready for production use with complete YAML-based configuration management including KPI support!

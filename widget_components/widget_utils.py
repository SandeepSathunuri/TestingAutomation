import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from excel_merger import ExcelMerger
from widgetstoreprocedures import read_widget_values, fetch_db_widget_values, compare_widget_data, normalize
from selenium.webdriver.common.by import By

class WidgetUtils:
    def __init__(self, driver):
        self.driver = driver
        self.widget_dir = os.path.abspath("download/widgets")

    def process_widget(self, widget):
        try:
            title_elem = widget.find_element(By.CLASS_NAME, "chart-title")
            title = title_elem.text.strip()
            print(f"🧩 Processing widget: {title}")
            return title
        except:
            return None

    def handle_widget_download_and_compare(self, drill_targets):
        """Compare landing page widgets with database - creates landing folder structure"""
        
        print("🔄 Starting handle_widget_download_and_compare...")
        print(f"📋 Drill targets received: {drill_targets}")
        
        # Create landing page folder structure
        landing_dir = os.path.join(self.widget_dir, "landing")
        os.makedirs(landing_dir, exist_ok=True)
        print(f"📁 Created/verified landing directory: {landing_dir}")
        
        # Use YAML configuration for widget mapping
        try:
            from config_loader import config_loader
            widget_sp_map = config_loader.get_landing_page_widgets()
            print(f"📋 Loaded widget mapping from YAML: {widget_sp_map}")
        except Exception as e:
            print(f"⚠️ Could not load YAML config, using dynamic mapping: {e}")
            # Fallback to dynamic mapping
            widget_sp_map = {}
            for target in drill_targets:
                if "Store" in target and "Sales" in target:
                    widget_sp_map[target] = "SP_TopStoresbySales"
                elif "Brand" in target and "Sales" in target:
                    widget_sp_map[target] = "SP_TopBrandsBySales"
                elif "Categories" in target and "Sales" in target:
                    widget_sp_map[target] = "SP_TopCategoriesBySaleswidget"
                elif "Sub Categories" in target and "Sales" in target:
                    widget_sp_map[target] = "SP_TopSubCategoriesBySales"
                elif "Product" in target and "Sales" in target:
                    widget_sp_map[target] = "SP_TopProductsBySaleswidget"
                elif "Weekly" in target or "Trends" in target:
                    widget_sp_map[target] = "SP_WeeklyTrendswidget"
                elif "Store" in target and "Target" in target:
                    widget_sp_map[target] = "SP_StorewiseActualVsTarget_Vertical_SortedByActual"
                else:
                    widget_sp_map[target] = "SP_TopStoresbySales"
            print(f"📋 Created dynamic widget mapping: {widget_sp_map}")

        # Look for combined file in landing directory (primary location)
        landing_combined_path = os.path.join(landing_dir, "Combined_Widgets_Landing.xlsx")
        
        if os.path.exists(landing_combined_path):
            widget_excel_path = landing_combined_path
            print(f"📊 Found combined file in landing directory: {landing_combined_path}")
        else:
            print(f"❌ Combined widget file not found in landing directory: {landing_combined_path}")
            print("⚠️ Skipping landing page widget database comparison")
            
            # List files in landing directory for debugging
            if os.path.exists(landing_dir):
                files = os.listdir(landing_dir)
                print(f"📁 Files in landing dir: {files}")
            else:
                print(f"📁 Landing directory doesn't exist: {landing_dir}")
            return

        try:
            print(f"📊 Reading widget data from: {widget_excel_path}")
            
            # Create normalized mapping for widget identification
            normalized_map = {normalize(v): k for k, v in widget_sp_map.items()}
            
            # Read Excel widget data
            excel_widgets = read_widget_values(widget_excel_path, normalized_map)
            print(f"📈 Found {len(excel_widgets)} widget data points in Excel")
            
            # Debug: Show some Excel data
            if excel_widgets:
                print("📊 Sample Excel data:")
                for i, (key, value) in enumerate(list(excel_widgets.items())[:5]):
                    print(f"   {key}: {value}")
            else:
                print("⚠️ No Excel data found - checking file structure...")
                try:
                    import pandas as pd
                    df = pd.read_excel(widget_excel_path, sheet_name=None)
                    print(f"📄 Excel sheets found: {list(df.keys())}")
                    for sheet_name, sheet_df in df.items():
                        print(f"   Sheet '{sheet_name}': {sheet_df.shape[0]} rows, {sheet_df.shape[1]} columns")
                        if not sheet_df.empty:
                            print(f"   Columns: {list(sheet_df.columns)}")
                except Exception as e:
                    print(f"❌ Error reading Excel file: {e}")
            
            # Set database parameters (landing page - no specific filters)
            year = 2024
            month = store = state = channel = fromdate = todate = None
            initial_params = (year, month, store, state, channel, fromdate, todate)
            
            # Check data freshness and update parameters if needed
            params = self._add_data_freshness_check(widget_sp_map, initial_params)
            
            print(f"🔍 Database parameters: Year={year}, Month={month}, Store={store}, State={state}, Channel={channel}")
            print("🔍 Fetching widget data from database...")
            db_widgets = fetch_db_widget_values(widget_sp_map, params)
            print(f"📈 Found {len(db_widgets)} widget data points in Database")
            
            # Debug: Show some DB data with detailed analysis
            if db_widgets:
                print("🗄️ Sample DB data:")
                for i, (key, value) in enumerate(list(db_widgets.items())[:5]):
                    print(f"   {key}: {value} (type: {type(value)})")
                    
                # Check for data consistency issues
                print("\n🔍 Data consistency analysis:")
                value_types = {}
                for key, value in db_widgets.items():
                    value_type = type(value).__name__
                    if value_type not in value_types:
                        value_types[value_type] = 0
                    value_types[value_type] += 1
                
                print(f"   DB value types: {value_types}")
            else:
                print("⚠️ No database data found")
            
            # Debug: Compare Excel and DB key structures
            if excel_widgets and db_widgets:
                print("\n🔍 Key structure comparison:")
                excel_keys = set(excel_widgets.keys())
                db_keys = set(db_widgets.keys())
                
                common_keys = excel_keys.intersection(db_keys)
                excel_only = excel_keys - db_keys
                db_only = db_keys - excel_keys
                
                print(f"   Common keys: {len(common_keys)}")
                print(f"   Excel-only keys: {len(excel_only)}")
                print(f"   DB-only keys: {len(db_only)}")
                
                if excel_only:
                    print(f"   Sample Excel-only keys: {list(excel_only)[:3]}")
                if db_only:
                    print(f"   Sample DB-only keys: {list(db_only)[:3]}")
                
                # Show value comparison for common keys
                if common_keys:
                    print(f"\n🔍 Value comparison for common keys:")
                    for key in list(common_keys)[:3]:
                        excel_val = excel_widgets[key]
                        db_val = db_widgets[key]
                        match = excel_val == db_val
                        print(f"   {key}:")
                        print(f"     Excel: {excel_val} (type: {type(excel_val)})")
                        print(f"     DB: {db_val} (type: {type(db_val)})")
                        print(f"     Match: {match}")
            else:
                print("⚠️ Cannot compare key structures - missing data")
            
            # Generate comparison report in landing directory
            comparison_report_path = os.path.join(landing_dir, "landing_widgets_comparison_report.xlsx")
            print(f"📊 Generating comparison report: {comparison_report_path}")
            
            # Debug: Check if files exist before comparison
            print(f"🔍 Checking files before comparison:")
            print(f"   Excel file exists: {os.path.exists(widget_excel_path)}")
            print(f"   Excel file size: {os.path.getsize(widget_excel_path) if os.path.exists(widget_excel_path) else 'N/A'} bytes")
            
            # Normalize data before comparison to ensure consistency
            print("🔄 Normalizing data for consistent comparison...")
            normalized_excel_widgets = self._normalize_widget_data(excel_widgets)
            normalized_db_widgets = self._normalize_widget_data(db_widgets)
            
            print(f"📊 After normalization:")
            print(f"   Excel data points: {len(normalized_excel_widgets)}")
            print(f"   DB data points: {len(normalized_db_widgets)}")
            
            compare_widget_data(
                widget_excel_path,  # Pass file path for comparison function
                normalized_db_widgets,  # Use normalized DB data
                comparison_report_path,
                widget_sp_map
            )
            
            # Debug: Check if comparison file was created
            print(f"🔍 Checking comparison file after generation:")
            print(f"   Comparison file exists: {os.path.exists(comparison_report_path)}")
            print(f"   Comparison file size: {os.path.getsize(comparison_report_path) if os.path.exists(comparison_report_path) else 'N/A'} bytes")
            
            print(f"✅ Landing page widget database comparison completed!")
            print(f"📄 Comparison report saved: {comparison_report_path}")
            print(f"📄 Combined file location: {widget_excel_path}")
            print(f"🎯 Processed widgets: {', '.join(drill_targets)}")
            
        except Exception as e:
            print(f"❌ Error during widget database comparison: {str(e)}")
            import traceback
            print(f"❌ Full error traceback: {traceback.format_exc()}")
            print("⚠️ Continuing with drillthrough process...")
            # Don't raise exception - continue with drillthrough
    
    def _normalize_widget_data(self, data_dict):
        """Normalize widget data for consistent comparison"""
        if not data_dict:
            return {}
        
        normalized = {}
        
        for key, value in data_dict.items():
            # Normalize the key (remove extra spaces, standardize format)
            normalized_key = ' '.join(key.split())
            
            # Normalize the value
            normalized_value = self._normalize_value(value)
            
            normalized[normalized_key] = normalized_value
        
        return normalized
    
    def _normalize_value(self, value):
        """Normalize a single value for comparison"""
        if value is None:
            return 0
        
        # Convert to string first to handle all types
        str_value = str(value).strip()
        
        # Handle empty or null values
        if not str_value or str_value.lower() in ['none', 'null', 'nan', '']:
            return 0
        
        # Try to convert to number
        try:
            # Remove common formatting characters
            clean_value = str_value.replace(',', '').replace('$', '').replace('₹', '').replace('%', '')
            clean_value = clean_value.replace('K', '000').replace('M', '000000').replace('B', '000000000')
            
            # Try to convert to float first, then int if it's a whole number
            float_value = float(clean_value)
            if float_value.is_integer():
                return int(float_value)
            else:
                return round(float_value, 2)
        except (ValueError, AttributeError):
            # If conversion fails, return the original string value
            return str_value
    
    def _add_data_freshness_check(self, widget_sp_map, params):
        """Add timestamp checking to ensure data freshness"""
        try:
            print("🕐 Checking data freshness...")
            
            # Get current timestamp
            import datetime
            current_time = datetime.datetime.now()
            print(f"   Current time: {current_time}")
            
            # Check if we should use current date parameters
            year, month, store, state, channel, fromdate, todate = params
            
            # If no specific date filters, use current date context
            if not fromdate and not todate:
                # Use current year and month for more accurate comparison
                current_year = current_time.year
                current_month = current_time.month
                
                # Update parameters for current data
                updated_params = (current_year, current_month, store, state, channel, fromdate, todate)
                print(f"   Updated params for freshness: Year={current_year}, Month={current_month}")
                return updated_params
            
            return params
            
        except Exception as e:
            print(f"⚠️ Data freshness check failed: {e}")
            return params
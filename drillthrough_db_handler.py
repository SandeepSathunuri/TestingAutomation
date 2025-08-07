import os
from widgetstoreprocedures import widget_sp_map, fetch_db_widget_values, compare_widget_data
from dynamic_comparison_engine import DynamicComparisonEngine
import traceback
from config_loader import config_loader

# Drillthrough widget stored procedure mapping
# ONE SP per drillthrough - each SP matches one specific sheet in the Excel
DRILLTHROUGH_WIDGET_SP_MAP = {
    "Top Stores by Sales": {
        "Love Library": "SP_SalesTrend",  # For "Sales Summary_Sales Trends" sheet
        "default": "SP_SalesTrend"
    },
    "Top Brands by Sales": {
        "Routledge Publications": "SP_TopBrandsBySales",  # For "Sales Summary_Top Brands" sheet  
        "default": "SP_TopBrandsBySales"
    },
    "Top Categories by Sales": {
        "E-Books": "SP_TopProductsBySales",  # For "Sales Summary_Sales by Product" sheet
        "default": "SP_TopProductsBySales"
    },
    "Top Sub Categories by Sales": {
        "Non-Fiction": "SP_WeekdayWeekendSales",  # For "Sales Summary_Weekday Weekend" sheet
        "default": "SP_WeekdayWeekendSales"
    },
    "Top Products by Sales": {
        "MATLAB": "SP_TopProductsBySales",  # For "Sales Summary_Sales by Product" sheet
        "default": "SP_TopProductsBySales"
    },
    "Weekly Trends": {
        "Week1": "SP_WeekwiseSalesComparison",  # For "Sales Summary_Weekwise Sales" sheet
        "default": "SP_WeekwiseSalesComparison"
    }
}

class DrillthroughDBHandler:
    def __init__(self):
        # Drillthrough might need different parameters than landing page
        # You may need to adjust these based on your drillthrough requirements
        self.base_params = (2024, None, None, None, None, None, None)  # year, month, store, state, channel, fromdate, todate
        
        # Initialize dynamic comparison engine
        self.dynamic_engine = DynamicComparisonEngine()
        print("🧠 Dynamic comparison engine initialized")
        
        # Store name to ID mapping (as string for nvarchar parameter)
        self.store_name_to_id = {
            "Love Library": "717",
            "717": "717",  # Allow direct ID input as well
            # Add more store mappings as needed
        }
        
        # Brand/Channel name to ID mapping (if needed)
        self.brand_name_to_id = {
            "Routledge Publications": "Routledge Publications",  # Keep as string if that's what SP expects
            # Add more brand mappings as needed
        }
        
        # Alternative parameter sets for different drillthrough scenarios
        # IMPORTANT: These parameters should match the drillthrough context
        self.drillthrough_params = {
            # Store drillthrough - filter by specific store
            "Love Library": (2024, None, "717", None, None, None, None),  # Store 717
            
            # Brand drillthrough - currently not supported by SPs, use generic
            "Routledge Publications": (2024, None, None, None, None, None, None),  # Generic for now
            
            # Category drillthrough - SPs don't have category parameter, use generic
            "E-Books": (2024, None, None, None, None, None, None),  # Generic for now
            
            # Sub-category drillthrough - SPs don't have subcategory parameter
            "Non-Fiction": (2024, None, None, None, None, None, None),  # Generic for now
            
            # Product drillthrough - SPs don't have product parameter
            "MATLAB": (2024, None, None, None, None, None, None),  # Generic for now
            
            # Time-based drillthrough - SPs don't have week parameter
            "Week1": (2024, None, None, None, None, None, None),  # Generic for now
            
            "default": (2024, None, None, None, None, None, None)
        }
        
        # Track which drillthrough types have proper parameter support
        self.supported_filters = {
            "Love Library": "store",  # Store filter works
            "Routledge Publications": "none",  # Brand filter not supported
            "E-Books": "none",  # Category filter not supported
            "Non-Fiction": "none",  # Subcategory filter not supported
            "MATLAB": "none",  # Product filter not supported
            "Week1": "none"  # Time filter not supported
        }
    
    def get_store_id(self, store_name):
        """Convert store name to store ID (as string for nvarchar parameter)"""
        if store_name in self.store_name_to_id:
            return self.store_name_to_id[store_name]
        
        # If it's already a number string, return as is
        if str(store_name).isdigit():
            return str(store_name)
        
        return None
    
    def get_drillthrough_params(self, submenu_selection):
        """Get appropriate parameters for drillthrough based on submenu selection"""
        if submenu_selection in self.drillthrough_params:
            return self.drillthrough_params[submenu_selection]
        
        # Dynamic parameter generation based on submenu selection
        store_id = self.get_store_id(submenu_selection)
        if store_id:
            return (2024, None, store_id, None, None, None, None)  # store_id is now a string
        
        # Default fallback
        return self.base_params
    
    def get_drillthrough_sp_map(self, widget_title, submenu_selection):
        """Get the appropriate stored procedure map for drillthrough"""
        if widget_title in DRILLTHROUGH_WIDGET_SP_MAP:
            widget_map = DRILLTHROUGH_WIDGET_SP_MAP[widget_title]
            if submenu_selection in widget_map:
                sp_name = widget_map[submenu_selection]
            else:
                sp_name = widget_map.get("default", f"DR_{widget_title.replace(' ', '')}")
            
            # Return a map in the format expected by existing functions
            return {f"{widget_title} - {submenu_selection}": sp_name}
        else:
            # Fallback for unmapped widgets
            return {f"{widget_title} - {submenu_selection}": f"DR_{widget_title.replace(' ', '')}"}
    
    def test_all_drillthrough_sps(self, params):
        """Test all drillthrough stored procedures to see which ones return data"""
        all_sps = [
            "SP_SalesTrend",
            "SP_TopBrandsBySales", 
            "SP_TopPerformingEmployee",
            "SP_TopProductsBySales",
            "SP_WeekdayWeekendSales",
            "SP_WeekwiseSalesComparison"
        ]
        
        print(f"\n🧪 Testing all drillthrough SPs with params: {params}")
        print("="*60)
        
        working_sps = {}
        
        # Convert params to named parameters for better SQL compatibility
        year, month, store, state, channel, fromdate, todate = params
        
        for sp_name in all_sps:
            try:
                from dataBase import DatabaseConnector
                databaseconnect = DatabaseConnector()
                conn = databaseconnect.connect()
                cursor = conn.cursor()
                
                # Try with named parameters first (like SSMS)
                try:
                    sql_query = f"""
                    EXEC [{sp_name}] 
                    @Year=?, @Month=?, @Store=?, @State=?, @Channel=?, @FromDate=?, @ToDate=?
                    """
                    cursor.execute(sql_query, (year, month, store, state, channel, fromdate, todate))
                    result = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    
                    if result:
                        print(f"✅ {sp_name}: {len(result)} rows, columns: {columns}")
                        print(f"   Sample: {dict(zip(columns, result[0]))}")
                        working_sps[sp_name] = {
                            'rows': len(result),
                            'columns': columns,
                            'sample': dict(zip(columns, result[0]))
                        }
                    else:
                        print(f"⚠️ {sp_name}: 0 rows, columns: {columns}")
                        
                except Exception as named_error:
                    # Fallback to positional parameters
                    print(f"🔄 {sp_name}: Named params failed, trying positional...")
                    cursor.execute(f"EXEC [{sp_name}] ?, ?, ?, ?, ?, ?, ?", params)
                    result = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    
                    if result:
                        print(f"✅ {sp_name} (positional): {len(result)} rows, columns: {columns}")
                        working_sps[sp_name] = {
                            'rows': len(result),
                            'columns': columns,
                            'sample': dict(zip(columns, result[0]))
                        }
                    else:
                        print(f"⚠️ {sp_name} (positional): 0 rows, columns: {columns}")
                
                conn.close()
                
            except Exception as e:
                print(f"❌ {sp_name}: Error - {str(e)}")
        
        print("="*60)
        return working_sps

    def fetch_drillthrough_db_data(self, sp_name, params):
        """Fetch data from drillthrough stored procedure with proper formatting"""
        try:
            from dataBase import DatabaseConnector
            databaseconnect = DatabaseConnector()
            conn = databaseconnect.connect()
            cursor = conn.cursor()
            
            # Try named parameters first (like SSMS)
            year, month, store, state, channel, fromdate, todate = params
            
            try:
                sql_query = f"""
                EXEC [{sp_name}] 
                @Year=?, @Month=?, @Store=?, @State=?, @Channel=?, @FromDate=?, @ToDate=?
                """
                print(f"🔍 Executing {sp_name} with named parameters...")
                cursor.execute(sql_query, (year, month, store, state, channel, fromdate, todate))
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
            except Exception as named_error:
                print(f"⚠️ Named parameters failed for {sp_name}, trying positional...")
                cursor.execute(f"EXEC [{sp_name}] ?, ?, ?, ?, ?, ?, ?", params)
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
            
            print(f"📊 SP {sp_name} returned {len(result)} rows with columns: {columns}")
            
            if not result:
                print(f"⚠️ {sp_name} returned no data - trying to test all SPs...")
                working_sps = self.test_all_drillthrough_sps(params)
                if working_sps:
                    print(f"💡 Found {len(working_sps)} working SPs. Consider updating the mapping.")
                return {}
            
            db_data = {}
            
            # Debug: Show sample data from SP
            if result:
                sample_row = dict(zip(columns, result[0]))
                print(f"🔍 Sample SP data: {sample_row}")
            
            # Handle different SP return formats
            if 'Month' in columns and 'CurrentYearSales' in columns and 'PreviousYearSales' in columns:
                # Sales Trend format - convert full month names to abbreviated
                month_abbreviations = {
                    'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
                    'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
                    'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
                }
                
                for row in result:
                    row_dict = dict(zip(columns, row))
                    full_month = str(row_dict['Month']).strip()
                    # Convert to abbreviated month to match Excel format
                    month = month_abbreviations.get(full_month, full_month)
                    current_sales = row_dict['CurrentYearSales']
                    previous_sales = row_dict['PreviousYearSales']
                    
                    if current_sales is not None:
                        db_data[f"Sales Summary_Sales Trends - {month} Current Year"] = str(current_sales).strip()
                    if previous_sales is not None:
                        db_data[f"Sales Summary_Sales Trends - {month} Previous Year"] = str(previous_sales).strip()
            
            elif ('DayType' in columns or 'WeekCategory' in columns) and 'CurrentYearSales' in columns and 'PreviousYearSales' in columns:
                # Check if this is weekday/weekend data by looking at the actual values
                sample_row = result[0] if result else None
                if sample_row:
                    sample_dict = dict(zip(columns, sample_row))
                    sample_value = str(sample_dict.get('DayType') or sample_dict.get('WeekCategory', '')).strip().upper()
                    
                    # If it contains "WEEKDAY" or "WEEKEND", it's weekday/weekend data
                    if 'WEEKDAY' in sample_value or 'WEEKEND' in sample_value:
                        # Weekday/Weekend format
                        for row in result:
                            row_dict = dict(zip(columns, row))
                            day_type = str(row_dict.get('DayType') or row_dict.get('WeekCategory', 'Unknown')).strip().upper()
                            current_sales = row_dict['CurrentYearSales']
                            previous_sales = row_dict['PreviousYearSales']
                            
                            if current_sales is not None:
                                # Create multiple key formats to match different Excel structures
                                db_data[f"Sales Summary_Weekday Weekend - {day_type} Current Year"] = str(current_sales).strip()
                                db_data[f"Weekly Trends - {day_type} Current Year"] = str(current_sales).strip()
                                # Handle the specific case where Excel shows "WEEKDAY SALES" or "WEEKEND SALES"
                                if day_type in ['WEEKDAY', 'WEEKEND']:
                                    db_data[f"Weekly Trends - {day_type} SALES Current Year"] = str(current_sales).strip()
                            if previous_sales is not None:
                                db_data[f"Sales Summary_Weekday Weekend - {day_type} Previous Year"] = str(previous_sales).strip()
                                db_data[f"Weekly Trends - {day_type} Previous Year"] = str(previous_sales).strip()
                                # Handle the specific case where Excel shows "WEEKDAY SALES" or "WEEKEND SALES"
                                if day_type in ['WEEKDAY', 'WEEKEND']:
                                    db_data[f"Weekly Trends - {day_type} SALES Previous Year"] = str(previous_sales).strip()
                    else:
                        # Weekly format - handle both 'Week' and 'WeekCategory' columns
                        for row in result:
                            row_dict = dict(zip(columns, row))
                            week = str(row_dict.get('Week') or row_dict.get('WeekCategory', 'Unknown')).strip()
                            current_sales = row_dict['CurrentYearSales']
                            previous_sales = row_dict['PreviousYearSales']
                            
                            if current_sales is not None:
                                db_data[f"Sales Summary_Weekwise Sales - {week} Current Year"] = str(current_sales).strip()
                            if previous_sales is not None:
                                db_data[f"Sales Summary_Weekwise Sales - {week} Previous Year"] = str(previous_sales).strip()
            
            elif ('Week' in columns) and 'CurrentYearSales' in columns and 'PreviousYearSales' in columns:
                # Pure Weekly format (Week column only)
                for row in result:
                    row_dict = dict(zip(columns, row))
                    week = str(row_dict.get('Week', 'Unknown')).strip()
                    current_sales = row_dict['CurrentYearSales']
                    previous_sales = row_dict['PreviousYearSales']
                    
                    if current_sales is not None:
                        db_data[f"Sales Summary_Weekwise Sales - {week} Current Year"] = str(current_sales).strip()
                    if previous_sales is not None:
                        db_data[f"Sales Summary_Weekwise Sales - {week} Previous Year"] = str(previous_sales).strip()
            
            elif 'ProductName' in columns and 'Sales' in columns:
                # Product sales format
                for row in result:
                    row_dict = dict(zip(columns, row))
                    product_name = str(row_dict['ProductName']).strip()
                    sales = row_dict['Sales']
                    
                    if sales is not None:
                        db_data[f"Sales Summary_Sales by Product - {product_name}"] = str(sales).strip()
            
            elif 'BrandName' in columns and 'Sales' in columns:
                # Brand sales format
                for row in result:
                    row_dict = dict(zip(columns, row))
                    brand_name = str(row_dict['BrandName']).strip()
                    sales = row_dict['Sales']
                    
                    if sales is not None:
                        db_data[f"Sales Summary_Top Brands by Sales - {brand_name}"] = str(sales).strip()
            
            elif 'EmployeeName' in columns and 'Sales' in columns:
                # Employee performance format
                for row in result:
                    row_dict = dict(zip(columns, row))
                    employee_name = str(row_dict['EmployeeName']).strip()
                    sales = row_dict['Sales']
                    
                    if sales is not None:
                        db_data[f"Sales Summary_Top Performing Employee - {employee_name}"] = str(sales).strip()
            
            else:
                # Generic format - try to match first column as identifier, second as value
                print(f"🔍 Using generic format for {sp_name} with columns: {columns}")
                if result and len(columns) >= 2:
                    for row in result:
                        row_dict = dict(zip(columns, row))
                        identifier = str(row[0]).strip() if row[0] else "Unknown"
                        value = str(row[1]).strip() if row[1] is not None else "0"
                        db_data[f"Generic_{sp_name} - {identifier}"] = value
            
            conn.close()
            
            # Debug: Show generated database keys
            if db_data:
                print(f"🔑 Generated {len(db_data)} database keys:")
                for key in sorted(db_data.keys())[:10]:  # Show first 10 keys
                    print(f"   📋 {key} = {db_data[key]}")
                if len(db_data) > 10:
                    print(f"   ... and {len(db_data) - 10} more keys")
            else:
                print("⚠️ No database keys generated!")
            
            return db_data
            
        except Exception as e:
            print(f"❌ Error fetching drillthrough DB data: {str(e)}")
            return {}

    def compare_drillthrough_widgets(self, excel_path, widget_title, submenu_selection, output_path):
        """Enhanced drillthrough comparison using specific SPs for each drillthrough type"""
        try:
            print(f"🧠 Starting SPECIFIC drillthrough comparison for: {widget_title} -> {submenu_selection}")
            
            # Check if this is Love Library drillthrough (use specific SP approach)
            if submenu_selection == "Love Library":
                print(f"✅ Using Love Library specific stored procedures")
                return self._compare_love_library_drillthrough(excel_path, output_path)
            
            # Check if this drillthrough type has proper parameter support
            filter_support = self.supported_filters.get(submenu_selection, "none")
            if filter_support == "none":
                print(f"⚠️ WARNING: {submenu_selection} drillthrough may show data scope mismatch")
                print(f"   Excel shows filtered data, but stored procedures return full dataset")
                print(f"   This is expected until SP parameters are enhanced for this drillthrough type")
            else:
                print(f"✅ {submenu_selection} drillthrough has proper {filter_support} filtering")
            
            # Verify the Excel file exists
            if not os.path.exists(excel_path):
                print(f"❌ Excel file not found: {excel_path}")
                return False
            
            # Get appropriate parameters for this drillthrough
            drillthrough_params = self.get_drillthrough_params(submenu_selection)
            print(f"📋 Using drillthrough params: {drillthrough_params}")
            
            # Use dynamic comparison engine (eliminates hardcoded mappings!)
            print(f"🚀 Using dynamic comparison engine...")
            success = self.dynamic_engine.dynamic_compare_data(
                excel_path=excel_path,
                params=drillthrough_params,
                output_path=output_path
            )
            
            if success:
                file_size = os.path.getsize(output_path)
                print(f"✅ DYNAMIC drillthrough comparison completed!")
                print(f"📄 Output: {os.path.basename(output_path)} ({file_size:,} bytes)")
                print(f"🎉 No hardcoded mappings needed - automatically detected patterns!")
                return True
            else:
                print(f"❌ Dynamic comparison failed for {widget_title}")
                # Fallback to legacy method if dynamic fails
                print(f"🔄 Attempting fallback to legacy method...")
                return self._legacy_compare_drillthrough_widgets(excel_path, widget_title, submenu_selection, output_path)
            
        except Exception as e:
            print(f"❌ Dynamic drillthrough comparison failed for {widget_title}: {str(e)}")
            print(f"🔄 Attempting fallback to legacy method...")
            return self._legacy_compare_drillthrough_widgets(excel_path, widget_title, submenu_selection, output_path)
    
    def _compare_love_library_drillthrough(self, excel_path, output_path):
        """Compare Love Library drillthrough using specific stored procedures"""
        try:
            print(f"🏬 Love Library specific comparison...")
            
            # Love Library specific stored procedures
            love_library_sps = {
                "SP_SalesTrend": "Sales Summary_Sales Trends",
                "SP_TopPerformingEmployee": "Sales Summary_Top Performing Employee", 
                "SP_TopProductsBySales": "Sales Summary_Sales by Product",
                "SP_WeekdayWeekendSales": "Sales Summary_Weekday Weekend",
                "SP_WeekwiseSalesComparison": "Sales Summary_Weekwise Sales"
            }
            
            # Get Love Library parameters (Store 717)
            params = (2024, None, "717", None, None, None, None)
            all_data = {}
            
            for sp_name, sheet_name in love_library_sps.items():
                print(f"📊 Fetching data from {sp_name}...")
                
                try:
                    sp_data = self.fetch_drillthrough_db_data(sp_name, params)
                    if sp_data:
                        all_data.update(sp_data)
                        print(f"✅ {sp_name}: Added {len(sp_data)} values")
                    else:
                        print(f"⚠️ {sp_name}: No data returned")
                except Exception as sp_error:
                    print(f"❌ Error with {sp_name}: {str(sp_error)}")
            
            print(f"📊 Total Love Library data points: {len(all_data)}")
            
            if not all_data:
                print("❌ No Love Library data retrieved")
                return False
            
            # Use the existing comparison function
            dummy_sp_map = {"Love Library Drillthrough": "Multiple_Love_Library_SPs"}
            compare_widget_data(excel_path, all_data, output_path, dummy_sp_map)
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ Love Library comparison completed!")
                print(f"📄 Output: {os.path.basename(output_path)} ({file_size:,} bytes)")
                return True
            else:
                print(f"❌ Love Library comparison file was not created")
                return False
                
        except Exception as e:
            print(f"❌ Love Library comparison failed: {str(e)}")
            return False
    
    def _legacy_compare_drillthrough_widgets(self, excel_path, widget_title, submenu_selection, output_path):
        """Legacy drillthrough comparison method (fallback)"""
        try:
            print(f"🔄 Legacy drillthrough comparison for: {widget_title} -> {submenu_selection}")
            
            # Get appropriate parameters for this drillthrough
            drillthrough_params = self.get_drillthrough_params(submenu_selection)
            
            # Use MULTIPLE stored procedures to get data for different sheets
            print(f"🔍 Fetching DB values from multiple SPs (legacy method)...")
            db_data = {}
            
            # Map of sheet patterns to stored procedures
            sheet_sp_mapping = {
                "Sales Trends": "SP_SalesTrend",
                "Weekwise Sales": "SP_WeekwiseSalesComparison", 
                "Weekday Weekend": "SP_WeekdayWeekendSales",
                "Sales by Product": "SP_TopProductsBySales"
            }
            
            # Fetch data from each relevant SP
            for sheet_pattern, sp_name in sheet_sp_mapping.items():
                print(f"🔍 Fetching data from {sp_name} for {sheet_pattern} sheets...")
                try:
                    sp_data = self.fetch_drillthrough_db_data(sp_name, drillthrough_params)
                    if sp_data:
                        db_data.update(sp_data)
                        print(f"✅ Got {len(sp_data)} values from {sp_name}")
                    else:
                        print(f"⚠️ No data from {sp_name}")
                except Exception as sp_error:
                    print(f"❌ Error with {sp_name}: {str(sp_error)}")
            
            print(f"📊 Total fetched: {len(db_data)} DB values")
            
            if not db_data:
                print("❌ No DB data returned from any SP!")
                return False
            
            # Compare with Excel data using the specialized function
            print(f"🔍 Starting legacy comparison...")
            # Create a dummy SP map for the comparison function
            dummy_sp_map = {f"{widget_title} - {submenu_selection}": "Multiple_SPs"}
            compare_widget_data(excel_path, db_data, output_path, dummy_sp_map)
            print(f"✅ Legacy drillthrough comparison completed: {output_path}")
            
            # Verify comparison file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📄 Legacy comparison file created: {os.path.basename(output_path)} ({file_size:,} bytes)")
                return True
            else:
                print(f"❌ Legacy comparison file was not created: {output_path}")
                return False
            
        except Exception as e:
            print(f"❌ Legacy drillthrough comparison failed for {widget_title}: {str(e)}")

            print(f"🔍 Error details: {traceback.format_exc()}")
            return False
    
    def process_drillthrough_directory(self, drillthrough_dir, widget_title, submenu_selection):
        """Process all widget files in a drillthrough directory"""
        try:
            # Look for the merged widget file
            merged_files = [f for f in os.listdir(drillthrough_dir) 
                          if f.endswith("_drillthrough_widgets.xlsx")]
            
            if not merged_files:
                print(f"⚠️ No merged drillthrough widget file found in: {drillthrough_dir}")
                return False
            
            merged_file = merged_files[0]  # Take the first one
            excel_path = os.path.join(drillthrough_dir, merged_file)
            
            # Create comparison report path
            safe_title = widget_title.replace(" ", "_").replace("/", "_")
            safe_submenu = submenu_selection.replace(" ", "_").replace("/", "_")
            comparison_filename = f"{safe_title}_{safe_submenu}_widget_comparison.xlsx"
            output_path = os.path.join(drillthrough_dir, comparison_filename)
            
            # Perform comparison
            return self.compare_drillthrough_widgets(
                excel_path, widget_title, submenu_selection, output_path
            )
            
        except Exception as e:
            print(f"❌ Error processing drillthrough directory {drillthrough_dir}: {str(e)}")
            return False
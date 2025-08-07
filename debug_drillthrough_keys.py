"""
Debug Drillthrough Key Matching
==============================
Script to help debug why drillthrough database values show as "Not Found"
"""

def debug_key_matching():
    """Debug the key matching issue"""
    print("🔍 Drillthrough Key Matching Debug")
    print("=" * 50)
    
    # Example of what we're seeing in the error
    excel_identifiers = [
        "WEEKDAY SALES",
        "WEEKEND SALES"
    ]
    
    excel_metrics = [
        "Previous Year", 
        "Current Year"
    ]
    
    widget_name = "Weekly Trends"
    
    print("📊 Excel is looking for keys like:")
    for identifier in excel_identifiers:
        for metric in excel_metrics:
            key = f"{widget_name} - {identifier} {metric}"
            print(f"   🔍 {key}")
    
    print("\n🗄️ Database is generating keys like:")
    # Based on the drillthrough_db_handler.py logic
    day_types = ["WEEKDAY", "WEEKEND"]
    for day_type in day_types:
        for metric in excel_metrics:
            # Original format
            key1 = f"Sales Summary_Weekday Weekend - {day_type} {metric}"
            print(f"   📋 {key1}")
            
            # New format we added
            key2 = f"Weekly Trends - {day_type} {metric}"
            print(f"   📋 {key2}")
            
            # Format for "SALES" suffix
            key3 = f"Weekly Trends - {day_type} SALES {metric}"
            print(f"   📋 {key3}")
    
    print("\n🔧 Key Matching Analysis:")
    print("❌ MISMATCH: Excel looks for 'WEEKDAY SALES' but DB has 'WEEKDAY'")
    print("❌ MISMATCH: Excel looks for 'WEEKEND SALES' but DB has 'WEEKEND'")
    
    print("\n💡 SOLUTION: The alternative key matching should work!")
    print("✅ Excel: 'Weekly Trends - WEEKDAY SALES Previous Year'")
    print("✅ DB:    'Weekly Trends - WEEKDAY SALES Previous Year' (new format)")
    
    print("\n🧪 Test the fix by running your automation and checking the debug output!")

if __name__ == "__main__":
    debug_key_matching()
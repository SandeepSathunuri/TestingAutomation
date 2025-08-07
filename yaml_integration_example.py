#!/usr/bin/env python3
"""
YAML Configuration Integration Example
=====================================
This example shows how to use the YAML configuration files
"""

from config_loader import config_loader

def example_usage():
    """Example of using YAML configurations"""
    
    print("🔧 YAML Configuration Integration Example")
    print("=" * 50)
    
    # 1. Get landing page widget mappings
    print("\n📊 Landing Page Widget Mappings:")
    widget_mappings = config_loader.get_landing_page_widgets()
    for widget, sp in widget_mappings.items():
        print(f"  {widget} → {sp}")
    
    # 2. Get drillthrough parameters
    print("\n🎯 Drillthrough Parameters:")
    love_library_params = config_loader.get_drillthrough_parameters("Love Library")
    print(f"  Love Library: {love_library_params}")
    
    # 3. Get store mappings
    print("\n🏪 Store Mappings:")
    store_id = config_loader.get_store_mapping("Love Library")
    print(f"  Love Library → Store ID: {store_id}")
    
    # 4. Check filter support
    print("\n🔍 Filter Support:")
    filter_type = config_loader.is_filter_supported("Love Library")
    print(f"  Love Library filter type: {filter_type}")
    
    # 5. Get dynamic engine SPs
    print("\n🧠 Dynamic Engine SPs:")
    dynamic_sps = config_loader.get_dynamic_engine_sps()
    print(f"  Available SPs: {len(dynamic_sps)}")
    for sp in dynamic_sps[:5]:  # Show first 5
        print(f"    - {sp}")
    
    # 6. Get configuration summary
    print("\n📋 Configuration Summary:")
    summary = config_loader.get_config_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

def example_drillthrough_integration():
    """Example of integrating YAML config with drillthrough"""
    
    print("\n🔄 Drillthrough Integration Example:")
    print("-" * 40)
    
    # Get drillthrough configuration
    submenu = "Love Library"
    params = config_loader.get_drillthrough_parameters(submenu)
    procedures = config_loader.get_drillthrough_procedures("love_library")
    
    print(f"Target: {submenu}")
    print(f"Parameters: {params}")
    print(f"Procedures: {list(procedures.keys())}")
    
    # Validate parameters
    is_valid = config_loader.validate_parameters(params)
    print(f"Parameters valid: {is_valid}")

def example_widget_integration():
    """Example of integrating YAML config with widgets"""
    
    print("\n🧩 Widget Integration Example:")
    print("-" * 40)
    
    # Get widget mappings
    widget_mappings = config_loader.get_widget_mappings()
    landing_widgets = widget_mappings.get("widget_sheet_mappings", {}).get("landing_page", {})
    
    print("Landing Page Widgets:")
    for sheet_name, config in landing_widgets.items():
        display_name = config.get("display_name", "Unknown")
        data_type = config.get("data_type", "Unknown")
        has_targets = config.get("has_targets", False)
        print(f"  {display_name} ({data_type}) - Targets: {has_targets}")

if __name__ == "__main__":
    example_usage()
    example_drillthrough_integration()
    example_widget_integration()
    
    print("\n✅ YAML Configuration Integration Example Completed!")

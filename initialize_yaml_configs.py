#!/usr/bin/env python3
"""
Initialize YAML Configurations
==============================
This script updates the existing code to use YAML configuration files
"""

import os
import sys
from config_loader import config_loader

def update_widget_stored_procedures():
    """Update widgetstoreprocedures.py to use YAML config"""
    print("🔧 Updating widgetstoreprocedures.py...")
    
    # Get the widget SP mapping from YAML
    widget_sp_map = config_loader.get_landing_page_widgets()
    
    print(f"📊 Loaded {len(widget_sp_map)} widget mappings from YAML")
    
    # Read the current file
    file_path = "widgetstoreprocedures.py"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create the new widget_sp_map content
    yaml_import = "from config_loader import config_loader\n"
    new_map_line = "widget_sp_map = config_loader.get_landing_page_widgets()"
    
    # Add import at the top if not already present
    if "from config_loader import config_loader" not in content:
        # Find the last import line
        lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_end = i
        
        # Insert the new import after the last import
        lines.insert(import_end + 1, yaml_import.strip())
        content = '\n'.join(lines)
    
    # Replace the hardcoded widget_sp_map
    if "widget_sp_map = {" in content:
        # Find the start and end of the widget_sp_map definition
        start_marker = "widget_sp_map = {"
        end_marker = "}"
        
        start_pos = content.find(start_marker)
        if start_pos != -1:
            # Find the matching closing brace
            brace_count = 0
            end_pos = start_pos + len(start_marker)
            
            for i in range(start_pos + len(start_marker), len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    if brace_count == 0:
                        end_pos = i + 1
                        break
                    brace_count -= 1
            
            # Replace the hardcoded map with YAML loader
            new_content = content[:start_pos] + new_map_line + content[end_pos:]
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            print(f"✅ Updated {file_path} to use YAML configuration")
            return True
    
    print(f"⚠️ Could not find widget_sp_map in {file_path}")
    return False

def update_drillthrough_db_handler():
    """Update drillthrough_db_handler.py to use YAML config"""
    print("🔧 Updating drillthrough_db_handler.py...")
    
    file_path = "drillthrough_db_handler.py"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Add import at the top if not already present
    yaml_import = "from config_loader import config_loader\n"
    
    if "from config_loader import config_loader" not in content:
        # Find the last import line
        lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_end = i
        
        # Insert the new import after the last import
        lines.insert(import_end + 1, yaml_import.strip())
        content = '\n'.join(lines)
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"✅ Added YAML config import to {file_path}")
        return True
    
    print(f"✅ {file_path} already has YAML config import")
    return True

def update_dynamic_comparison_engine():
    """Update dynamic_comparison_engine.py to use YAML config"""
    print("🔧 Updating dynamic_comparison_engine.py...")
    
    file_path = "dynamic_comparison_engine.py"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Add import at the top if not already present
    yaml_import = "from config_loader import config_loader\n"
    
    if "from config_loader import config_loader" not in content:
        # Find the last import line
        lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_end = i
        
        # Insert the new import after the last import
        lines.insert(import_end + 1, yaml_import.strip())
        content = '\n'.join(lines)
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"✅ Added YAML config import to {file_path}")
        return True
    
    print(f"✅ {file_path} already has YAML config import")
    return True

def create_yaml_integration_example():
    """Create an example showing how to use YAML configs"""
    print("📝 Creating YAML integration example...")
    
    example_content = '''#!/usr/bin/env python3
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
    print("\\n📊 Landing Page Widget Mappings:")
    widget_mappings = config_loader.get_landing_page_widgets()
    for widget, sp in widget_mappings.items():
        print(f"  {widget} → {sp}")
    
    # 2. Get drillthrough parameters
    print("\\n🎯 Drillthrough Parameters:")
    love_library_params = config_loader.get_drillthrough_parameters("Love Library")
    print(f"  Love Library: {love_library_params}")
    
    # 3. Get store mappings
    print("\\n🏪 Store Mappings:")
    store_id = config_loader.get_store_mapping("Love Library")
    print(f"  Love Library → Store ID: {store_id}")
    
    # 4. Check filter support
    print("\\n🔍 Filter Support:")
    filter_type = config_loader.is_filter_supported("Love Library")
    print(f"  Love Library filter type: {filter_type}")
    
    # 5. Get dynamic engine SPs
    print("\\n🧠 Dynamic Engine SPs:")
    dynamic_sps = config_loader.get_dynamic_engine_sps()
    print(f"  Available SPs: {len(dynamic_sps)}")
    for sp in dynamic_sps[:5]:  # Show first 5
        print(f"    - {sp}")
    
    # 6. Get configuration summary
    print("\\n📋 Configuration Summary:")
    summary = config_loader.get_config_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

def example_drillthrough_integration():
    """Example of integrating YAML config with drillthrough"""
    
    print("\\n🔄 Drillthrough Integration Example:")
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
    
    print("\\n🧩 Widget Integration Example:")
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
    
    print("\\n✅ YAML Configuration Integration Example Completed!")
'''
    
    with open("yaml_integration_example.py", 'w', encoding='utf-8') as file:
        file.write(example_content)
    
    print("✅ Created yaml_integration_example.py")

def main():
    """Main initialization function"""
    print("🚀 Initializing YAML Configuration Integration")
    print("=" * 60)
    
    # Check if config directory exists
    if not os.path.exists("config"):
        print("❌ Config directory not found. Please ensure YAML files are created first.")
        return False
    
    # Test configuration loading
    print("🔍 Testing configuration loading...")
    try:
        summary = config_loader.get_config_summary()
        print(f"✅ Successfully loaded {len(summary['loaded_configs'])} configurations")
    except Exception as e:
        print(f"❌ Error loading configurations: {str(e)}")
        return False
    
    # Update existing files
    success_count = 0
    
    if update_widget_stored_procedures():
        success_count += 1
    
    if update_drillthrough_db_handler():
        success_count += 1
    
    if update_dynamic_comparison_engine():
        success_count += 1
    
    # Create example
    create_yaml_integration_example()
    success_count += 1
    
    print(f"\\n📊 Initialization Summary:")
    print(f"  ✅ Successfully updated: {success_count} files")
    print(f"  📁 Configuration files: {len(summary['config_files'])}")
    print(f"  🔧 Total stored procedures: {summary['total_stored_procedures']}")
    print(f"  🎯 Total drillthrough targets: {summary['total_drillthrough_targets']}")
    
    print(f"\\n🎉 YAML Configuration Integration Complete!")
    print(f"\\n📝 Next Steps:")
    print(f"  1. Review the updated files for any needed adjustments")
    print(f"  2. Test the application with: python newmain.py")
    print(f"  3. Run the example with: python yaml_integration_example.py")
    print(f"  4. Customize YAML files as needed for your environment")
    
    return True

if __name__ == "__main__":
    main()
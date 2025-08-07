#!/usr/bin/env python3
"""
Test the new operation order (Expand first, then Download for landing page)
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from login import Authenticator
from dashboardSelection import DashboardManager
from filters import FilterAutomation
from widgetsdataextract import WidgetExtractor

def setup_chrome_driver():
    """Setup Chrome driver"""
    download_dir = os.path.abspath("download")
    os.makedirs(download_dir, exist_ok=True)
    
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def test_operation_order():
    """Test the new operation order for landing page"""
    driver = None
    try:
        print("🚀 Testing new operation order (Expand first, then Download)...")
        
        # Setup
        driver = setup_chrome_driver()
        
        # Login
        login = Authenticator(driver)
        login.login()
        print("✅ Login successful")
        
        # Select Dashboard
        dashboard = DashboardManager(driver)
        dashboard.choose_dashboard("Sales Summary")
        print("✅ Dashboard selected")
        
        # Apply filters
        try:
            filter_automation = FilterAutomation(driver)
            filter_automation.run()
            print("✅ Filters applied")
        except:
            print("⚠️ Filter application failed, continuing...")
        
        # Wait for page to fully load
        time.sleep(3)
        
        # Test the new operation order
        print("\n🔍 Testing new operation order on landing page...")
        widget_extractor = WidgetExtractor(driver)
        
        # Find first widget
        from widget_components.widget_loader import WidgetLoader
        loader = WidgetLoader(driver)
        widgets = loader.get_widgets()
        
        if widgets:
            first_widget = widgets[0]
            title = loader.get_widget_title(first_widget)
            print(f"🎯 Testing widget: {title}")
            
            # Test the improved both operations method with new order
            download_success, expand_success = widget_extractor._handle_both_operations(first_widget, title)
            
            print(f"\n📊 Results:")
            print(f"   🔍 Expand result: {expand_success}")
            print(f"   📥 Download result: {download_success}")
            
            if download_success and expand_success:
                print("🎉 Both operations successful with new order!")
                print("✅ Landing page expand issue is FIXED!")
            elif expand_success and not download_success:
                print("✅ Expand working, ⚠️ download needs attention")
            elif download_success and not expand_success:
                print("✅ Download working, ❌ expand still has issues")
            else:
                print("❌ Both operations still have issues")
                
            # Check if files were downloaded
            download_dir = os.path.abspath("download")
            if os.path.exists(download_dir):
                files = [f for f in os.listdir(download_dir) if f.endswith('.xlsx')]
                print(f"📁 Downloaded files: {len(files)}")
                for f in files[-3:]:  # Show last 3 files
                    print(f"   • {f}")
            
        else:
            print("❌ No widgets found")
        
        print(f"\n📋 Summary:")
        print(f"   - New order: Expand first, then Download")
        print(f"   - This should prevent menu closing issues")
        print(f"   - Landing page expand should now work!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            try:
                input("\n⏸️  Press Enter to close browser...")
                driver.quit()
                print("🔄 Browser closed")
            except:
                pass

if __name__ == "__main__":
    test_operation_order()
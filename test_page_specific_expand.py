#!/usr/bin/env python3
"""
Test page-specific expand logic
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

def test_page_specific_expand():
    """Test the page-specific expand logic"""
    driver = None
    try:
        print("🚀 Testing page-specific expand logic...")
        
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
        
        # Test landing page expand
        print("\n🔍 Testing landing page expand...")
        widget_extractor = WidgetExtractor(driver)
        
        # Detect page type
        page_type = widget_extractor._detect_page_type()
        print(f"📍 Detected page type: {page_type}")
        
        # Find first widget
        from widget_components.widget_loader import WidgetLoader
        loader = WidgetLoader(driver)
        widgets = loader.get_widgets()
        
        if widgets:
            first_widget = widgets[0]
            title = loader.get_widget_title(first_widget)
            print(f"🎯 Testing widget: {title}")
            
            # Test the improved both operations method
            download_success, expand_success = widget_extractor._handle_both_operations(first_widget, title)
            
            print(f"📥 Download result: {download_success}")
            print(f"🔍 Expand result: {expand_success}")
            
            if expand_success:
                print("🎉 Landing page expand is now working!")
            else:
                print("❌ Landing page expand still has issues")
                
            # If we have drillthrough capability, test that too
            if download_success:
                print("\n🔄 Testing drillthrough expand...")
                try:
                    # Perform drillthrough
                    from widget_components.drillthrough_handler import DrillthroughHandler
                    drill_handler = DrillthroughHandler(driver)
                    
                    # This would test drillthrough expand, but let's keep it simple for now
                    print("✅ Drillthrough test would go here")
                    
                except Exception as drill_error:
                    print(f"⚠️ Drillthrough test skipped: {drill_error}")
        else:
            print("❌ No widgets found")
        
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
    test_page_specific_expand()
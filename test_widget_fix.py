#!/usr/bin/env python3
"""
Test script to verify widget menu fixes
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from login import Authenticator
from dashboardSelection import DashboardManager
from filters import FilterAutomation
from widgetsdataextract import WidgetExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_chrome_driver():
    """Setup Chrome driver for testing"""
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
    
    # Performance optimizations
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": download_dir
    })
    
    return driver

def test_widget_processing():
    """Test the improved widget processing"""
    driver = None
    try:
        print("🚀 Starting widget processing test...")
        
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
        filter_automation = FilterAutomation(driver)
        filter_automation.run()
        print("✅ Filters applied")
        
        # Test widget processing with improved logic
        print("🧩 Testing improved widget processing...")
        widget_extractor = WidgetExtractor(driver)
        
        # Process just the first widget to test the fix
        from widget_components.widget_loader import WidgetLoader
        loader = WidgetLoader(driver)
        widgets = loader.get_widgets()
        
        if widgets:
            first_widget = widgets[0]
            title = loader.get_widget_title(first_widget)
            print(f"🎯 Testing widget: {title}")
            
            # Test the improved download method
            download_success = widget_extractor._handle_widget_download(first_widget, title)
            print(f"📥 Download result: {download_success}")
            
            # Test the improved expand method
            expand_success = widget_extractor._handle_widget_expand(first_widget, title)
            print(f"🔍 Expand result: {expand_success}")
            
            if download_success or expand_success:
                print("✅ Widget processing improvements working!")
            else:
                print("❌ Widget processing still has issues")
        else:
            print("❌ No widgets found for testing")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            try:
                time.sleep(2)
                driver.quit()
                print("🔄 Browser closed")
            except:
                pass

if __name__ == "__main__":
    test_widget_processing()
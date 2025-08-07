#!/usr/bin/env python3
"""
Test the single menu session approach
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
from widget_components.widget_menu import WidgetMenuHandler
from selenium.webdriver.common.action_chains import ActionChains

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

def test_single_menu_session():
    """Test the single menu session approach"""
    driver = None
    try:
        print("🚀 Testing single menu session approach...")
        
        # Setup
        driver = setup_chrome_driver()
        wait = WebDriverWait(driver, 10)
        actions = ActionChains(driver)
        
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
        
        # Wait for widgets to load
        time.sleep(3)
        
        # Test the menu handler with single session approach
        menu_handler = WidgetMenuHandler(driver, wait, actions)
        
        # Find first widget
        widgets = driver.find_elements(By.CSS_SELECTOR, ".chart-container")
        if widgets:
            first_widget = widgets[0]
            
            # Get widget title
            try:
                title = first_widget.find_element(By.CLASS_NAME, "chart-title").text.strip()
                print(f"🎯 Testing widget: {title}")
            except:
                title = "Unknown Widget"
                print(f"🎯 Testing widget: {title}")
            
            # Test single menu session approach
            print("🔄 Testing single menu session...")
            if menu_handler.click_widget_menu(first_widget):
                print("✅ Menu opened successfully!")
                
                # Test both operations in one session
                download_success, expand_success = menu_handler.handle_both_operations()
                
                print(f"📥 Download result: {download_success}")
                print(f"🔍 Expand result: {expand_success}")
                
                if download_success and expand_success:
                    print("🎉 Single menu session approach working perfectly!")
                elif download_success or expand_success:
                    print("✅ Single menu session partially working")
                else:
                    print("❌ Single menu session approach needs improvement")
                    
            else:
                print("❌ Menu opening failed")
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
    test_single_menu_session()
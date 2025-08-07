#!/usr/bin/env python3
"""
Focused test for Expand button clicking issue on landing page
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

def test_expand_button_click():
    """Test specifically the Expand button clicking on landing page"""
    driver = None
    try:
        print("🚀 Testing Expand button clicking on landing page...")
        
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
        try:
            filter_automation = FilterAutomation(driver)
            filter_automation.run()
            print("✅ Filters applied")
        except:
            print("⚠️ Filter application failed, continuing...")
        
        # Wait for page to fully load
        time.sleep(3)
        
        # Find first widget
        widgets = driver.find_elements(By.CSS_SELECTOR, ".chart-container")
        if not widgets:
            print("❌ No widgets found")
            return
        
        first_widget = widgets[0]
        
        # Get widget title
        try:
            title = first_widget.find_element(By.CLASS_NAME, "chart-title").text.strip()
            print(f"🎯 Testing widget: {title}")
        except:
            title = "Unknown Widget"
            print(f"🎯 Testing widget: {title}")
        
        # Setup menu handler
        menu_handler = WidgetMenuHandler(driver, wait, actions)
        
        # Test 1: Open menu and try to click Expand
        print("\n🔍 Test 1: Direct Expand button click")
        if menu_handler.click_widget_menu(first_widget):
            print("✅ Menu opened successfully")
            
            # Try to click Expand with enhanced debugging
            expand_success = menu_handler.click_menu_item("Expand", "landing")
            
            if expand_success:
                print("🎉 Expand button clicked successfully!")
                
                # Wait and check if anything happened
                time.sleep(3)
                
                # Check for modal or any changes
                modal_selectors = ["ngb-modal-window", ".modal", "[role='dialog']", ".cdk-overlay-pane"]
                modal_found = False
                for selector in modal_selectors:
                    if driver.find_elements(By.CSS_SELECTOR, selector):
                        modal_found = True
                        print(f"✅ Modal appeared: {selector}")
                        break
                
                if not modal_found:
                    print("⚠️ No modal detected, but click succeeded")
                
                # Try to close any modal that appeared
                try:
                    from selenium.webdriver.common.keys import Keys
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    print("✅ Attempted to close modal with ESC")
                except:
                    pass
                    
            else:
                print("❌ Expand button click failed")
                
                # Debug: Show current page state
                print("🔍 Debug: Current page state")
                try:
                    current_url = driver.current_url
                    page_title = driver.title
                    print(f"   URL: {current_url}")
                    print(f"   Title: {page_title}")
                    
                    # Check if menu is still open
                    menu_items = driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item")
                    print(f"   Menu items still visible: {len(menu_items)}")
                    
                except Exception as debug_error:
                    print(f"   Debug failed: {debug_error}")
        else:
            print("❌ Could not open menu")
        
        # Test 2: Try alternative approach - double click on title
        print("\n🔍 Test 2: Alternative approach - double click on title")
        try:
            # Refresh widget reference
            widgets = driver.find_elements(By.CSS_SELECTOR, ".chart-container")
            if widgets:
                fresh_widget = widgets[0]
                title_elem = fresh_widget.find_element(By.CLASS_NAME, "chart-title")
                
                print("🔄 Double-clicking on widget title...")
                actions.double_click(title_elem).perform()
                time.sleep(3)
                
                # Check if modal appeared
                modal_found = False
                for selector in ["ngb-modal-window", ".modal", "[role='dialog']"]:
                    if driver.find_elements(By.CSS_SELECTOR, selector):
                        modal_found = True
                        print(f"✅ Modal appeared from double-click: {selector}")
                        break
                
                if modal_found:
                    print("🎉 Double-click approach worked!")
                    # Close modal
                    from selenium.webdriver.common.keys import Keys
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(1)
                else:
                    print("⚠️ Double-click didn't open modal")
                    
        except Exception as double_click_error:
            print(f"❌ Double-click approach failed: {double_click_error}")
        
        print("\n📊 Test Summary:")
        print("   - If Expand button click worked: The fix is successful")
        print("   - If only double-click worked: We need to use alternative approach")
        print("   - If neither worked: More investigation needed")
        
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
    test_expand_button_click()
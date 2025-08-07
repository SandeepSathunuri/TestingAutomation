#!/usr/bin/env python3
"""
Test specifically for modal closing on landing page
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

def test_modal_closing():
    """Test specifically the modal closing functionality"""
    driver = None
    try:
        print("🚀 Testing modal closing on landing page...")
        
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
        
        # Test: Open menu, click Expand, and focus on closing
        print("\n🔍 Testing modal opening and closing cycle")
        
        if menu_handler.click_widget_menu(first_widget):
            print("✅ Menu opened successfully")
            
            # Click Expand
            if menu_handler.click_menu_item("Expand", "landing"):
                print("✅ Expand clicked successfully")
                
                # Wait for modal to appear
                time.sleep(2)
                
                # Check if modal appeared
                modal_selectors = ["ngb-modal-window", ".modal", "[role='dialog']"]
                modal_found = False
                modal_type = None
                
                for selector in modal_selectors:
                    if driver.find_elements(By.CSS_SELECTOR, selector):
                        modal_found = True
                        modal_type = selector
                        print(f"✅ Modal appeared: {selector}")
                        break
                
                if modal_found:
                    print(f"🔍 Testing modal closing for {modal_type}...")
                    
                    # Test the enhanced landing page modal closing
                    close_success = menu_handler._close_landing_page_modal()
                    
                    if close_success:
                        print("🎉 Modal closed successfully!")
                        
                        # Verify modal is actually closed
                        time.sleep(1)
                        still_open = any(driver.find_elements(By.CSS_SELECTOR, sel) for sel in modal_selectors)
                        
                        if not still_open:
                            print("✅ Confirmed: Modal is completely closed")
                        else:
                            print("⚠️ Warning: Modal might still be partially open")
                            
                    else:
                        print("❌ Modal closing failed")
                        
                        # Show what's still on screen
                        print("🔍 Debug: What's still visible:")
                        for selector in modal_selectors:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                print(f"   - {selector}: {len(elements)} elements")
                                for i, elem in enumerate(elements[:2]):
                                    try:
                                        visible = elem.is_displayed()
                                        size = elem.size
                                        print(f"     {i+1}. visible: {visible}, size: {size}")
                                    except:
                                        print(f"     {i+1}. (could not read element)")
                        
                        # Try manual ESC as final test
                        print("🔄 Trying manual ESC as final test...")
                        try:
                            from selenium.webdriver.common.keys import Keys
                            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                            time.sleep(2)
                            
                            final_check = any(driver.find_elements(By.CSS_SELECTOR, sel) for sel in modal_selectors)
                            if not final_check:
                                print("✅ Manual ESC worked!")
                            else:
                                print("❌ Even manual ESC didn't work")
                                
                        except Exception as manual_esc_error:
                            print(f"❌ Manual ESC failed: {manual_esc_error}")
                else:
                    print("❌ No modal appeared after Expand click")
            else:
                print("❌ Expand click failed")
        else:
            print("❌ Could not open menu")
        
        print("\n📊 Test Summary:")
        print("   - Modal opening: Check if ✅ Modal appeared")
        print("   - Modal closing: Check if 🎉 Modal closed successfully")
        print("   - If closing failed, check the debug output for clues")
        
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
    test_modal_closing()
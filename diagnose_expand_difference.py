#!/usr/bin/env python3
"""
Diagnostic script to compare expand behavior between landing page and drillthrough
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

def analyze_expand_modal(driver, page_type):
    """Analyze what happens when expand is clicked"""
    print(f"\n🔍 Analyzing expand behavior on {page_type} page...")
    
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
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    menu_handler = WidgetMenuHandler(driver, wait, actions)
    
    # Open menu
    if not menu_handler.click_widget_menu(first_widget):
        print("❌ Could not open menu")
        return
    
    print("✅ Menu opened, clicking Expand...")
    
    # Click expand and analyze what happens
    if not menu_handler.click_menu_item("Expand"):
        print("❌ Could not click Expand")
        return
    
    print("✅ Expand clicked, analyzing modal behavior...")
    
    # Wait and check for modal
    time.sleep(3)
    
    # Check different modal types
    modal_types = {
        "ngb-modal-window": "NgBootstrap Modal",
        ".modal": "Generic Modal",
        "[role='dialog']": "Dialog Role",
        ".modal-dialog": "Modal Dialog",
        ".modal-content": "Modal Content",
        "mat-dialog-container": "Material Dialog",
        ".cdk-overlay-pane": "CDK Overlay"
    }
    
    found_modals = []
    for selector, description in modal_types.items():
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            for elem in elements:
                if elem.is_displayed():
                    found_modals.append({
                        'type': description,
                        'selector': selector,
                        'element': elem
                    })
    
    print(f"📊 Found {len(found_modals)} modal elements:")
    for i, modal in enumerate(found_modals):
        print(f"   {i+1}. {modal['type']} ({modal['selector']})")
        
        # Analyze modal content
        try:
            modal_elem = modal['element']
            
            # Check for close buttons
            close_patterns = [
                ".close",
                "[aria-label='Close']",
                ".icon-close",
                ".demo-icon",
                "button[type='button']"
            ]
            
            close_buttons = []
            for pattern in close_patterns:
                buttons = modal_elem.find_elements(By.CSS_SELECTOR, pattern)
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        close_buttons.append({
                            'pattern': pattern,
                            'element': btn,
                            'classes': btn.get_attribute('class'),
                            'text': btn.text.strip()[:20]
                        })
            
            print(f"      📋 Close buttons found: {len(close_buttons)}")
            for j, btn in enumerate(close_buttons[:3]):  # Show first 3
                print(f"         {j+1}. Pattern: {btn['pattern']}, Classes: {btn['classes'][:50]}..., Text: '{btn['text']}'")
            
            # Check modal size and position
            size = modal_elem.size
            location = modal_elem.location
            print(f"      📐 Size: {size['width']}x{size['height']}, Position: ({location['x']}, {location['y']})")
            
        except Exception as modal_error:
            print(f"      ❌ Error analyzing modal: {modal_error}")
    
    # Try to close the modal using different strategies
    print(f"\n🔄 Testing modal closing strategies for {page_type}...")
    
    strategies = [
        ("ESC Key", lambda: driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)),
        ("Click Outside", lambda: driver.find_element(By.TAG_NAME, "body").click()),
        ("Close Button", lambda: _try_close_buttons(driver)),
        ("Backdrop Click", lambda: _try_backdrop_click(driver))
    ]
    
    from selenium.webdriver.common.keys import Keys
    
    for strategy_name, strategy_func in strategies:
        try:
            print(f"   🔄 Trying: {strategy_name}")
            strategy_func()
            time.sleep(1)
            
            # Check if modal is still open
            still_open = any(driver.find_elements(By.CSS_SELECTOR, selector) 
                           for selector in modal_types.keys())
            
            if not still_open:
                print(f"   ✅ {strategy_name} worked!")
                return strategy_name
            else:
                print(f"   ❌ {strategy_name} didn't close modal")
                
        except Exception as strategy_error:
            print(f"   ❌ {strategy_name} failed: {str(strategy_error)[:50]}...")
    
    print(f"⚠️ No closing strategy worked for {page_type}")
    return None

def _try_close_buttons(driver):
    """Try clicking close buttons"""
    close_selectors = [
        ".close",
        "[aria-label='Close']",
        ".icon-close",
        ".demo-icon",
        "button[type='button']"
    ]
    
    for selector in close_selectors:
        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
        for button in buttons:
            if button.is_displayed() and button.is_enabled():
                try:
                    driver.execute_script("arguments[0].click();", button)
                    return
                except:
                    continue

def _try_backdrop_click(driver):
    """Try clicking modal backdrop"""
    backdrop_selectors = [
        ".modal-backdrop",
        ".cdk-overlay-backdrop",
        "ngb-modal-backdrop"
    ]
    
    for selector in backdrop_selectors:
        backdrops = driver.find_elements(By.CSS_SELECTOR, selector)
        if backdrops:
            driver.execute_script("arguments[0].click();", backdrops[0])
            return

def perform_drillthrough(driver):
    """Perform drillthrough to compare expand behavior"""
    print("\n🔄 Performing drillthrough...")
    
    # Find first widget and perform drillthrough
    widgets = driver.find_elements(By.CSS_SELECTOR, ".chart-container")
    if not widgets:
        print("❌ No widgets found for drillthrough")
        return False
    
    first_widget = widgets[0]
    
    # Setup menu handler
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    menu_handler = WidgetMenuHandler(driver, wait, actions)
    
    # Open menu and click drillthrough
    if menu_handler.click_widget_menu(first_widget):
        if menu_handler.click_menu_item("Drill Through"):
            print("✅ Drillthrough initiated")
            time.sleep(5)  # Wait for drillthrough page to load
            return True
    
    print("❌ Drillthrough failed")
    return False

def main():
    """Main diagnostic function"""
    driver = None
    try:
        print("🚀 Starting expand behavior diagnosis...")
        
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
        
        # Wait for page to fully load
        time.sleep(3)
        
        # Analyze expand behavior on landing page
        landing_strategy = analyze_expand_modal(driver, "Landing")
        
        # Perform drillthrough
        if perform_drillthrough(driver):
            # Analyze expand behavior on drillthrough page
            drillthrough_strategy = analyze_expand_modal(driver, "Drillthrough")
            
            # Compare results
            print(f"\n📊 COMPARISON RESULTS:")
            print(f"   Landing Page: {landing_strategy or 'No working strategy'}")
            print(f"   Drillthrough: {drillthrough_strategy or 'No working strategy'}")
            
            if landing_strategy != drillthrough_strategy:
                print(f"🎯 DIFFERENCE FOUND!")
                print(f"   Landing page needs: {landing_strategy}")
                print(f"   Drillthrough needs: {drillthrough_strategy}")
            else:
                print(f"🤔 Both pages behave similarly")
        else:
            print("❌ Could not perform drillthrough for comparison")
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {str(e)}")
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
    main()
#!/usr/bin/env python3
"""
DOM Inspector to find correct widget menu selectors
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

def inspect_widget_structure(driver):
    """Inspect the actual DOM structure of widgets"""
    print("🔍 Inspecting widget DOM structure...")
    
    try:
        # Wait for widgets to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "chart-container")))
        
        # Find all widgets
        widgets = driver.find_elements(By.CSS_SELECTOR, ".chart-container")
        print(f"📊 Found {len(widgets)} widgets")
        
        if widgets:
            # Inspect the first widget in detail
            first_widget = widgets[0]
            print(f"\n🎯 Inspecting first widget:")
            
            # Get widget title
            try:
                title_elem = first_widget.find_element(By.CLASS_NAME, "chart-title")
                title = title_elem.text.strip()
                print(f"   📋 Title: {title}")
            except:
                print("   📋 Title: (not found)")
            
            # Get all child elements
            all_elements = first_widget.find_elements(By.CSS_SELECTOR, "*")
            print(f"   📊 Total child elements: {len(all_elements)}")
            
            # Look for potential menu buttons
            print(f"\n🔍 Looking for menu button elements:")
            
            potential_menu_elements = []
            
            # Search patterns for menu buttons
            search_patterns = [
                # Icon patterns
                "*[class*='icon']",
                "*[class*='more']", 
                "*[class*='vertical']",
                "*[class*='dots']",
                "*[class*='menu']",
                "*[class*='options']",
                "*[class*='kebab']",
                
                # Common button patterns
                "button",
                "span[role='button']",
                "*[role='button']",
                
                # Material Design patterns
                "*[class*='mat-']",
                "*[mattooltip]",
                
                # Generic clickable patterns
                "*[onclick]",
                "*[ng-click]",
                "*[@click]"
            ]
            
            for pattern in search_patterns:
                try:
                    elements = first_widget.find_elements(By.CSS_SELECTOR, pattern)
                    for elem in elements:
                        try:
                            # Check if element is visible and potentially clickable
                            if elem.is_displayed() and elem.is_enabled():
                                tag = elem.tag_name
                                classes = elem.get_attribute("class") or ""
                                elem_id = elem.get_attribute("id") or ""
                                role = elem.get_attribute("role") or ""
                                tooltip = elem.get_attribute("mattooltip") or elem.get_attribute("title") or ""
                                onclick = elem.get_attribute("onclick") or ""
                                text = elem.text.strip()[:20] if elem.text else ""
                                
                                # Check if this looks like a menu button
                                menu_indicators = ['more', 'vertical', 'dots', 'menu', 'options', 'kebab']
                                is_potential_menu = any(indicator in classes.lower() or 
                                                      indicator in elem_id.lower() or
                                                      indicator in tooltip.lower() or
                                                      indicator in onclick.lower()
                                                      for indicator in menu_indicators)
                                
                                if is_potential_menu or tag == 'button' or role == 'button':
                                    element_info = {
                                        'tag': tag,
                                        'classes': classes,
                                        'id': elem_id,
                                        'role': role,
                                        'tooltip': tooltip,
                                        'text': text,
                                        'onclick': onclick,
                                        'element': elem
                                    }
                                    potential_menu_elements.append(element_info)
                                    
                        except Exception as elem_error:
                            continue
                            
                except Exception as pattern_error:
                    continue
            
            # Remove duplicates and show results
            unique_elements = []
            seen_elements = set()
            
            for elem_info in potential_menu_elements:
                elem_key = (elem_info['tag'], elem_info['classes'], elem_info['id'])
                if elem_key not in seen_elements:
                    seen_elements.add(elem_key)
                    unique_elements.append(elem_info)
            
            print(f"   🎯 Found {len(unique_elements)} potential menu elements:")
            
            for i, elem_info in enumerate(unique_elements[:10]):  # Show first 10
                print(f"      {i+1}. <{elem_info['tag']}>")
                if elem_info['classes']:
                    print(f"         class='{elem_info['classes']}'")
                if elem_info['id']:
                    print(f"         id='{elem_info['id']}'")
                if elem_info['role']:
                    print(f"         role='{elem_info['role']}'")
                if elem_info['tooltip']:
                    print(f"         tooltip='{elem_info['tooltip']}'")
                if elem_info['text']:
                    print(f"         text='{elem_info['text']}'")
                print()
            
            # Test clicking on the most promising candidates
            print(f"🧪 Testing clicks on promising candidates:")
            
            for i, elem_info in enumerate(unique_elements[:5]):  # Test first 5
                try:
                    print(f"   🔄 Testing element {i+1}: <{elem_info['tag']}> class='{elem_info['classes'][:50]}...'")
                    
                    element = elem_info['element']
                    
                    # Try JavaScript click (safest)
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(1)
                    
                    # Check if menu appeared
                    menu_items = driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item, .dropdown-item, [role='menuitem']")
                    if menu_items:
                        print(f"      ✅ SUCCESS! Menu opened with {len(menu_items)} items")
                        print(f"      🎯 Working selector: {elem_info['tag']}")
                        if elem_info['classes']:
                            print(f"         CSS: {elem_info['tag']}.{elem_info['classes'].replace(' ', '.')}")
                        if elem_info['id']:
                            print(f"         ID: #{elem_info['id']}")
                        
                        # Show menu items
                        print(f"      📋 Menu items:")
                        for j, item in enumerate(menu_items[:5]):
                            try:
                                item_text = item.text.strip()
                                print(f"         {j+1}. '{item_text}'")
                            except:
                                print(f"         {j+1}. (unreadable)")
                        
                        # Close menu by clicking elsewhere
                        try:
                            driver.find_element(By.TAG_NAME, "body").click()
                            time.sleep(0.5)
                        except:
                            pass
                        
                        return elem_info  # Return the working element info
                    else:
                        print(f"      ❌ No menu appeared")
                        
                except Exception as test_error:
                    print(f"      ❌ Test failed: {str(test_error)[:50]}...")
                    continue
            
            print(f"❌ No working menu button found")
            return None
            
    except Exception as inspect_error:
        print(f"❌ DOM inspection failed: {inspect_error}")
        return None

def main():
    """Main inspection function"""
    driver = None
    try:
        print("🚀 Starting DOM inspection...")
        
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
        
        # Inspect widget structure
        working_element = inspect_widget_structure(driver)
        
        if working_element:
            print(f"\n🎉 SOLUTION FOUND!")
            print(f"   Tag: {working_element['tag']}")
            print(f"   Classes: {working_element['classes']}")
            print(f"   ID: {working_element['id']}")
            print(f"   Role: {working_element['role']}")
            print(f"   Tooltip: {working_element['tooltip']}")
            
            # Generate CSS selectors
            print(f"\n📝 Recommended CSS selectors:")
            if working_element['classes']:
                class_selector = f"{working_element['tag']}.{working_element['classes'].replace(' ', '.')}"
                print(f"   1. {class_selector}")
            if working_element['id']:
                id_selector = f"#{working_element['id']}"
                print(f"   2. {id_selector}")
            if working_element['role']:
                role_selector = f"{working_element['tag']}[role='{working_element['role']}']"
                print(f"   3. {role_selector}")
            if working_element['tooltip']:
                tooltip_selector = f"[mattooltip='{working_element['tooltip']}']"
                print(f"   4. {tooltip_selector}")
        else:
            print(f"\n❌ No working menu button found. Manual inspection needed.")
        
    except Exception as e:
        print(f"❌ Inspection failed: {str(e)}")
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
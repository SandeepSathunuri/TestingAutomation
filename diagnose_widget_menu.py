"""
Widget Menu Diagnostic Script
============================
Quick diagnostic to see what's happening with widget menus
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

def diagnose_widgets():
    """Diagnose widget menu issues"""
    print("🔍 Widget Menu Diagnostic Starting...")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        print("⚠️ Please navigate to your dashboard manually and press Enter...")
        input("Press Enter when you're on the dashboard with widgets visible...")
        
        # Find widgets
        print("\n🔍 Looking for widgets...")
        widget_selectors = [
            ".chart-parent",
            ".chart-container", 
            "[id='chart-container']",
            ".widget",
            ".dashboard-widget"
        ]
        
        widgets = []
        for selector in widget_selectors:
            try:
                found_widgets = driver.find_elements(By.CSS_SELECTOR, selector)
                if found_widgets:
                    print(f"✅ Found {len(found_widgets)} widgets with selector: {selector}")
                    widgets = found_widgets
                    break
            except:
                continue
        
        if not widgets:
            print("❌ No widgets found! Check if you're on the right page.")
            return
        
        # Analyze first widget
        widget = widgets[0]
        print(f"\n🧪 Analyzing first widget...")
        
        # Get widget title
        try:
            title_element = widget.find_element(By.CLASS_NAME, "chart-title")
            title = title_element.text.strip()
            print(f"📊 Widget title: {title}")
        except:
            print("📊 Widget title: (not found)")
        
        # Look for menu buttons
        print("\n🔍 Looking for menu buttons...")
        menu_selectors = [
            "span.icon-more-vertical.keepPopup",
            "span.icon-more-vertical",
            ".icon-more-vertical", 
            "[class*='more-vertical']",
            "[class*='menu']",
            "[mattooltip='More Details']",
            "button",
            ".btn"
        ]
        
        for i, selector in enumerate(menu_selectors):
            try:
                buttons = widget.find_elements(By.CSS_SELECTOR, selector)
                if buttons:
                    print(f"✅ Selector '{selector}' found {len(buttons)} elements:")
                    for j, btn in enumerate(buttons[:3]):  # Show first 3
                        try:
                            classes = btn.get_attribute("class") or "(no class)"
                            visible = btn.is_displayed()
                            enabled = btn.is_enabled()
                            text = btn.text.strip() or "(no text)"
                            print(f"   {j+1}. class='{classes}' visible={visible} enabled={enabled} text='{text}'")
                        except Exception as btn_error:
                            print(f"   {j+1}. (error reading button: {btn_error})")
            except:
                continue
        
        # Try to click the most likely menu button
        print("\n🔄 Attempting to click menu button...")
        menu_clicked = False
        
        for selector in ["span.icon-more-vertical", ".icon-more-vertical", "[class*='more-vertical']"]:
            try:
                menu_btn = widget.find_element(By.CSS_SELECTOR, selector)
                if menu_btn.is_displayed() and menu_btn.is_enabled():
                    print(f"🔄 Trying to click: {selector}")
                    
                    # Scroll into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu_btn)
                    time.sleep(0.5)
                    
                    # Try JavaScript click
                    driver.execute_script("arguments[0].click();", menu_btn)
                    time.sleep(1)
                    
                    # Check if menu appeared
                    menu_items = driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item")
                    if menu_items:
                        print(f"✅ Menu opened! Found {len(menu_items)} menu items:")
                        for k, item in enumerate(menu_items):
                            try:
                                item_text = item.text.strip()
                                print(f"   📋 {k+1}. '{item_text}'")
                            except:
                                print(f"   📋 {k+1}. (text not readable)")
                        menu_clicked = True
                        break
                    else:
                        print("⚠️ Click executed but no menu items appeared")
                        
            except Exception as click_error:
                print(f"❌ Failed to click {selector}: {click_error}")
                continue
        
        if not menu_clicked:
            print("❌ Could not open any menu")
        else:
            # Test clicking Download
            print("\n📥 Testing Download click...")
            try:
                download_btn = wait.until(lambda d: d.find_element(By.XPATH, "//button[contains(@class, 'mat-menu-item') and .//span[text()='Download']]"))
                download_btn.click()
                print("✅ Download clicked successfully!")
            except Exception as download_error:
                print(f"❌ Download click failed: {download_error}")
        
        print("\n🔍 Diagnostic completed!")
        
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    diagnose_widgets()
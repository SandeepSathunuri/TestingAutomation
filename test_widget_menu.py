"""
Widget Menu Test Script
======================
Test script to debug widget menu clicking issues
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from widget_components.widget_menu import WidgetMenuHandler
from widget_components.widget_loader import WidgetLoader

def test_widget_menu():
    """Test widget menu functionality"""
    print("🧪 Starting Widget Menu Test...")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    
    try:
        # You'll need to navigate to your dashboard first
        print("⚠️ Please manually navigate to your dashboard and press Enter...")
        input("Press Enter when you're on the dashboard page...")
        
        # Initialize handlers
        loader = WidgetLoader(driver)
        menu_handler = WidgetMenuHandler(driver, wait, actions)
        
        # Get widgets
        widgets = loader.get_widgets()
        print(f"📊 Found {len(widgets)} widgets")
        
        if not widgets:
            print("❌ No widgets found!")
            return
        
        # Test first widget
        widget = widgets[0]
        title = loader.get_widget_title(widget)
        print(f"🧪 Testing widget: {title}")
        
        # Test menu opening
        print("\n🔄 Testing menu opening...")
        if menu_handler.click_widget_menu(widget):
            print("✅ Menu opened successfully!")
            
            # Wait to see the menu
            time.sleep(2)
            
            # Test download
            print("\n📥 Testing Download...")
            if menu_handler.handle_download():
                print("✅ Download test passed!")
            else:
                print("❌ Download test failed!")
            
            # Wait between operations
            time.sleep(1)
            
            # Test expand
            print("\n🔍 Testing Expand...")
            if menu_handler.click_widget_menu(widget):
                if menu_handler.handle_expand():
                    print("✅ Expand test passed!")
                else:
                    print("❌ Expand test failed!")
            else:
                print("❌ Could not reopen menu for expand test!")
        else:
            print("❌ Menu opening failed!")
        
        print("\n🧪 Test completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    test_widget_menu()
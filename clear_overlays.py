#!/usr/bin/env python3
"""
Emergency overlay clearing script for when dashboard gets stuck
Run this when CDK overlays are blocking interactions
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def clear_all_overlays(driver):
    """Comprehensive overlay clearing function"""
    print("🧹 Clearing all overlays and backdrops...")
    
    try:
        # Step 1: Remove all CDK overlay elements
        overlay_selectors = [
            ".cdk-overlay-backdrop",
            ".cdk-overlay-backdrop-showing", 
            ".chart-title-header-more-icon-section",
            ".cdk-overlay-pane",
            "[id^='cdk-overlay-']",
            ".mat-menu-panel",
            ".mat-tooltip",
            ".ngb-modal-backdrop",
            ".modal-backdrop"
        ]
        
        removed_count = 0
        for selector in overlay_selectors:
            try:
                overlays = driver.find_elements(By.CSS_SELECTOR, selector)
                for overlay in overlays:
                    driver.execute_script("arguments[0].remove();", overlay)
                    removed_count += 1
            except Exception as e:
                continue
        
        print(f"✅ Removed {removed_count} overlay elements")
        
        # Step 2: Close any open menus/modals with Escape
        for _ in range(3):
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(0.2)
            except:
                pass
        
        # Step 3: Click outside any potential menu areas
        try:
            driver.execute_script("""
                document.body.click();
                document.documentElement.click();
            """)
        except:
            pass
        
        # Step 4: Reset any stuck states
        try:
            driver.execute_script("""
                // Remove any stuck hover states
                var elements = document.querySelectorAll(':hover');
                elements.forEach(el => {
                    el.blur();
                    el.style.pointerEvents = 'auto';
                });
                
                // Clear any active states
                var activeElements = document.querySelectorAll('.active-state, .cdk-focused, .cdk-mouse-focused');
                activeElements.forEach(el => {
                    el.classList.remove('active-state', 'cdk-focused', 'cdk-mouse-focused');
                });
            """)
        except:
            pass
        
        print("✅ Overlay clearing completed")
        time.sleep(0.5)
        
    except Exception as e:
        print(f"❌ Error during overlay clearing: {e}")

def emergency_reset(driver):
    """Emergency reset when dashboard is completely stuck"""
    print("🚨 Performing emergency reset...")
    
    try:
        # Clear overlays
        clear_all_overlays(driver)
        
        # Refresh the page if needed
        current_url = driver.current_url
        if "dashboard" in current_url.lower():
            print("🔄 Refreshing dashboard page...")
            driver.refresh()
            time.sleep(3)
            print("✅ Page refreshed")
        
    except Exception as e:
        print(f"❌ Emergency reset failed: {e}")

if __name__ == "__main__":
    print("This is a utility module. Import and use clear_all_overlays(driver) function.")
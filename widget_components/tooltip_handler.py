import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class TooltipHandler:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
        self.actions = ActionChains(driver)

    def get_tooltip(self, elem):
        """
        Get tooltip for Angular Material elements
        Works with elements that have mattooltip attribute or mat-tooltip-trigger class
        """
        try:
            # Method 1: Check for mattooltip attribute (direct tooltip content)
            mattooltip = elem.get_attribute("mattooltip")
            if mattooltip:
                return mattooltip.strip()
            
            # Method 2: Trigger tooltip by hovering and look for mat-tooltip element
            try:
                # Hover over the element to trigger tooltip
                self.actions.move_to_element(elem).perform()
                time.sleep(0.2)  # Reduced wait time for tooltip
                
                # Look for the tooltip element
                tooltip_selectors = [
                    ".mat-tooltip",
                    ".cdk-overlay-pane .mat-tooltip",
                    "[role='tooltip']",
                    ".custom-tooltip-opacity"
                ]
                
                for selector in tooltip_selectors:
                    try:
                        tooltip_elem = self.wait.until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if tooltip_elem and tooltip_elem.is_displayed():
                            tooltip_text = tooltip_elem.text.strip()
                            if tooltip_text:
                                return tooltip_text
                    except:
                        continue
                
            except Exception as hover_error:
                print(f"⚠️ Hover tooltip failed: {hover_error}")
            
            # Method 3: Check aria-describedby (fallback)
            try:
                tooltip_id = elem.get_attribute("aria-describedby")
                if tooltip_id:
                    tooltip_elem = self.driver.find_element(By.ID, tooltip_id)
                    if tooltip_elem:
                        tooltip_text = tooltip_elem.text.strip()
                        if tooltip_text:
                            return tooltip_text
            except:
                pass
            
            # Method 4: Check for title attribute
            title = elem.get_attribute("title")
            if title:
                return title.strip()
            
            # Method 5: Use element text as fallback
            element_text = elem.text.strip()
            if element_text:
                return f"Text: {element_text}"
            
            return "❌ No tooltip found"
            
        except Exception as e:
            return f"❌ Tooltip error: {str(e)}"
        finally:
            # Move mouse away to hide tooltip
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                self.actions.move_to_element(body).perform()
            except:
                pass

    def test_tooltip_methods(self, elem):
        """
        Test different tooltip detection methods for debugging
        """
        results = {}
        
        # Test mattooltip attribute
        results['mattooltip'] = elem.get_attribute("mattooltip")
        
        # Test aria-describedby
        results['aria-describedby'] = elem.get_attribute("aria-describedby")
        
        # Test title attribute
        results['title'] = elem.get_attribute("title")
        
        # Test element text
        results['element_text'] = elem.text.strip()
        
        # Test classes
        results['classes'] = elem.get_attribute("class")
        
        # Test hover tooltip
        try:
            self.actions.move_to_element(elem).perform()
            time.sleep(1)
            
            tooltip_elem = self.driver.find_element(By.CSS_SELECTOR, ".mat-tooltip")
            results['hover_tooltip'] = tooltip_elem.text.strip() if tooltip_elem.is_displayed() else "Not visible"
        except:
            results['hover_tooltip'] = "Not found"
        
        return results
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

class WidgetMenuHandler:
    def __init__(self, driver, wait, actions):
        self.driver = driver
        self.wait = wait
        self.actions = actions

    def clear_overlays(self):
        """Clear any overlays that might interfere with clicking"""
        try:
            overlay_selectors = [
                "[id^='cdk-overlay-']",
                ".cdk-overlay-pane",
                ".cdk-overlay-backdrop",
                ".mat-menu-panel"
            ]
            
            for selector in overlay_selectors:
                try:
                    overlays = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for overlay in overlays:
                        if overlay.is_displayed():
                            self.driver.execute_script("arguments[0].remove();", overlay)
                except:
                    continue
        except:
            pass

    def check_browser_health(self):
        """Check if browser session is still healthy"""
        try:
            # Simple check - try to get page title
            title = self.driver.title
            return True
        except Exception as health_error:
            print(f"⚠️ Browser health check failed: {str(health_error)[:50]}...")
            return False

    def recover_browser_session(self):
        """Attempt to recover from browser session issues"""
        print("🔄 Attempting browser session recovery...")
        try:
            # Try to refresh the page
            self.driver.refresh()
            time.sleep(3)
            
            # Wait for dashboard to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "chart-container")))
            print("✅ Browser session recovered")
            return True
            
        except Exception as recovery_error:
            print(f"❌ Browser session recovery failed: {recovery_error}")
            return False

    def _scroll_and_js_click(self, element):
        """Scroll element into view and click with JavaScript"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", element)

    def _action_chains_with_pause(self, element):
        """ActionChains click with pause"""
        self.actions.move_to_element(element).pause(0.5).click().perform()

    def _direct_click_with_scroll(self, element):
        """Direct click with scroll into view"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.3)
        element.click()

    def click_widget_menu(self, widget, retry_count=0):
        """Enhanced widget menu clicking with multiple strategies and retry logic"""
        print("🔄 Attempting to click widget menu...")
        
        # Debug: Show widget info
        try:
            widget_title = widget.find_element(By.CLASS_NAME, "chart-title").text.strip()
            print(f"🎯 Widget: {widget_title}")
        except:
            print("🎯 Widget: (title not found)")
        
        # Clear any existing overlays first
        self.clear_overlays()
        
        # Wait longer between operations if this is a retry
        if retry_count > 0:
            print(f"🔄 Retry attempt {retry_count}, waiting longer...")
            time.sleep(2 + retry_count)  # Progressive delay
        
        menu_selectors = [
            # Correct selector found by DOM inspection
            "span.mat-tooltip-trigger.demo-icon.icon-more-vertical.keepPopup",
            # Alternative selectors as fallbacks
            "[mattooltip='More Details']",
            "span.icon-more-vertical.keepPopup",
            ".mat-menu-trigger.toggleIcon.keepPopup",
            "span.demo-icon.icon-more-vertical",
            ".icon-more-vertical.keepPopup",
            "span.icon-more-vertical", 
            ".icon-more-vertical",
            "[class*='icon-more-vertical']"
        ]
        
        for i, selector in enumerate(menu_selectors):
            try:
                print(f"🔄 Trying menu selector {i+1}: {selector}")
                menu_button = widget.find_element(By.CSS_SELECTOR, selector)
                
                # Debug: Show button info
                print(f"   📍 Button found - visible: {menu_button.is_displayed()}, enabled: {menu_button.is_enabled()}")
                
                # Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu_button)
                time.sleep(0.2)
                
                # Try multiple click methods
                click_methods = [
                    ("Direct click", lambda: menu_button.click()),
                    ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", menu_button)),
                    ("ActionChains move+click", lambda: self.actions.move_to_element(menu_button).click().perform()),
                    ("ActionChains click", lambda: self.actions.click(menu_button).perform())
                ]
                
                for j, (method_name, click_method) in enumerate(click_methods):
                    try:
                        print(f"   🔄 Trying {method_name}")
                        click_method()
                        time.sleep(0.5)
                        
                        # Verify menu opened by checking for menu items
                        menu_items = self.driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item")
                        if menu_items:
                            print(f"✅ Widget menu opened! Found {len(menu_items)} menu items")
                            print(f"✅ Success with selector {i+1} ({selector}), method: {method_name}")
                            
                            # Debug: Show menu items
                            for k, item in enumerate(menu_items[:5]):  # Show first 5 items
                                try:
                                    item_text = item.text.strip()
                                    print(f"   📋 Menu item {k+1}: '{item_text}'")
                                except:
                                    print(f"   📋 Menu item {k+1}: (text not readable)")
                            
                            return True
                        else:
                            print(f"   ⚠️ Click executed but no menu items found")
                            
                    except Exception as click_error:
                        error_msg = str(click_error)
                        if "HTTPConnectionPool" in error_msg or "Connection" in error_msg:
                            print(f"   🚨 Connection error detected: {error_msg[:50]}...")
                            if not self.check_browser_health():
                                print("🔄 Browser unhealthy, attempting recovery...")
                                if self.recover_browser_session():
                                    # Retry this method after recovery
                                    return self.click_widget_menu(widget, retry_count + 1)
                                else:
                                    print("❌ Browser recovery failed")
                                    return False
                        else:
                            print(f"   ❌ {method_name} failed: {error_msg[:50]}...")
                        continue
                        
            except Exception as selector_error:
                print(f"❌ Selector {i+1} failed: {str(selector_error)[:50]}...")
                continue
        
        # Enhanced debug: Show what elements are actually available in the widget
        try:
            print("🔍 Debug: Available elements in widget:")
            all_elements = widget.find_elements(By.CSS_SELECTOR, "*")
            clickable_elements = [elem for elem in all_elements if elem.is_displayed() and elem.is_enabled()]
            print(f"   📊 Total elements: {len(all_elements)}, Clickable: {len(clickable_elements)}")
            
            # Look for any elements with menu-related keywords
            potential_menu_elements = []
            for elem in clickable_elements:
                try:
                    classes = elem.get_attribute("class") or ""
                    elem_id = elem.get_attribute("id") or ""
                    tooltip = elem.get_attribute("mattooltip") or elem.get_attribute("title") or ""
                    tag = elem.tag_name
                    
                    # Check for menu indicators
                    menu_keywords = ['more', 'menu', 'vertical', 'dots', 'options', 'kebab', 'toggle']
                    has_menu_indicator = any(keyword in classes.lower() or 
                                           keyword in elem_id.lower() or 
                                           keyword in tooltip.lower()
                                           for keyword in menu_keywords)
                    
                    if has_menu_indicator or tag == 'button':
                        potential_menu_elements.append({
                            'element': elem,
                            'tag': tag,
                            'classes': classes,
                            'id': elem_id,
                            'tooltip': tooltip
                        })
                except:
                    continue
            
            print(f"   🎯 Potential menu elements found: {len(potential_menu_elements)}")
            for i, elem_info in enumerate(potential_menu_elements[:5]):  # Show first 5
                try:
                    print(f"      {i+1}. <{elem_info['tag']}> class='{elem_info['classes'][:60]}...'")
                    if elem_info['tooltip']:
                        print(f"         tooltip='{elem_info['tooltip']}'")
                    
                    # Generate potential CSS selector
                    if elem_info['classes']:
                        css_selector = f"{elem_info['tag']}.{elem_info['classes'].replace(' ', '.')}"
                        print(f"         CSS: {css_selector[:80]}...")
                        
                except:
                    print(f"      {i+1}. (could not read element info)")
                    
        except Exception as debug_error:
            print(f"🔍 Debug failed: {debug_error}")
        
        # If this is the first attempt and we failed, try refreshing the widget element
        if retry_count == 0:
            print("🔄 First attempt failed, trying to refresh widget element...")
            try:
                # Try to find the widget again by its title
                widget_title = widget.find_element(By.CLASS_NAME, "chart-title").text.strip()
                widgets = self.driver.find_elements(By.CSS_SELECTOR, ".chart-container")
                for fresh_widget in widgets:
                    try:
                        fresh_title = fresh_widget.find_element(By.CLASS_NAME, "chart-title").text.strip()
                        if fresh_title == widget_title:
                            print(f"🔄 Found fresh widget element for: {widget_title}")
                            return self.click_widget_menu(fresh_widget, retry_count + 1)
                    except:
                        continue
            except Exception as refresh_error:
                print(f"❌ Widget refresh failed: {refresh_error}")
        
        print("❌ All widget menu click attempts failed")
        return False

    def click_menu_item(self, label, page_type="landing"):
        """Enhanced menu item clicking with page-specific handling"""
        print(f"🔄 Attempting to click menu item: {label} on {page_type} page")
        
        # Wait a moment for menu to fully appear
        time.sleep(0.5)
        
        # First, verify menu is still open
        menu_items = self.driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item")
        if not menu_items:
            print("⚠️ Menu not visible, trying to reopen...")
            return False
        
        print(f"📋 Menu has {len(menu_items)} items visible")
        
        # Debug: Show all available menu items
        print("📋 Available menu items:")
        for i, item in enumerate(menu_items):
            try:
                item_text = item.text.strip()
                item_classes = item.get_attribute("class") or ""
                item_enabled = item.is_enabled()
                item_displayed = item.is_displayed()
                print(f"   {i+1}. '{item_text}' - enabled: {item_enabled}, visible: {item_displayed}")
                print(f"      classes: {item_classes[:50]}...")
            except Exception as debug_error:
                print(f"   {i+1}. (could not read item: {debug_error})")
        
        # Try to find and click the specific menu item
        for attempt in range(3):  # Reduced attempts to prevent hanging
            try:
                print(f"🔄 Attempt {attempt + 1} to click '{label}'")
                
                # Refresh the menu items list to avoid stale elements
                menu_items = self.driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item")
                
                # Quick check: if no items are visible, don't waste time
                visible_items = [item for item in menu_items if item.is_displayed()]
                if not visible_items:
                    print(f"⚠️ No visible menu items found on attempt {attempt + 1}")
                    if attempt < 2:  # Not last attempt
                        time.sleep(0.5)
                        continue
                    else:
                        print("❌ All menu items are invisible - menu is broken")
                        return False
                
                # Look for the specific item by text with multiple matching strategies
                target_item = None
                matching_strategies = [
                    lambda text, target: target.lower() in text.lower(),  # Contains
                    lambda text, target: text.lower() == target.lower(),  # Exact match
                    lambda text, target: text.lower().startswith(target.lower()),  # Starts with
                    lambda text, target: target.lower().replace(" ", "") in text.lower().replace(" ", "")  # No spaces
                ]
                
                for strategy_name, strategy_func in [("contains", matching_strategies[0]), 
                                                   ("exact", matching_strategies[1]),
                                                   ("starts_with", matching_strategies[2]),
                                                   ("no_spaces", matching_strategies[3])]:
                    if target_item:
                        break
                        
                    for item in menu_items:
                        try:
                            item_text = item.text.strip()
                            if strategy_func(item_text, label):
                                target_item = item
                                print(f"✅ Found menu item: '{item_text}' using {strategy_name} strategy")
                                break
                        except:
                            continue
                
                if target_item:
                    # Special handling for Expand button on landing page
                    if label.lower() == "expand" and page_type == "landing":
                        print("🎯 Using special Expand button handling for landing page")
                        
                        # Landing page specific click approaches
                        click_approaches = [
                            ("Scroll and JavaScript click", lambda: self._scroll_and_js_click(target_item)),
                            ("Force JavaScript click", lambda: self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", target_item)),
                            ("ActionChains with pause", lambda: self._action_chains_with_pause(target_item)),
                            ("Direct click with scroll", lambda: self._direct_click_with_scroll(target_item)),
                            ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", target_item)),
                            ("Direct click", lambda: target_item.click()),
                            ("ActionChains click", lambda: self.actions.move_to_element(target_item).click().perform())
                        ]
                    else:
                        # Standard click approaches for other items
                        click_approaches = [
                            ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", target_item)),
                            ("Direct click", lambda: target_item.click()),
                            ("ActionChains click", lambda: self.actions.move_to_element(target_item).click().perform())
                        ]
                    
                    for approach_name, click_func in click_approaches:
                        try:
                            print(f"   🔄 Trying {approach_name}")
                            
                            # Ensure element is still valid - quick timeout prevention
                            try:
                                is_displayed = target_item.is_displayed()
                                is_enabled = target_item.is_enabled()
                                
                                if not is_displayed or not is_enabled:
                                    print(f"   ⚠️ Element not clickable: displayed={is_displayed}, enabled={is_enabled}")
                                    continue
                                    
                            except Exception as element_check_error:
                                print(f"   ❌ Element check failed: {str(element_check_error)[:30]}...")
                                continue
                            
                            click_func()
                            print(f"✅ Menu item '{label}' clicked with {approach_name}")
                            time.sleep(0.5)
                            return True
                        except ElementClickInterceptedException:
                            print(f"   ⚠️ {approach_name} intercepted, clearing overlays...")
                            self.clear_overlays()
                            time.sleep(0.3)
                            continue
                        except Exception as click_error:
                            print(f"   ❌ {approach_name} failed: {str(click_error)[:50]}...")
                            continue
                else:
                    print(f"❌ Menu item '{label}' not found in visible items")
                    # Show what items are available
                    available_items = []
                    for item in menu_items:
                        try:
                            available_items.append(item.text.strip())
                        except:
                            available_items.append("(unreadable)")
                    print(f"📋 Available items: {available_items}")
                
                # Wait before next attempt
                if attempt < 2:
                    time.sleep(0.5)
                    
            except Exception as attempt_error:
                print(f"❌ Attempt {attempt + 1} failed: {str(attempt_error)[:50]}...")
                if attempt < 2:
                    time.sleep(0.5)
                continue
        
        print(f"❌ All attempts to click '{label}' failed")
        return False

    def handle_expand(self, page_type="landing"):
        """Handle expand with page-specific logic"""
        print(f"🔄 Starting Expand operation for {page_type} page...")
        
        # Check if menu is still open
        menu_items = self.driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item")
        if not menu_items:
            print("⚠️ Menu closed, cannot proceed with expand")
            return False
        
        if not self.click_menu_item("Expand", page_type):
            print("❌ Failed to click Expand menu item")
            return False
        
        try:
            print("🔄 Waiting for expand modal to open...")
            
            # Different wait times for different pages
            if page_type == "landing":
                time.sleep(3)  # Landing page might need more time
            else:
                time.sleep(2)  # Drillthrough page
            
            # Check if modal opened with page-specific selectors
            modal_selectors = [
                "ngb-modal-window",
                ".modal",
                "[role='dialog']",
                ".modal-dialog",
                "mat-dialog-container",
                ".cdk-overlay-pane"
            ]
            
            modal_found = False
            modal_selector_used = None
            for selector in modal_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        modal_found = True
                        modal_selector_used = selector
                        print(f"✅ Modal found with selector: {selector}")
                        break
                if modal_found:
                    break
            
            if not modal_found:
                print("⚠️ No modal detected, trying alternative expand approach...")
                return self._try_alternative_expand(page_type)
            
            # Page-specific modal closing
            return self._close_modal_by_page_type(page_type, modal_selector_used)
            
        except Exception as expand_error:
            print(f"❌ Expand operation failed: {expand_error}")
            return self._try_alternative_expand(page_type)

    def _try_alternative_expand(self, page_type):
        """Try alternative expand approaches when modal doesn't appear"""
        print(f"🔄 Trying alternative expand for {page_type} page...")
        
        try:
            # Alternative 1: Look for any new content that appeared
            time.sleep(1)
            
            # Check if any overlay or new content appeared
            overlay_selectors = [
                ".cdk-overlay-container",
                ".mat-overlay-pane",
                "[class*='overlay']",
                "[class*='popup']",
                "[class*='expanded']"
            ]
            
            for selector in overlay_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        print(f"✅ Found alternative content: {selector}")
                        # Try to close it
                        try:
                            from selenium.webdriver.common.keys import Keys
                            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                            time.sleep(1)
                            print("✅ Alternative expand completed with ESC")
                            return True
                        except:
                            pass
            
            # Alternative 2: Check if the widget itself expanded in place
            widgets = self.driver.find_elements(By.CSS_SELECTOR, ".chart-container")
            for widget in widgets:
                try:
                    # Check if widget has expanded classes or larger size
                    classes = widget.get_attribute("class") or ""
                    if any(keyword in classes.lower() for keyword in ['expanded', 'fullscreen', 'maximized']):
                        print("✅ Widget expanded in place")
                        # Click elsewhere to collapse
                        self.driver.find_element(By.TAG_NAME, "body").click()
                        time.sleep(1)
                        return True
                except:
                    continue
            
            # Alternative 3: For landing page, try double-click approach
            if page_type == "landing":
                print("🔄 Trying double-click approach for landing page...")
                try:
                    # Find the widget again and double-click its title
                    widgets = self.driver.find_elements(By.CSS_SELECTOR, ".chart-container")
                    if widgets:
                        first_widget = widgets[0]
                        title_elem = first_widget.find_element(By.CLASS_NAME, "chart-title")
                        
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        actions.double_click(title_elem).perform()
                        time.sleep(2)
                        
                        # Check if modal appeared after double-click
                        modal_appeared = any(self.driver.find_elements(By.CSS_SELECTOR, sel) 
                                           for sel in ["ngb-modal-window", ".modal", "[role='dialog']"])
                        
                        if modal_appeared:
                            print("✅ Double-click opened modal")
                            return self._close_modal_comprehensive()
                        else:
                            print("✅ Double-click expand completed (no modal)")
                            return True
                            
                except Exception as double_click_error:
                    print(f"❌ Double-click approach failed: {double_click_error}")
            
            print("⚠️ No alternative expand method worked")
            return False
            
        except Exception as alt_error:
            print(f"❌ Alternative expand failed: {alt_error}")
            return False

    def _close_modal_by_page_type(self, page_type, modal_selector):
        """Close modal with page-specific strategies"""
        print(f"🔄 Closing modal for {page_type} page using {modal_selector}...")
        
        if page_type == "landing":
            # Landing page specific closing strategies
            return self._close_landing_page_modal()
        else:
            # Drillthrough page specific closing strategies
            return self._close_drillthrough_modal()

    def _close_landing_page_modal(self):
        """Landing page specific modal closing with enhanced strategies"""
        print("🔄 Using enhanced landing page modal closing strategy...")
        
        # First, let's identify what type of modal we're dealing with
        modal_info = self._analyze_modal_structure()
        print(f"📊 Modal analysis: {modal_info}")
        
        # Strategy 1: Try specific close button patterns for landing page
        landing_close_selectors = [
            # NgBootstrap specific patterns
            "ngb-modal-window .close",
            "ngb-modal-window .btn-close",
            "ngb-modal-window [aria-label='Close']",
            "ngb-modal-window .modal-header .close",
            
            # Icon-based close buttons
            "ngb-modal-window .icon-close",
            "ngb-modal-window .demo-icon",
            "ngb-modal-window .fa-times",
            "ngb-modal-window .fa-close",
            
            # Generic close patterns within modal
            ".modal .close",
            ".modal .btn-close",
            ".modal [aria-label='Close']",
            
            # Any button that looks like a close button
            "ngb-modal-window button[type='button']",
            ".modal button[type='button']"
        ]
        
        for i, selector in enumerate(landing_close_selectors):
            try:
                print(f"🔄 Trying landing close selector {i+1}: {selector}")
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for j, close_button in enumerate(close_buttons):
                    try:
                        if close_button.is_displayed() and close_button.is_enabled():
                            print(f"   🔄 Found close button {j+1}: {close_button.get_attribute('class')}")
                            
                            # Enhanced click methods for landing page
                            click_methods = [
                                ("Scroll and JavaScript click", lambda: self._scroll_and_js_click(close_button)),
                                ("Force JavaScript click", lambda: self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", close_button)),
                                ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", close_button)),
                                ("Direct click", lambda: close_button.click()),
                                ("ActionChains click", lambda: self.actions.move_to_element(close_button).click().perform())
                            ]
                            
                            for method_name, click_func in click_methods:
                                try:
                                    print(f"      🔄 Trying {method_name}")
                                    click_func()
                                    time.sleep(1.5)  # Longer wait for landing page
                                    
                                    if not self._is_modal_open():
                                        print(f"✅ Landing page modal closed with {method_name}")
                                        return True
                                    else:
                                        print(f"      ⚠️ {method_name} executed but modal still open")
                                        
                                except Exception as click_error:
                                    print(f"      ❌ {method_name} failed: {str(click_error)[:50]}...")
                                    continue
                    except Exception as button_error:
                        print(f"   ❌ Button {j+1} error: {str(button_error)[:50]}...")
                        continue
                        
            except Exception as selector_error:
                print(f"❌ Selector {i+1} failed: {str(selector_error)[:50]}...")
                continue
        
        # Strategy 2: Try ESC key multiple times with different focuses
        print("🔄 Trying enhanced ESC key strategy...")
        try:
            from selenium.webdriver.common.keys import Keys
            
            # Try ESC on different elements
            esc_targets = [
                ("Modal window", "ngb-modal-window"),
                ("Modal body", ".modal-body"),
                ("Document body", "body"),
                ("Active element", None)  # Will use driver.switch_to.active_element
            ]
            
            for target_name, target_selector in esc_targets:
                try:
                    print(f"   🔄 Trying ESC on {target_name}")
                    
                    if target_selector:
                        target = self.driver.find_element(By.CSS_SELECTOR, target_selector)
                    else:
                        target = self.driver.switch_to.active_element
                    
                    target.send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    
                    if not self._is_modal_open():
                        print(f"✅ Landing page modal closed with ESC on {target_name}")
                        return True
                        
                except Exception as esc_error:
                    print(f"   ❌ ESC on {target_name} failed: {str(esc_error)[:30]}...")
                    continue
                    
        except Exception as esc_strategy_error:
            print(f"❌ ESC strategy failed: {esc_strategy_error}")
        
        # Strategy 3: Try clicking outside modal with precise coordinates
        print("🔄 Trying enhanced outside click strategy...")
        try:
            # Get modal dimensions to click outside it
            modal_elements = self.driver.find_elements(By.CSS_SELECTOR, "ngb-modal-window, .modal")
            if modal_elements:
                modal = modal_elements[0]
                modal_rect = modal.rect
                
                # Calculate click coordinates outside the modal
                viewport_width = self.driver.execute_script("return window.innerWidth")
                viewport_height = self.driver.execute_script("return window.innerHeight")
                
                # Try clicking in different areas outside the modal
                outside_coordinates = [
                    (50, 50),  # Top-left corner
                    (viewport_width - 50, 50),  # Top-right corner
                    (50, viewport_height - 50),  # Bottom-left corner
                    (viewport_width - 50, viewport_height - 50),  # Bottom-right corner
                    (viewport_width // 2, 50),  # Top center
                ]
                
                for x, y in outside_coordinates:
                    try:
                        print(f"   🔄 Clicking outside modal at ({x}, {y})")
                        self.actions.move_by_offset(x, y).click().perform()
                        self.actions.reset_actions()  # Reset action chain
                        time.sleep(1)
                        
                        if not self._is_modal_open():
                            print(f"✅ Landing page modal closed by clicking outside at ({x}, {y})")
                            return True
                            
                    except Exception as coord_error:
                        print(f"   ❌ Click at ({x}, {y}) failed: {str(coord_error)[:30]}...")
                        continue
                        
        except Exception as outside_click_error:
            print(f"❌ Outside click strategy failed: {outside_click_error}")
        
        # Strategy 4: Try backdrop click
        print("🔄 Trying backdrop click strategy...")
        try:
            backdrop_selectors = [
                ".modal-backdrop",
                ".cdk-overlay-backdrop", 
                "ngb-modal-backdrop",
                ".fade.show"
            ]
            
            for backdrop_selector in backdrop_selectors:
                backdrops = self.driver.find_elements(By.CSS_SELECTOR, backdrop_selector)
                if backdrops:
                    for backdrop in backdrops:
                        try:
                            print(f"   🔄 Clicking backdrop: {backdrop_selector}")
                            self.driver.execute_script("arguments[0].click();", backdrop)
                            time.sleep(1)
                            
                            if not self._is_modal_open():
                                print(f"✅ Landing page modal closed with backdrop click")
                                return True
                                
                        except Exception as backdrop_click_error:
                            print(f"   ❌ Backdrop click failed: {str(backdrop_click_error)[:30]}...")
                            continue
                            
        except Exception as backdrop_strategy_error:
            print(f"❌ Backdrop strategy failed: {backdrop_strategy_error}")
        
        # Strategy 5: Force close by removing modal elements (last resort)
        print("🔄 Trying force removal strategy...")
        try:
            modal_selectors_to_remove = [
                "ngb-modal-window",
                ".modal",
                "[role='dialog']",
                ".modal-backdrop",
                ".cdk-overlay-backdrop"
            ]
            
            for selector in modal_selectors_to_remove:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        self.driver.execute_script("arguments[0].remove();", element)
                    except:
                        continue
            
            time.sleep(0.5)
            if not self._is_modal_open():
                print("✅ Landing page modal closed by force removal")
                return True
                
        except Exception as remove_error:
            print(f"❌ Force removal failed: {remove_error}")
        
        print("❌ All landing page modal closing strategies failed")
        return False

    def _analyze_modal_structure(self):
        """Analyze the modal structure to understand what we're dealing with"""
        try:
            modal_info = {
                'type': 'unknown',
                'close_buttons': 0,
                'has_backdrop': False,
                'size': 'unknown'
            }
            
            # Check modal type
            if self.driver.find_elements(By.CSS_SELECTOR, "ngb-modal-window"):
                modal_info['type'] = 'ngb-modal'
            elif self.driver.find_elements(By.CSS_SELECTOR, ".modal"):
                modal_info['type'] = 'bootstrap-modal'
            elif self.driver.find_elements(By.CSS_SELECTOR, "[role='dialog']"):
                modal_info['type'] = 'dialog'
            
            # Count close buttons
            close_selectors = [".close", ".btn-close", "[aria-label='Close']", ".icon-close"]
            for selector in close_selectors:
                modal_info['close_buttons'] += len(self.driver.find_elements(By.CSS_SELECTOR, selector))
            
            # Check for backdrop
            backdrop_selectors = [".modal-backdrop", ".cdk-overlay-backdrop", "ngb-modal-backdrop"]
            modal_info['has_backdrop'] = any(self.driver.find_elements(By.CSS_SELECTOR, sel) for sel in backdrop_selectors)
            
            return modal_info
            
        except Exception as analyze_error:
            return {'error': str(analyze_error)}

    def _close_drillthrough_modal(self):
        """Drillthrough page specific modal closing"""
        print("🔄 Using drillthrough page modal closing strategy...")
        
        # Drillthrough pages seem to work better with the comprehensive approach
        return self._close_modal_comprehensive()
    
    def _close_modal_comprehensive(self):
        """Comprehensive modal closing with multiple strategies"""
        print("🔄 Starting comprehensive modal closing...")
        
        # Strategy 1: Try common close button selectors
        close_selectors = [
            # NgBootstrap modal close buttons
            "//ngb-modal-window//span[contains(@class, 'close')]",
            "//ngb-modal-window//span[contains(@class, 'icon-close')]",
            "//ngb-modal-window//button[contains(@class, 'close')]",
            "//ngb-modal-window//span[contains(@class, 'demo-icon')]",
            "//ngb-modal-window//*[contains(@class, 'close')]",
            
            # Generic modal close buttons
            "//div[contains(@class, 'modal')]//span[contains(@class, 'close')]",
            "//div[contains(@class, 'modal')]//button[contains(@class, 'close')]",
            "//div[contains(@class, 'modal')]//button[@aria-label='Close']",
            "//div[contains(@class, 'modal')]//*[contains(@class, 'close')]",
            
            # Dialog close buttons
            "//*[@role='dialog']//span[contains(@class, 'close')]",
            "//*[@role='dialog']//button[contains(@class, 'close')]",
            "//*[@role='dialog']//*[contains(@class, 'close')]",
            
            # Generic close patterns
            "//*[contains(@class, 'close') and (self::span or self::button or self::i)]",
            "//*[contains(@class, 'icon-close')]",
            "//*[contains(@class, 'modal-close')]",
            "//*[@title='Close' or @aria-label='Close']",
            
            # X button patterns
            "//*[text()='×' or text()='✕' or text()='X']",
            "//*[contains(@class, 'fa-times') or contains(@class, 'fa-close')]"
        ]
        
        for i, selector in enumerate(close_selectors):
            try:
                print(f"🔄 Trying close selector {i+1}: {selector}")
                close_buttons = self.driver.find_elements(By.XPATH, selector)
                
                if close_buttons:
                    for j, close_button in enumerate(close_buttons):
                        try:
                            if close_button.is_displayed() and close_button.is_enabled():
                                print(f"   🔄 Clicking close button {j+1}")
                                
                                # Try multiple click methods
                                click_methods = [
                                    ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", close_button)),
                                    ("Direct click", lambda: close_button.click()),
                                    ("ActionChains click", lambda: self.actions.move_to_element(close_button).click().perform())
                                ]
                                
                                for method_name, click_func in click_methods:
                                    try:
                                        click_func()
                                        time.sleep(1)
                                        
                                        # Verify modal is closed
                                        if not self._is_modal_open():
                                            print(f"✅ Modal closed with selector {i+1}, button {j+1}, method: {method_name}")
                                            return True
                                        else:
                                            print(f"   ⚠️ {method_name} executed but modal still open")
                                            
                                    except Exception as click_error:
                                        print(f"   ❌ {method_name} failed: {str(click_error)[:50]}...")
                                        continue
                        except Exception as button_error:
                            print(f"   ❌ Button {j+1} error: {str(button_error)[:50]}...")
                            continue
                else:
                    print(f"   ❌ No elements found for selector {i+1}")
                    
            except Exception as selector_error:
                print(f"❌ Selector {i+1} failed: {str(selector_error)[:50]}...")
                continue
        
        # Strategy 2: Try clicking outside the modal (backdrop click)
        print("🔄 Trying backdrop click...")
        try:
            backdrop_selectors = [
                ".modal-backdrop",
                ".cdk-overlay-backdrop",
                "ngb-modal-backdrop"
            ]
            
            for backdrop_selector in backdrop_selectors:
                backdrops = self.driver.find_elements(By.CSS_SELECTOR, backdrop_selector)
                if backdrops:
                    backdrop = backdrops[0]
                    self.driver.execute_script("arguments[0].click();", backdrop)
                    time.sleep(1)
                    if not self._is_modal_open():
                        print("✅ Modal closed with backdrop click")
                        return True
                        
        except Exception as backdrop_error:
            print(f"❌ Backdrop click failed: {backdrop_error}")
        
        # Strategy 3: Try ESC key multiple times
        print("🔄 Trying ESC key (multiple attempts)...")
        try:
            from selenium.webdriver.common.keys import Keys
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            for attempt in range(3):
                body.send_keys(Keys.ESCAPE)
                time.sleep(0.5)
                if not self._is_modal_open():
                    print(f"✅ Modal closed with ESC key (attempt {attempt + 1})")
                    return True
                    
        except Exception as esc_error:
            print(f"❌ ESC key failed: {esc_error}")
        
        # Strategy 4: Try clicking on the main content area
        print("🔄 Trying to click main content area...")
        try:
            main_selectors = [
                ".main-content",
                ".dashboard",
                ".chart-container",
                "#main",
                "body"
            ]
            
            for main_selector in main_selectors:
                main_elements = self.driver.find_elements(By.CSS_SELECTOR, main_selector)
                if main_elements:
                    main_element = main_elements[0]
                    self.driver.execute_script("arguments[0].click();", main_element)
                    time.sleep(1)
                    if not self._is_modal_open():
                        print(f"✅ Modal closed by clicking {main_selector}")
                        return True
                        
        except Exception as main_click_error:
            print(f"❌ Main content click failed: {main_click_error}")
        
        # Strategy 5: Force close by removing modal elements
        print("🔄 Trying to force remove modal elements...")
        try:
            modal_selectors_to_remove = [
                "ngb-modal-window",
                ".modal",
                "[role='dialog']",
                ".modal-backdrop",
                ".cdk-overlay-backdrop"
            ]
            
            for selector in modal_selectors_to_remove:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    self.driver.execute_script("arguments[0].remove();", element)
            
            time.sleep(0.5)
            if not self._is_modal_open():
                print("✅ Modal closed by force removal")
                return True
                
        except Exception as remove_error:
            print(f"❌ Force removal failed: {remove_error}")
        
        # Final debug: Show what modal elements are present
        print("🔍 Final debug - showing modal elements present:")
        self._debug_modal_elements()
        
        print("❌ All modal closing strategies failed")
        print("⚠️ Continuing anyway - modal may close automatically later")
        return False
    
    def _debug_modal_elements(self):
        """Debug what modal elements are present"""
        try:
            # Check for any modal-related elements
            debug_selectors = [
                "ngb-modal-window",
                ".modal",
                "[role='dialog']",
                "*[class*='modal']",
                "*[class*='close']",
                "*[id*='modal']"
            ]
            
            for selector in debug_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   📋 Found {len(elements)} elements for '{selector}':")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        try:
                            tag = elem.tag_name
                            classes = elem.get_attribute("class") or "(no class)"
                            visible = elem.is_displayed()
                            enabled = elem.is_enabled()
                            text = elem.text.strip()[:30] if elem.text else "(no text)"
                            print(f"      {i+1}. <{tag}> class='{classes}' visible={visible} enabled={enabled} text='{text}'")
                        except Exception as elem_error:
                            print(f"      {i+1}. (error reading element: {elem_error})")
                            
        except Exception as debug_error:
            print(f"❌ Debug failed: {debug_error}")
    
    def _is_modal_open(self):
        """Check if any modal is currently open"""
        modal_selectors = [
            "ngb-modal-window",
            ".modal",
            "[role='dialog']"
        ]
        
        for selector in modal_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    return True
        return False

    def handle_both_operations(self, page_type="landing"):
        """Handle both Download and Expand in a single menu session with page-specific order"""
        print(f"🔄 Starting both Download and Expand operations for {page_type} page...")
        
        # Check if menu is open
        menu_items = self.driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item")
        if not menu_items:
            print("⚠️ Menu not open, cannot proceed")
            return False, False
        
        download_success = False
        expand_success = False
        
        # Different order based on page type
        if page_type == "landing":
            print("🎯 Landing page: Expand first, then Download (separate sessions)")
            
            # Step 1: Handle Expand first
            print("🔄 Step 1: Handling Expand...")
            if self.click_menu_item("Expand", page_type):
                print("✅ Expand menu item clicked successfully")
                expand_success = True
                time.sleep(2)  # Wait for modal to open
                
                # Close the expand modal
                if self._close_landing_page_modal():
                    print("✅ Landing page expand modal closed successfully")
                else:
                    print("⚠️ Landing page expand modal closing had issues")
            else:
                print("❌ Failed to click Expand menu item")
            
            # Step 2: Skip download in same session (menu is broken after modal)
            print("🔄 Step 2: Skipping download in same session (menu broken after modal)")
            print("⚠️ Download will be handled in separate menu session")
            # Don't attempt download here - always use separate session for landing page
        
        else:
            print("🎯 Drillthrough page: Download first, then Expand (original order)")
            
            # Step 1: Handle Download
            print("🔄 Step 1: Handling Download...")
            if self.click_menu_item("Download", page_type):
                print("✅ Download initiated successfully")
                download_success = True
                time.sleep(1)  # Wait for download to start
            else:
                print("❌ Failed to click Download menu item")
            
            # Step 2: Handle Expand (menu should still be open on drillthrough)
            print("🔄 Step 2: Handling Expand...")
            menu_items = self.driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item")
            if menu_items:
                if self.click_menu_item("Expand", page_type):
                    print("✅ Expand menu item clicked successfully")
                    expand_success = True
                    time.sleep(2)  # Wait for modal to open
                    
                    # Close the expand modal
                    if self._close_drillthrough_modal():
                        print("✅ Drillthrough expand modal closed successfully")
                    else:
                        print("⚠️ Drillthrough expand modal closing had issues")
                else:
                    print("❌ Failed to click Expand menu item")
            else:
                print("⚠️ Menu closed after download, trying alternative expand...")
                expand_success = self._try_alternative_expand(page_type)
        
        return download_success, expand_success

    def handle_download(self):
        """Handle download with enhanced error handling"""
        print("🔄 Starting Download operation...")
        
        # Check if menu is still open
        menu_items = self.driver.find_elements(By.CSS_SELECTOR, ".mat-menu-item")
        if not menu_items:
            print("⚠️ Menu closed, cannot proceed with download")
            return False
        
        if self.click_menu_item("Download", "landing"):  # Default to landing for backward compatibility
            print("✅ Download initiated successfully")
            time.sleep(1)  # Wait for download to start
            return True
        else:
            print("❌ Failed to click Download menu item")
            return False
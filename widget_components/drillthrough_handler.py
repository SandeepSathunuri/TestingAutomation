import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from kpisdataextraction import KPidataextract
from excel_merger import ExcelMerger
from kpistoreprocedures import Data, compare_kpi_data, read_kpi_from_excel

extra_params = {"Store": "717"}

# Mapping for drillthrough submenus
DRILLTHROUGH_MAP = {
    "Top Stores by Sales": "Love Library",
    "Top Brands by Sales": "Routledge Publications",
    "Top Categories by Sales": "E-Books",
    "Top Sub Categories by Sales": "Non-Fiction",
    "Top Products by Sales": "MATLAB",
    "Weekly Trends": "Week1"
}

class DrillthroughHandler:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)  # Reduced from 20 to 15
        self.actions = ActionChains(driver)
        
        # Optimize driver settings to prevent timeouts
        try:
            driver.set_page_load_timeout(60)  # 1 minute page load timeout
            driver.set_script_timeout(30)    # 30 second script timeout
            driver.implicitly_wait(5)        # 5 second implicit wait
            print("✅ Selenium timeouts optimized")
        except Exception as e:
            print(f"⚠️ Could not optimize timeouts: {e}")

    def check_browser_health(self):
        """Check if browser is still responsive"""
        try:
            self.driver.current_url
            ready_state = self.driver.execute_script("return document.readyState")
            return ready_state == "complete"
        except:
            return False

    def get_fresh_widget(self, title, retries=3):
        for attempt in range(retries):
            try:
                widgets = self.driver.find_elements(By.ID, "chart-container")
                for widget in widgets:
                    try:
                        widget_title = widget.find_element(By.CLASS_NAME, "chart-title").text.strip()
                        if widget_title == title:
                            return widget
                    except:
                        continue
                time.sleep(2)  # wait before next retry
            except Exception as e:
                print(f"❌ Attempt {attempt+1} failed to locate widget: {e}")
        print(f"❌ Widget not found after retries: {title}")
        return None

    def open_drillthrough_menu(self, widget_title):
        widget = self.get_fresh_widget(widget_title)
        if not widget:
            print(f"❌ Widget not found: {widget_title}")
            return False

        try:
            print(f"🔄 Opening drillthrough menu for: {widget_title}")
            
            # Step 1: Open widget menu - try multiple selectors
            menu_selectors = [
                "span.icon-more-vertical.keepPopup",
                "span.icon-more-vertical",
                "[class*='icon-more-vertical']",
                "[mattooltip='More Details']"
            ]
            
            menu_btn = None
            for selector in menu_selectors:
                try:
                    menu_btn = widget.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found menu button with selector: {selector}")
                    break
                except:
                    continue
            
            if not menu_btn:
                print(f"❌ Could not find menu button for widget: {widget_title}")
                return False
            
            # Clear overlays before clicking
            self._clear_drillthrough_overlays()
            
            # Click menu button with JavaScript
            self.driver.execute_script("arguments[0].scrollIntoView(true);", menu_btn)
            time.sleep(0.2)
            self.driver.execute_script("arguments[0].click();", menu_btn)
            print("✅ Widget menu opened")
            time.sleep(1)

            # Step 2: Click Drill Through - try multiple approaches
            drill_xpaths = [
                "//button[contains(@class, 'mat-menu-trigger') and contains(@class, 'mat-menu-item-submenu-trigger') and .//span[text()='Drill Through']]",
                "//button[contains(@class, 'mat-menu-item') and .//span[text()='Drill Through']]",
                "//mat-menu//button[.//span[text()='Drill Through']]"
            ]
            
            drill_menu = None
            for xpath in drill_xpaths:
                try:
                    drill_menu = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    print(f"✅ Found Drill Through button with xpath")
                    break
                except:
                    continue
            
            if not drill_menu:
                print(f"❌ Could not find Drill Through button")
                return False
            
            self.driver.execute_script("arguments[0].click();", drill_menu)
            print("✅ Drill Through menu opened")
            
            # Wait longer and check if submenu appears
            print("⏳ Waiting for submenu to appear...")
            time.sleep(2)
            
            # Debug: Take a screenshot to see what's happening
            try:
                screenshot_path = f"debug_drillthrough_{widget_title.replace(' ', '_')}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")
            except:
                pass
            
            # Debug: Check page structure after Drill Through click
            print("🔍 Checking page structure after Drill Through click...")
            try:
                # Look for any new elements that appeared
                all_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'mat-menu') or contains(@class, 'menu') or contains(@class, 'dropdown')]")
                print(f"📋 Found {len(all_elements)} menu-related elements:")
                for i, elem in enumerate(all_elements):
                    try:
                        elem_class = elem.get_attribute("class")
                        elem_text = elem.text.strip()[:50] if elem.text else "(no text)"
                        elem_visible = elem.is_displayed()
                        print(f"   {i+1}. class='{elem_class}' text='{elem_text}' visible={elem_visible}")
                    except:
                        continue
            except Exception as struct_debug:
                print(f"❌ Could not debug page structure: {struct_debug}")

            # Step 3: Click specific submenu option
            submenu_text = DRILLTHROUGH_MAP.get(widget_title, widget_title.split()[-1])
            print(f"🎯 Looking for submenu: {submenu_text}")
            
            # Wait longer for submenu to appear after Drill Through click
            time.sleep(3)
            
            # Try to trigger submenu appearance by hovering over Drill Through
            print("🔄 Trying to trigger submenu by hovering over Drill Through...")
            try:
                self.actions.move_to_element(drill_menu).perform()
                time.sleep(1)
            except Exception as hover_error:
                print(f"⚠️ Hover failed: {hover_error}")
            
            # Check if we need to click Drill Through again to open submenu
            print("🔄 Checking if submenu needs another trigger...")
            try:
                # Look for submenu indicators
                submenu_indicators = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'submenu') or contains(@class, 'sub-menu') or @role='menu']")
                if not submenu_indicators:
                    print("⚠️ No submenu found, trying to click Drill Through again...")
                    self.driver.execute_script("arguments[0].click();", drill_menu)
                    time.sleep(2)
            except Exception as retrigger_error:
                print(f"⚠️ Retrigger failed: {retrigger_error}")
            
            # First, debug what menu items are actually available
            print("🔍 Debugging available menu items after Drill Through click...")
            try:
                all_menu_items = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'mat-menu-item')]")
                print(f"📋 Found {len(all_menu_items)} total menu items:")
                for i, item in enumerate(all_menu_items):
                    try:
                        item_text = item.text.strip()
                        item_visible = item.is_displayed()
                        item_enabled = item.is_enabled()
                        print(f"   {i+1}. '{item_text}' (visible: {item_visible}, enabled: {item_enabled})")
                    except Exception as debug_e:
                        print(f"   {i+1}. (could not read text: {debug_e})")
                        
                # Also check for any elements that might contain the submenu text
                print("🔍 Searching for any elements containing submenu text...")
                submenu_elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{submenu_text}')]")
                print(f"📋 Found {len(submenu_elements)} elements containing '{submenu_text}':")
                for i, elem in enumerate(submenu_elements):
                    try:
                        elem_text = elem.text.strip()
                        elem_tag = elem.tag_name
                        elem_class = elem.get_attribute("class")
                        print(f"   {i+1}. <{elem_tag}> '{elem_text}' (class: {elem_class})")
                    except Exception as debug_e:
                        print(f"   {i+1}. (could not read element: {debug_e})")
                        
            except Exception as debug_error:
                print(f"❌ Could not debug menu items: {debug_error}")
            
            # Try multiple XPath variations with more flexible matching
            submenu_xpaths = [
                # Exact text match
                f"//button[contains(@class, 'mat-menu-item') and .//span[text()='{submenu_text}']]",
                f"//button[contains(@class, 'mat-menu-item') and text()='{submenu_text}']",
                
                # Contains text match
                f"//button[contains(@class, 'mat-menu-item') and .//span[contains(text(), '{submenu_text}')]]",
                f"//button[contains(@class, 'mat-menu-item') and contains(text(), '{submenu_text}')]",
                
                # More flexible selectors
                f"//mat-menu//button[contains(text(), '{submenu_text}')]",
                f"//div[contains(@class, 'mat-menu-panel')]//button[contains(text(), '{submenu_text}')]",
                f"//button[@role='menuitem' and contains(text(), '{submenu_text}')]",
                
                # Very flexible - just look for the text anywhere in clickable elements
                f"//*[contains(@class, 'mat-menu-item') and contains(., '{submenu_text}')]",
                f"//*[contains(text(), '{submenu_text}') and (self::button or self::a or self::div[@role='menuitem'])]"
            ]
            
            submenu = None
            successful_xpath = None
            
            for i, xpath in enumerate(submenu_xpaths):
                try:
                    print(f"🔄 Trying XPath {i+1}: {xpath}")
                    submenu = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    successful_xpath = xpath
                    print(f"✅ Found submenu button: {submenu_text} with XPath {i+1}")
                    break
                except Exception as xpath_error:
                    print(f"❌ XPath {i+1} failed: {str(xpath_error)[:100]}...")
                    continue
            
            if not submenu:
                print(f"❌ Could not find submenu: {submenu_text}")
                
                # Try alternative approach - look for any clickable elements with the submenu text
                print("🔄 Trying alternative approach - looking for ANY clickable elements...")
                try:
                    # Very broad search for any element containing the text
                    broad_elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{submenu_text}')]")
                    print(f"📋 Found {len(broad_elements)} elements containing '{submenu_text}':")
                    
                    for i, elem in enumerate(broad_elements):
                        try:
                            elem_tag = elem.tag_name
                            elem_class = elem.get_attribute('class') or 'no-class'
                            elem_text = elem.text.strip()
                            elem_clickable = elem.is_enabled() and elem.is_displayed()
                            print(f"   {i+1}. <{elem_tag}> class='{elem_class}' clickable={elem_clickable} text='{elem_text}'")
                            
                            # If it looks clickable, try clicking it
                            if elem_clickable and (elem_tag in ['button', 'a', 'div', 'span'] or 'menu' in elem_class.lower()):
                                print(f"🔄 Attempting to click element {i+1}...")
                                try:
                                    self.driver.execute_script("arguments[0].click();", elem)
                                    print(f"✅ Successfully clicked element {i+1}!")
                                    time.sleep(3)
                                    return True
                                except Exception as click_attempt_error:
                                    print(f"❌ Click attempt {i+1} failed: {click_attempt_error}")
                                    continue
                        except Exception as elem_debug_error:
                            print(f"   {i+1}. (could not analyze element: {elem_debug_error})")
                            continue
                    
                    # If no broad elements found, check page source
                    if not broad_elements:
                        print("🔍 No elements found, checking page source...")
                        page_source = self.driver.page_source
                        if submenu_text in page_source:
                            print(f"✅ '{submenu_text}' text found in page source but not in clickable elements")
                            print("🔍 This suggests the submenu structure is different than expected")
                        else:
                            print(f"❌ '{submenu_text}' text NOT found anywhere on page")
                            print("🔍 Possible issues:")
                            print("   - Submenu didn't load")
                            print("   - Text is different (check DRILLTHROUGH_MAP)")
                            print("   - Submenu appears in a different location")
                            
                except Exception as alt_approach_error:
                    print(f"❌ Alternative approach failed: {alt_approach_error}")
                
                return False
            
            # Try to click the submenu
            try:
                # Scroll into view first
                self.driver.execute_script("arguments[0].scrollIntoView(true);", submenu)
                time.sleep(0.2)
                
                # Try JavaScript click
                self.driver.execute_script("arguments[0].click();", submenu)
                print(f"✅ Drillthrough submenu clicked: {submenu_text}")
                print(f"✅ Used successful XPath: {successful_xpath}")
                time.sleep(3)  # Wait longer for page to load
                return True
                
            except Exception as click_error:
                print(f"❌ Failed to click submenu: {click_error}")
                # Try regular click as fallback
                try:
                    submenu.click()
                    print(f"✅ Drillthrough submenu clicked with regular click: {submenu_text}")
                    time.sleep(3)
                    return True
                except Exception as regular_click_error:
                    print(f"❌ Regular click also failed: {regular_click_error}")
                    return False
            
        except Exception as e:
            print(f"❌ Drillthrough menu error: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return False
    
    def _clear_drillthrough_overlays(self):
        """Clear overlays that might interfere with drillthrough menu"""
        try:
            overlay_selectors = [
                "[id^='cdk-overlay-']",
                ".cdk-overlay-pane",
                ".cdk-overlay-backdrop"
            ]
            
            for selector in overlay_selectors:
                try:
                    overlays = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for overlay in overlays:
                        self.driver.execute_script("arguments[0].remove();", overlay)
                except:
                    continue
        except:
            pass

    def extract_kpis(self, widget_title, drillthrough_dir):
        try:
            print(f"🔍 Looking for KPIs on drillthrough page for: {widget_title}")
            kpis = self.driver.find_elements(By.CLASS_NAME, 'kpiCardParent')
            print(f"📊 Found {len(kpis)} KPIs on drillthrough page")
            
            if not kpis:
                print(f"ℹ️ No KPIs found for drillthrough: {widget_title}")
                return

            print(f"📥 Extracting KPIs for: {widget_title}")
            safe_title = widget_title.replace(" ", "_").replace("/", "_")
            kpi_filename = f"{safe_title}_drillthrough_kpi.xlsx"
            kpi_output_path = os.path.join('download/kpis', kpi_filename)

            # Extract KPI data and save to Excel
            kpi = KPidataextract(self.driver, 'download/kpis')
            kpi.kpidata(custom_filename=kpi_filename)
            print(f"✅ Drillthrough KPI saved: {kpi_output_path}")

            # Get drillthrough parameters based on widget
            from config_loader import config_loader
            submenu_text = DRILLTHROUGH_MAP.get(widget_title, widget_title.split()[-1])
            
            # Get extra parameters for drillthrough KPI comparison
            extra_params = {}
            if submenu_text in ["Love Library", "Willis Library", "Healey Library"]:
                # For store-based drillthrough, get store ID
                store_id = config_loader.get_store_mapping(submenu_text)
                if store_id:
                    extra_params = {"Store": store_id}
                    print(f"🏪 Using store parameter for {submenu_text}: Store={store_id}")

            # Submit KPI comparison to background
            from background_processor import submit_kpi_comparison_bg
            
            comparison_file = os.path.join(drillthrough_dir, f"{safe_title}_kpi_comparison.xlsx")
            task_id = submit_kpi_comparison_bg(
                excel_path=kpi_output_path,
                output_path=comparison_file,
                is_drillthrough=True,
                extra_params=extra_params
            )
            print(f"📊 KPI Comparison submitted to background (ID: {task_id})")

        except Exception as kpi_err:
            print(f"⚠️ Drillthrough KPI Extraction/Comparison Failed: {kpi_err}")

    def process_drillthrough_widgets(self, widget_title, drillthrough_dir):
        """Process widgets in drillthrough page with timeout handling"""
        default_download_path = os.path.abspath("download")
        
        # Quick browser health check
        if not self.check_browser_health():
            print("⚠️ Browser not responsive, attempting refresh...")
            try:
                self.driver.refresh()
                time.sleep(2)  # Reduced from 5s
            except:
                print("❌ Could not refresh browser")
        
        widgets = self.driver.find_elements(By.CSS_SELECTOR, ".chart-container")
        print(f"🔍 Found {len(widgets)} widgets in drillthrough for: {widget_title}")
        
        for idx, widget in enumerate(widgets):
            widget_name = f"Unknown_Widget_{idx + 1}"
            
            # Quick health check every 3 widgets
            if idx % 3 == 0 and not self.check_browser_health():
                print(f"⚠️ Browser health check failed at widget {idx + 1}")
                time.sleep(1)  # Brief pause to recover
                
            try:
                # Get widget title and name for tracking
                title_element = widget.find_element(By.CLASS_NAME, "chart-title")
                widget_name = title_element.text.strip()
                print(f"📊 Processing Widget {idx + 1}: {widget_name}")
                
                # Move to widget for interaction
                self.actions.move_to_element(widget).pause(0.2).perform()
                
                # Test tooltip functionality (restored)
                try:
                    self.actions.move_to_element(title_element).pause(0.5).perform()
                    tooltip = self.driver.find_element(By.CLASS_NAME, "mat-tooltip")
                    if tooltip.is_displayed():
                        print(f"✅ Tooltip working for: {widget_name}")
                    else:
                        print(f"⚠️ Tooltip not visible for: {widget_name}")
                except:
                    print(f"⚠️ Tooltip test failed for: {widget_name}")
                
                # Find and click menu button
                menu_btn = widget.find_element(By.CSS_SELECTOR, "span.icon-more-vertical.keepPopup")
                self.actions.move_to_element(menu_btn).pause(0.1).click().perform()
                time.sleep(0.4)
                
                # Test Expand functionality (restored)
                try:
                    expand_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'mat-menu-item') and .//span[text()='Expand']]")))
                    self.actions.move_to_element(expand_btn).pause(0.1).click().perform()
                    time.sleep(1.5)  # Reduced from 2s
                    
                    # Check if expand modal opened
                    try:
                        modal = self.driver.find_element(By.XPATH, "//ngb-modal-window")
                        if modal.is_displayed():
                            print(f"✅ Expand working for: {widget_name}")
                            # Close modal
                            close_btn = self.driver.find_element(By.XPATH, "//ngb-modal-window//span[contains(@class, 'close')]")
                            close_btn.click()
                            time.sleep(0.5)  # Reduced from 1s
                        else:
                            print(f"⚠️ Expand modal not visible for: {widget_name}")
                    except:
                        print(f"⚠️ Expand modal not found for: {widget_name}")
                        
                except Exception as expand_error:
                    print(f"⚠️ Expand test failed for {widget_name}: {str(expand_error)}")
                
                # Click menu again for download
                try:
                    self.actions.move_to_element(menu_btn).pause(0.1).click().perform()
                    time.sleep(0.4)
                    download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'mat-menu-item') and .//span[text()='Download']]")))
                    download_btn.click()
                    print(f"📥 Download initiated for: {widget_name}")
                    
                    # Wait for file to download
                    time.sleep(2)
                    
                    # Move new .xlsx file to drillthrough_dir
                    downloaded_files = [f for f in os.listdir(default_download_path) if f.endswith(".xlsx")]
                    downloaded_files.sort(key=lambda f: os.path.getmtime(os.path.join(default_download_path, f)), reverse=True)
                    
                    if downloaded_files:
                        latest_file = downloaded_files[0]
                        src = os.path.join(default_download_path, latest_file)
                        dst = os.path.join(drillthrough_dir, latest_file)
                        os.rename(src, dst)
                        print(f"✅ Downloaded and moved: {latest_file}")
                    else:
                        print(f"⚠️ No new .xlsx file found for: {widget_name}")
                        
                except Exception as download_error:
                    print(f"⚠️ Download failed for {widget_name}: {str(download_error)}")
                
            except Exception as widget_error:
                print(f"❌ Error processing widget {widget_name}: {str(widget_error)}")
                # Save screenshot for debugging
                try:
                    os.makedirs("errors", exist_ok=True)
                    screenshot_path = f"errors/drill_widget_{widget_name.replace(' ', '_')}_error.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"📸 Error screenshot saved: {screenshot_path}")
                except:
                    print("⚠️ Could not save error screenshot")
                
                # Continue with next widget

    def drillthrough_widget(self, widget_title):
        print(f"🧪 Starting Drillthrough: {widget_title}")
        submenu_text = None
        drillthrough_dir = None
        
        try:
            submenu_text = DRILLTHROUGH_MAP.get(widget_title, widget_title.split()[-1])
            safe_title = widget_title.replace(" ", "_").replace("/", "_")
            safe_submenu = submenu_text.replace(" ", "_").replace("/", "_")
            drillthrough_dir = os.path.join("download/widgets", f"{safe_title}_{safe_submenu}")
            os.makedirs(drillthrough_dir, exist_ok=True)
            
            print(f"📁 Created drillthrough directory: {drillthrough_dir}")
            print(f"🎯 Target submenu: {submenu_text}")

            # Open drillthrough menu
            print(f"🔄 Attempting to open drillthrough menu for: {widget_title}")
            menu_success = self.open_drillthrough_menu(widget_title)
            
            if menu_success:
                print(f"✅ Drillthrough menu opened successfully for: {widget_title}")
                
                # Verify we're on the drillthrough page
                try:
                    # Check if page has changed (look for drillthrough indicators)
                    time.sleep(2)
                    current_url = self.driver.current_url
                    print(f"🔍 Current URL after drillthrough: {current_url}")
                    
                    # Look for drillthrough page indicators
                    page_indicators = self.driver.find_elements(By.CLASS_NAME, "chart-title")
                    print(f"🔍 Found {len(page_indicators)} chart elements on drillthrough page")
                    
                except Exception as verify_error:
                    print(f"⚠️ Could not verify drillthrough page: {verify_error}")
                
                # STEP 1: Extract KPIs from drillthrough page
                try:
                    print(f"🔄 STEP 1: Starting KPI extraction for: {widget_title}")
                    self.extract_kpis(widget_title, drillthrough_dir)
                    print("✅ KPI extraction completed")
                except Exception as kpi_error:
                    print(f"⚠️ KPI extraction failed for {widget_title}: {str(kpi_error)}")

                # STEP 2: Process drillthrough widgets
                try:
                    print(f"\n🔄 STEP 2: Processing drillthrough widgets for: {widget_title}")
                    before_files = set(os.listdir(drillthrough_dir))
                    print(f"📁 Files before widget processing: {before_files}")
                    
                    self.process_drillthrough_widgets(widget_title, drillthrough_dir)
                    
                    time.sleep(3)  # Allow time for all downloads

                    # STEP 3: Check for new files and merge
                    after_files = set(os.listdir(drillthrough_dir))
                    new_files = [f for f in after_files - before_files if f.endswith(".xlsx") and "kpi" not in f.lower()]
                    print(f"📁 Files after widget processing: {after_files}")
                    print(f"📊 New widget files found: {new_files}")

                    if new_files:
                        print(f"🔄 STEP 3: Merging {len(new_files)} widget files...")
                        output_path = os.path.join(drillthrough_dir, f"{safe_title}_{safe_submenu}_widgets.xlsx")
                        new_file_paths = [os.path.join(drillthrough_dir, f) for f in new_files]

                        # Merge Excel files
                        ExcelMerger.merge_specific_files(
                            file_paths=new_file_paths,
                            output_path=output_path,
                            one_sheet=False
                        )

                        # Clean up downloaded files (preserve KPI files)
                        merger = ExcelMerger(drillthrough_dir)
                        merged_filename = os.path.basename(output_path)
                        exclude_files = [merged_filename] + [f for f in os.listdir(drillthrough_dir) if "kpi" in f.lower()]
                        merger.cleanup_files(exclude_files=exclude_files)

                        print(f"✅ Widgets merged and cleaned: {output_path}")
                        print(f"📊 Widget files processed: {len(new_files)}")
                        
                        # STEP 4: Submit drillthrough widget comparison to background
                        try:
                            print(f"\n🔄 STEP 4: Submitting drillthrough widget comparison to background...")
                            from background_processor import submit_drillthrough_widget_comparison_bg
                            
                            comparison_output_path = os.path.join(drillthrough_dir, f"{safe_title}_{safe_submenu}_widget_comparison.xlsx")
                            task_id = submit_drillthrough_widget_comparison_bg(
                                excel_path=output_path,
                                widget_title=widget_title,
                                submenu_selection=submenu_text,
                                output_path=comparison_output_path
                            )
                            
                            print(f"✅ Drillthrough widget comparison submitted to background (ID: {task_id})")
                            print("🔄 Continuing with next drillthrough while comparison runs in background...")
                                
                        except Exception as comparison_error:
                            print(f"❌ Background submission failed: {str(comparison_error)}")
                            print("⚠️ Continuing with navigation back...")
                        
                    else:
                        print(f"📭 No widget files found for: {widget_title}")
                        print("🔍 This could mean:")
                        print("   - Widget processing failed")
                        print("   - No widgets available on drillthrough page")
                        print("   - Download/file detection issues")
                        
                except Exception as widget_error:
                    print(f"⚠️ Widget processing failed for {widget_title}: {str(widget_error)}")
                    import traceback
                    print(f"❌ Widget processing traceback: {traceback.format_exc()}")
            else:
                print(f"❌ Failed to open drillthrough menu for: {widget_title}")
                print("🔍 Possible reasons:")
                print("   - Widget menu button not found")
                print("   - Drill Through option not available")
                print("   - Submenu option not found")
                print("   - Page loading issues")

        except Exception as e:
            print(f"❌ Drillthrough Error for {widget_title}: {str(e)}")
            
        finally:
            # Always try to navigate back to landing page
            try:
                self.navigate_back()
                print(f"🔙 Navigated back to landing page from: {widget_title}")
            except Exception as nav_error:
                print(f"⚠️ Navigation back failed for {widget_title}: {str(nav_error)}")
                # Try alternative navigation or refresh
                try:
                    self.driver.refresh()
                    time.sleep(5)
                    print("🔄 Page refreshed as fallback")
                except:
                    print("❌ Page refresh also failed")

    def navigate_back(self):
        try:
            back_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="view-report-section"]/div/div[1]/div/app-page-navigator/div/span[1]')
            ))
            back_btn.click()
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "chart-title")))
            print("✅ Returned to Landing Page")
            time.sleep(2)
        except Exception as nav_err:
            print(f"❌ Failed to return: {nav_err}")
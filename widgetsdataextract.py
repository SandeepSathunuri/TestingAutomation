import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from widget_components.widget_loader import WidgetLoader
from widget_components.tooltip_handler import TooltipHandler
from widget_components.widget_menu import WidgetMenuHandler
from widget_components.drillthrough_handler import DrillthroughHandler
from widget_components.widget_utils import WidgetUtils
from excel_merger import ExcelMerger
import os

class WidgetExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.actions = ActionChains(driver)
        self.loader = WidgetLoader(driver)
        self.tooltip_handler = TooltipHandler(driver)
        self.menu_handler = WidgetMenuHandler(driver, self.wait, self.actions)
        self.drillthrough_handler = DrillthroughHandler(driver)
        self.widget_utils = WidgetUtils(driver)

    def smart_wait_for_downloads(self, download_dir, expected_count, max_wait=30, check_interval=0.5):
        """Smart waiting for downloads instead of fixed wait time
        Polls directory until expected files are present or timeout"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if os.path.exists(download_dir):
                xlsx_files = [f for f in os.listdir(download_dir) if f.endswith('.xlsx') and f.startswith('Sales Summary_')]
                if len(xlsx_files) >= expected_count:
                    # Wait a bit more to ensure files are fully written
                    time.sleep(0.5)  # Reduced validation wait
                    print(f"✅ Found {len(xlsx_files)} files in {time.time() - start_time:.1f}s")
                    return xlsx_files
            time.sleep(0.3)  # Reduced check interval for faster polling
        
        # Return whatever we have after timeout
        xlsx_files = []
        if os.path.exists(download_dir):
            xlsx_files = [f for f in os.listdir(download_dir) if f.endswith('.xlsx') and f.startswith('Sales Summary_')]
        print(f"⚠️ Timeout reached. Found {len(xlsx_files)} files in {max_wait}s")
        return xlsx_files

    def _find_fresh_widget(self, original_widget, title):
        """Find a fresh widget element by title to avoid stale element issues"""
        try:
            widgets = self.driver.find_elements(By.CSS_SELECTOR, ".chart-container")
            for widget in widgets:
                try:
                    widget_title = widget.find_element(By.CLASS_NAME, "chart-title").text.strip()
                    if widget_title == title:
                        return widget
                except:
                    continue
            return original_widget  # Fallback to original if not found
        except:
            return original_widget

    def _detect_page_type(self):
        """Detect if we're on landing page or drillthrough page"""
        try:
            # Check for drillthrough indicators
            drillthrough_indicators = [
                ".drillthrough-page",
                ".drill-through-content",
                "[class*='drillthrough']",
                "[class*='drill-through']"
            ]
            
            for indicator in drillthrough_indicators:
                if self.driver.find_elements(By.CSS_SELECTOR, indicator):
                    return "drillthrough"
            
            # Check URL for drillthrough patterns
            current_url = self.driver.current_url
            if any(keyword in current_url.lower() for keyword in ['drill', 'detail', 'expanded']):
                return "drillthrough"
            
            # Check page title or breadcrumbs
            try:
                page_title = self.driver.title.lower()
                if any(keyword in page_title for keyword in ['drill', 'detail', 'expanded']):
                    return "drillthrough"
            except:
                pass
            
            # Default to landing page
            return "landing"
            
        except Exception as detect_error:
            print(f"⚠️ Page type detection failed: {detect_error}, defaulting to landing")
            return "landing"

    def _handle_both_operations(self, widget, title):
        """Handle both download and expand with page-specific logic"""
        print(f"🔄 Starting both operations for: {title}")
        
        # Detect page type
        page_type = self._detect_page_type()
        print(f"📍 Detected page type: {page_type}")
        
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                # Get fresh widget element to avoid stale references
                if attempt > 0:
                    widget = self._find_fresh_widget(widget, title)
                    time.sleep(1)  # Wait between attempts
                
                if self.menu_handler.click_widget_menu(widget):
                    download_success, expand_success = self.menu_handler.handle_both_operations(page_type)
                    
                    # Special handling for landing page where download might need separate session
                    if page_type == "landing" and expand_success and not download_success:
                        print(f"🔄 Landing page: Expand succeeded, trying separate download session for: {title}")
                        
                        # Wait a moment and try download in separate menu session
                        time.sleep(2)  # Longer wait for landing page
                        widget = self._find_fresh_widget(widget, title)
                        
                        # Try up to 2 times for separate download
                        for download_attempt in range(2):
                            try:
                                if self.menu_handler.click_widget_menu(widget):
                                    if self.menu_handler.handle_download():
                                        download_success = True
                                        print(f"✅ Separate download session succeeded for: {title}")
                                        break
                                    else:
                                        print(f"❌ Separate download attempt {download_attempt + 1} failed for: {title}")
                                else:
                                    print(f"❌ Could not reopen menu for separate download attempt {download_attempt + 1}: {title}")
                                
                                if download_attempt < 1:  # If not last attempt
                                    time.sleep(1)
                                    widget = self._find_fresh_widget(widget, title)
                                    
                            except Exception as download_error:
                                print(f"❌ Separate download attempt {download_attempt + 1} error: {str(download_error)[:50]}...")
                                if download_attempt < 1:
                                    time.sleep(1)
                                    widget = self._find_fresh_widget(widget, title)
                    
                    # Return final results
                    if download_success and expand_success:
                        print(f"✅ Both operations completed for: {title}")
                        return True, True
                    elif download_success:
                        print(f"✅ Download completed, ⚠️ expand had issues for: {title}")
                        return True, False
                    elif expand_success:
                        print(f"✅ Expand completed, ⚠️ download had issues for: {title}")
                        return False, True
                    else:
                        print(f"❌ Both operations had issues for: {title}")
                        return False, False
                else:
                    print(f"⚠️ Could not open menu for: {title}")
                    
            except Exception as operation_error:
                print(f"❌ Operation attempt {attempt + 1} failed: {str(operation_error)[:50]}...")
                
            if attempt < max_attempts - 1:
                print(f"🔄 Retrying both operations for: {title}")
        
        # Try alternative approach - separate operations with fresh widget lookups
        print(f"🔄 Trying fallback: separate operations for: {title}")
        return self._handle_separate_operations(widget, title, page_type)

    def _handle_separate_operations(self, widget, title, page_type="landing"):
        """Fallback: Handle download and expand as separate operations"""
        print(f"🔄 Fallback: Separate operations for: {title} on {page_type} page")
        
        download_success = False
        expand_success = False
        
        # Try download first
        try:
            widget = self._find_fresh_widget(widget, title)
            if self.menu_handler.click_widget_menu(widget):
                if self.menu_handler.handle_download():
                    download_success = True
                    print(f"✅ Fallback download completed for: {title}")
        except Exception as download_error:
            print(f"❌ Fallback download failed: {str(download_error)[:50]}...")
        
        # Wait and try expand with page-specific approach
        time.sleep(2)
        try:
            widget = self._find_fresh_widget(widget, title)
            
            if page_type == "landing":
                # Landing page: Try double-click approach
                print(f"🔄 Trying landing page expand approach for: {title}")
                title_element = widget.find_element(By.CLASS_NAME, "chart-title")
                self.actions.double_click(title_element).perform()
                time.sleep(3)  # Landing page might need more time
                
                # Check if modal opened
                modal_selectors = ["ngb-modal-window", ".modal", "[role='dialog']"]
                modal_found = any(self.driver.find_elements(By.CSS_SELECTOR, sel) for sel in modal_selectors)
                
                if modal_found:
                    # Use landing page specific closing
                    from selenium.webdriver.common.keys import Keys
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    expand_success = True
                    print(f"✅ Landing page fallback expand completed for: {title}")
                else:
                    # Maybe it expanded in place
                    expand_success = True
                    print(f"✅ Landing page expand (no modal) completed for: {title}")
            else:
                # Drillthrough page: Try menu approach
                print(f"🔄 Trying drillthrough expand approach for: {title}")
                if self.menu_handler.click_widget_menu(widget):
                    if self.menu_handler.handle_expand("drillthrough"):
                        expand_success = True
                        print(f"✅ Drillthrough fallback expand completed for: {title}")
                
        except Exception as expand_error:
            print(f"❌ Fallback expand failed: {str(expand_error)[:50]}...")
        
        return download_success, expand_success

    def widgetdata(self):
        processed = set()
        drill_targets = []
        widget_dir = os.path.abspath("download/widgets")
        os.makedirs(widget_dir, exist_ok=True)

        widgets = self.loader.get_widgets()
        if not widgets:
            print("🔚 No widgets found.")
            return

        # Download landing page widgets with optimized processing
        for widget in widgets:
            title = self.loader.get_widget_title(widget)
            if not title or title in processed:
                continue

            processed.add(title)
            print(f"🧩 Processing widget: {title}")
            try:
                # Streamlined processing - no unnecessary moves
                # Get tooltip quickly
                try:
                    title_element = widget.find_element(By.CLASS_NAME, "chart-title")
                    tooltip = self.tooltip_handler.get_tooltip(title_element)
                    print(f"📝 Tooltip: {tooltip}")
                except Exception as tooltip_error:
                    print(f"📝 Tooltip: (failed - {str(tooltip_error)[:30]}...)")

                # Enhanced menu operations - single menu session approach
                print(f"🔄 Starting menu operations for: {title}")
                
                # Try to handle both operations in a single menu session
                download_success, expand_success = self._handle_both_operations(widget, title)
                
                if download_success and expand_success:
                    print(f"✅ Both operations succeeded for: {title}")
                elif download_success:
                    print(f"✅ Download succeeded, ⚠️ expand had issues for: {title}")
                elif expand_success:
                    print(f"⚠️ Download had issues, ✅ expand succeeded for: {title}")
                else:
                    print(f"❌ Both operations had issues for: {title}")
                    print(f"⚠️ Continuing anyway - widget data may still be available")

                drill_targets.append(title)
                print(f"✅ Widget processing completed: {title}\n")
                # No delay - continue immediately to next widget
                
            except Exception as e:
                print(f"❌ Error processing widget '{title}': {str(e)}")

        # STEP 1: Merge landing page widget files
        print("\n" + "="*60)
        print("📁 STEP 1: Merging Landing Page Widget Files")
        print("="*60)

        # Smart wait for downloads to complete
        print("⏳ Waiting for downloads to complete...")
        expected_count = len(drill_targets)
        widget_files = self.smart_wait_for_downloads(os.path.abspath("download"), expected_count, max_wait=8)  # Reduced from 15 to 8

        # Validate and prepare widget files (already collected by smart_wait_for_downloads)
        download_dir = os.path.abspath("download")
        validated_files = []
        for f in widget_files:
            file_path = os.path.join(download_dir, f)
            # Quick validation - files should already be complete from smart wait
            if (os.path.isfile(file_path) and os.path.getsize(file_path) > 0):
                validated_files.append(file_path)
        widget_files = validated_files

        print(f"🔍 Scanning download directory: {download_dir}")
        print(f"📊 Found {len(widget_files)} widget files:")
        for f in widget_files:
            file_size = os.path.getsize(f) if os.path.exists(f) else 0
            print(f"  • {os.path.basename(f)} ({file_size:,} bytes)")

        if widget_files:
            merged_path = os.path.join(widget_dir, "Combined_Widgets_Landing.xlsx")
            print(f"\n📊 Merging {len(widget_files)} files into: {merged_path}")
            try:
                # Merge all widget files into combined file
                ExcelMerger.merge_specific_files(
                    file_paths=widget_files,
                    output_path=merged_path,
                    one_sheet=False
                )
                print(f"✅ Successfully created combined file: {merged_path}")

                # Verify merged file was created
                if os.path.exists(merged_path):
                    merged_size = os.path.getsize(merged_path)
                    print(f"📄 Combined file size: {merged_size} bytes")
                else:
                    print("❌ Combined file was not created!")
                    return

                # STEP 2: Delete individual widget files
                print(f"\n🗑️ STEP 2: Cleaning up individual widget files...")
                deleted_count = 0
                for widget_file in widget_files:
                    try:
                        if os.path.exists(widget_file):
                            os.remove(widget_file)
                            print(f"  ✅ Deleted: {os.path.basename(widget_file)}")
                            deleted_count += 1
                        else:
                            print(f"  ⚠️ File not found: {os.path.basename(widget_file)}")
                    except Exception as e:
                        print(f"  ❌ Could not delete {os.path.basename(widget_file)}: {e}")
                print(f"✅ Cleaned up {deleted_count}/{len(widget_files)} individual files")

            except Exception as merge_error:
                print(f"❌ Error during file merging: {str(merge_error)}")
                return

            # STEP 3: Submit widget comparison to background
            print(f"\n" + "="*60)
            print("🔍 STEP 3: Submitting Landing Page Widget Comparison to Background")
            print("="*60)
            try:
                from background_processor import submit_landing_widget_comparison_bg
                comparison_output_path = os.path.join(widget_dir, "landing_widget_comparison_report.xlsx")
                task_id = submit_landing_widget_comparison_bg(merged_path, comparison_output_path)
                print(f"✅ Landing page widget comparison submitted to background (ID: {task_id})")
                print("🔄 Continuing with drillthrough while comparison runs in background...")
            except Exception as compare_error:
                print(f"❌ Background submission failed: {str(compare_error)}")
                print("⚠️ Continuing with drillthrough...")

        else:
            print("❌ No widget files found to merge!")
            print("💡 Possible issues:")
            print("  • Downloads may have failed")
            print("  • Files may be in different location")
            print("  • File naming pattern may have changed")
            
            # List all files in download directory for debugging
            if os.path.exists(download_dir):
                all_files = [f for f in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, f))]
                if all_files:
                    print(f"\n📁 All files in {download_dir}:")
                    for f in all_files:
                        print(f"  • {f}")
                else:
                    print(f"📁 Download directory is empty: {download_dir}")
            print("⚠️ Skipping drillthrough due to missing widget files")
            return  # Exit if no widgets to process

        # Start drillthrough phase AFTER landing page comparison is complete
        print("\n" + "="*60)
        print("📦 Starting Drillthrough Phase...")
        print("="*60)

        for idx, title in enumerate(drill_targets, 1):
            print(f"\n🔄 [{idx}/{len(drill_targets)}] Processing drillthrough for: {title}")
            try:
                self.drillthrough_handler.drillthrough_widget(title)
                print(f"✅ [{idx}/{len(drill_targets)}] Completed drillthrough for: {title}")
            except Exception as e:
                print(f"❌ [{idx}/{len(drill_targets)}] Drillthrough failed for {title}: {str(e)}")
                # Continue with next widget

        print("\n" + "="*60)
        print("🎉 All drillthrough operations completed!")
        print("="*60)

        return drill_targets
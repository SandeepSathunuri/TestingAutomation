import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from login import Authenticator
from dashboardSelection import DashboardManager
from kpisdataextraction import KPidataextract
from widgetsdataextract import WidgetExtractor
from excel_merger import ExcelMerger
from kpistoreprocedures import Data, compare_kpi_data, read_kpi_from_excel
from filters import FilterAutomation
from drillthrough_db_handler import DrillthroughDBHandler
from error_handler import error_handler
from widgetstoreprocedures import (
    read_widget_values,
    fetch_db_widget_values,
    compare_widget_data,
    normalize,
    widget_sp_map
)
# Basic imports only

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def setup_directories():
    """Create necessary directories for downloads"""
    download_dir = os.path.abspath("download")
    kpi_dir = os.path.join(download_dir, "kpis")
    widget_dir = os.path.join(download_dir, "widgets")
    
    os.makedirs(kpi_dir, exist_ok=True)
    os.makedirs(widget_dir, exist_ok=True)
    
    logging.info(f"Directories created: {download_dir}")
    return download_dir, kpi_dir, widget_dir

def setup_chrome_driver(download_dir):
    """Configure and initialize Chrome WebDriver with performance optimizations"""
    chrome_options = Options()
    
    # Download preferences
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 2  # Block images for faster loading
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Performance optimizations
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # Security and compatibility arguments
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Memory optimizations
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": download_dir
        })
        
        # Set faster page load strategy
        driver.execute_cdp_cmd("Page.enable", {})
        driver.execute_cdp_cmd("Runtime.enable", {})
        
        logging.info("Chrome driver initialized successfully with performance optimizations")
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize Chrome driver: {str(e)}")
        raise

def setup_selenium_fallback(download_dir):
    """Fallback Selenium driver setup with performance optimizations"""
    chrome_options = Options()
    
    # Download preferences
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 2  # Block images for faster loading
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Performance optimizations
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # Security and compatibility arguments
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Memory optimizations
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": download_dir
        })
        
        # Set faster page load strategy
        driver.execute_cdp_cmd("Page.enable", {})
        driver.execute_cdp_cmd("Runtime.enable", {})
        
        logging.info("Chrome driver initialized successfully with performance optimizations")
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize Chrome driver: {str(e)}")
        raise

def process_kpis(driver, kpi_dir):
    """Process KPI extraction and submit comparison to background"""
    try:
        logging.info("🔍 Starting KPI processing...")
        
        # Extract KPI data
        kpi_extractor = KPidataextract(driver, kpi_dir)
        kpi_extractor.kpidata()
        logging.info("✅ KPI data extraction completed")

        # Submit KPI comparison to background processing
        excel_kpi_path = os.path.join(kpi_dir, "kpi_data.xlsx")
        
        if os.path.exists(excel_kpi_path):
            try:
                from background_processor import submit_kpi_comparison_bg
                
                comparison_report_path = os.path.join(kpi_dir, "landing_kpi_comparison_report.xlsx")
                task_id = submit_kpi_comparison_bg(excel_kpi_path, comparison_report_path)
                
                logging.info(f"✅ KPI comparison submitted to background (ID: {task_id})")
                print("✅ KPI comparison submitted to background - continuing with widgets...")
                
            except Exception as kpi_comp_error:
                error_handler.log_error("KPI Comparison", "Landing Page", "Background Submission", str(kpi_comp_error))
                logging.error(f"❌ KPI background submission failed: {str(kpi_comp_error)}")
                print(f"❌ KPI background submission failed: {str(kpi_comp_error)}")
                # Continue with workflow
        else:
            error_handler.log_warning("KPI Processing", "Landing Page", "File Not Found", f"KPI Excel file not found: {excel_kpi_path}")
            logging.warning(f"❌ KPI Excel file not found: {excel_kpi_path}")
            print("❌ KPI Excel file not found")
            
    except Exception as e:
        error_handler.log_error("KPI Processing", "Landing Page", "General Error", str(e))
        logging.error(f"❌ Error in KPI processing: {str(e)}")
        print(f"❌ KPI Processing Error: {str(e)}")
        # Continue with workflow

def process_landing_widgets(driver, widget_dir):
    """Process landing page widgets with error handling"""
    try:
        logging.info("🧩 Starting landing page widget processing...")
        print("🧩 Starting landing page widget processing...")
        
        # Extract Widget Data (includes landing page comparison)
        print("🔄 Creating WidgetExtractor...")
        widget_extractor = WidgetExtractor(driver)
        
        print("🔄 Calling widgetdata()...")
        result = widget_extractor.widgetdata()
        print(f"📊 widgetdata() returned: {result}")
        
        logging.info("✅ Landing page widget extraction and comparison completed")
        print("✅ Landing page widget extraction and comparison completed")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Error in landing widget processing: {str(e)}")
        print(f"❌ Landing Widget Processing Error: {str(e)}")
        print(f"❌ Error details: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def process_drillthrough_widgets(driver, drill_targets):
    """Process drillthrough for each widget with error handling"""
    drillthrough_handler = DrillthroughDBHandler()
    
    for widget_title in drill_targets:
        try:
            logging.info(f"🔄 Starting drillthrough for: {widget_title}")
            print(f"🔄 Processing drillthrough for: {widget_title}")
            
            # Simple drillthrough processing
            
            # Import here to avoid circular imports
            from widget_components.drillthrough_handler import DrillthroughHandler
            drill_handler = DrillthroughHandler(driver)
            
            # Perform drillthrough with retry logic
            max_retries = 2
            success = False
            
            for retry in range(max_retries):
                try:
                    drill_handler.drillthrough_widget(widget_title)
                    success = True
                    break
                except Exception as drill_error:
                    print(f"❌ Drillthrough attempt {retry + 1} failed: {str(drill_error)}")
                    if retry < max_retries - 1:
                        print("🔄 Retrying drillthrough...")
                        time.sleep(2)
                    else:
                        raise drill_error
            
            if success:
                # Get the submenu text for database comparison
                from widget_components.drillthrough_handler import DRILLTHROUGH_MAP
                submenu_text = DRILLTHROUGH_MAP.get(widget_title, widget_title.split()[-1])
                
                # Drillthrough comparison is handled automatically by the background processor
                # in the drillthrough_handler.py (step 4), so no additional comparison needed here
                
                logging.info(f"✅ Drillthrough completed for: {widget_title}")
                print(f"✅ Drillthrough completed for: {widget_title}")
            
        except Exception as e:
            logging.error(f"❌ Error in drillthrough for {widget_title}: {str(e)}")
            print(f"❌ Drillthrough Error for {widget_title}: {str(e)}")
            # Continue with next widget

def main():
    """Main automation workflow with comprehensive error handling"""
    driver = None
    try:
        logging.info("🚀 Starting automation workflow...")
        print("🚀 Starting Swift Insights Dashboard Automation...")
        
        # Setup directories and driver
        download_dir, kpi_dir, widget_dir = setup_directories()
        driver = setup_chrome_driver(download_dir)
        
        # Login
        try:
            login = Authenticator(driver)
            login.login()
            logging.info("✅ Login completed successfully")
            print("✅ Login successful")
        except Exception as e:
            logging.error(f"❌ Login failed: {str(e)}")
            print(f"❌ Login failed: {str(e)}")
            return

        # Select Dashboard
        try:
            dashboard = DashboardManager(driver)
            dashboard.choose_dashboard("Sales Summary")
            logging.info("✅ Dashboard selected successfully")
            print("✅ Sales Summary dashboard opened")
        except Exception as e:
            logging.error(f"❌ Dashboard selection failed: {str(e)}")
            print(f"❌ Dashboard selection failed: {str(e)}")
            return
        
        # Apply filters
        try:
            filter_automation = FilterAutomation(driver)
            filter_automation.run()
            logging.info("✅ Filters applied successfully")
            print("✅ Filters applied")
        except Exception as e:
            logging.error(f"❌ Filter application failed: {str(e)}")
            print(f"❌ Filter application failed: {str(e)}")
            # Continue without filters
        
        # Process KPIs
        print("🔄 Starting KPI processing...")
        process_kpis(driver, kpi_dir)
        print("✅ KPI processing completed, continuing to widgets...")
        
        # Process Landing Page Widgets
        try:
            print("🔄 About to start widget processing...")
            widget_result = process_landing_widgets(driver, widget_dir)
            print(f"📊 Widget processing result: {widget_result}")
            
            if widget_result:
                print("✅ Widget processing succeeded, proceeding to drillthrough...")
                # Get drill targets from widget extractor
                try:
                    from widgetsdataextract import WidgetExtractor
                    widget_extractor = WidgetExtractor(driver)
                    
                    # Get widget titles for drillthrough
                    from widget_components.widget_loader import WidgetLoader
                    loader = WidgetLoader(driver)
                    widgets = loader.get_widgets()
                    
                    drill_targets = []
                    for widget in widgets:
                        title = loader.get_widget_title(widget)
                        if title:
                            drill_targets.append(title)
                    
                    if drill_targets:
                        print(f"📋 Found {len(drill_targets)} widgets for drillthrough: {drill_targets}")
                        process_drillthrough_widgets(driver, drill_targets)
                    else:
                        print("⚠️ No widgets found for drillthrough")
                        
                except Exception as e:
                    logging.error(f"❌ Error getting drill targets: {str(e)}")
                    print(f"❌ Error getting drill targets: {str(e)}")
            else:
                print("❌ Widget processing failed, skipping drillthrough...")
                print("🔄 Continuing to background processing completion...")
                
        except Exception as widget_section_error:
            print(f"🚨 CRITICAL ERROR in widget section: {widget_section_error}")
            print(f"🚨 Error type: {type(widget_section_error).__name__}")
            import traceback
            print(f"🚨 Full traceback: {traceback.format_exc()}")
            print("🔄 Continuing to background processing despite widget error...")

        # Wait for all background comparisons to complete
        print("\n" + "="*60)
        print("⏳ Waiting for background data comparisons to complete...")
        print("="*60)
        
        try:
            from background_processor import wait_for_all_comparisons, get_background_status, shutdown_background_processor
            
            # Show status while waiting
            if wait_for_all_comparisons(timeout=300):  # 5 minute timeout
                print("✅ All background data comparisons completed successfully")
                
                # Show final results
                import background_processor
                results = background_processor.background_processor.get_completed_results()
                successful = len([r for r in results if r.get('status') == 'completed'])
                failed = len([r for r in results if r.get('status') == 'failed'])
                
                print(f"📊 Background processing summary:")
                print(f"  ✅ Successful comparisons: {successful}")
                print(f"  ❌ Failed comparisons: {failed}")
                
            else:
                print("⚠️ Some background comparisons may still be running")
                status = get_background_status()
                print(f"📊 Final status: {status}")
            
            # Shutdown background processor
            shutdown_background_processor()
            
        except Exception as bg_error:
            print(f"⚠️ Background processing error: {str(bg_error)}")

        logging.info("🎉 Automation workflow completed successfully")
        print("🎉 Automation workflow completed successfully!")

    except WebDriverException as e:
        error_handler.log_error("Main Workflow", "System", "WebDriver Error", str(e))
        if driver:
            error_handler.take_screenshot(driver, "System", "WebDriver_Error")
    except TimeoutException as e:
        error_handler.log_error("Main Workflow", "System", "Timeout Error", str(e))
        if driver:
            error_handler.take_screenshot(driver, "System", "Timeout_Error")
    except Exception as e:
        error_handler.log_error("Main Workflow", "System", "Unexpected Error", str(e))
        if driver:
            error_handler.take_screenshot(driver, "System", "Unexpected_Error")
    finally:
        # Generate comprehensive error report
        error_handler.generate_error_report()
        error_handler.print_summary()
        
        if driver:
            try:
                time.sleep(3)  # Wait for any pending downloads
                driver.quit()
                logging.info("🔄 Browser closed successfully")
                print("🔄 Browser closed")
            except Exception as e:
                logging.error(f"❌ Error closing browser: {str(e)}")
                print(f"❌ Error closing browser: {str(e)}")

if __name__ == "__main__":
    main()
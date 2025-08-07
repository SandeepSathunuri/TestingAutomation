import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
 
 
filter_values = {
        "Year": "2024",
        # "Month": ["April"],
        # "Region": None,
        # "State": None,
        # "Store": None,
        # "Channel": None
    }
class FilterAutomation:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
 
    def setup(self):
        """Open the filter section."""
        try:
            filter_section = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'filter-section')))
            filter_section.click()
            print("Opened filter section")
        except Exception as e:
            print(f"Error during setup: {str(e)}")
            self.cleanup()
            raise
 
    def scroll_to_element(self, element):
        """Scroll to a given element."""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)
 
    def select_dropdown_option(self, filter_label, option_text):
        """Select dropdown option for Year."""
        try:
            # Locate the filter button by its label
            filter_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//div[contains(@class, 'filter-label-sec') and .//span[text()='{filter_label}']]//following-sibling::div[contains(@class, 'filter-item-data-wrapper')]//button")
            ))
           
            self.scroll_to_element(filter_button)
            filter_button.click()
            print(f"Clicked on {filter_label} filter")
 
            # Select the option
            option = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//*[contains(text(), '{option_text}') and not(contains(@class, 'filter-item-title'))]")
            ))
            self.scroll_to_element(option)
            self.driver.execute_script("arguments[0].click();", option)
            print(f"Selected {option_text} from {filter_label} filter")
            time.sleep(0.5)
           
        except Exception as e:
            print(f"Error selecting {option_text} from {filter_label}: {str(e)}")
 
    def select_checkbox_option(self, filter_label, option_texts):
        try:
            print(f"\n➡️ Selecting checkbox filter: {filter_label} → {option_texts}")
            if isinstance(option_texts, str):
                option_texts = [option_texts]

            # Click to open the filter dropdown
            filter_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//div[contains(@class, 'filter-label-sec') and .//span[text()='{filter_label}']]"
                           f"//following-sibling::div[contains(@class, 'filter-item-data-wrapper')]//button")
            ))
            self.scroll_to_element(filter_button)
            filter_button.click()
            print(f"✅ Opened {filter_label} filter")

            # Loop through options
            for option_text in option_texts:
                print(f"🔍 Looking for {option_text} in {filter_label}")
                label_xpath = f"//label[contains(., '{option_text}')]/input[@type='checkbox']"
                checkbox = self.wait.until(EC.element_to_be_clickable((By.XPATH, label_xpath)))
                self.scroll_to_element(checkbox)
                if not checkbox.is_selected():
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    print(f"✅ Selected {option_text}")
                else:
                    print(f"ℹ️ {option_text} already selected")
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error selecting checkboxes in {filter_label}: {str(e)}")

 
    def apply_filters(self):
        """Process filter selections and click the Apply button."""
        try:
            for filter_label, value in filter_values.items():
                if value is not None:
                    if filter_label == "Year":
                        self.select_dropdown_option(filter_label, value)
                    else:
                        self.select_checkbox_option(filter_label, value)
                else:
                    print(f"Keeping default 'All' for {filter_label}")
 
            # Click the Apply button
            self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'apply-btn'))).click()
            print("Clicked the Apply button")
            time.sleep(10)
            # For filter close button
            close_filter_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/app-root/app-layout/div/mat-sidenav-container/mat-sidenav-content/div/app-view-report/mat-drawer-container/mat-drawer/div/app-report-filter/div/div[1]/div/div[2]')))
            close_filter_button.click()
            
        except Exception as e:
            print(f"Error processing filters or clicking Apply button: {str(e)}")
 
    def cleanup(self):
        """Quit the WebDriver."""
        time.sleep(5)
 
    def run(self):
        """Main method to run the automation."""
        try:
            self.setup()
            self.apply_filters()
        finally:
            self.cleanup()
 

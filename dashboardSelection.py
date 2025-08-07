from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

class DashboardManager:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def choose_dashboard(self, dashboard_name):
        try:
            dashboards = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "home-icon-group")))
            found = False

            for i in range(len(dashboards)):
                try:
                    # Re-fetch each element in the loop to avoid stale references
                    dashboards = self.driver.find_elements(By.CLASS_NAME, "home-icon-group")
                    dashboard = dashboards[i]
                    text = dashboard.text.strip()
                    print(text)

                    if text == dashboard_name:
                        link = dashboard.find_element(By.TAG_NAME, 'a')
                        link.click()
                        print(f"Opened dashboard: {dashboard_name}")
                        found = True
                        break

                except StaleElementReferenceException:
                    print("Stale element, trying again...")

            if not found:
                print(f" Dashboard '{dashboard_name}' not found!")

        except Exception as e:
            print(f"Error while choosing dashboard: {e}")

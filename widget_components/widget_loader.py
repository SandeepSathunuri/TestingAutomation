from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class WidgetLoader:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def get_widgets(self):
        try:
            return self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "chart-parent")))
        except TimeoutException:
            print("❌ Timeout fetching widgets")
            return []

    def get_widget_title(self, widget):
        try:
            return widget.find_element(By.CLASS_NAME, "chart-title").text.strip()
        except:
            return None
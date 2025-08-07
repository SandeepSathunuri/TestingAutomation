from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from openpyxl import Workbook
import os
import time

class KPidataextract:
    def __init__(self, driver, kpi_dir):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.download_dir = kpi_dir
        self.action = ActionChains(driver)

    def kpidata(self, custom_filename="kpi_data.xlsx"):
        wb = Workbook()
        ws = wb.active
        ws.title = 'kpi_data'
        ws.append(["kpi name", "kpi_dashboard_value"]) 

        kpis = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'kpiCardParent')))
        time.sleep(2)

        for kpi in kpis:
            try:
                kpiCard = kpi.find_element(By.CLASS_NAME, "cardText")
                kpiname_elem = kpiCard.find_element(By.CLASS_NAME, "title-label")
                kpiname = kpiname_elem.text.strip()
                kpidata = kpiCard.find_element(By.CLASS_NAME, 'kpi-data-value').text.strip()

                # Hover to trigger tooltip (optional visual check)
                self.action.move_to_element(kpiname_elem).perform()
                time.sleep(0.5)

                # Check tooltip presence (for logging only, not saving)
                tooltip_text = "❌ Not found"
                try:
                    tooltip = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "mat-tooltip"))
                    )
                    if tooltip.text.strip():
                        tooltip_text = tooltip.text.strip()
                except:
                    pass

                print(f"{kpiname} | {kpidata} | Tooltip: {tooltip_text}")  # Just print, not saving to Excel
                ws.append([kpiname, kpidata])

            except Exception as e:
                print(f"❌ Error with KPI: {e}")

        # Save Excel
        excel_path = os.path.join(self.download_dir, custom_filename)
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)  
        wb.save(excel_path)
        print(f"\n✅ KPI data saved to: {excel_path}")


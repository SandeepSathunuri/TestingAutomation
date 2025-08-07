from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os

class Authenticator:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        load_dotenv()  # Load environment variables
        self.base_url = os.environ.get('LOGIN_URL')
        self.email = os.environ.get('EMAIL')
        self.password = os.environ.get('PASSWORD')
    
    def login(self):
        print("Logging into the application...")
        try:
            self.driver.get(self.base_url)
            self.driver.maximize_window()
            
            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.XPATH, '//app-login-page//input')))
            email_field.send_keys(self.email)

            # Click next
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//app-login-page//button'))).click()

            # Enter password
            password_field = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))
            password_field.send_keys(self.password)

            # Click sign in
            sign_in_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-login-page/div/div[1]/div[2]/div/div[2]/div[2]/form/div[3]/div[2]/div[2]/button'))
            )
            sign_in_button.click()

            print("Logged in successfully.")
            self.wait.until(EC.presence_of_element_located((By.ID, "pills-tabContent")))
        except Exception as e:
            print(f"Error occurred during login: {e}")

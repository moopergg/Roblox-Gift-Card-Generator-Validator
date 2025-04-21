from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import os
import colorama
from colorama import Fore
import sys
import random

colorama.init()

def setup_driver():
    """Setup and return a Chrome WebDriver with error handling"""
    print(f"{Fore.YELLOW}[INFO] Setting up Chrome WebDriver...{Fore.RESET}")
    
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # First try to initialize without webdriver-manager
        print(f"{Fore.YELLOW}[INFO] Attempting to initialize Chrome WebDriver...{Fore.RESET}")
        driver = webdriver.Chrome(options=chrome_options)
        print(f"{Fore.GREEN}[SUCCESS] Chrome WebDriver initialized successfully{Fore.RESET}")
        return driver
    except WebDriverException as e:
        print(f"{Fore.RED}[ERROR] Failed to initialize Chrome WebDriver: {str(e)}{Fore.RESET}")
        print(f"{Fore.YELLOW}[INFO] Trying alternative method with webdriver-manager...{Fore.RESET}")
        
        try:
            # Try with webdriver-manager as fallback
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"{Fore.GREEN}[SUCCESS] Chrome WebDriver initialized successfully with webdriver-manager{Fore.RESET}")
            return driver
        except Exception as e2:
            print(f"{Fore.RED}[ERROR] Failed to initialize Chrome WebDriver with webdriver-manager: {str(e2)}{Fore.RESET}")
            print(f"{Fore.RED}[CRITICAL] Cannot continue without a working WebDriver{Fore.RESET}")
            
            print(f"\n{Fore.YELLOW}=== TROUBLESHOOTING TIPS ===={Fore.RESET}")
            print(f"{Fore.CYAN}1. Make sure you have Google Chrome installed{Fore.RESET}")
            print(f"{Fore.CYAN}2. Try installing the required packages: pip install selenium webdriver-manager colorama{Fore.RESET}")
            print(f"{Fore.CYAN}3. Check if your Chrome version matches the ChromeDriver version{Fore.RESET}")
            print(f"{Fore.CYAN}4. Try running the script with administrator privileges{Fore.RESET}")
            
            sys.exit(1)

def find_code_input_field(driver):
    """Try different methods to find the code input field on the redemption page"""
    possible_selectors = [
        (By.ID, "pin-code"),
        (By.ID, "code-input"),
        (By.NAME, "code"),
        (By.CSS_SELECTOR, "input[placeholder*='code']"),
        (By.CSS_SELECTOR, "input[placeholder*='Code']"),
        (By.CSS_SELECTOR, "input[placeholder*='PIN']"),
        (By.CSS_SELECTOR, "input[placeholder*='pin']"),
        (By.CSS_SELECTOR, "input.code-input"),
        (By.CSS_SELECTOR, "input.pin-input"),
        (By.CSS_SELECTOR, "input[type='text']"),  # Last resort, might find wrong field
    ]
    
    for selector_type, selector_value in possible_selectors:
        try:
            elements = driver.find_elements(selector_type, selector_value)
            if elements:
                for element in elements:
                    if element.is_displayed():
                        print(f"{Fore.GREEN}[SUCCESS] Found input field with selector: {selector_type}={selector_value}{Fore.RESET}")
                        return element
        except:
            continue
    
    return None

def find_redeem_button(driver):
    """Try different methods to find the redeem button"""
    possible_selectors = [
        (By.ID, "redeem-button"),
        (By.ID, "redeem-code-button"),
        (By.ID, "redeem"),
        (By.NAME, "redeem"),
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(text(), 'Redeem')]"),
        (By.XPATH, "//button[contains(text(), 'REDEEM')]"),
        (By.XPATH, "//input[contains(@value, 'Redeem')]"),
        (By.XPATH, "//a[contains(text(), 'Redeem')]"),
    ]
    
    for selector_type, selector_value in possible_selectors:
        try:
            elements = driver.find_elements(selector_type, selector_value)
            if elements:
                for element in elements:
                    if element.is_displayed():
                        print(f"{Fore.GREEN}[SUCCESS] Found redeem button with selector: {selector_type}={selector_value}{Fore.RESET}")
                        return element
        except:
            continue
    
    return None

def check_code_result(driver):
    """Check if code redemption was successful or failed"""
    # Wait a bit for the result to appear
    time.sleep(3)
    
    # Check for success indicators
    success_selectors = [
        (By.CSS_SELECTOR, ".redeemed-code-container"),
        (By.CSS_SELECTOR, ".success-message"),
        (By.CSS_SELECTOR, ".redemption-success"),
        (By.XPATH, "//div[contains(text(), 'success')]"),
        (By.XPATH, "//div[contains(text(), 'Success')]"),
        (By.XPATH, "//span[contains(text(), 'success')]"),
        (By.XPATH, "//span[contains(text(), 'Success')]"),
        (By.XPATH, "//div[contains(text(), 'redeemed')]"),
        (By.XPATH, "//div[contains(text(), 'Redeemed')]"),
    ]
    
    for selector_type, selector_value in success_selectors:
        try:
            elements = driver.find_elements(selector_type, selector_value)
            if elements:
                for element in elements:
                    if element.is_displayed():
                        return True, ""
        except:
            continue
    
    # Check for error messages
    error_selectors = [
        (By.CSS_SELECTOR, ".error-message"),
        (By.CSS_SELECTOR, ".response-error"),
        (By.CSS_SELECTOR, ".redemption-error"),
        (By.XPATH, "//div[contains(text(), 'error')]"),
        (By.XPATH, "//div[contains(text(), 'Error')]"),
        (By.XPATH, "//span[contains(text(), 'error')]"),
        (By.XPATH, "//span[contains(text(), 'Error')]"),
        (By.XPATH, "//div[contains(text(), 'invalid')]"),
        (By.XPATH, "//div[contains(text(), 'Invalid')]"),
    ]
    
    for selector_type, selector_value in error_selectors:
        try:
            elements = driver.find_elements(selector_type, selector_value)
            if elements:
                for element in elements:
                    if element.is_displayed():
                        return False, element.text
        except:
            continue
    
    return False, "Unknown status (no success or error message found)"

def check_roblox_codes():
    print(f"{Fore.GREEN}===== ROBLOX CODE CHECKER ====={Fore.RESET}")
    print(f"{Fore.YELLOW}[INFO] Loading codes from roblox.txt...{Fore.RESET}")
    
    # Check if roblox.txt exists
    if not os.path.exists("roblox.txt"):
        print(f"{Fore.RED}[ERROR] roblox.txt not found! Generate codes first.{Fore.RESET}")
        return
    
    # Read all codes from file
    with open("roblox.txt", "r") as file:
        codes = file.read().splitlines()
    
    print(f"{Fore.YELLOW}[INFO] Found {len(codes)} codes to check{Fore.RESET}")
    
    # Ask for Roblox login credentials
    print(f"{Fore.CYAN}Please enter your Roblox login details to proceed:{Fore.RESET}")
    username = input(f"{Fore.CYAN}Username: {Fore.RESET}")
    password = input(f"{Fore.CYAN}Password: {Fore.RESET}")
    
    driver = None
    valid_codes = []
    
    try:
        driver = setup_driver()
        if not driver:
            return
            
        # Login to Roblox
        print(f"{Fore.YELLOW}[INFO] Logging into Roblox...{Fore.RESET}")
        driver.get("https://www.roblox.com/login")
        
        # Wait for login page to load
        try:
            # Try different possible login field IDs
            found_username = False
            found_password = False
            
            # Try to find username field
            for selector in ["#login-username", "input[name='username']", "#username", "input[placeholder*='Username']"]:
                try:
                    username_field = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if username_field.is_displayed():
                        username_field.send_keys(username)
                        found_username = True
                        print(f"{Fore.GREEN}[SUCCESS] Found username field with selector: {selector}{Fore.RESET}")
                        break
                except:
                    continue
                    
            # Try to find password field
            for selector in ["#login-password", "input[name='password']", "#password", "input[type='password']"]:
                try:
                    password_field = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if password_field.is_displayed():
                        password_field.send_keys(password)
                        found_password = True
                        print(f"{Fore.GREEN}[SUCCESS] Found password field with selector: {selector}{Fore.RESET}")
                        break
                except:
                    continue
                    
            # Try to find login button
            login_button = None
            for selector in ["#login-button", "button[type='submit']", "input[type='submit']", 
                           "button:contains('Log In')", "button:contains('Login')", "input[value='Log In']"]:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed():
                            login_button = button
                            print(f"{Fore.GREEN}[SUCCESS] Found login button with selector: {selector}{Fore.RESET}")
                            break
                    if login_button:
                        break
                except:
                    continue
                    
            if not found_username or not found_password or not login_button:
                print(f"{Fore.RED}[ERROR] Could not find all login elements.{Fore.RESET}")
                print(f"{Fore.YELLOW}[INFO] The login page structure may have changed.{Fore.RESET}")
                
                # Take screenshot for debugging
                screenshot_path = "login_page_debug.png"
                driver.save_screenshot(screenshot_path)
                print(f"{Fore.YELLOW}[INFO] Screenshot saved to {screenshot_path} for debugging{Fore.RESET}")
                
                # Ask user to continue manually
                print(f"{Fore.YELLOW}[INFO] Please log in manually in the browser window.{Fore.RESET}")
                input(f"{Fore.CYAN}Press Enter after you've logged in...{Fore.RESET}")
            else:
                # Click login button
                login_button.click()
                print(f"{Fore.YELLOW}[INFO] Login credentials submitted.{Fore.RESET}")
                
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Issue with login page: {str(e)}{Fore.RESET}")
            # Take screenshot for debugging
            screenshot_path = "login_error_debug.png"
            driver.save_screenshot(screenshot_path)
            print(f"{Fore.YELLOW}[INFO] Screenshot saved to {screenshot_path} for debugging{Fore.RESET}")
            
            # Ask user to continue manually
            print(f"{Fore.YELLOW}[INFO] Please log in manually in the browser window.{Fore.RESET}")
            input(f"{Fore.CYAN}Press Enter after you've logged in...{Fore.RESET}")
        
        # Wait for login to complete
        print(f"{Fore.YELLOW}[INFO] Waiting for login process...{Fore.RESET}")
        time.sleep(5)  # Give time for login to process
        
        # Always prompt for verification just to be safe
        print(f"{Fore.YELLOW}[INFO] You may need to complete human verification steps in the browser window.{Fore.RESET}")
        input(f"{Fore.CYAN}Press Enter after you've completed any verification steps (or if no verification was needed)...{Fore.RESET}")
        
        # Go to redeem page
        print(f"{Fore.YELLOW}[INFO] Navigating to code redemption page...{Fore.RESET}")
        driver.get("https://www.roblox.com/redeem")
        
        # Wait for the page to load
        time.sleep(5)
        
        # Take a screenshot of the redeem page for debugging
        screenshot_path = "redeem_page_debug.png"
        driver.save_screenshot(screenshot_path)
        print(f"{Fore.YELLOW}[INFO] Screenshot saved to {screenshot_path} for debugging{Fore.RESET}")
        
        # Find the code input field
        print(f"{Fore.YELLOW}[INFO] Looking for code input field...{Fore.RESET}")
        input_field = find_code_input_field(driver)
        
        if not input_field:
            print(f"{Fore.RED}[ERROR] Could not find the code input field.{Fore.RESET}")
            print(f"{Fore.YELLOW}[INFO] Please check the screenshot and locate the field manually.{Fore.RESET}")
            
            # Ask for manual input
            input_field_id = input(f"{Fore.CYAN}Please enter the ID or CSS selector of the input field (or press Enter to exit): {Fore.RESET}")
            if not input_field_id:
                return
                
            try:
                input_field = driver.find_element(By.CSS_SELECTOR, input_field_id)
            except:
                print(f"{Fore.RED}[ERROR] Could not find element with that selector.{Fore.RESET}")
                return
                
        # Find the redeem button
        print(f"{Fore.YELLOW}[INFO] Looking for redeem button...{Fore.RESET}")
        redeem_button = find_redeem_button(driver)
        
        if not redeem_button:
            print(f"{Fore.RED}[ERROR] Could not find the redeem button.{Fore.RESET}")
            print(f"{Fore.YELLOW}[INFO] Please check the screenshot and locate the button manually.{Fore.RESET}")
            
            # Ask for manual input
            button_id = input(f"{Fore.CYAN}Please enter the ID or CSS selector of the redeem button (or press Enter to exit): {Fore.RESET}")
            if not button_id:
                return
                
            try:
                redeem_button = driver.find_element(By.CSS_SELECTOR, button_id)
            except:
                print(f"{Fore.RED}[ERROR] Could not find element with that selector.{Fore.RESET}")
                return
        
        # Check each code
        total = len(codes)
        print(f"{Fore.YELLOW}[INFO] Starting to check {total} codes...{Fore.RESET}")
        
        for index, code in enumerate(codes):
            try:
                # Clean the code (remove any unwanted characters if needed)
                clean_code = code.strip().replace("-", "")  # Remove hyphens if present
                
                print(f"{Fore.BLUE}[{index+1}/{total}] Checking code: {code}{Fore.RESET}")
                
                # Clear the input field and enter the code
                input_field.clear()
                input_field.send_keys(clean_code)
                
                # Click the redeem button
                redeem_button.click()
                
                # Check the result
                is_valid, message = check_code_result(driver)
                
                if is_valid:
                    print(f"{Fore.GREEN}[VALID] Code {code} is valid!{Fore.RESET}")
                    valid_codes.append(code)
                    
                    # Save immediately to avoid losing if script crashes
                    with open("valid_codes.txt", "a") as valid_file:
                        valid_file.write(f"{code}\n")
                else:
                    print(f"{Fore.RED}[INVALID] Code {code} - {message}{Fore.RESET}")
                
                # Refresh page to prepare for next code
                driver.get("https://www.roblox.com/redeem")
                time.sleep(3)
                
                # Re-find elements after refresh
                input_field = find_code_input_field(driver)
                if not input_field:
                    print(f"{Fore.RED}[ERROR] Could not find the code input field after refresh.{Fore.RESET}")
                    break
                    
                redeem_button = find_redeem_button(driver)
                if not redeem_button:
                    print(f"{Fore.RED}[ERROR] Could not find the redeem button after refresh.{Fore.RESET}")
                    break
            
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Error checking code {code}: {str(e)}{Fore.RESET}")
                
                # Try to refresh page and continue
                try:
                    driver.get("https://www.roblox.com/redeem")
                    time.sleep(3)
                    
                    # Re-find elements after refresh
                    input_field = find_code_input_field(driver)
                    if not input_field:
                        print(f"{Fore.RED}[ERROR] Could not find the code input field after error recovery.{Fore.RESET}")
                        break
                        
                    redeem_button = find_redeem_button(driver)
                    if not redeem_button:
                        print(f"{Fore.RED}[ERROR] Could not find the redeem button after error recovery.{Fore.RESET}")
                        break
                        
                except:
                    print(f"{Fore.RED}[CRITICAL] Failed to recover. The script will now exit.{Fore.RESET}")
                    break
            
            # Sleep between requests to prevent being flagged as a bot
            time.sleep(random.uniform(1.5, 3.0))  # Random delay to seem more human-like
    
    except Exception as e:
        print(f"{Fore.RED}[ERROR] An unexpected error occurred: {str(e)}{Fore.RESET}")
    
    finally:
        # Close the browser
        if driver:
            print(f"{Fore.YELLOW}[INFO] Closing browser...{Fore.RESET}")
            try:
                driver.quit()
            except:
                pass
        
        # Print results
        print(f"\n{Fore.GREEN}===== RESULTS ====={Fore.RESET}")
        print(f"{Fore.YELLOW}Total codes checked: {len(codes)}{Fore.RESET}")
        print(f"{Fore.GREEN}Valid codes found: {len(valid_codes)}{Fore.RESET}")
        
        if valid_codes:
            print(f"{Fore.GREEN}Valid codes have been saved to valid_codes.txt{Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}No valid codes found.{Fore.RESET}")

if __name__ == "__main__":
    try:
        check_roblox_codes()
        print(f"\n{Fore.CYAN}Press Enter to exit...{Fore.RESET}")
        input()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO] Process interrupted by user{Fore.RESET}")
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR] An unexpected error occurred: {str(e)}{Fore.RESET}")
import pyautogui
import time
from pathlib import Path
import cv2
import pygetwindow as gw

# Define the consistent part of the window title
target_window_keyword = "AmiBroker"

# Set the save directory for screenshots
save_dir = Path(r"E:\App Dev\GitHub\chart_ocr\data\15-01-2025")
save_dir.mkdir(parents=True, exist_ok=True)

# List of symbols to iterate through
symbols = ["BIOCON", "ADANIENT", "ATGL", "BPCL"] 

# Logging function
def log_error(message):
    with open(save_dir / "error_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


def find_and_activate_amibroker_window(keyword):

    # Get all active windows
    windows = gw.getAllTitles()

    # Find a window title that contains the target keyword
    for title in windows:
        if keyword in title:
            print(f"Found target window: {title}")
            target_window = gw.getWindowsWithTitle(title)[0]
            target_window.activate()
            time.sleep(2)
            #pyautogui.click(x=495, y=93)
            return target_window
    print(f"No window found containing: {keyword}")
    log_error("No window found containing: " + keyword)
    return None

# Wait for the chart to load
def wait_for_chart_load(timeout=7):
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(0.5)  # Poll every 500 ms
    return True

# Select a symbol from the dropdown
def select_symbol(amibroker_window, symbol):
    try:
        # Simulate clicking the dropdown and selecting the symbol
        x, y, width, height = amibroker_window.box
        pyautogui.click(x+495, y+93)  # Adjust coordinates for dropdown
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.typewrite(symbol)
        pyautogui.press("enter")
        time.sleep(1)  # Small delay for dropdown action
    except Exception as e:
        log_error(f"Failed to select symbol {symbol}: {e}")
        return False
    return True

# Capture and save a screenshot
def capture_screenshot(symbol):
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(save_dir / f"{symbol}.png")
    except Exception as e:
        log_error(f"Failed to capture screenshot for {symbol}: {e}")
        return False
    return True

# Main automation loop
# Activate the AmiBroker window
amibroker_window = find_and_activate_amibroker_window(target_window_keyword)

if not amibroker_window or not amibroker_window.isActive:
    print(f"Error: Could not open Amibroker....")
    log_error("Failed to open Amibroker")
else:
    for symbol in symbols:
        print(f"Processing symbol: {symbol}")
        
        # Select the symbol
        if not select_symbol(amibroker_window, symbol):
            print(f"Error: Could not select symbol {symbol}. Skipping...")
            log_error(f"Failed to select symbol {symbol}")
            continue

        # Wait for the chart to load
        if not wait_for_chart_load(timeout=7):  # Adjust timeout as needed
            log_error(f"Timeout while waiting for chart to load for {symbol}")
            print(f"Error: Chart did not load for {symbol}. Skipping...")
            continue

        # Capture the screenshot
        if not capture_screenshot(symbol):
            print(f"Error: Could not capture screenshot for {symbol}. Skipping...")
            log_error(f"Failed to capture screenshot for {symbol}")
            continue

        print(f"Successfully processed symbol: {symbol}")

    print("Automation completed. Check the error log for any issues.")

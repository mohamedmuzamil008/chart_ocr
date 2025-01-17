import pyautogui
import time
from pathlib import Path
import cv2
import pygetwindow as gw
import pandas as pd
import argparse

save_dir_base = r"E:\App Dev\GitHub\chart_ocr\data"
save_dir = None 

# Define the consistent part of the window title
target_window_keyword = "AmiBroker"

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
def capture_screenshot(amibroker_window, symbol):
    try:
        x, y, width, height = amibroker_window.box
        screenshot = pyautogui.screenshot(region=(x+1570, y+140, 335, 830))
        screenshot.save(save_dir / f"{symbol}.jpg")
    except Exception as e:
        log_error(f"Failed to capture screenshot for {symbol}: {e}")
        return False
    return True

def parse_arguments():
    try:
        parser = argparse.ArgumentParser(description='Chart Screenshot Automation Tool')
        parser.add_argument('--save_dir', type=str, required=True,
                          help='Directory name to save screenshots')
        parser.add_argument('--symbols_file', type=str, required=True,
                          help='Path to CSV file containing symbols')
        
        args = parser.parse_args()

        global save_dir
        save_dir = Path(save_dir_base) / args.save_dir
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate symbols file exists
        if not Path(Path(save_dir_base) / args.symbols_file).exists():
            log_error(f"Symbols file not found: {args.symbols_file}")
            raise FileNotFoundError(f"Symbols file not found: {args.symbols_file}")
            
        # Validate symbols file is CSV
        if not args.symbols_file.lower().endswith('.csv'):
            log_error("Symbols file must be a CSV file")
            raise ValueError("Symbols file must be a CSV file")            
            
        return args
        
    except FileNotFoundError as e:
        print(f"File Error: {str(e)}")
        log_error(f"File Error: {str(e)}")
        exit(1)
    except ValueError as e:
        print(f"Value Error: {str(e)}")
        log_error(f"Value Error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error during argument parsing: {str(e)}")
        log_error(f"Unexpected error during argument parsing: {str(e)}")
        exit(1)

# Main automation loop
def main():   

    args = parse_arguments()

    symbols = pd.read_csv(Path(save_dir_base) / args.symbols_file)["Symbol"].tolist()
    
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
            if not capture_screenshot(amibroker_window, symbol):
                print(f"Error: Could not capture screenshot for {symbol}. Skipping...")
                log_error(f"Failed to capture screenshot for {symbol}")
                continue

            print(f"Successfully processed symbol: {symbol}")
        
        pyautogui.alert(
        text='Chart Screenshot Automation Completed Successfully!',
        title='Process Complete',
        button='OK'
        )
        print("Automation completed. Check the error log for any issues.")

if __name__ == "__main__":
    main()
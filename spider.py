import os
import time
import random
import pandas as pd
from tkinter import filedialog, Tk, messagebox
from customtkinter import CTk, CTkButton
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    # Add more user agents as needed
]

def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))

def retry_with_backoff(func, max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        try:
            return func()
        except Exception as e:
            wait_time = 2 ** attempt + random.uniform(0, 1)
            print(f"Retrying in {wait_time:.2f} seconds due to: {e}")
            time.sleep(wait_time)
            attempt += 1
    raise Exception(f"Failed after {max_attempts} attempts")

def main():
    # Function to open file dialog
    def select_file():
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        return file_path

    # Load the file
    file_path = select_file()
    print(f"Selected file: {file_path}")
    if not file_path:
        messagebox.showerror("Error", "No file selected. Exiting.")
        return

    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    else:
        data = pd.read_excel(file_path)

    part_numbers = data['Part Number'].tolist()
    print(f"Loaded {len(part_numbers)} part numbers.")

    # Create data folder if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        for user_agent in USER_AGENTS:
            context = browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1280, 'height': 800},
                locale='en-US',
                timezone_id='America/New_York',
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                permissions=['geolocation'],
                bypass_csp=True,
                java_script_enabled=True,
            )
            page = context.new_page()
            retry_with_backoff(lambda: page.goto('https://www.motion.com/'))

            print("Navigated to https://www.motion.com/ or https://www.motioncanada.ca/")

            # Wait for the user to manually solve the Cloudflare verification
            messagebox.showinfo("Cloudflare Verification", "Please solve the Cloudflare verification, then click OK to continue.")
            random_delay()

            # Interact with the page to help bypass Cloudflare
            try:
                page.wait_for_selector('body', timeout=60000)  # Wait for up to 60 seconds
                page.mouse.move(400, 400)  # Move mouse to simulate activity
                page.mouse.click(400, 400)  # Click to simulate activity
                random_delay(1, 2)
                page.reload()  # Reload the page to help pass the verification
                print("Page reloaded to bypass Cloudflare verification.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to bypass Cloudflare: {e}")
                browser.close()
                return

            # Allow the user to identify the search field
            messagebox.showinfo("Identify Search Field", "Please identify the search field, then click OK to continue.")
            search_field = None

            try:
                search_field = page.wait_for_selector('//input[contains(@placeholder, "Search")]', timeout=30000)
                print("Search field located.")
            except Exception as e:
                messagebox.showerror("Error", f"Search field not found: {e}")
                browser.close()
                return

            # Store the search field selector
            search_field_selector = '//input[contains(@placeholder, "Search")]'

            for part_number in part_numbers:
                part_number_str = str(part_number)

                # Locate the search field
                search_field = page.query_selector(search_field_selector)
                
                # Type the part number into the search field with delays between keystrokes
                search_field.fill("")
                for char in part_number_str:
                    search_field.type(char)
                    random_delay(0.1, 0.3)
                search_field.press("Enter")
                random_delay()

                # Prompt the user to confirm if a relevant product is on the page
                relevant_product = messagebox.askyesno("Product Confirmation", f"Is there a relevant product for part number {part_number_str} on the page?")
                if not relevant_product:
                    continue

                # Wait for the content to load and extract the text
                item_info_selector = 'div.item-info-row.row.flex-nowrap.mb-42p.mb-lg-56p'
                try:
                    page.wait_for_selector(item_info_selector, timeout=20000)
                    content = page.query_selector(item_info_selector).inner_text()
                except Exception as e:
                    content = f"Content not found: {e}"

                # Save the content to a text file
                with open(f'data/{part_number_str}.txt', 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Saved content for part number {part_number_str}")

                # Go back to the main page for the next search
                retry_with_backoff(lambda: page.goto('https://www.motion.com/'))
                random_delay()

        browser.close()
        print("Scraping completed.")

# GUI setup
def start_scraper():
    main()

app = CTk()
app.title("Motion Scraper")

button = CTkButton(app, text="Start Scraper", command=start_scraper)
button.pack(padx=20, pady=20)

app.mainloop()

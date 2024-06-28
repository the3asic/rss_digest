import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get width from environment variable
WIDTH = int(os.getenv('WIDTH', 800))
DEVICE_PIXEL_RATIO = 2  # Set device pixel ratio for HiDPI

def render_html_to_png(html_file_path, output_png_path):
    # Set up Selenium with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size={WIDTH * DEVICE_PIXEL_RATIO},{1000 * DEVICE_PIXEL_RATIO}")  # Set initial window size

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"file://{os.path.abspath(html_file_path)}")

    # Adjust the window size to the content
    height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(WIDTH * DEVICE_PIXEL_RATIO, height * DEVICE_PIXEL_RATIO)

    # Set device pixel ratio
    driver.execute_script(f"document.body.style.zoom='{DEVICE_PIXEL_RATIO * 100}%'")

    # Take screenshot
    screenshot = driver.get_screenshot_as_png()
    driver.quit()

    # Save the screenshot as a PNG file
    with open(output_png_path, 'wb') as f:
        f.write(screenshot)

    # Optionally, crop the image to remove any extra space
    image = Image.open(output_png_path)
    image = image.crop((0, 0, WIDTH * DEVICE_PIXEL_RATIO, height * DEVICE_PIXEL_RATIO))
    image.save(output_png_path)

if __name__ == "__main__":
    html_file_path = "newsletter.html"  # Path to your HTML file
    output_png_path = "newsletter.png"  # Path to save the PNG file
    render_html_to_png(html_file_path, output_png_path)

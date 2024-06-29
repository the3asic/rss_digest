import os
from playwright.sync_api import sync_playwright
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get width from environment variable
WIDTH = int(os.getenv('WIDTH', 800))
DEVICE_PIXEL_RATIO = 2  # Set device pixel ratio for HiDPI

def render_html_to_png(html_file_path, output_png_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=DEVICE_PIXEL_RATIO)
        
        # Set viewport size
        page.set_viewport_size({"width": WIDTH, "height": 1000})
        
        # Navigate to the HTML file
        page.goto(f"file://{os.path.abspath(html_file_path)}")
        
        # Add padding and increase font size
        page.evaluate("""() => {
            document.body.style.padding = '40px';
            document.body.style.fontSize = '24px';
            document.body.style.boxSizing = 'border-box';
        }""")
        
        # Wait for any animations or dynamic content to load
        page.wait_for_load_state("networkidle")
        
        # Get the full height of the page
        height = page.evaluate("document.documentElement.scrollHeight")
        
        # Update viewport to match full page height
        page.set_viewport_size({"width": WIDTH, "height": height})
        
        # Capture screenshot
        screenshot = page.screenshot(full_page=True)
        
        browser.close()
    
    # Save the screenshot
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

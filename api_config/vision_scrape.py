import time
from selenium import webdriver
from PIL import Image
from io import BytesIO
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin, urlparse

image_path_list = []
web_image_path_list = []
i = 0

def save_png(screenshot):
    """
    Saves a screenshot to the local file system.

    Args:
        screenshot (bytes): The screenshot in PNG format.

    Returns:
        None
    """
    global i
    image_path = f'./image_saves/screenshot{i}.jpg'
    with open(image_path, 'wb') as f:
        f.write(screenshot)
    
    web_image_path_list.append(image_path)
    i += 1

def combine_images(image_paths, output_path):
    """
    Combines multiple images vertically into a single image.

    Args:
        image_paths (list): List of paths to the images to combine.
        output_path (str): Path to save the combined image.

    Returns:
        None
    """
    images = [Image.open(path) for path in image_paths]
    widths, heights = zip(*(i.size for i in images))

    max_width = max(widths)
    total_height = sum(heights)

    combined_image = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))

    y_offset = 0
    for image in images:
        combined_image.paste(image, (0, y_offset))
        y_offset += image.size[1]

    combined_image.save(output_path)

def scroll_to_bottom(driver):
    """
    Scrolls to the bottom of the webpage and captures screenshots.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.

    Returns:
        None
    """
    window_height = driver.execute_script("return window.innerHeight")
    last_height = driver.execute_script("return document.body.scrollHeight")
    current_scroll = 0
    while current_scroll <= last_height - window_height:
        driver.execute_script(f"window.scrollTo(0, {current_scroll + window_height});")
        time.sleep(3)
        screenshot = driver.get_screenshot_as_png()
        save_png(screenshot=screenshot)
        current_scroll += window_height

def is_valid_image_url(url):
    """
    Validates if the given URL is a valid image URL based on its extension.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL has a valid image extension, False otherwise.
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    parsed_url = urlparse(url)
    return any(parsed_url.path.lower().endswith(ext) for ext in valid_extensions)

def scraper_main(url):
    """
    Main function to scrape images and screenshots from a webpage.
    It also scrapes all the images url 

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        None
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)  # Adjust this time as needed
        driver.execute_script("window.scrollTo(0, 0);")

        # Capture the screenshot after the content has loaded
        screenshot_before_scroll = driver.get_screenshot_as_png()
        save_png(screenshot_before_scroll)

        # Scroll down to the bottom of the page
        scroll_to_bottom(driver)

        # Scrape the images
        img_elements = driver.find_elements(By.TAG_NAME, 'img')
        
        if not img_elements:
            print("No images found on the webpage.")
            return
        
        for img in img_elements:
            img_url = img.get_attribute('src')
            if img_url:
                img_url = urljoin(url, img_url)  # Join with base URL to form absolute URL
                if is_valid_image_url(img_url):
                    image_path_list.append(img_url)

        # print(image_path_list)

        # Output path for the combined image
        output_path = './test/combined_screenshots.jpg'
        # Combine images into one
        combine_images(web_image_path_list, output_path)
        return image_path_list
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

# Example usage
# scraper_main('https://www.scrapethissite.com/pages/advanced/')

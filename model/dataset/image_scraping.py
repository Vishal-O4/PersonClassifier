from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, Keys
import os
import requests
from PIL import Image, ImageFilter
import hashlib
import io
import numpy as np
import cv2


class Images:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.action = ActionChains(self.driver)
        sleep(2)

    def fetch_image_url(self, query):
        self.driver.get("https://www.google.co.in/")
        sleep(1)
        self.driver.find_element(By.ID, "APjFqb").send_keys(query + "face images")
        self.action.send_keys(Keys.ENTER).perform()
        self.driver.find_element(By.XPATH, "//div[text()='Images']").click()
        sleep(2)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        sleep(5)
        img_results = self.driver.find_elements(By.TAG_NAME, "img")
        print(len(img_results))
        src = []
        for img in img_results:
            source = img.get_attribute('src')
            if source:
                src.append(img.get_attribute('src'))
        return src

    def image_download(self, folder_path, url):
        global image_content
        try:
            image_content = requests.get(url).content

        except Exception as e:
            print(f"ERROR - Could not download {url} - {e}")

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert("RGB")
            file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + ".jpg")

            image = self.image_quality_improve(image)

            with open(file_path, "wb") as f:
                image.save(f, "JPEG", quality=100)
            print(f"SUCCESS - saved {url} - as {file_path}")

        except Exception as e:
            print(f"ERROR - Could not save {url} - {e}")

    def image_quality_improve(self, image):
        # Convert PIL Image to NumPy array for OpenCV processing
        img = np.array(image)

        # Resize the image using a higher-quality interpolation method
        scale_percent = 150  # Scale up by 150%
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)

        # Apply denoising
        denoised_img = cv2.fastNlMeansDenoisingColored(resized_img, None, 10, 10, 7, 21)

        # Sharpen the image
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened_img = cv2.filter2D(denoised_img, -1, kernel)

        # Histogram equalization
        img_yuv = cv2.cvtColor(sharpened_img, cv2.COLOR_BGR2YUV)
        img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
        enhanced_img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

        # Convert the enhanced image back to a PIL image for saving
        enhanced_pil_img = Image.fromarray(enhanced_img)
        return enhanced_pil_img

    def search_and_download(self, search_term, target_path):
        # target_folder = os.path.join(target_path, '_'.join(search_term.split(' ')))

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        with webdriver.Chrome():
            res = self.fetch_image_url(search_term)

        if res:
            for elem in res:
                self.image_download(target_path, elem)

    def add_pics(self, dataset_path):
        player_name = {}
        for team in os.scandir(dataset_path):
            for player in os.scandir(team.path):
                p_name = str(player).split("'")[-2]
                player_name[p_name[:len(p_name)]] = player.path
                # player_name[str(player)] = player.path
        return player_name


if __name__ == '__main__':
    img = Images()
    # img.search_and_download("Virat Kohli face", "D:\\Programming\\Projects\\selenium_test_web_scraping")
    player_name_list = img.add_pics("D:\\Programming\\Projects\\selenium_test_web_scraping\\Virat")
    print(player_name_list)
    for player_name, path in player_name_list.items():
        img.search_and_download(player_name, path)
    print("Process finished!")

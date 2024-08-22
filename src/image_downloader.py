import uuid
import requests
from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem

class ImageDownloader:
    def __init__(self, save_directory="output/images"):
        self.browser = Selenium()
        self.fs = FileSystem()
        self.save_directory = save_directory
        self.fs.create_directory(self.save_directory)

    def download_image(self, image_url):
        """Downloads an image from a given URL using the browser and saves it in the specified directory."""
        fs = FileSystem()
        save_directory = "output"
        fs.create_directory(save_directory)

        image_filename = f"{uuid.uuid4()}.jpg"
        image_path = f"{save_directory}/{image_filename}"

        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                fs.create_binary_file(image_path, response.content)
                print(f"Image saved as {image_path}")
            else:
                print("Failed to download image.")
        except requests.RequestException as e:
            print(f"Error downloading image: {e}")

        return image_filename

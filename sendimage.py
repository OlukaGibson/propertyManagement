import requests
import time
import os

# Endpoint URL
url = "http://127.0.0.1:5000/recognize"

# Directory containing images to send
images_directory = "./propertymngt/images"

def send_image(image_path):
    """
    Send an image to the /recognize endpoint and return the response.
    """
    with open(image_path, 'rb') as image_file:
        files = {'file': image_file}
        try:
            response = requests.post(url, files=files)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending image {image_path}: {e}")
            return None

def main():
    """
    Main function to send images one at a time.
    """
    # Get all image files in the directory
    image_files = [f for f in os.listdir(images_directory) if os.path.isfile(os.path.join(images_directory, f))]

    if not image_files:
        print("No images found in the directory to send.")
        return

    for image_file in image_files:
        image_path = os.path.join(images_directory, image_file)
        print(f"Sending image: {image_file}")

        # Send the image and wait for the response
        response = send_image(image_path)

        if response:
            print(f"Response for {image_file}: {response}")
        else:
            print(f"Failed to get a response for {image_file}.")

        # Wait for 1 second before sending the next image (adjust as needed)
        time.sleep(1)

if __name__ == "__main__":
    main()

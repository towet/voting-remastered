from base64 import b64decode
import requests
import time
import os
import json
import pickle

# Face++ API credentials
API_KEY = "yLpzmRB7uunCbk9UpDzI7xlE_tBXhtin"  # Face++ API key
API_SECRET = "1e7oYHL9YiGzteSdsHjmEX8dX2zGdEWp"  # Face++ API secret

def login_check(email, image):
    try:
        # Split the image string into header and encoded image data
        header, encoded = image.split(",", 1)

        # Generate unique filename using the current timestamp
        current_time = str(time.time_ns())
        file_new = f"{current_time}_uploaded.png"

        # Decode and save the uploaded image
        with open(file_new, "wb") as f:
            f.write(b64decode(encoded))

        # Load the stored user data
        if not os.path.exists("users.pkl"):
            os.remove(file_new)
            return "User not found!"

        with open("users.pkl", "rb") as f:
            users = pickle.load(f)

        if email not in users:
            os.remove(file_new)
            return "User not found!"

        # Get the stored image path for the user
        stored_image = users[email]

        # Face++ API endpoint for face comparison
        compare_url = "https://api-us.faceplusplus.com/facepp/v3/compare"
        
        # Prepare the files for upload
        files = {
            'image_file1': open(file_new, 'rb'),
            'image_file2': open(stored_image, 'rb')
        }
        
        # Prepare the data payload
        data = {
            'api_key': API_KEY,
            'api_secret': API_SECRET
        }

        # Make the API request
        response = requests.post(compare_url, files=files, data=data)
        result = response.json()

        # Close and remove files
        files['image_file1'].close()
        files['image_file2'].close()
        os.remove(file_new)

        # Check the confidence score
        if 'confidence' in result and result['confidence'] > 80:  # You can adjust this threshold
            return "Successfully Logged in!"
        else:
            return "Face verification failed!"

    except Exception as e:
        # Clean up in case of error
        if os.path.exists(file_new):
            os.remove(file_new)
        return f"An error occurred: {str(e)}"

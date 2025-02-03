from base64 import b64decode
import requests
import os
import pickle
import time

# Face++ API credentials - same as in login.py
API_KEY = "yLpzmRB7uunCbk9UpDzI7xlE_tBXhtin"
API_SECRET = "1e7oYHL9YiGzteSdsHjmEX8dX2zGdEWp"

def register_on_submit(email, image):
    try:
        # Split the image string into header and encoded image data
        header, encoded = image.split(",", 1)

        # Create images directory if it doesn't exist
        if not os.path.exists("user_images"):
            os.makedirs("user_images")

        # Generate unique filename for the user's image
        image_filename = f"user_images/{email}.png"

        # Check if user already exists
        if os.path.exists("users.pkl"):
            with open("users.pkl", "rb") as f:
                users = pickle.load(f)
            if email in users:
                return "User already exists!"
        else:
            users = {}

        # Save the image
        with open(image_filename, "wb") as f:
            f.write(b64decode(encoded))

        # Verify that the image contains a face using Face++ API
        detect_url = "https://api-us.faceplusplus.com/facepp/v3/detect"
        
        files = {
            'image_file': open(image_filename, 'rb')
        }
        
        data = {
            'api_key': API_KEY,
            'api_secret': API_SECRET
        }

        response = requests.post(detect_url, files=files, data=data)
        files['image_file'].close()
        
        result = response.json()

        # Check if a face was detected
        if 'faces' not in result or len(result['faces']) == 0:
            os.remove(image_filename)
            return "No face detected in the image!"

        if len(result['faces']) > 1:
            os.remove(image_filename)
            return "Multiple faces detected! Please use an image with only one face."

        # Store the user data
        users[email] = image_filename
        with open("users.pkl", "wb") as f:
            pickle.dump(users, f)

        return "Registration Successful!"

    except Exception as e:
        if os.path.exists(image_filename):
            os.remove(image_filename)
        return f"An error occurred: {str(e)}"
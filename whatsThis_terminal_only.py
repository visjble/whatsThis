import os, time
import subprocess
import openai
import base64
import requests

# Global variables initialization
api_key = ""                 # Stores the API key for authentication
base64_image = ""            # Stores the base64 encoded image
conversation_id = None       # Stores the conversation ID for the API session
first_api_call = True        # Flag to track if it's the first call to the API

#typewriter effect
def typewrite(text, delay=0.01):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # for newline after the text

# Function to take a screenshot and save it to a temporary file
def take_screenshot():
    temp_file = "/tmp/screenshot.jpg" # CUSTOMIZE PATH FOR YOUR NEEDS HERE
    subprocess.run(["gnome-screenshot", "-a", "-f", temp_file])
    return temp_file

# Function to encode the image in base64 format
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to upload the image and get its description from GPT-4 Vision API
def upload_image_and_get_description(base64_image, additional_text="What’s in this image? Be concise and to the point"):
    global conversation_id, first_api_call
    if first_api_call:
        typewrite('Querying gpt4-vision...')
        first_api_call = False  # Set the flag to False after the first call

    # Headers for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Payload for the API request
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": additional_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 200
    }

    # Add conversation ID to the payload if it exists
    if conversation_id:
        payload["conversation_id"] = conversation_id

    # Send the request and handle the response
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if 'conversation_id' in data:
                conversation_id = data['conversation_id']  # Update the conversation ID
            return data['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code}\n{response.text}"
    except Exception as e:
        return f"An error occurred: {e}"

# Main function of the script
def main():
    global api_key, base64_image
    
    # Try-except block to handle KeyboardInterrupt
    try:
        with open("/path/to/your/api_key.txt", "r") as file: #EDIT HERE
            api_key = file.read().strip()

        # Taking a screenshot and encoding it
        screenshot_file = take_screenshot()
        base64_image = encode_image(screenshot_file)

        # Main loop to interact with the user
        while True:
            additional_text = "What’s in this image? Be concise and to the point"
            description = upload_image_and_get_description(base64_image, additional_text)
            typewrite("\nAI Response::\n" + description)
            
            # Input prompt for continuation or termination of the conversation
            user_input = input("\nYou:: ").strip().lower()
            if user_input == 'q':
                typewrite('BYENOW')
                break

    # Handling the KeyboardInterrupt exception
    except KeyboardInterrupt:
        typewrite('\nBYENOW')

# Entry point of the script
if __name__ == "__main__":
    main()

import os
import subprocess
import openai
import base64
import requests

# Global variables
api_key = ""
base64_image = ""

def take_screenshot():
    temp_file = "/tmp/screenshot.jpg"
    subprocess.run(["gnome-screenshot", "-a", "-f", temp_file])
    return temp_file

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def upload_image_and_get_description(base64_image, additional_text="What’s in this image in cyber security? Be somewhat brief"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

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
        "max_tokens": 200  # Customize here
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code}\n{response.text}"
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    global api_key, base64_image
    with open("/path/to/api_key.txt", "r") as file:
        api_key = file.read().strip()

    screenshot_file = take_screenshot()
    base64_image = encode_image(screenshot_file)

    additional_text = input("Enter your question (or press Enter for default): ").strip()
    if not additional_text:
        additional_text = "What’s in this image in cyber security? Be somewhat brief"

    description = upload_image_and_get_description(base64_image, additional_text)
    print("\nAI Response:\n" + description)

if __name__ == "__main__":
    main()

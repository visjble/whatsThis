import os
import subprocess
import openai
import base64
import requests

# Global variables
api_key = ""
base64_image = ""
conversation_id = None

def take_screenshot():
    temp_file = "/tmp/screenshot.jpg" # edit for your machine needs
    subprocess.run(["gnome-screenshot", "-a", "-f", temp_file])
    return temp_file

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def upload_image_and_get_description(base64_image, additional_text="What’s in this image? Be concised and to the point"):
    global conversation_id
    print('Quering gpt4-vision...')
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
        "max_tokens": 200
    }

    if conversation_id:
        payload["conversation_id"] = conversation_id

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

def main():
    global api_key, base64_image
    conversation = []  # List to store the entire conversation

    with open("/path/to/api_key.txt", "r") as file: #EDIT HERE FOR YOUR OPENAI KEY
        api_key = file.read().strip()

    screenshot_file = take_screenshot()
    base64_image = encode_image(screenshot_file)

    while True:
        additional_text = input("Enter your question (or press Enter for default): ").strip()
        if not additional_text:
            additional_text = "What’s in this image? Be concise and to the point"

        conversation.append(f"User: {additional_text}")  # Save user input to conversation
        description = upload_image_and_get_description(base64_image, additional_text)
        print("\nAI Response:\n" + description)
        conversation.append(f"AI: {description}")  # Save AI response to conversation

        # Option to continue or end the conversation
        user_input = input("\nAnything else? (press 'q' to quit): ").strip().lower()
        if user_input == 'q':
            break

    # Ask if the user wants to save the conversation. Comment if not needed
    if input("\nSave this conversation? (y/n): ").strip().lower() == 'y':
        save_path = input("Enter the full path to save the conversation (e.g., /home/user/conversation.txt): ").strip()
        try:
            with open(save_path, "w") as file:
                file.write("\n".join(conversation))
            print(f"Conversation saved to {save_path}.")
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")
    else:
        print('BYENOW')

if __name__ == "__main__":
    main()

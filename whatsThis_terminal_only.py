import os, time
import subprocess
import openai
import base64
import requests

# Global variables
api_key = ""
base64_image = ""
conversation_id = None
first_api_call = True


def mute_sound():
    # mutes the clicking sound produced by gnome-clipboard
    subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"])

def unmute_sound():
    # mutes the clicking sound produced by gnome-clipboard
    subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"])


def typewrite(text, delay=0.1): 
    # one can also do for char in text: etc... set.05 for typewriter
    words = text.split()
    for word in words:
        print(word, end=' ', flush=True)
        time.sleep(delay)
    print()  # for newline after the text


def take_screenshot():
    temp_file = "/tmp/screenshot.jpg" # customize per your needs
    mute_sound() # remove if not needed
    subprocess.run(["gnome-screenshot", "-a", "-f", temp_file])
    unmute_sound()
    return temp_file

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def upload_image_and_get_description(base64_image, additional_text):
    global conversation_id, first_api_call
    if first_api_call:
        additional_text = "What’s in this image? Be concised and to the point"
        typewrite('Querying gpt4-vision...')
        first_api_call = False  # Set the flag to False after the first call

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

    try:
        with open("/path/to/api_key.txt", "r") as file:
            api_key = file.read().strip()

        screenshot_file = take_screenshot()
        base64_image = encode_image(screenshot_file)

        # Initial query related to the image
        initial_text = "What’s in this image? Be concise and to the point"
        initial_description = upload_image_and_get_description(base64_image, initial_text)
        typewrite("\nAI Response::\n" + initial_description)

        while True:
        # Additional questions or user input
            user_input = input("\nYou:: ").strip().lower()

            if user_input in ['q', 'quit', 'exit']:
                print('-------\nBYENOW')
                break
            elif user_input == 's':
                # Take a new screenshot, encode it, and send to API
                screenshot_file = take_screenshot()
                base64_image = encode_image(screenshot_file)
                description = upload_image_and_get_description(base64_image, initial_text)
                print("Querying gpt4-vision")
                typewrite('AI Response::\n' + description)

            elif user_input in ['l']:  # Add an option for clearing the screen
                # Clear the screen (implementation depends on your system)
                os.system("clear")  # Example for Unix-based systems
            else:
                # Send the user's input as additional text for the conversation
                description = upload_image_and_get_description(base64_image, user_input)
                typewrite("\nAI Response::\n" + description)


    except KeyboardInterrupt:
        print('-------\n\nBYENOW')


if __name__ == "__main__":
    main()

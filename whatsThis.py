'''
2024 VISJBLE
python3: Specifies the desired Python interpreter (replace with the appropriate version if needed)
'''
#! /usr/bin/env python3
import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext
import openai
import base64
import requests

# Global variables
root = None
text_area = None
question_input = None
api_key = ""
base64_image = ""

def take_screenshot():
    temp_file = "/tmp/screenshot.jpg"
    subprocess.run(["gnome-screenshot", "-a", "-f", temp_file])
    return temp_file

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def upload_image_and_get_description(base64_image, additional_text="What’s in this image?"):
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
        "max_tokens": 10  # Customize here
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

def update_text(content):
    global text_area
    if text_area:
        text_area.configure(state='normal')
        text_area.delete('1.0', tk.END)
        text_area.insert(tk.INSERT, content)
        text_area.configure(state='disabled')

def quit_application():
    global root
    if root:
        root.destroy()

def handle_question():
    global base64_image
    new_question = question_input.get().strip()
    
    if new_question:  # Check if the question is not empty
        # Append the new question to the text_area
        text_area.configure(state='normal')
        text_area.insert(tk.END, f"\nMe: {new_question}\n")
        text_area.configure(state='disabled')

        # Get and display the response
        response = upload_image_and_get_description(base64_image, new_question)
        text_area.configure(state='normal')
        text_area.insert(tk.END, f"AI: {response}\n")
        text_area.configure(state='disabled')
        
        # Clear the input field after submitting the question
        question_input.delete(0, tk.END)


def initialize_gui(description):
    global root, text_area, question_input
    
    # Setting up the widgets
    root = tk.Tk()
    root.title("WhatsThis")

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
    text_area.pack(padx=5, pady=5)
    text_area.configure(state='disabled')
    update_text(description)

    question_input = tk.Entry(root, width=50)
    question_input.pack(padx=5, pady=5)
    question_input.bind('<Return>', lambda event: handle_question())  # Binding the Enter key

    quit_button = tk.Button(root, text="Quit", command=quit_application)
    quit_button.pack(side=tk.RIGHT,padx=5, pady=5)

    submit_button = tk.Button(root, text="Submit Question", command=handle_question)
    submit_button.pack(side=tk.RIGHT, padx=5, pady=5)

    # This updates the layout
    root.update_idletasks()

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Window size (you can adjust the size as needed)
    window_width = 500
    window_height = 300

    # Calculate x and y coordinates
    x = screen_width - window_width
    y = screen_height - window_height

    # Position the window at the bottom right of the screen
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    root.mainloop()

def main():
    global api_key, base64_image
    with open("/path/to/api_key.txt", "r") as file:  # EDIT THE PATH TO YOUR NEEDS
        api_key = file.read().strip()

    screenshot_file = take_screenshot()
    base64_image = encode_image(screenshot_file)
    description = upload_image_and_get_description(base64_image)
    initialize_gui(description)

if __name__ == "__main__":
    main()

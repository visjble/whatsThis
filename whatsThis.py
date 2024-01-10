'''
2024 VISJBLE
python3: Specifies the desired Python interpreter (replace with the appropriate version if needed)
'''

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

def upload_image_and_get_description(base64_image, additional_text="What’s in this image? No more than 20 words"):
    # EDIT additiona_text if needed
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

def update_text(content):
    global text_area
    if text_area:
        text_area.configure(state='normal')
        text_area.delete('1.0', tk.END)
        text_area.insert(tk.END, f"{content}\n")
        text_area.insert(tk.END, f"{'-' * 67}\n", "center")


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

        # Scroll to the end
        text_area.yview_moveto(1.0)

        # Get and display the response
        response = upload_image_and_get_description(base64_image, new_question)
        text_area.configure(state='normal')
        text_area.insert(tk.END, f"\nAI: {response}\n")
        text_area.insert(tk.END, '-' * 67 + '\n', 'center')
        text_area.configure(state='disabled')

        # Scroll to the end
        text_area.yview_moveto(1.0)
        
        # Clear the input field after submitting the question
        question_input.delete(0, tk.END)


def initialize_gui(description):
    global root, text_area, question_input

    # Setting up the widgets
    root = tk.Tk()
    root.title("WhatsThis")

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
    text_area.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
    text_area.configure(state='disabled')
    update_text(description)

    question_input = tk.Entry(root, width=50)
    question_input.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    question_input.bind('<Return>', lambda event: handle_question())  # Binding the Enter key

    quit_button = tk.Button(root, text="Quit", command=quit_application)
    quit_button.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    submit_button = tk.Button(root, text="Submit Question", command=handle_question)
    submit_button.grid(row=2, column=0, padx=5, pady=5, sticky="e")  # Centered horizontally

    # Configure grid to stretch properly
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)  # Make column 1 stretch too

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Window size (you can adjust the size as needed)
    window_width = 500
    window_height = 300

    # Calculate x and y coordinates
    x = screen_width - window_width
    y = screen_height - window_height + 600

    # Position the window at the bottom right of the screen
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    root.mainloop()


def main():
    global api_key, base64_image
    with open("/path/to/api_key.txt", "r") as file: #EDIT HERE
        api_key = file.read().strip()

    screenshot_file = take_screenshot()
    base64_image = encode_image(screenshot_file)
    description = upload_image_and_get_description(base64_image)
    initialize_gui(description)

if __name__ == "__main__":
    main()

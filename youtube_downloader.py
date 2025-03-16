import requests
from bs4 import BeautifulSoup
import json
import re
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time

def download_video(video_url, download_type, output_callback):
    """Downloads the video from the given URL using yt-dlp."""

    if download_type == 'v':
        format_arg = 'bv*[ext=mp4][height<=1080]+ba/b[ext=mp4]'
        format_sort_arg = '-S ext:webm:none'
    elif download_type == 'a':
        format_arg = 'ba[ext=m4a]/ba[ext=mp3]'
        format_sort_arg = '-S ares'
    else:
        output_callback("Invalid download type.\n")
        return

    command = [
        "yt-dlp",
        "-f", format_arg,
        format_sort_arg,
        "--no-playlist",
        "-o", "%(title)s.%(ext)s",
        video_url
    ]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                output_callback(output) # Call the callback immediately
        _, stderr = process.communicate()
        if stderr:
            output_callback(stderr)

    except subprocess.CalledProcessError as e:
        output_callback(f"Error downloading video:\n{e.stderr}\n")

def download_button_clicked(root, url_entry, download_type, output_text):
    """Handles the download button click event."""
    video_url = url_entry.get()
    download_type_str = 'v' if download_type.get() == 1 else 'a'
    output_text.insert(tk.END, f"Downloading: {video_url}\n")
    output_text.see(tk.END)
    root.update() # Force update
    
    def update_output(text):
        output_text.insert(tk.END, text)
        output_text.see(tk.END)
        root.update()  # Force GUI update after each insert

    download_video(video_url, download_type_str, update_output)
    output_text.insert(tk.END, "Download Success!\n")
    output_text.see(tk.END)
    root.update()
    # Clear text after 3 seconds and also clear the URL entry
    root.after(3000, lambda: (output_text.delete("1.0", tk.END), url_entry.delete(0, tk.END)))

def check_ffmpeg():
    """Check if FFmpeg is available in the system PATH"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def create_gui():
    """Creates the Tkinter GUI."""
    root = tk.Tk()
    root.title("YouTube Downloader")

    # Check FFmpeg availability
    if not check_ffmpeg():
        tk.messagebox.showerror(
            "FFmpeg Not Found", 
            "FFmpeg is required but not found in system PATH.\n"
            "Please install FFmpeg from https://ffmpeg.org/download.html"
        )

    # URL Entry
    url_label = ttk.Label(root, text="YouTube URL:")
    url_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    url_entry = ttk.Entry(root, width=50)
    url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)

    # Download Type (Radio Buttons)
    download_type = tk.IntVar(value=1)  # 1 for video, 2 for audio
    video_radio = ttk.Radiobutton(root, text="Video", variable=download_type, value=1)
    video_radio.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    audio_radio = ttk.Radiobutton(root, text="Audio", variable=download_type, value=2)
    audio_radio.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    # Download Button
    download_button = ttk.Button(root, text="Download", command=lambda: download_button_clicked(root, url_entry, download_type, output_text))
    download_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    # Output Text Area
    output_text = scrolledtext.ScrolledText(root, width=60, height=10)
    output_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
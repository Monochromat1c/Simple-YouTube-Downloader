import requests
from bs4 import BeautifulSoup
import json
import re
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import time
import os
from typing import List, Tuple

def get_downloads_folder():
    """Get the default downloads folder path"""
    return os.path.join(os.path.expanduser("~"), "Downloads")

def get_available_formats(video_url) -> List[Tuple[str, str]]:
    """Gets available MP4 video formats and returns list of (resolution, format_id) tuples"""
    try:
        # Add startupinfo to hide console window
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        command = [
            "yt-dlp",
            "-j",
            "--no-playlist",
            video_url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, startupinfo=startupinfo)
        video_info = json.loads(result.stdout)
        
        formats = []
        seen_resolutions = set()
        
        # Get all MP4 video formats
        for fmt in video_info.get('formats', []):
            if fmt.get('ext') == 'mp4' and fmt.get('vcodec') != 'none':
                height = fmt.get('height')
                if height and height not in seen_resolutions:
                    seen_resolutions.add(height)
                    formats.append((f"{height}p", fmt['format_id']))
        
        # Sort by resolution (highest first)
        formats.sort(key=lambda x: int(x[0][:-1]), reverse=True)
        return formats
    
    except Exception as e:
        print(f"Error getting formats: {e}")
        return []

def download_video(video_url, download_type, output_callback, download_path, update_progress_callback, resolution_id=None):
    """Downloads the video, updates progress, and sends output to callback."""
    if download_type == 'v':
        if resolution_id:
            format_arg = f'{resolution_id}+ba/b[ext=mp4]'
        else:
            format_arg = 'bv*[ext=mp4][height<=1080]+ba/b[ext=mp4]'
        format_sort_arg = '-S ext:webm:none'
    elif download_type == 'a':
        format_arg = 'ba[ext=m4a]/ba[ext=mp3]'
        format_sort_arg = '-S ares'
    else:
        output_callback("Invalid download type.\n")
        return

    # Create output template with download path
    output_template = os.path.join(download_path, "%(title)s.%(ext)s")

    command = [
        "yt-dlp",
        "-f", format_arg,
        format_sort_arg,
        "--no-playlist",
        "-o", output_template,
        video_url
    ]

    try:
        # Add startupinfo to hide console window
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=startupinfo
        )

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Extract percentage using regex
                match = re.search(r'\[download\]\s+([\d.]+)%', output)
                if match:
                    try:
                        percentage = float(match.group(1))
                        update_progress_callback(percentage)  # Update progress bar
                    except ValueError:
                        pass  # Ignore if parsing fails
                output_callback(output) # Still output to scrolled text

        _, stderr = process.communicate()
        if stderr:
            output_callback(stderr)


    except subprocess.CalledProcessError as e:
        output_callback(f"Error downloading video:\n{e.stderr}\n")
    except Exception as e:
        output_callback(f"An unexpected error occurred: {e}\n")

def select_directory(current_path_var):
    """Open directory selection dialog"""
    dir_path = filedialog.askdirectory(initialdir=current_path_var.get())
    if dir_path:  # If a directory was selected
        current_path_var.set(dir_path)

def url_changed(event, url_entry, res_dropdown, download_type, root):
    """Handle URL entry changes"""
    url = url_entry.get()
    if url.strip():
        # Clear existing options
        res_dropdown['values'] = []
        res_dropdown.set('')
        
        if download_type.get() == 1:  # Only for video downloads
            # Get available formats
            formats = get_available_formats(url)
            if formats:
                # Add "Auto (up to 1080p)" option at the beginning
                formats = [("Auto (up to 1080p)", "")] + formats
                # Update dropdown values
                res_dropdown['values'] = [f[0] for f in formats]
                res_dropdown.format_ids = {f[0]: f[1] for f in formats}
                res_dropdown.set("Auto (up to 1080p)")
            else:
                res_dropdown['values'] = ["Auto (up to 1080p)"]
                res_dropdown.set("Auto (up to 1080p)")

def download_button_clicked(root, url_entry, download_type, output_text, download_path_var, progress_var, res_dropdown):
    """Handles download button, updates progress, and manages output."""
    video_url = url_entry.get()
    download_type_str = 'v' if download_type.get() == 1 else 'a'
    
    # Get selected resolution format_id
    resolution_id = None
    if download_type_str == 'v' and hasattr(res_dropdown, 'format_ids'):
        selected_res = res_dropdown.get()
        resolution_id = res_dropdown.format_ids.get(selected_res, None)
    
    output_text.insert(tk.END, f"Downloading to: {download_path_var.get()}\n")
    output_text.insert(tk.END, f"Downloading: {video_url}\n")
    output_text.see(tk.END)
    root.update()

    def update_output(text):
        output_text.insert(tk.END, text)
        output_text.see(tk.END)
        root.update()

    def update_progress(percentage):
        progress_var.set(percentage)
        root.update_idletasks()

    download_video(video_url, download_type_str, update_output, download_path_var.get(), 
                  update_progress, resolution_id)
    progress_var.set(0)
    output_text.insert(tk.END, "Download Success!\n")
    output_text.see(tk.END)
    root.update()
    root.after(2000, lambda: (output_text.delete("1.0", tk.END), url_entry.delete(0, tk.END)))

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
    
    # Set window icon using sys._MEIPASS for PyInstaller
    try:
        import sys
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(base_path, 'assets', 'icon', 'icon.ico')
        root.iconbitmap(icon_path)
    except:
        # If icon loading fails, continue without icon
        pass
    
    # Make window stay on top and prevent resizing
    # root.attributes('-topmost', True)
    root.resizable(False, False)

    # Change title bar color (Windows 11 only)
    try:
        from ctypes import windll, c_int, byref, sizeof
        HWND = windll.user32.GetParent(root.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(
            HWND,
            35,  # DWMWA_CAPTION_COLOR
            byref(c_int(0x00382515)),  # RGB(21, 37, 56) -> BGR format
            sizeof(c_int)
        )
    except:
        pass  # Fail silently if not on Windows 11 or if it doesn't work

    # Check FFmpeg availability
    if not check_ffmpeg():
        tk.messagebox.showerror(
            "FFmpeg Not Found", 
            "FFmpeg is required but not found in system PATH.\n"
            "Please install FFmpeg from https://ffmpeg.org/download.html"
        )

    # Download Path
    download_path_var = tk.StringVar(value=get_downloads_folder())
    path_frame = ttk.Frame(root)
    path_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    
    path_label = ttk.Label(path_frame, text="Download Location:")
    path_label.pack(side=tk.LEFT, padx=(0, 5))
    
    path_entry = ttk.Entry(path_frame, textvariable=download_path_var, width=40)
    path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    browse_button = ttk.Button(path_frame, text="Browse", 
                             command=lambda: select_directory(download_path_var))
    browse_button.pack(side=tk.RIGHT, padx=(5, 0))

    # URL Entry and Download Button Frame
    url_button_frame = ttk.Frame(root)
    url_button_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    # URL Entry
    url_label = ttk.Label(url_button_frame, text="YouTube URL:")
    url_label.pack(side=tk.LEFT, padx=(0, 5))
    url_entry = ttk.Entry(url_button_frame, width=50)
    url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Progress Bar (added here)
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    # Download Button
    download_button = ttk.Button(
        url_button_frame,
        text="Download",
        command=lambda: download_button_clicked(
            root, url_entry, download_type, output_text, download_path_var, progress_var, res_dropdown
        )
    )
    download_button.pack(side=tk.LEFT, padx=(5,0))

    # Download Type (Radio Buttons)
    radio_frame = ttk.Frame(root)
    radio_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
    
    download_type = tk.IntVar(value=1)  # 1 for video, 2 for audio
    video_radio = ttk.Radiobutton(radio_frame, text="Video", variable=download_type, value=1)
    video_radio.pack(side=tk.LEFT)
    audio_radio = ttk.Radiobutton(radio_frame, text="Audio", variable=download_type, value=2)
    audio_radio.pack(side=tk.LEFT, padx=(10, 0))  # 10 pixels space between radio buttons

    # Add Resolution Dropdown after radio buttons
    res_frame = ttk.Frame(root)
    res_frame.grid(row=2, column=1, padx=5, pady=5, sticky="e")
    
    res_label = ttk.Label(res_frame, text="Resolution:")
    res_label.pack(side=tk.LEFT, padx=(0, 5))
    
    res_dropdown = ttk.Combobox(res_frame, width=15, state="readonly")
    res_dropdown['values'] = ["Auto (up to 1080p)"]
    res_dropdown.set("Auto (up to 1080p)")
    res_dropdown.pack(side=tk.LEFT)

    # Bind URL entry changes
    url_entry.bind('<KeyRelease>', lambda e: url_changed(e, url_entry, res_dropdown, download_type, root))

    # Output Text Area
    output_text = scrolledtext.ScrolledText(root, width=60, height=10)
    output_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
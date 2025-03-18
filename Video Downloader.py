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
import threading
from queue import Queue

def get_downloads_folder():
    """Get the default downloads folder path"""
    return os.path.join(os.path.expanduser("~"), "Downloads")

class LoadingIndicator:
    def __init__(self, parent, text="Loading..."):
        # Create a transparent overlay window instead of a frame
        self.overlay = tk.Toplevel(parent)
        self.overlay.withdraw()  # Hide initially to prevent flicker
        
        # Remove window decorations
        self.overlay.overrideredirect(True)
        self.overlay.attributes('-topmost', True)
        self.overlay.attributes('-alpha', 0.3)  # 30% opacity
        
        # Configure background
        self.overlay.configure(bg='gray')
        
        # Function to update overlay position and size
        def update_overlay():
            x = parent.winfo_rootx()
            y = parent.winfo_rooty()
            w = parent.winfo_width()
            h = parent.winfo_height()
            self.overlay.geometry(f"{w}x{h}+{x}+{y}")
        
        # Update position initially
        parent.update_idletasks()  # Ensure parent geometry is up to date
        update_overlay()
        
        # Bind to parent movement to keep overlay aligned
        parent.bind('<Configure>', lambda e: update_overlay())
        
        # Show the overlay
        self.overlay.deiconify()
        self.overlay.lift()
        
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        
        # Configure border and background
        self.window.configure(bg='black')  # Border color
        
        # Create inner frame for content with margin (acting as border)
        self.border_frame = tk.Frame(self.window, bg='#f0f0f0', padx=1, pady=1)
        self.border_frame.pack(expand=True, fill='both', padx=1, pady=1)
        
        # Make window size fixed
        self.window.grid_propagate(False)
        self.window.geometry("400x80")
        
        # Store original position
        self.parent_x = parent.winfo_x()
        self.parent_y = parent.winfo_y()
        
        # Disable parent window movement
        self.parent.bind('<Configure>', lambda e: self.prevent_move(e))
        
        # Center the window
        self.center_window()
        
        # Create main frame
        self.frame = ttk.Frame(self.border_frame)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Add loading text
        self.label = ttk.Label(
            self.frame,
            text="Fetching available resolution. Please wait.",
            font=('Segoe UI', 10)
        )
        self.label.pack(pady=(0, 10))
        
        # Create canvas for spinner
        self.canvas = tk.Canvas(
            self.frame,
            width=30,
            height=30,
            bg='#f0f0f0',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Create spinner circle
        self.spinner = self.canvas.create_arc(
            5, 5, 25, 25,
            start=0,
            extent=300,
            width=2,
            style=tk.ARC,
            outline='black'
        )
        
        # Add rounded corners (Windows only)
        try:
            from ctypes import windll, byref, sizeof, c_int
            HWND = windll.user32.GetParent(self.window.winfo_id())
            windll.dwmapi.DwmSetWindowAttribute(
                HWND,
                33,  # DWMWA_WINDOW_CORNER_PREFERENCE
                byref(c_int(2)),  # DWMWCP_ROUND
                sizeof(c_int)
            )
        except:
            pass
        
        self.window.lift()
        self.angle = 0
        self.animate_spinner()
    
    def center_window(self):
        """Center the loading window relative to parent"""
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - 400) // 2
        y = parent_y + (parent_height - 80) // 2
        
        self.window.geometry(f"+{x}+{y}")
    
    def prevent_move(self, event):
        """Prevent parent window from moving"""
        if event.widget == self.parent:
            self.parent.geometry(f'+{self.parent_x}+{self.parent_y}')
    
    def animate_spinner(self):
        """Animate the spinning loader"""
        self.angle = (self.angle + 10) % 360
        self.canvas.itemconfig(
            self.spinner,
            start=self.angle
        )
        self.animation_id = self.window.after(20, self.animate_spinner)
        
    def destroy(self):
        """Clean up and destroy the window"""
        if hasattr(self, 'animation_id'):
            self.window.after_cancel(self.animation_id)
        # Unbind parent events
        self.parent.unbind('<Configure>')
        self.parent.unbind('<Unmap>')
        self.parent.unbind('<Map>')
        # Just remove the overlay
        self.overlay.destroy()
        self.window.destroy()

def get_available_formats(video_url, result_queue: Queue, format_type='v') -> List[Tuple[str, str]]:
    """Gets available formats and returns list of (quality, format_id) tuples"""
    try:
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
        seen_qualities = set()
        
        for fmt in video_info.get('formats', []):
            if format_type == 'v':
                if fmt.get('ext') == 'mp4' and fmt.get('vcodec') != 'none':
                    height = fmt.get('height')
                    if height and height not in seen_qualities:
                        seen_qualities.add(height)
                        formats.append((f"{height}p", fmt['format_id']))
            else:  # audio formats
                # Check for audio-only formats or formats with audio
                if fmt.get('acodec') != 'none':
                    # Get audio quality indicators
                    abr = fmt.get('abr', 0)  # audio bitrate
                    asr = fmt.get('asr', 0)  # audio sample rate
                    
                    # Create quality string
                    quality = ""
                    if abr:
                        quality = f"{int(abr)}kbps"
                    elif asr:
                        quality = f"{int(asr/1000)}kHz"
                    else:
                        continue  # Skip if no quality info
                        
                    if quality and quality not in seen_qualities:
                        seen_qualities.add(quality)
                        formats.append((quality, fmt['format_id']))
        
        if format_type == 'v':
            formats.sort(key=lambda x: int(x[0][:-1]), reverse=True)  # Sort video by height
        else:
            # Sort audio by bitrate/frequency (removing 'kbps' or 'kHz' and converting to int)
            formats.sort(key=lambda x: int(x[0][:-4]), reverse=True)
            
        result_queue.put(('success', formats))
    
    except Exception as e:
        result_queue.put(('error', str(e)))

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
    
    # Clear existing options
    res_dropdown['values'] = []
    res_dropdown.set('')
    
    if url.strip() and download_type.get() == 1:  # Only for video downloads with non-empty URL
        loading = LoadingIndicator(root, "Fetching available formats")
        result_queue = Queue()
        
        def fetch_formats():
            get_available_formats(url, result_queue)
            
        def check_queue():
            try:
                if not result_queue.empty():
                    status, data = result_queue.get()
                    loading.destroy()
                    
                    if status == 'success':
                        formats = data
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
                    else:
                        messagebox.showerror("Error", f"Failed to fetch formats: {data}")
                        res_dropdown['values'] = ["Auto (up to 1080p)"]
                        res_dropdown.set("Auto (up to 1080p)")
                else:
                    root.after(100, check_queue)
            except tk.TkError:
                # Handle case where window was closed during loading
                pass
                
        # Start the background thread
        thread = threading.Thread(target=fetch_formats, daemon=True)
        thread.start()
        
        # Start checking for results
        root.after(100, check_queue)

def download_button_clicked(root, url_entry, download_type, output_text, download_path_var, progress_var, res_dropdown):
    """Handles download button, updates progress, and manages output."""
    video_url = url_entry.get()
    download_type_str = 'v' if download_type.get() == 1 else 'a'
    
    # Get selected resolution format_id
    resolution_id = None
    if download_type_str == 'v' and hasattr(res_dropdown, 'format_ids'):
        selected_res = res_dropdown.get()
        resolution_id = res_dropdown.format_ids.get(selected_res, None)
    
    output_text.configure(state="normal")
    output_text.insert(tk.END, f"Downloading to: {download_path_var.get()}\n")
    output_text.insert(tk.END, f"Downloading: {video_url}\n")
    output_text.see(tk.END)
    output_text.configure(state="disabled")
    root.update()

    def update_output(text):
        output_text.configure(state="normal")
        output_text.insert(tk.END, text)
        output_text.see(tk.END)
        output_text.configure(state="disabled")
        root.update()

    def update_progress(percentage):
        progress_var.set(percentage)
        root.update_idletasks()

    download_video(video_url, download_type_str, update_output, download_path_var.get(), 
                  update_progress, resolution_id)
    progress_var.set(0)
    output_text.configure(state="normal")
    output_text.insert(tk.END, "Download Success!\n")
    output_text.see(tk.END)
    output_text.configure(state="disabled")
    root.update()
    
    # Get reference to download button
    download_button = None
    for widget in url_entry.master.winfo_children():
        if isinstance(widget, ttk.Button) and widget['text'] == 'Download':
            download_button = widget
            break
            
    # Clear everything after 2 seconds
    def clear_all():
        output_text.configure(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.configure(state="disabled")
        url_entry.delete(0, tk.END)
        res_dropdown['values'] = ["Auto (up to 1080p only)"]
        res_dropdown.set("Auto (up to 1080p only)")
        if download_button:
            download_button.configure(state='disabled')
            
    root.after(2000, clear_all)

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
    root.title("Video Downloader")
    
    root.resizable(False, False)  # Keep this
    
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
    url_label = ttk.Label(url_button_frame, text="Video URL:")
    url_label.pack(side=tk.LEFT, padx=(0, 5))
    url_entry = ttk.Entry(url_button_frame, width=50)
    url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Check Button (new)
    check_button = ttk.Button(
        url_button_frame,
        text="Check",
        command=lambda: check_url(url_entry, res_dropdown, download_type, root)
    )
    check_button.pack(side=tk.LEFT, padx=(5,0))

    # Download Button
    download_button = ttk.Button(
        url_button_frame,
        text="Download",
        command=lambda: download_button_clicked(
            root, url_entry, download_type, output_text, download_path_var, progress_var, res_dropdown
        ),
        state="disabled"  # Disable button by default
    )
    download_button.pack(side=tk.LEFT, padx=(5,0))

    # Progress Bar (added here)
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    # Download Type (Radio Buttons)
    radio_frame = ttk.Frame(root)
    radio_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
    
    download_type = tk.IntVar(value=1)  # 1 for video, 2 for audio
    
    # Add radio button callback
    def on_radio_change():
        is_video = download_type.get() == 1
        default_text = "Auto (up to 1080p only)" if is_video else "Auto (best quality)"
        # Update dropdown text
        res_dropdown['values'] = [default_text]
        res_dropdown.set(default_text)
        # Update label text
        res_label.configure(text="Resolution:" if is_video else "Quality:")
        
        # Reset download button state
        for widget in url_entry.master.winfo_children():
            if isinstance(widget, ttk.Button) and widget['text'] == 'Download':
                widget.configure(state='disabled')
                break
        
        # Clear format IDs if they exist
        if hasattr(res_dropdown, 'format_ids'):
            delattr(res_dropdown, 'format_ids')
    
    video_radio = ttk.Radiobutton(radio_frame, text="Video", variable=download_type, value=1, 
                                 command=on_radio_change)
    video_radio.pack(side=tk.LEFT)
    audio_radio = ttk.Radiobutton(radio_frame, text="Audio", variable=download_type, value=2,
                                 command=on_radio_change)
    audio_radio.pack(side=tk.LEFT, padx=(10, 0))  # 10 pixels space between radio buttons

    # Add Resolution Dropdown after radio buttons
    res_frame = ttk.Frame(root)
    res_frame.grid(row=2, column=1, padx=5, pady=5, sticky="e")
    
    res_label = ttk.Label(res_frame, text="Resolution:")
    res_label.pack(side=tk.LEFT, padx=(0, 5))
    
    res_dropdown = ttk.Combobox(res_frame, width=20, state="readonly")
    res_dropdown['values'] = ["Auto (up to 1080p only)"]  # Default for video
    res_dropdown.set("Auto (up to 1080p only)")
    res_dropdown.pack(side=tk.LEFT)

    # Output Text Area
    output_text = scrolledtext.ScrolledText(root, height=10, state="disabled")
    output_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    root.mainloop()

def check_url(url_entry, res_dropdown, download_type, root):
    """Handle Check button click"""
    url = url_entry.get()
    format_type = 'v' if download_type.get() == 1 else 'a'
    
    # Clear existing options
    res_dropdown['values'] = []
    res_dropdown.set('')
    
    # Update resolution label based on format type
    for widget in res_dropdown.master.winfo_children():
        if isinstance(widget, ttk.Label):
            widget.configure(text="Resolution:" if format_type == 'v' else "Quality:")
    
    # Get reference to download button
    download_button = None
    for widget in url_entry.master.winfo_children():
        if isinstance(widget, ttk.Button) and widget['text'] == 'Download':
            download_button = widget
            break
    
    # Disable download button when starting new check
    if download_button:
        download_button.configure(state='disabled')
    
    if url.strip():  # Check URL for both video and audio
        loading = LoadingIndicator(root, "Fetching available formats")
        result_queue = Queue()
        
        def fetch_formats():
            get_available_formats(url, result_queue, format_type)
            
        def check_queue():
            try:
                if not result_queue.empty():
                    status, data = result_queue.get()
                    loading.destroy()
                    
                    if status == 'success':
                        formats = data
                        if formats:
                            # Add auto option at beginning
                            auto_text = "Auto (up to 1080p only)" if format_type == 'v' else "Auto (best quality)"
                            formats = [(auto_text, "")] + formats
                            # Update dropdown values
                            res_dropdown['values'] = [f[0] for f in formats]
                            res_dropdown.format_ids = {f[0]: f[1] for f in formats}
                            res_dropdown.set(auto_text)
                            # Enable download button on successful fetch
                            if download_button:
                                download_button.configure(state='normal')
                        else:
                            default_text = "Auto (up to 1080p only)" if format_type == 'v' else "Auto (best quality)"
                            res_dropdown['values'] = [default_text]
                            res_dropdown.set(default_text)
                    else:
                        messagebox.showerror("Error", f"Failed to fetch formats: {data}")
                        default_text = "Auto (up to 1080p only)" if format_type == 'v' else "Auto (best quality)"
                        res_dropdown['values'] = [default_text]
                        res_dropdown.set(default_text)
                else:
                    root.after(100, check_queue)
            except tk.TkError:
                # Handle case where window was closed during loading
                pass
                
        # Start the background thread
        thread = threading.Thread(target=fetch_formats, daemon=True)
        thread.start()
        
        # Start checking for results
        root.after(100, check_queue)

if __name__ == "__main__":
    create_gui()
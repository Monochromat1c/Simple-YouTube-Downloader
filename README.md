# YouTube Downloader

This script allows you to download YouTube videos and audio.

## Dependencies

This project uses the following dependencies:

*   **yt-dlp:** The core library for downloading videos.
*   **ffmpeg (Optional but Recommended):** For improved audio/video quality.

## Installation

1.  **Install Python packages:**

    ```bash
    pip install yt-dlp
    ```

2.  **Install ffmpeg (Optional):**

    *   **Windows:** The recommended way is using Chocolatey:
        1.  Install Chocolatey: Open PowerShell as Administrator and run:

            ```powershell
            Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            ```
        2.  Install ffmpeg: Close and reopen PowerShell (as Administrator), then run:

            ```powershell
            choco install ffmpeg -y
            ```
    *   **macOS:** The recommended way is using Homebrew:
        1. Install Homebrew (if you don't have it):
           ```bash
           /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
           ```
        2. Install ffmpeg:
           ```bash
           brew install ffmpeg
           ```
    *   **Linux (Debian/Ubuntu):**
        ```bash
        sudo apt update
        sudo apt install ffmpeg
        ```
    *   **Linux (Fedora/CentOS/RHEL):**
        ```bash
        sudo dnf install ffmpeg
        ```

## Running the Application

### Method 1: Running from Source
```bash
python youtube_downloader.py
```

### Method 2: Using the Executable
1. Download the latest release
2. Make sure FFmpeg is installed on your system
3. Run the executable file

The application will provide a simple GUI where you can:
- Enter a YouTube URL
- Choose between video or audio download
- Click Download to start the process

## Building the Executable
To build the executable yourself:

1. Install the required packages:
   ```bash
   pip install pyinstaller yt-dlp
   ```

2. Run the build script:
   ```
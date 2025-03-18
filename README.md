# Video Downloader

This script allows you to download videos and audios from websites.

## Dependencies

This project uses the following dependencies:

*   **yt-dlp:** The core library for downloading videos.
*   **ffmpeg (Optional but Recommended):** For improved audio/video quality.

## Installation

1.  **Install Python packages:**

    ```bash
    pip install yt-dlp requests bs4 pyinstaller
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
- Enter a video URL
- Choose between video or audio download
- Click Download to start the process

## Building the Executable
To build the executable yourself:

1. Install the required packages:
   ```bash
   pip install pyinstaller yt-dlp requests bs4
   ```

2. Run the build script:
   ```bash
   python build.py
   ```

## Antivirus Warning

Some browsers or antivirus software may flag the downloaded executable as suspicious. This is a false positive due to how PyInstaller packages Python applications into executables. PyInstaller bundles Python code and dependencies into a single executable file, which can trigger antivirus heuristic detection patterns.

> **Important Note:** If you scan this executable on VirusTotal, it WILL be flagged as suspicious/malware. This is a known issue with PyInstaller-generated executables and does NOT indicate actual malware. PyInstaller bundles all dependencies into a single file, which often triggers false positives in antivirus scanners.

These false positives are common for PyInstaller-generated executables and do not indicate actual malware. To verify the safety of the application, you can:

1. Download the source code and build it yourself (recommended)
2. Add an exception in your antivirus software
3. Compare the file hash with the one provided in our releases
4. Review the source code in this repository

The application is open-source, and you can review all the code in this repository. If you're concerned about security, we recommend building the executable yourself from the source code.

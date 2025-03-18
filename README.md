# Video Downloader

This script allows you to download videos and audios from websites.

## Dependencies

This project uses the following dependencies:

*   **yt-dlp:** The core library for downloading videos.
*   **ffmpeg (Optional but Recommended):** For improved audio/video quality.

## Installation

1.  **Install Python packages:**

    ```bash
    pip install yt-dlp requests bs4 nuitka
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
   python -m pip install nuitka yt-dlp requests bs4
   ```

2. Run the build command:
   ```bash
   python -m nuitka --onefile --enable-plugin=tk-inter "Video Downloader.py"
   ```

   This command will:
   - Create a single executable file (--onefile)
   - Include the necessary Tkinter dependencies (--enable-plugin=tk-inter)
   - Generate the executable in the output directory

The executable will be generated using Nuitka, which creates more efficient and reliable executables compared to other Python compilers. Nuitka compiles Python code directly to standalone executables, resulting in better performance and fewer false positives from antivirus software.

## Note About Executables

The application executable is built using Nuitka, a Python compiler that converts Python code into standalone executables. Unlike other packaging methods, Nuitka-generated executables are less likely to trigger false positives in antivirus software while providing better performance.

If you prefer to verify the safety of the application, you can:

1. Download the source code and build it yourself
2. Compare the file hash with the one provided in our releases
3. Verify the executable on [VirusTotal](https://www.virustotal.com)

The application is open-source, and you can review all the code in this repository.

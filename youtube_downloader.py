import requests
from bs4 import BeautifulSoup
import json
import re
import subprocess  # Importing the subprocess module

def get_user_input():
    """Gets the YouTube video URL from the user."""
    return input("Enter the YouTube video URL: ")

def download_video(video_url, download_type):
    """Downloads the video from the given URL using yt-dlp."""

    if download_type == 'v':
        format_arg = 'bv*[ext=mp4][height<=1080]+ba/b[ext=mp4]'  # Prioritize MP4, then 1080p
        format_sort_arg = '-S ext:webm:none'
    elif download_type == 'a':
        format_arg = 'ba[ext=m4a]/ba[ext=mp3]'
        format_sort_arg = '-S ares'
    else:
        print("Invalid download type.")
        return

    command = [
        "yt-dlp",
        "-f", format_arg,
        format_sort_arg,
        "--no-playlist",  # Don't download the entire playlist if the URL is part of one
        "-o", "%(title)s.%(ext)s",  # Output template
        video_url
    ]

    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        print(process.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video:\n{e.stderr}")


def main():
    """Main function to run the YouTube scraper."""
    video_url = get_user_input()
    print(f"You entered: {video_url}")

    download_type = input("Download as (v)ideo or (a)udio? [v/a]: ").lower()
    while download_type not in ('v', 'a'):
        download_type = input("Invalid choice. Download as (v)ideo or (a)udio? [v/a]: ").lower()

    download_video(video_url, download_type)


if __name__ == "__main__":
    main()
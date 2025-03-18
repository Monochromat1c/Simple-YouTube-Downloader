import os
import site
import subprocess
import sys

def find_ytdlp():
    # Get the scripts directory
    if hasattr(site, 'getsitepackages'):
        paths = site.getsitepackages()
    else:
        paths = [site.getusersitepackages()]
    
    # Add Scripts directory to paths
    scripts_dir = os.path.join(os.path.dirname(sys.executable), 'Scripts')
    paths.append(scripts_dir)
    
    # Look for yt-dlp executable
    for path in paths:
        ytdlp_path = os.path.join(path, 'yt-dlp.exe')
        if os.path.exists(ytdlp_path):
            return ytdlp_path
    
    return None

def build_exe():
    ytdlp_path = find_ytdlp()
    if not ytdlp_path:
        print("Error: Could not find yt-dlp.exe")
        return

    icon_path = os.path.join('assets', 'icon', 'icon.ico')
    
    command = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        f'--icon={icon_path}',
        f'--add-binary={ytdlp_path};.',
        f'--add-data={icon_path};assets/icon',
        '--clean',
        '--noupx',
        '--disable-windowed-traceback',
        'Video Downloader.py'
    ]
    
    print(f"Building with yt-dlp from: {ytdlp_path}")
    subprocess.run(command)

if __name__ == "__main__":
    build_exe() 
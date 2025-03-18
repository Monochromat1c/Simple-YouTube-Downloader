import os
import site
import subprocess
import sys
import shutil

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

def cleanup_build_files():
    # Move the executable to root directory
    exe_path = os.path.join('dist', 'Video Downloader.exe')
    if os.path.exists(exe_path):
        shutil.move(exe_path, 'Video Downloader.exe')
        print("Moved executable to root directory")
    
    # Delete build and dist folders
    folders_to_delete = ['build', 'dist']
    for folder in folders_to_delete:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Deleted {folder} folder")
    
    # Delete spec file
    spec_file = 'Video Downloader.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print("Deleted spec file")

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
    
    # Clean up after successful build
    cleanup_build_files()

if __name__ == "__main__":
    build_exe() 
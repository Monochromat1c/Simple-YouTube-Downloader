# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['youtube_downloader.py'],
    pathex=[],
    binaries=[('C:\\Users\\Charles\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\yt-dlp.exe', '.')],
    datas=[('assets\\icon\\icon.ico', 'assets/icon')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='youtube_downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icon\\icon.ico'],
)

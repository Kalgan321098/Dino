# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['t-rex.py'],
    pathex=[],
    binaries=[],
    datas=[('background.png', '.'), ('game_over.png', '.'), ('dino-0.png', '.'), ('dino-1.png', '.'), ('dino-2.png', '.'), ('bird1.png', '.'), ('bird2.png', '.'), ('bird3.png', '.'), ('bird4.png', '.'), ('kaktus.png', '.'), ('kaktus2.png', '.'), ('kaktus3.png', '.'), ('Subway_Surfers.mp3', '.'), ('dark-souls.mp3', '.'), ('jump.mp3', '.'), ('coin.mp3', '.'), ('speed.mp3', '.')],
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
    name='T-Rex Game',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)

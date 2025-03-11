# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Game.py'],
    pathex=[],
    binaries=[],
    datas=[('question.ogg', '.'), ('dead.ogg', '.'), ('mobdie.ogg', '.'), ('collectheart.ogg', '.'), ('music.ogg', '.'), ('background.png', '.'), ('level1bg.png', '.'), ('level2bg.png', '.'), ('level3bg.png', '.'), ('heart.png', '.'), ('boxy-bold.ttf', '.'), ('Soldier-Idle.png', '.'), ('Soldier-Walk.png', '.'), ('Orc-Idle.png', '.'), ('Orc-Walk.png', '.'), ('idle', 'idle'), ('run', 'run'), ('1_atk', '1_atk'), ('menu.png', '.')],
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
    name='Game',
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
)

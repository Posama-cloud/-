# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['maincharacter.py'],
    pathex=[],
    binaries=[],
    datas=[('image_0.png', '.')],
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
    [],
    exclude_binaries=True,
    name='久坐提醒助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='image_0.png',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='久坐提醒助手.app',
)
app = BUNDLE(
    coll,
    name='久坐提醒助手.app',
    icon='image_0.png',
    bundle_identifier='com.yourname.sedentary-reminder',
)

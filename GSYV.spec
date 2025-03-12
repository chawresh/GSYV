# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['GSYV.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/chawresh/Desktop/files', 'files')],
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
    name='GSYV',
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
    icon=['/Users/chawresh/Desktop/logo.icns'],
)
app = BUNDLE(
    exe,
    name='GSYV.app',
    icon='/Users/chawresh/Desktop/logo.icns',
    bundle_identifier=None,
)

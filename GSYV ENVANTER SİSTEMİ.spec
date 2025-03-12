import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['GSYV ENVANTER SİSTEMİ.py'],
             pathex=['/Users/chawresh/Desktop'],
             binaries=[],
             datas=[('/Users/chawresh/Desktop/files', 'files')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=["PyQt6", "PySide6"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='GSYV ENVANTER SİSTEMİ',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='/Users/chawresh/Desktop/files/logo.icns')





pyinstaller -F -w --add-data "/Users/chawresh/Desktop/files:files" --icon "/Users/chawresh/Desktop/logo.icns" --name "GSYV" GSYV.py
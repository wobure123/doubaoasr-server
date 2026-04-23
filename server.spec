# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 完整收集这些包的所有文件（含原生扩展）
datas_extra, binaries_extra, hiddenimports_extra = [], [], []
for pkg in ['doubaoime_asr', 'cffi','opuslib', 'aiohttp']:
    d, b, h = collect_all(pkg)
    datas_extra += d
    binaries_extra += b
    hiddenimports_extra += h

a = Analysis(
    ['src/server.py'],
    pathex=['.'],
    binaries=binaries_extra,
    datas=datas_extra,
    hiddenimports=hiddenimports_extra + [
        '_cffi_backend',
        'cffi',
        'doubaoime_asr',
        'asyncio',
        'aiohttp',
        'websockets',
        'google.protobuf',
        'google.protobuf.descriptor',
        'google.protobuf.descriptor_pool',
        'google.protobuf.message',
        'ctypes',
        'ctypes.util',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='doubaoime-asr-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

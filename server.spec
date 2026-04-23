# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for doubaoime-asr-server
Produces a single-file Windows executable.
"""

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['src/server.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        # doubaoime_asr internals
        'doubaoime_asr',
        'doubaoime_asr.asr',
        'doubaoime_asr.config',
        'doubaoime_asr.credentials',
        'doubaoime_asr.audio',
        # async / network
        'asyncio',
        'aiohttp',
        'websockets',
        # protobuf
        'google.protobuf',
        'google.protobuf.descriptor',
        'google.protobuf.descriptor_pool',
        'google.protobuf.message',
        'google.protobuf.reflection',
        'google.protobuf.symbol_database',
        # opuslib / soundfile fallback
        'ctypes',
        'ctypes.util',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'PIL'],
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
    console=True,          # keep console so users see the log
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

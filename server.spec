# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/server.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        # cffi / opuslib
        '_cffi_backend',
        'cffi',
        # doubaoime_asr
        'doubaoime_asr',
        'doubaoime_asr.asr',
        'doubaoime_asr.config',
        'doubaoime_asr.credentials',
        'doubaoime_asr.audio',
        # async / network
        'asyncio',
        'aiohttp',
        'aiohttp.web',
        'websockets',
        # protobuf
        'google.protobuf',
        'google.protobuf.descriptor',
        'google.protobuf.descriptor_pool',
        'google.protobuf.message',
        'google.protobuf.reflection',
        'google.protobuf.symbol_database',
        # stdlib
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
    collect_all=['doubaoime_asr', 'cffi', 'opuslib'],
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

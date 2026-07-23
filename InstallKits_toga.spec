# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

hiddenimports = (
    collect_submodules("toga")
    + collect_submodules("toga_winforms")
    + ["pythonnet", "clr"]
)

a = Analysis(
    ["run_toga.py"],
    pathex=[],
    binaries=[],
    datas=[
        *copy_metadata("toga"),
        *copy_metadata("toga_core"),
        *copy_metadata("toga_winforms"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["toga_runtime_hook.py"],
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
    name="InstallKits",
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="InstallKits",
)

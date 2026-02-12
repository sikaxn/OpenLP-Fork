# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, collect_submodules

pyside_datas, pyside_binaries, pyside_hiddenimports = collect_all('PySide6')

a = Analysis(
    ['run_openlp.py'],
    pathex=[],
    binaries=pyside_binaries,
    datas=pyside_datas + [
        ('openlp/core', 'core'),
        ('openlp/plugins', 'plugins'),
        ('resources/i18n', 'i18n'),
    ],
    hiddenimports=collect_submodules('openlp') + pyside_hiddenimports,
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
    name='OpenLP',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OpenLP',
)

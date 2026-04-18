# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

datas = [
    ('ui', 'ui'),
    ('models', 'models'),
    ('data', 'data'),
    ('axolexis_intelligent_reports', 'axolexis_intelligent_reports'),
]

hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'torch',
    'torchvision',
    'transformers',
    'timm',
    'monai',
    'sklearn',
    'pandas',
    'numpy',
    'matplotlib',
    'pyqtgraph',
    'seaborn',
    'scipy',
    'requests',
    'tqdm',
    'PIL',
]

a = Analysis(
    ['main_enhanced.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='AxoLexis',
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
    icon='app_icon.ico',
    version='version.txt',
)
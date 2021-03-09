# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\User\\Documents\\Work\\SIRCo\\loadForecasting\\theNewSoftware'],
             binaries=[],
             datas=[('images/header.png', './images')],
             hiddenimports=['cython', 'sklearn', 'sklearn.ensemble', 'sklearn.neighbors._typedefs', 'sklearn.neighbors._quad_tree', 'sklearn.tree._utils', 'sklearn.utils._cython_blas','sklearn.preprocessing', 'sklearn.compose', 'cytoolz.compose', 'greenlet', 'sklearn.utils.sparsetools._graph_validation', 'sklearn.utils.sparsetools._graph_tools', 'scipy.special._ufuncs_cxx', 'sklearn.utils.lgamma', 'sklearn.utils.weight_vector', 'selenium', 'sklearn.utils._weight_vector'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='PAHBAR',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='PAHBAR')

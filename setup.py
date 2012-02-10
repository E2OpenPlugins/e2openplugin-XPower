from distutils.core import setup, Extension

pkg = 'Extensions.XPower'
setup (name = 'enigma2-plugin-extensions-xpower',
       version = '1.50',
       description = 'remote PC power management for win and linux',
       packages = [pkg],
       package_dir = {pkg: 'plugin'},
       package_data = {pkg:
           ['plugin.png']},
      )

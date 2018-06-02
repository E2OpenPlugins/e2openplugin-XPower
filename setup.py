from distutils.core import setup
import setup_translate

pkg = 'Extensions.XPower'
setup (name = 'enigma2-plugin-extensions-xpower',
       version = '1.59',
       description = 'remote PC power management for Win and linux',
       packages = [pkg],
       package_dir = {pkg: 'plugin'},
       package_data = {pkg: ['*.png', '*.xml', '*/*.png', 'locale/*.pot', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass = setup_translate.cmdclass, # for translation
      )

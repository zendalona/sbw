###########################################################################
#    SBW - Sharada-Braille-Writer
#
#    Copyright (C) 2012-2014 Nalin <nalin.x.linux@gmail.com>
#    Copyright (C) 2021-2022 Nalin <nalin.x.linux@gmail.com>
#    
#    This project is funded by State Council of Educational Research and Training (S.C.E.R.T) Kerala 
#    Supervised by Zendalona(2021-2022) and Keltron(2012-2014)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

from distutils.core import setup
from glob import glob
setup(name='sbw',
      version='3.0',
      description='Simple text editor with braille input',
      author='Nalin.x.Linux',
      author_email='nalin.x.Linux@gmail.com',
      url='https://gitlab.com/Nalin-x-Linux/lios-3',
      license = 'GPL-3',
      packages=['sbw','sbw/texttools'],
      data_files=[('share/sbw/',['share/sbw/about.glade', 'share/sbw/audio_converter.glade', 'share/sbw/find_and_replace.glade',
      'share/sbw/find.glade', 'share/sbw/icon.png', 'share/sbw/spellcheck.glade',
      'share/sbw/main.glade', 'share/sbw/user_abbreviation_manager.glade','share/sbw/preferences.glade' ]),
      ('share/sbw/user-guide/',['share/sbw/user-guide/user-guide.html', 'share/sbw/user-guide/user-guide-malayalam.html', 'share/sbw/user-guide/method.jpg']),
      ('share/applications/',['share/applications/sharada-braille-writer.desktop']),
      ('share/man/man1/',['share/man/man1/sharada-braille-writer.1.gz']),
      ('share/doc/sbw/',['share/doc/sbw/copyright']),
      ('bin',['bin/sharada-braille-writer'])]
      )
# sudo python3 setup.py install --install-data=/usr

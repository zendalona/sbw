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

import os
import gettext
_ = gettext.gettext

version = "3.0"

#Where the data is located
data_dir = "/usr/share/sbw/";

user_guide_file_path = data_dir+"user-guide/user-guide.html"

user_conf_dir = os.environ['HOME']+"/.sbw/"

user_preferences_file_path = user_conf_dir+'user-preferences.cfg'

abbreviations_file_path = user_conf_dir+"abbreviations.json"

#Changing directory to Home folder
home_dir = os.environ['HOME']

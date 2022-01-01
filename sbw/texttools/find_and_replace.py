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


import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

from sbw.textview import BrailleInputTextView
from sbw.texttools.find import Find
from sbw import global_var

from sbw import localization
_ = localization._

class FindAndReplace(Find):
	def __init__(self,editor,glade_file="find_and_replace"):
		Find.__init__(self,editor,glade_file="find_and_replace")

		self.replace_entry = BrailleInputTextView()
		self.replace_entry.set_variables_from_object(editor)
		self.replace_entry.set_accepts_tab(False)
		self.replace_entry.set_single_line_mode(True)

		label = Gtk.Label()
		label.set_text(_("Replace with : "))
		label.set_mnemonic_widget(self.replace_entry)

		box = self.builder.get_object("box_replace_with")			
		box.pack_start(label,True,True,0)
		box.pack_start(self.replace_entry,True,True,0)
		label.show()
		self.replace_entry.show()
		box.set_hexpand(True)
		box.set_vexpand(False)

		
	def replace(self,widget,data=None):
		replace_word = self.replace_entry.get_text()
		self.textbuffer.delete(self.match_start, self.match_end)
		self.textbuffer.insert(self.match_end,replace_word)
		self.match_start = self.match_end.copy()
		self.find(True)
	
	def replace_all(self,widget,data=None):
		word = self.entry.get_text()
		replace_word = self.replace_entry.get_text()
		end = self.textbuffer.get_end_iter()
		while(True):
			self.match_start.forward_word_end()
			results = self.match_start.forward_search(word, 0, end)
			if results:
				self.match_start, self.match_end = results
				self.textbuffer.delete(self.match_start, self.match_end)
				self.textbuffer.insert(self.match_end,replace_word)
				self.match_start = self.match_end.copy()
			else:
				break

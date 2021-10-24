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
from sbw import global_var

import gettext
_ = gettext.gettext

class Find():
	def __init__ (self,editor,glade_file="find"):
		self.textbuffer = editor.get_buffer();
		self.textview = editor;
				
		mark = self.textbuffer.get_insert()
		self.iter = self.textbuffer.get_iter_at_mark(mark)
		self.match_start = self.iter.copy()
		self.match_start.backward_word_start()
		self.match_end = self.iter.copy()
		self.match_end.forward_word_end()
		
		
		self.tag = self.textbuffer.create_tag(foreground = "Blue")


		#Builder And Gui
		self.builder = Gtk.Builder()
		self.builder.add_from_file("{0}{1}.glade".format(global_var.data_dir,glade_file))
		self.window = self.builder.get_object("window")
		self.builder.connect_signals(self)

		
		self.entry = BrailleInputTextView()
		self.entry.set_variables_from_object(editor)
		self.entry.set_accepts_tab(False)
		self.entry.set_single_line_mode(True)

		label = Gtk.Label()
		label.set_text("Search for : ")
		label.set_mnemonic_widget(self.entry)

		box = self.builder.get_object("box_search_for")			
		box.pack_start(label,True,True,0)
		box.pack_start(self.entry,True,True,0)
		label.show()
		self.entry.show()
		box.set_hexpand(True)
		box.set_vexpand(False)
		

		self.context_label = self.builder.get_object("context_label")
		
				

	def close(self,widget,data=None):
		start,end = self.textbuffer.get_bounds()
		self.textbuffer.remove_all_tags(start,end)
		self.window.destroy()	

	def trim_context_text(self,text):
		"""cut the line if it is too lengthy (more than 10 words)
		without rearranging existing lines. This will avoid the resizing of spell window"""
		new_text = ""
		for line in text.split('\n'):
			if (len(line.split(' ')) > 10):
				new_line = ""
				pos = 1
				for word in line.split(" "):
					new_line += word
					pos += 1
					if (pos % 10 == 0):
						new_line += '\n'
					else:
						new_line += ' '

				new_text += new_line
				if (pos % 10 > 3):
					new_text += '\n'
			else:
				new_text += line + '\n'
		return new_text
	
	def find_next(self,widget,data=None):
		self.find(True)

	def find_previous(self,widget,data=None):
		self.find(False)		
		
	def find(self,data):
		word = self.entry.get_text()
		start , end = self.textbuffer.get_bounds()
		if (data == True):
			self.match_start.forward_word_end()
			results = self.match_start.forward_search(word, 0, end)
		else:
			self.match_end.backward_word_start()
			results = self.match_end.backward_search(word, 0,start)
		
		if results:
			self.textbuffer.remove_all_tags(start,end)
			self.match_start, self.match_end = results
			self.textbuffer.place_cursor(self.match_start)
			self.textbuffer.apply_tag(self.tag,self.match_start, self.match_end)
			self.textview.scroll_to_iter(self.match_start, 0.2, use_align=False, xalign=0.5, yalign=0.5)
			sentence_start=self.match_start.copy()
			sentence_start.backward_sentence_start()
			sentence_end=self.match_start.copy()
			sentence_end.forward_sentence_end()
			sentence = self.textbuffer.get_text(sentence_start,sentence_end,True)
			self.context_label.set_text(self.trim_context_text(sentence))
			self.context_label.grab_focus()
		else:
			self.context_label.set_text(_("Word {0} Not found").format(word))
			self.context_label.grab_focus()

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

from gi.repository import Gtk
from gi.repository import Gdk

import os
from subprocess import getoutput
from threading import Thread

from sbw.textview import BrailleInputTextView
from sbw import global_var

import gettext
_ = gettext.gettext

class Recorder:
	def __init__(self,text, copy_braille_view):
		self.copy_braille_view = copy_braille_view
		to_convert = open("temp.txt",'w')
		to_convert.write(text)
		to_convert.close()
		
		builder = Gtk.Builder()
		builder.add_from_file("%s/audio_converter.glade" % (global_var.data_dir))
		builder.connect_signals(self)
		self.audio_converter_window = builder.get_object("window")
			
		self.spinbutton_speed = builder.get_object("spinbutton_speed")
		self.spinbutton_pitch = builder.get_object("spinbutton_pitch")
		self.spinbutton_split = builder.get_object("spinbutton_split")
		self.spinbutton_vloume = builder.get_object("spinbutton_vloume")
		self.spinbutton_speed.set_value(170)
		self.spinbutton_pitch.set_value(50)
		self.spinbutton_split.set_value(5)
		self.spinbutton_vloume.set_value(100)
			
		voice_combo = builder.get_object("combobox_language_convert")
		
		list_store = Gtk.ListStore(str)
		output = getoutput("espeak --voices")
		for line in output.split("\n"):
			list_store.append([line.split()[3]])
		
		voice_combo.set_model(list_store)
		self.model_voice = voice_combo.get_model()
		self.index_voice = voice_combo.get_active()
		
				
		voice_combo.connect('changed', self.change_voice)
		self.audio_converter_window.show()		                

	def change_voice(self, voice):
		self.model_voice = voice.get_model()
		self.index_voice = voice.get_active()
		
	def close_audio_converter(self,widget,data=None):
		self.audio_converter_window.destroy()
		
	def convert_to_audio(self,widget,data=None):
		filechooser =  Gtk.FileChooserDialog(
		title=_("Type the output wav name"),
		parent=None,
		action=Gtk.FileChooserAction.SELECT_FOLDER)
		filechooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
		filechooser.set_current_folder("%s"%(os.environ['HOME']))

		entry = BrailleInputTextView()
		entry.set_variables_from_object(self.copy_braille_view)
		entry.set_accepts_tab(False)
		entry.set_single_line_mode(True)

		label = Gtk.Label()
		label.set_text("Filename : ")
		label.set_mnemonic_widget(entry)
			
		box = Gtk.HBox()
		box.pack_start(label,True,True,0)
		box.pack_start(entry,True,True,0)
		label.show()
		entry.show()
		box.set_hexpand(True)
		box.set_border_width(10)
			
		filechooser.set_extra_widget(box)
		response = filechooser.run()
		if response == Gtk.ResponseType.OK:
			file_name = entry.get_text()
			path = filechooser.get_filename()
			
			self.file_to_output  = path+"/"+file_name
			
			filechooser.destroy()
			Thread(target=self.record_to_wave,args=()).start()
			self.audio_converter_window.destroy()
		else:
			filechooser.destroy()           
		
	def record_to_wave(self):
		os.system('espeak -a %s -v %s -f temp.txt -w %s.wav --split=%s -p %s -s %s' % (self.spinbutton_vloume.get_value(),self.model_voice[self.index_voice][0],self.file_to_output,self.spinbutton_split.get_value(),self.spinbutton_pitch.get_value(),self.spinbutton_speed.get_value()))
		os.system('espeak "Conversion finish and saved to %s"' % (self.file_to_output))

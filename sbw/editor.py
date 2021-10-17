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

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

from sbw.textview import BrailleInputTextView
from sbw import global_var

from sbw.texttools.find import Find
from sbw.texttools.find_and_replace import FindAndReplace
from sbw.texttools.audio_converter import Recorder
from sbw.texttools.spellcheck import SpellCheck

import gettext
_ = gettext.gettext

# For Undo/Redo
import queue

class BrailleEditor(Gtk.VBox):
	def __init__(self):
		Gtk.VBox.__init__(self)
		self.set_hexpand(True)
		self.set_vexpand(True)
		
		self.brailletextview = BrailleInputTextView()
		self.brailletextview.set_hexpand(True)
		self.brailletextview.set_vexpand(True)
		
		self.brailletextview.set_wrap_mode(Pango.WrapMode.WORD_CHAR)

		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_border_width(5)
		scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolled_window.add(self.brailletextview)
		self.pack_start(scrolled_window,True,True,0)
		scrolled_window.show()
		self.brailletextview.show()


		# Undo/Redo 
		self.undo_queue = queue.LifoQueue()
		self.redo_queue = queue.LifoQueue()

		# connect engine signals
		self.brailletextview.set_event_callback(self.push_text_to_undobuffer)
		
		# For changing language while switching between tabs
		self.brailletextview.set_notify_language_callback(self.set_notify_language)
		self.brailletextview.connect("focus-in-event", self.on_brailletextview_focused)
		
		# Add inetial text to undo_queue
		self.push_text_to_undobuffer("")

		# Start as unsaved document
		self.save_file_path = None

		hbox = Gtk.HBox()
		hbox.set_hexpand(True)
		hbox.set_vexpand(False)

		label = Gtk.Label()
		label.set_text("Font ")
		self.font_button = Gtk.FontButton()
		self.font_button.connect("font-set", self.on_font_set)
		label.set_mnemonic_widget(self.font_button)
		hbox.pack_start(label,False,True,0)
		hbox.pack_start(self.font_button,False,True,0)
		fixed = Gtk.Fixed()
		hbox.pack_start(fixed,True,True,0)

		self.font_color = "#ffffff"
		self.background_color = "#000000"
		
		label = Gtk.Label()
		label.set_text("Theme ")
		self.combobox_theme = Gtk.ComboBox()
		self.combobox_theme.connect("changed", self.on_theme_changed)
		label.set_mnemonic_widget(self.combobox_theme)
		hbox.pack_start(label,False,True,0)
		hbox.pack_start(self.combobox_theme,False,True,0)
		fixed = Gtk.Fixed()
		hbox.pack_start(fixed,True,True,0)


		label = Gtk.Label()
		label.set_text("Line limit")
		self.spinbutton_line_limit = Gtk.SpinButton()
		adjustment = Gtk.Adjustment(upper=400, step_increment=1, page_increment=10)
		self.spinbutton_line_limit.set_adjustment(adjustment)
		self.spinbutton_line_limit.connect("value-changed",self.on_line_limit_set)
		label.set_mnemonic_widget(self.spinbutton_line_limit)
		hbox.pack_start(label,False,True,0)
		hbox.pack_start(self.spinbutton_line_limit,False,True,0)
		fixed = Gtk.Fixed()
		hbox.pack_start(fixed,True,True,0)


		self.checkbutton_auto_new_line = Gtk.CheckButton("Auto new line")
		self.checkbutton_auto_new_line.connect("toggled",self.on_auto_new_line_toggled)
		hbox.pack_start(self.checkbutton_auto_new_line,False,True,0)
		fixed = Gtk.Fixed()
		hbox.pack_start(fixed,True,True,0)

		self.checkbutton_speech = Gtk.CheckButton("Speech")
		self.checkbutton_speech.connect("toggled",self.on_speech_toggled)
		hbox.pack_start(self.checkbutton_speech,False,True,0)
		fixed = Gtk.Fixed()
		hbox.pack_start(fixed,True,True,0)

		self.checkbutton_simple_mode = Gtk.CheckButton("Simple mode")
		self.checkbutton_simple_mode.connect("toggled",self.on_simple_mode_toggled)
		hbox.pack_start(self.checkbutton_simple_mode,False,True,0)
		fixed = Gtk.Fixed()
		hbox.pack_start(fixed,True,True,0)

		self.checkbutton_auto_capitalize_sentence = Gtk.CheckButton("Auto capitalize sentence")
		self.checkbutton_auto_capitalize_sentence.connect("toggled",self.on_auto_capitalize_sentence_toggled)
		hbox.pack_start(self.checkbutton_auto_capitalize_sentence,False,True,0)
		fixed = Gtk.Fixed()
		hbox.pack_start(fixed,True,True,0)

		self.checkbutton_auto_capitalize_line = Gtk.CheckButton("Auto capitalize line")
		self.checkbutton_auto_capitalize_line.connect("toggled",self.on_auto_capitalize_line_toggled)
		hbox.pack_start(self.checkbutton_auto_capitalize_line,False,True,0)
		fixed = Gtk.Fixed()
		hbox.pack_start(fixed,True,True,0)

		
		# Pack bottom HBox
		self.pack_start(hbox,False,True,0)
		hbox.show_all()

	def on_font_set(self,widget):
		font = widget.get_font_name();
		pangoFont = Pango.FontDescription(font)
		self.brailletextview.modify_font(pangoFont)

	def set_theme_store(self, store):
		self.theme_store = store
		self.combobox_theme.set_model(self.theme_store)
		renderer_text = Gtk.CellRendererText()
		self.combobox_theme.pack_start(renderer_text, True)
		self.combobox_theme.add_attribute(renderer_text, "text", 0)

	def on_theme_changed(self,widget):
		self.theme = widget.get_active()

		self.font_color = self.theme_store[self.theme][1]
		self.background_color = self.theme_store[self.theme][2] 

		if(self.theme == 0):
			self.brailletextview.modify_fg(Gtk.StateFlags.NORMAL, None)
			self.brailletextview.modify_bg(Gtk.StateFlags.NORMAL, None)
			
			self.font_color = "#000000" 
			self.background_color = "#ffffff"
		else:
			self.brailletextview.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.font_color))
			self.brailletextview.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.background_color ))
		
		self.set_cursor_color(self.font_color)
		self.set_selection_color()


	def on_line_limit_set(self,widget):
		value = widget.get_value_as_int()
		self.brailletextview.set_line_limit(value)
	
	def on_auto_capitalize_sentence_toggled(self,widget):
		value = int(widget.get_active())
		self.brailletextview.set_auto_capitalize_sentence(value)

	def on_auto_capitalize_line_toggled(self,widget):
		value = int(widget.get_active())
		self.brailletextview.set_auto_capitalize_line(value)

	def on_simple_mode_toggled(self,widget):
		value = int(widget.get_active())
		self.brailletextview.set_simple_mode(value)

	def on_speech_toggled(self,widget):
		value = int(widget.get_active())
		self.brailletextview.set_notification(value)

	def on_auto_new_line_toggled(self,widget):
		value = int(widget.get_active());
		self.brailletextview.set_auto_new_line(value)



	def change_font_size(self, increase = True):
		font = self.font_button.get_font()
		size = int(str(font.split(" ")[-1]))
		print("FFFFFFFFFFFFFF")
		print(size)

		if(increase):
			size = size + 2
			self.notify2(_("Font size increased to ")+str(size));
		else:
			size = size - 2
			self.notify2(_("Font size decreased to ")+str(size));

		new_font = (" ".join(font.split(" ")[:-1])+" "+str(size))
		pangoFont = Pango.FontDescription(new_font)
		self.brailletextview.modify_font(pangoFont)
		self.font_button.set_font(new_font)

	def set_font(self, font):
		self.font_button.set_font_name(font)
		pangoFont = Pango.FontDescription(font)
		self.brailletextview.modify_font(pangoFont)

	def set_cursor_color(self, color):
		colors_in_float = Gdk.color_parse(color).to_floats()
		cursor_color_hex = "#" + "".join(["%02x" % (int(color * 255)) for color in colors_in_float])
		
		try:
		    cssProvider = Gtk.CssProvider()
		    cssProvider.load_from_data((" * {   caret-color: "+cursor_color_hex+";    }").encode('ascii'))
		
		    style = self.brailletextview.get_style_context()
		    style.add_provider(cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
		except:
		    print("Unnable to set cursor color!")

	def set_selection_color(self):
		color1 = Gdk.color_parse(self.font_color)
		color2 = Gdk.color_parse(self.background_color)
		
		selection_color = Gdk.Color((color1.red + color2.red)/2, (color1.green + color2.green)/2 ,(color1.blue + color2.blue)/2)
		
		
		selection_colors_in_float = selection_color.to_floats()
		
		selection_background_colors_in_float = color2.to_floats()
		
		selection_color_hex = "#" + "".join(["%02x" % (int(color * 255)) for color in selection_colors_in_float])
		
		selection_background_color_hex = "#" + "".join(["%02x" % (int(color * 255)) for color in selection_background_colors_in_float])
		
		try:
		    cssProvider = Gtk.CssProvider()
		    cssProvider.load_from_data((" * selection { color: "+selection_color_hex+";  background: "+selection_background_color_hex+";}").encode('ascii'))
		
		    style = self.brailletextview.get_style_context()
		    style.add_provider(cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
		except:
		    print("Unnable to set selection color!")
		

	def set_theme(self, theme):
		self.theme = theme
		self.combobox_theme.set_active(self.theme)

		self.font_color = self.theme_store[self.theme][1]
		self.background_color = self.theme_store[self.theme][2] 

		if(self.theme == 0):
			self.brailletextview.modify_fg(Gtk.StateFlags.NORMAL, None)
			self.brailletextview.modify_bg(Gtk.StateFlags.NORMAL, None)			
			self.font_color = "#000000" 
			self.background_color = "#ffffff"
		else:
			self.brailletextview.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.font_color))
			self.brailletextview.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.background_color ))
		
		self.set_cursor_color(self.font_color)
		self.set_selection_color()

	def set_notify_language(self,language):
		self.notify_language = language
		self.notify_language_callback(language)

	def set_notify_language_callback(self,func):
		self.notify_language_callback = func

	def on_brailletextview_focused(self,widget, data=None):
		self.notify_language_callback(self.notify_language)
		self.brailletextview.reset()
		print("FFFFFFFFFFFOOOOOOCCCCCCCC")


	def set_line_limit(self, limit):
		self.spinbutton_line_limit.set_value(limit)
		self.brailletextview.set_line_limit(limit)

	def set_auto_capitalize_sentence(self, value):
		self.checkbutton_auto_capitalize_sentence.set_active(value)
		self.brailletextview.set_auto_capitalize_sentence(value)

	def set_auto_capitalize_line(self, value):
		self.checkbutton_auto_capitalize_line.set_active(value)
		self.brailletextview.set_auto_capitalize_line(value)

	def set_simple_mode(self, value):
		self.checkbutton_simple_mode.set_active(value)
		self.brailletextview.set_simple_mode(value)	

	def set_speech(self, value):
		self.checkbutton_speech.set_active(value)
		self.brailletextview.set_notification(value)
		
	def set_auto_new_line(self, value):
		self.checkbutton_auto_new_line.set_active(value)
		self.brailletextview.set_auto_new_line(value)


	def get_braille_input_text_view(self):
		return self.brailletextview

	def get_modified(self):
		textbuffer = self.brailletextview.get_buffer()
		return textbuffer.get_modified()

	def get_file_path(self):
		return self.save_file_path;

	def set_notify2_callback(self, function):
		self.notify2 = function

	def set_tab_title_callback(self, function):
		self.set_tab_title = function
	
	def go_to_line(self,wedget,data=None):
		textbuffer = self.brailletextview.get_buffer()
		insert_mark = textbuffer.get_insert()
		offset = textbuffer.get_iter_at_mark(insert_mark)
		current_line = offset.get_line()
		maximum_line = textbuffer.get_line_count()
		adj = Gtk.Adjustment(value=1, lower=1, upper=maximum_line, step_incr=1, page_incr=5, page_size=0) 
		spinbutton_line = Gtk.SpinButton()
		spinbutton_line.set_adjustment(adj)
		spinbutton_line.set_value(current_line+1)		
		spinbutton_line.show()

		dialog =  Gtk.Dialog(_("Go to Line "),None,True,(_("Go"), Gtk.ResponseType.ACCEPT,_("Close!"), Gtk.ResponseType.REJECT))
		spinbutton_line.connect("activate",lambda x : dialog.response(Gtk.ResponseType.ACCEPT))
		box = dialog.get_content_area();
		box.add(spinbutton_line)
		spinbutton_line.grab_focus()
		dialog.show_all()
		response = dialog.run()
		dialog.destroy()
		if response == Gtk.ResponseType.ACCEPT:
			to = spinbutton_line.get_value_as_int()
			textbuffer = self.brailletextview.get_buffer()
			iter = textbuffer.get_iter_at_line(to-1)
			textbuffer.place_cursor(iter)
			self.brailletextview.scroll_to_iter(iter, 0.0,False,0.0,0.0)

			
	def say_line_number(self):
		textbuffer = self.brailletextview.get_buffer()
		insert_mark = textbuffer.get_insert()
		offset = textbuffer.get_iter_at_mark(insert_mark)
		current_line = offset.get_line()+1
		self.notify2(_("Current Line : ")+str(current_line));
		

	def open_find_dialog(self):
		Find(self.brailletextview).window.show()
			
	def open_find_and_replace_dialog(self):
		FindAndReplace(self.brailletextview).window.show()

	def open_audio_converter_dialog(self):
		textbuffer = self.brailletextview.get_buffer()
		if(textbuffer.get_has_selection()):
			start,end = textbuffer.get_selection_bounds()
		else:
			start,end = textbuffer.get_bounds()		
		text = textbuffer.get_text(start,end,False)		
		Recorder(text, self.brailletextview)

	def spell_check(self):
		SpellCheck(self.brailletextview,self.notify_language)

	
	def new(self,wedget,data=None):
		textbuffer = self.brailletextview.get_buffer()
		if (textbuffer.get_modified() == True):
			dialog =  Gtk.Dialog(_("Start new without saving ?"),self.window,True,
			(_("Save"), Gtk.ResponseType.ACCEPT,_("Start-New!"), Gtk.ResponseType.REJECT))                           						

			label = Gtk.Label(_("Start new without saving ?"))
			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()

			response = dialog.run()
			dialog.destroy()				
			if response == Gtk.ResponseType.ACCEPT:
				self.save(self)
		self.brailletextview.set_text("")
		self.brailletextview.grab_focus();
		self.notify2("New");

	# Note : Unused function  
	def open(self,wedget,data=None):
		if (self.brailletextview.get_modified() == True):
			return False
		else:
			open_file_chooser = Gtk.FileChooserDialog(_("Select the file to open"),None,
			Gtk.FileChooserAction.OPEN,
			buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
			Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
			open_file_chooser.set_current_folder("%s"%(os.environ['HOME']))
			response = open_file_chooser.run()
			if response == Gtk.ResponseType.OK:
				if(self.open_file(open_file_chooser.get_filename())):
					open_file_chooser.destroy()
					return True
			open_file_chooser.destroy()
			return True

	def open_file(self, file_name):
		try:
			to_read = open(file_name)
			text = to_read.read()
			self.brailletextview.set_text(text)
		except FileNotFoundError:
			return False
		else:
			self.save_file_path = file_name
			textbuffer = self.brailletextview.get_buffer()
			textbuffer.place_cursor(textbuffer.get_end_iter())
			self.set_tab_title(self.save_file_path.split("/")[-1])
			return True

	def save(self,wedget,data=None):
		textbuffer = self.brailletextview.get_buffer()
		text = self.brailletextview.get_text()
		if(self.save_file_path == None):
			filechooser =  Gtk.FileChooserDialog(
			title="Please choose a folder and type filename",
			parent=None,
			action=Gtk.FileChooserAction.SELECT_FOLDER)
			filechooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Save", Gtk.ResponseType.OK)
			filechooser.set_current_folder("%s"%(os.environ['HOME']))

			entry = BrailleInputTextView()
			entry.set_variables_from_object(self.brailletextview)
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

			entry.grab_focus()
			
			box_full = filechooser.get_children()[0].get_children()[0]
			print(box_full)
			folder_selecter_item, file_name_item = box_full.get_children() 
			print(folder_selecter_item, file_name_item)
			box_full.set_focus_chain([file_name_item, folder_selecter_item])


			
			
			response = filechooser.run()
			print("Hai")
			if response == Gtk.ResponseType.OK:
				file_name = entry.get_text()
				path = filechooser.get_filename()
				self.save_file_path = path+"/"+file_name
				
				if(not os.path.exists(self.save_file_path)):
					self.set_tab_title(file_name)
					open("%s" %(self.save_file_path),'w').write(text)
					self.notify2(_("Text saved to {}").format(self.save_file_path));
					textbuffer.set_modified(False)	
					filechooser.destroy()
					return True
				else:
					dialog =  Gtk.Dialog("Save", None,1,
					(_("Replace"),Gtk.ResponseType.YES,_("Save as"), Gtk.ResponseType.NO))
					label = Gtk.Label(_("File exist! Do you want to replace it ?"))
					box = dialog.get_content_area();
					box.add(label)
					dialog.show_all()
					response = dialog.run()
					dialog.destroy()
					if response == Gtk.ResponseType.YES:
						self.set_tab_title(file_name)
						open("%s" %(self.save_file_path),'w').write(text)
						self.notify2(_("Text saved to {}").format(self.save_file_path));
						textbuffer.set_modified(False)	
						filechooser.destroy()
						return True
					elif response == Gtk.ResponseType.NO:
						filechooser.destroy()
						self.save_file_path = None
						return self.save(self)
			else:
				filechooser.destroy()
			return False
		else:
			open("%s" %(self.save_file_path),'w').write(text)
			self.notify2(_("Text saved to {}").format(self.save_file_path));	
			textbuffer.set_modified(False)
			return True		

	def save_as(self,wedget,data=None):
		self.save_file_path = None
		self.save(self);


	def close(self):
		textbuffer = self.brailletextview.get_buffer()
		if textbuffer.get_modified() == True:
			dialog =  Gtk.Dialog(None,None,1,
			(_("Close without saving"),Gtk.ResponseType.YES,_("Save"), Gtk.ResponseType.NO,_("Cancel"), Gtk.ResponseType.CANCEL))			
			label = Gtk.Label(_("Close without saving ?."))
			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()
			
			response = dialog.run()
			dialog.destroy()
			if response == Gtk.ResponseType.YES:
				return True		
			elif response == Gtk.ResponseType.NO:
				if (self.save(self)):
					return True
				else:
					return False
			else:
				return False
		return True;


	def select_all(self):
		textbuffer = self.brailletextview.get_buffer()
		start,end = textbuffer.get_bounds()
		textbuffer.select_range(start,end)

	def copy_clipboard(self):
		textbuffer = self.brailletextview.get_buffer()
		clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		textbuffer.copy_clipboard(clipboard)

	def cut_clipboard(self):
		textbuffer = self.brailletextview.get_buffer()
		clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		textbuffer.cut_clipboard(clipboard, True)

	def paste_clipboard(self):
		textbuffer = self.brailletextview.get_buffer()
		clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		textbuffer.paste_clipboard(clipboard, None, True)

	def delete(self):
		textbuffer = self.brailletextview.get_buffer()
		if (textbuffer.get_has_selection()):
			textbuffer.delete_selection(True,True)
			self.notify2(_("Selection Deleted"));



	
	def set_dictionary(self,dict):
		self.dict = dict
	
	def undo(self):
		if( not self.undo_queue.empty()):
			text_in_queue = self.undo_queue.get()
			text_in_view = self.brailletextview.get_text()
			self.brailletextview.set_text(text_in_queue)
			self.redo_queue.put(text_in_view)
		
	def redo(self ):
		if( not self.redo_queue.empty()):
			text_in_queue = self.redo_queue.get()
			text_in_view = self.brailletextview.get_text()
			self.brailletextview.set_text(text_in_queue)
			self.undo_queue.put(text_in_view)
	
	def push_text_to_undobuffer(self, data1=None, data2=None, data3=None, data4=None):
		text = self.brailletextview.get_text()
		self.undo_queue.put(text)			




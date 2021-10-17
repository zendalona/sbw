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
import configparser
import re
import speechd
import webbrowser

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Pango

# For sending notifications to orca screen reader
from gi.repository import Atk


from brailleinput import engine


from sbw import preferences
from sbw.editor import BrailleEditor
from sbw import global_var
from sbw import user_abbreviation_manager

import gettext
_ = gettext.gettext
gettext.textdomain('sbw')


########################## Temporary fix ###################
espeak_available = 0
speechd_available = 0;
try:
	import speechd
	speechd_available = 1;
	client = speechd.Client()
except:
	try:
		from espeak import espeak
		espeak_available = 1;
	except:
		espeak_available = 0;


def speak(text):
	if(speechd_available):
		client.cancel()
		client.speak(text);
	elif (espeak_available):
		espeak.cancel()
		espeak.synth(text)
	else:
		print("No tts api available!(python3-espeak/python3-speechd)");

def set_tts_language(language):
	print(language)
	if(speechd_available):
		client.set_language(language)
	elif (espeak_available):
		espeak.set_voice(language)
	else:
		pass

def close_tts():
	if(speechd_available):
		client.close()

tts_dictionary = {"\n" : _("new_line"),
 " " : _("space"), "?" : _("questionmark"), 
 "," : _("comma"), "·" : _("multiplication dot"),"." : _("full stop"), "!" : _("exclamation"),
 "(" : _("opening bracket"), ")" : _("closing bracket"), 
 "\"" : _("double_quote"), "\'" : _("single_quote"), 
 "/" : _("slash"), "\\" : _("backslash"), ";" : _("semicolon"), "–" : _("Dash"),"…" : _("Ellipsis"),
 ":" : _("colon"), "{" : _("opening curly bracket"), "}" : _("closing curly bracket"),
"[" : _("opening square bracket"), "]" : _("closing square bracket"),
"⏢" : _("Trapezium"),
"☆" : _("White Star"),
"¶" : _("Paragraph mark"),
"￩" : _("Halfwidth leftwards arrow"),
"+-" : _("Plus followed by minus"),
"〃" : _("Ditto Mark"),
"ʹ" : _("Prime"),
"≮" : _("Note less than"),
"∠" : _("Acute angle"),
"▬" : _("Rectangle"),
"○" : _("Circle"),
"⊥" : _("is perpenticular to"),
"∥" : _("is parallel to"),
"✓" : _("Check mark"),
"″" : _("Ditto mark"),
"∶" : _("Ratio"),
"|" : _("Vertical"),
"―" : _("Horizondal"),
"<" : _("Less than"),
">" : _("Greater than"),
"⋝" : _("Bar over greater than"),
"⋜" : _("Bar over less than"),
"≦" : _("Is less than or equal to"),
"≧" : _("Is greater than or equal to"),
"≦" : _("Is equal to or less than"),
"≧" : _("Is equal to or greater than"),
"><" : _("Is greater than followed by less than"),
"<>" : _("Is less than followed by greater than"),
">=<" : _("Is greater than followed by equals sign followed by less than"),
"<=>" : _("Is less than followed by equals sign followed by greater than"),
"◺" : _("Right Triangle"),
"▱" : _("Parallellogram"),
"◠" : _("Arc upward"),
"◡" : _("Arc downward"),
"⬠" : _("Pentagon"),
"⬡" : _("Hexagon"),
"⩳" : _("Equall sign under single tilde"),
"≂" : _("Bar under single tilde"),
"∠" : _("Angle acute"),
"⦦" : _("Angle obtuse"),
"∟" : _("Right Angle"),
"△" : _("Acute triangle"),
"⊕" : _("Circle with interior plus sign"),
"⊗" : _("Circle with interior cross sign"),
"⊡" : _("Square with interior dot sign"),
"￫" : _("Right pointing short"),
"⇄" : _("Reverse arrows"),
"⇒" : _("Implication"),
"′" : _("Prime"),
"′" : _("Minute"),
"″" : _("Second"),
"❘" : _("such that"),
"❘" : _("Vertical Bar"),
"≯" : _("Is not greator than"),
"≮Is" : _("not less than"),
"∦" : _("Is not parallel to"),
"≟" : _("Question mark over equal sign"),
"ꞷ" : _("Small letter Omega"),
"∈" : _("is an element of (Membership)"),
"∍" : _("Contains the element"),
"⊂" : _("inclusion sign"),
"⊃" : _("reverse inclusion sign"),
"∩" : _("intersection set"),
"∪" : _("Union set"),
"∅" : _("Empty set"),
"{}" : _("Empty set"),
"⊆" : _("Bar under inclusion sign"),
"⊇" : _("Bar under reverse inclusion") }


####### End of Temporary fix #############


class BrailleWriter():
	def __init__ (self,file_list=[]):
		self.letter = {}
		self.guibuilder = Gtk.Builder()
		self.guibuilder.add_from_file(global_var.data_dir+"main.glade")
		self.window = self.guibuilder.get_object("window")
		
		self.label = self.guibuilder.get_object("info_label")
		self.built_in_language_menu = self.guibuilder.get_object("built_in_language_menu")
		self.liblouis_language_menu = self.guibuilder.get_object("liblouis_language_menu")
		
		
		self.notebook = Gtk.Notebook()

		box = self.guibuilder.get_object("box")
		box.pack_start(self.notebook, True, True, 0);
		box.reorder_child(self.notebook, 2)
		
		self.notebook.connect("key-press-event",self.on_key_press_event)
		
		
		self.guibuilder.connect_signals(self);

		#Switching off the event bell
		settings = Gtk.Settings.get_default()
		settings.set_property("gtk-error-bell", False)
		
		# Creating user configuration directory
		os.makedirs(global_var.user_conf_dir, exist_ok=True)
		
		# User Preferences
		self.pref = preferences.Preferences()
		self.pref.set_on_apply_preferences_callback(self.apply_preferences_on_existing_text_views)
		self.pref.load_preferences_from_file(global_var.user_preferences_file_path)
		
		# User Abbreviations
		self.uam = user_abbreviation_manager.UserAbbreviationManager()
		self.uam.set_on_apply_abbreviations_callback(self.apply_abbreviations_on_existing_text_views)
		self.uam.import_from_file(global_var.abbreviations_file_path)
		
		
		self.engine = engine.BrailleInputEngine()
		list_of_available_built_in_languages = self.engine.get_available_built_in_languages()
		list_of_available_liblouis_languages = self.engine.get_available_liblouis_languages()
		self.pref.set_built_in_language_list(list_of_available_built_in_languages)
		self.pref.set_liblouis_language_list(list_of_available_liblouis_languages)

		# Setting language menu items with keys
		menu_built_in_languages = Gtk.Menu()
		accel_group = Gtk.AccelGroup()
		self.window.add_accel_group(accel_group)
#		i = 1
		for item in list_of_available_built_in_languages:
			menuitem = Gtk.MenuItem()
			menuitem.set_label(item)
			menuitem.connect("activate",self.load_language);
#			key,mods=Gtk.accelerator_parse("F%d" % i)
#			if (i < 13):
#				menuitem.add_accelerator("activate", accel_group,key, mods, Gtk.AccelFlags.VISIBLE)
#				i = i + 1
			menu_built_in_languages.append(menuitem);
		self.built_in_language_menu.set_submenu(menu_built_in_languages);
			
		
		menu_liblouis_languages = Gtk.Menu()
		accel_group2 = Gtk.AccelGroup()
		for item in list_of_available_liblouis_languages:
			menuitem = Gtk.MenuItem()
			menuitem.set_label(item)
			menuitem.connect("activate",self.load_liblouis_language);
#			key,mods=Gtk.accelerator_parse("<Ctrl>F%d" % i)
#			if (i < 13):
#				menuitem.add_accelerator("activate", accel_group2,key, mods, Gtk.AccelFlags.VISIBLE)
#				i = i + 1
			menu_liblouis_languages.append(menuitem);

		self.liblouis_language_menu.set_submenu(menu_liblouis_languages);


		if(len(file_list) == 0):
			self.new(None,None)
		else:
			for file_ in file_list:
				self.new(None, None)
				be = self.get_current_focused_braille_editor()
				if(not be.open_file(file_)):
					pn = self.notebook.get_current_page()
					self.notebook.remove_page(pn)
					

		
		self.window.maximize();
		self.window.show_all();
		Gtk.main();
	
	def on_key_press_event(self, widget, event):
		print("Key press on widget: ", widget)
		print("          Modifiers: ", event.state)
		print("      Key val, name: ", event.keyval, Gdk.keyval_name(event.keyval))
		
		# check the event modifiers (can also use SHIFTMASK, etc)
		shift = (event.state & Gdk.ModifierType.SHIFT_MASK)
		ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
		alt = (event.state & Gdk.ModifierType.MOD1_MASK)
		
		# see if we recognise a keypress
		if alt and event.keyval == Gdk.KEY_1:
			self.notebook.set_current_page(0)

		if alt and event.keyval == Gdk.KEY_2:
			self.notebook.set_current_page(1)

		if alt and event.keyval == Gdk.KEY_3:
			self.notebook.set_current_page(2)

		if alt and event.keyval == Gdk.KEY_4:
			self.notebook.set_current_page(3)
			
		if alt and event.keyval == Gdk.KEY_5:
			self.notebook.set_current_page(4)		

		if alt and event.keyval == Gdk.KEY_6:
			self.notebook.set_current_page(5)

		if alt and event.keyval == Gdk.KEY_7:
			self.notebook.set_current_page(6)

		if alt and event.keyval == Gdk.KEY_8:
			self.notebook.set_current_page(7)

		if alt and event.keyval == Gdk.KEY_9:
			self.notebook.set_current_page(8)
			
		if alt and event.keyval == Gdk.KEY_0:
			self.notebook.set_current_page(9)
		
		if alt and event.keyval == Gdk.KEY_Left:
			self.notebook.prev_page()
			
		if alt and event.keyval == Gdk.KEY_Right:
			self.notebook.next_page()

		if ctrl and event.keyval == Gdk.KEY_w:
			be = self.get_current_focused_braille_editor()
			if(be.close()):
				pn = self.notebook.get_current_page()
				self.notebook.remove_page(pn)



	def apply_preferences_on_existing_text_views(self):
		notebook_page_count = self.notebook.get_n_pages()
		if (notebook_page_count > 1):
			dialog =  Gtk.Dialog("Warning!",self.window,0,("Yes",Gtk.ResponseType.YES, "No",Gtk.ResponseType.NO))
			label = Gtk.Label("Apply preferences on all existing tabs ?")
			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()
			response = dialog.run()
			dialog.destroy()
			if response == Gtk.ResponseType.NO:
				return
			
		
		for page_number in range(0, notebook_page_count):
			braille_editor = self.notebook.get_nth_page(page_number)

			braille_editor.set_font(self.pref.font)
			braille_editor.set_theme(self.pref.theme)

			braille_editor.set_auto_capitalize_sentence(self.pref.auto_capitalize_sentence)
			braille_editor.set_auto_capitalize_line(self.pref.auto_capitalize_line)
			braille_editor.set_simple_mode(self.pref.simple_mode)
			braille_editor.set_auto_new_line(self.pref.auto_new_line)
			braille_editor.set_line_limit(self.pref.line_limit)


			biv = braille_editor.get_braille_input_text_view()
			
			biv.set_checked_languages_built_in(self.pref.checked_languages_built_in)
			biv.set_checked_languages_liblouis(self.pref.checked_languages_liblouis)
		
			biv.set_keycode_map(self.pref.get_keycode_map())

			biv.set_conventional_braille(self.pref.conventional_braille)
			biv.set_one_hand_mode(self.pref.one_hand_mode)
			biv.set_one_hand_conversion_delay(self.pref.one_hand_conversion_delay)

		# Saving to file
		self.pref.save_preferences_to_file(global_var.user_preferences_file_path)



	def apply_abbreviations_on_existing_text_views(self):
		abbreviations = self.uam.get_abbreviations()
		for page_number in range(0, self.notebook.get_n_pages()):
			braille_editor = self.notebook.get_nth_page(page_number)
			biv = braille_editor.get_braille_input_text_view()
			biv.set_abbreviations(abbreviations)
		
		# Saving to file
		self.uam.save_to_file(global_var.abbreviations_file_path)

	# get_current_page() will not return exact page during this event
	def close_tab(self, widget, page_widget):
		if(page_widget.close()):
			pn = self.notebook.page_num(page_widget)
			self.notebook.remove_page(pn)

	def new(self,wedget,data=None):
		new_braille_editor = BrailleEditor()
		new_braille_editor.set_notify2_callback(self.notify2)
		new_braille_editor.set_tab_title_callback(self.set_notebook_tab_title)

		new_braille_editor.set_font(self.pref.font)
		new_braille_editor.set_theme_store(self.pref.theme_store)
		new_braille_editor.set_theme(self.pref.theme)

		new_braille_editor.set_auto_capitalize_sentence(self.pref.auto_capitalize_sentence)
		new_braille_editor.set_auto_capitalize_line(self.pref.auto_capitalize_line)
		new_braille_editor.set_simple_mode(self.pref.simple_mode)
		new_braille_editor.set_auto_new_line(self.pref.auto_new_line)
		new_braille_editor.set_line_limit(self.pref.line_limit)

		biv = new_braille_editor.get_braille_input_text_view()
		biv.set_checked_languages_built_in(self.pref.checked_languages_built_in)
		biv.set_checked_languages_liblouis(self.pref.checked_languages_liblouis)
		
		biv.set_keycode_map(self.pref.get_keycode_map())
		biv.set_abbreviations(self.uam.get_abbreviations())

		biv.set_conventional_braille(self.pref.conventional_braille)
		biv.set_one_hand_mode(self.pref.one_hand_mode)
		biv.set_one_hand_conversion_delay(self.pref.one_hand_conversion_delay)
		
		biv.set_notify_callback(self.notify)

		# For changing language while switching between tabs
		new_braille_editor.set_notify_language_callback(self.set_notify_language)
		
		number = self.notebook.get_n_pages()
		
		label = Gtk.Label(label="Unsaved document "+str(number+1))
		button = Gtk.Button(None,image=Gtk.Image(stock=Gtk.STOCK_CLOSE))
		button.set_relief(Gtk.ReliefStyle.NONE)
		button.connect("clicked",self.close_tab, new_braille_editor)
		button.show()
		label.show()
		title_box = Gtk.HBox()
		title_box.pack_start(label, True, True, 0)
		title_box.pack_start(button, False, False, 0)
		title_box.show()

		
		self.notebook.append_page(new_braille_editor, title_box)

		new_braille_editor.show()
		
		# Move focus to last added page
		self.notebook.set_current_page(number)
		
		#Grabing focus
		biv.grab_focus();
		
		#Load the first language by default
		biv.set_liblouis_mode(self.pref.default_liblouis_mode)
		
		# Inetialize
		biv.load_default_language()
		
		

		
	def set_notebook_tab_title(self, text):
		current_page_number = self.notebook.get_current_page()
		page = self.notebook.get_nth_page(current_page_number)

		label = Gtk.Label(text)
		button = Gtk.Button(None,image=Gtk.Image(stock=Gtk.STOCK_CLOSE))
		button.set_relief(Gtk.ReliefStyle.NONE)
		button.connect("clicked",self.close_tab, page)
		button.show()
		label.show()
		title_box = Gtk.HBox()
		title_box.pack_start(label, True, True, 0)
		title_box.pack_start(button, False, False, 0)
		title_box.show()

		self.notebook.set_tab_label(page, title_box)
	
	def notify(self, message, verbose=False):
		#frame = self.label.get_parent()
		#atk_ob = frame.get_accessible()
		#self.label.set_text(message)
		#atk_ob.notify_state_change(Atk.StateType.SHOWING,True);
		if not(verbose):
			speak(message)
		else:
			speak(self.convert_marks_in_text_to_words(message))

	def convert_marks_in_text_to_words(self, text):
		is_uppercase = text.upper() == text;
		result = "";
		for charecter in list(text):
			if (charecter in tts_dictionary):
				if(is_uppercase):
					result = result = result + (", "+tts_dictionary[charecter].upper()+", ");
				else:
					result = result = result + (", "+tts_dictionary[charecter]+", ");
			else:
				result = result + charecter;
		return result;


	def notify2(self, message):
		frame = self.label.get_parent()
		atk_ob = frame.get_accessible()
		self.label.set_text(message)
		atk_ob.notify_state_change(Atk.StateType.SHOWING,True);
		
	
	def set_notify_language(self,language):
		set_tts_language(language)
	
	def get_current_focused_braille_editor(self):
		current_page_number = self.notebook.get_current_page()
		return self.notebook.get_nth_page(current_page_number)

	def load_liblouis_language(self,widget):
		braille_editor = self.get_current_focused_braille_editor()
		biv = braille_editor.get_braille_input_text_view()
		biv.set_liblouis_mode(True)
		biv.set_liblouis_language(widget.get_label())
	
	def load_language(self,widget):
		braille_editor = self.get_current_focused_braille_editor()
		biv = braille_editor.get_braille_input_text_view()
		biv.set_liblouis_mode(False)
		biv.set_built_in_language(widget.get_label())

	def open_preferences(self, widget):
		self.pref.open_preferences_dialog()
	
	def manage_user_abbreviations(self, widget):
		editor = self.get_current_focused_braille_editor()
		self.uam.set_braille_view_copy_object(editor.get_braille_input_text_view())
		self.uam.show()

	def expand_short_hand(self,widget):
		try:
			start,end = self.textbuffer.get_selection_bounds()
		except ValueError:
			start,end = self.textbuffer.get_bounds()
		
		text = self.textbuffer.get_text(start,end,False)
		self.textbuffer.delete(start,end);
		
		for key in self.abbreviations.keys():
			if key in text.split():
				text = re.sub("(?<![\w\d])"+key+"(?![\w\d])",self.abbreviations[key],text)
		self.textbuffer.insert(start,text)

	def open_user_guide(self,wedget,data=None):
		url = global_var.user_guide_file_path
		try:
			webbrowser.get("firefox").open(url, new=2)
		except webbrowser.Error:
			webbrowser.open(url, new=2)

	def get_opened_file_list(self):
		file_list = []
		for page_number in range(0, self.notebook.get_n_pages()):
			braille_editor = self.notebook.get_nth_page(page_number)
			file_list.append(braille_editor.get_file_path())
		return file_list;

	def open(self,wedget,data=None):
		open_file_chooser = Gtk.FileChooserDialog(_("Select the file to open"),None, 
		Gtk.FileChooserAction.OPEN, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
		Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		open_file_chooser.set_current_folder("%s"%(os.environ['HOME']))
		open_file_chooser.set_select_multiple(True)
		response = open_file_chooser.run()
		already_opened_file_list = []
		if response == Gtk.ResponseType.OK:
			opened_file_list = self.get_opened_file_list()
			filename_list = open_file_chooser.get_filenames()
			for index in range(0, len(filename_list)):
				if (not filename_list[index] in opened_file_list):
					if(index == 0):
						be = self.get_current_focused_braille_editor()
						if(be.get_modified() == True):
							# Not saved
							self.new(None,None)
							be = self.get_current_focused_braille_editor()
					else:
						self.new(None,None)
						be = self.get_current_focused_braille_editor()
					
					be.open_file(filename_list[index])
				else:
					already_opened_file_list.append(filename_list[index])
		open_file_chooser.destroy()
		if(len(already_opened_file_list) > 0):
			dialog =  Gtk.Dialog(_("Files already opened!"), self.window,0,
			(_("Okay"), Gtk.ResponseType.OK))
			label = Gtk.Label(_("Following files are already opened in other tabs \n")+"\n".join(already_opened_file_list))
			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()	
			response = dialog.run()
			dialog.destroy()
			

	def save(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.save(wedget,data)

	def save_as(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.save_as(wedget,data)

	def go_to_line(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.go_to_line(wedget,data)

	def say_line_number(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.say_line_number()

#	def toggle_auto_capitalization(self,wedget,data=None):
#		be = self.get_current_focused_braille_editor()
#		be.say_line_number()

	def find(self,widget):
		be = self.get_current_focused_braille_editor()
		be.open_find_dialog()

	def find_and_replace(self,widget):
		be = self.get_current_focused_braille_editor()
		be.open_find_and_replace_dialog()

	def about(self,wedget,data=None):
		builder = Gtk.Builder()
		builder.add_from_file(global_var.data_dir+"about.glade")
		about_dialog = builder.get_object("aboutdialog")
		about_dialog.run()
		about_dialog.destroy()

	def audio_converter(self,widget):
		be = self.get_current_focused_braille_editor()
		be.open_audio_converter_dialog()
		
	def spell_check(self,widget):
		be = self.get_current_focused_braille_editor()
		be.spell_check()

	def select_all(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.select_all()
		
	def copy(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.copy_clipboard()

	def cut(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.cut_clipboard()

	def paste(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.paste_clipboard()

	def delete(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.delete()

	def undo(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.undo()

	def redo(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.redo()

	def increase_font_size(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.change_font_size(True)

	def decrease_font_size(self,wedget,data=None):
		be = self.get_current_focused_braille_editor()
		be.change_font_size(False)


	def tts_say(self,text):
		self.client.speak(text)
		 				



	def quit(self,widget, data=None):
		unsaved = False
		string_unsaved_tab_labels = _("Close ")
		for page_number in range(0, self.notebook.get_n_pages()):
			braille_editor = self.notebook.get_nth_page(page_number)
			if(braille_editor.get_modified()):
				unsaved = True
				label = self.notebook.get_tab_label(braille_editor)
				string_unsaved_tab_labels += label.get_children()[0].get_text()+", "
		
		if(unsaved):
			dialog =  Gtk.Dialog(_("Quit?"), self.window, 0,
			(_("No"), Gtk.ResponseType.NO,_("Quit without saving?"),Gtk.ResponseType.YES))
			label = Gtk.Label(string_unsaved_tab_labels[:-2]+" without saving?")

			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()	
			response = dialog.run()
			dialog.destroy()
			
			# If not quiting return True for keeping window from closing
			if (response != Gtk.ResponseType.YES):
				return	True

		close_tts()
		self.window.destroy()
		Gtk.main_quit()
		
		
if __name__ == "__main__":
	BrailleWriter()
	

#!/usr/bin/env python
# -*- coding: utf-8 -*

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import signal
import gettext
import sys
import threading
import copy
import subprocess
import os
import N4dManager
import xmlrpc.client
import ssl
import time
import Dialog
#import HomeEraserServer

signal.signal(signal.SIGINT, signal.SIG_DFL)
gettext.textdomain('home-eraser-gui')
_ = gettext.gettext



class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)

#class_spinner







class HomeEraser:
	
	net="net"
	home="home"
	students="students"
	teachers="teachers"
	admins="admins"
	
	resume_home={}
	resume_net=[]
	
	#log="/var/log/home_eraser.log"
	
	# ********HACKKKKKK
	server="server"
	
	detect_connected_clients_cancelled=False
	
	DEBUG=True
	
	def dprint(self,arg):
		self.n4d_man.lprint(self.user_val, "[HomeEraserGUI] %s"%arg)
		if HomeEraser.DEBUG:
			print("[HomeEraserGUI] %s"%arg)
		
	#def dprint	
	
	
	def __init__(self,args_dic):
		
		self.perfilreset_bin="/usr/sbin/home-eraser"
		
		self.n4d_man=N4dManager.N4dManager()
		self.n4d_man.set_server(args_dic[self.server])
		
		if args_dic["gui"]:
			
			self.start_gui()
			GObject.threads_init()
			Gtk.main()
		
	#def __init__(self):
	
	
	def start_gui(self):

		builder=Gtk.Builder()
		builder.set_translation_domain('home-eraser-gui')
		builder.add_from_file("/usr/share/home-eraser/rsrc/home-eraser.ui")
		self.main_window=builder.get_object("main_window")
		self.main_window.set_icon_from_file('/usr/share/home-eraser/rsrc/home-eraser-icon.svg')

		self.main_box=builder.get_object("main_box")
		self.login_box=builder.get_object("login_box")
		self.main_content_box=builder.get_object("main_content_box")
		
		self.stack=Gtk.Stack()
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack.set_transition_duration(500)
		self.stack.add_titled(self.login_box,"login","login")
		self.stack.add_titled(self.main_content_box,"main","main")
		
		self.stack.show_all()
		
		self.main_box.pack_start(self.stack,True,True,5)
		
		self.login_button=builder.get_object("login_button")
		self.entry_user=builder.get_object("entry1")
		self.entry_password=builder.get_object("entry2")
		self.login_msg_label=builder.get_object("login_msg_label")
		
		#self.separator3 = builder.get_object("separator3")
		#self.separator4 = builder.get_object("separator4")
		
		self.checkb1 = builder.get_object("checkbutton1")
		self.checkb2 = builder.get_object("checkbutton2")
		self.checkb3 = builder.get_object("checkbutton3")
		self.checkb4 = builder.get_object("checkbutton4")
		self.checkb5 = builder.get_object("checkbutton5")
		self.checkb6 = builder.get_object("checkbutton6")
		self.apply_button=builder.get_object("apply_button")
		self.txt_apply=builder.get_object("txt_apply")
		self.spinner=builder.get_object("spinner")
		
		self.num_clients_glade=builder.get_object("num_clients_glade")
		
		self.set_css_info()
		
		self.connect_signals()
		self.main_window.show()
		
	#def start_gui
	
	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()                     
		f=Gio.File.new_for_path("/usr/share/home-eraser/HomeEraser.css")
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.main_window.set_name("WINDOW")
		
		self.apply_button.set_name("OPTION_BUTTON")
		self.login_button.set_name("OPTION_BUTTON")
		
		#self.entry_user.set_name("OPTION_ENTRY")
		#self.entry_password.set_name("OPTION_ENTRY")
		
		#self.separator3.set_name("OPTION_SEPARATOR")
		#self.separator4.set_name("OPTION_SEPARATOR")
		
		'''self.checkb1.set_name("CHECKMARK")
		self.checkb2.set_name("CHECKMARK")
		self.checkb3.set_name("CHECKMARK")
		self.checkb4.set_name("CHECKMARK")
		self.checkb5.set_name("CHECKMARK")
		self.checkb6.set_name("CHECKMARK")'''
			
	#def set-css_info
	
	
	def connect_signals(self):
			
		self.main_window.connect("destroy",Gtk.main_quit)
		
		self.apply_button.connect("clicked",self.apply_button_clicked)
		
		self.login_button.connect("clicked",self.login_clicked)
		self.entry_password.connect("activate",self.entries_press_event)
		
	#def connect_signals

	# SIGNALS #######################################################	
	
	def entries_press_event(self,entry):
		
		self.login_clicked(None)
		
	#def entries_press_event
	
	def login_clicked(self,button):
		
		self.login_button.set_sensitive(False)
		self.login_msg_label.set_text(_("Validating user..."))
		
		user=self.entry_user.get_text()
		password=self.entry_password.get_text()
		self.user_val=(user,password)
		server="server"
		
		self.validate_user(user,password)
		
	#def login_clicked
	
	def validate_user(self,user,password):
		
		t=threading.Thread(target=self.n4d_man.validate_user,args=(user,password,))
		t.daemon=True
		t.start()
		GLib.timeout_add(500,self.validate_user_listener,t)
		
	#def validate_user
	
	def validate_user_listener(self,thread):
			
		if thread.is_alive():
			return True
				
		self.login_button.set_sensitive(True)
		
		if not self.n4d_man.user_validated:
			self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user, please only net admin users.")+"</span>")
		else:
			group_found=False
			for g in ["admins"]:
				if g in self.n4d_man.user_groups:
					group_found=True
					break

					
			if group_found:
				self.n4d_man.get_client_list()
				# ***START LOG
				self.dprint("")
				self.dprint("** START HOME ERASER GUI **")
				self.dprint("   ---------------------")
				self.dprint("")
				# ##########
				
				self.stack.set_visible_child_name("main")
				self.dprint("Clients connected: %s"%self.n4d_man.detected_clients)
				self.num_clients_glade.set_text(str(self.n4d_man.detected_clients))
				
				t2=threading.Thread(target=self.n4d_man.update_client_list_thread)
				t2.daemon=True
				t2.start()
				
				GLib.timeout_add(5000,self.client_list_listener)
			else:
				self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user, please only net admin users.")+"</span>")
		
	
	
	def client_list_listener(self):
		
		self.num_clients_glade.set_text(str(self.n4d_man.detected_clients))
		return True
		
	#def  client_list_listener



	
	def apply_button_clicked(self,widget=True):
		
		try:			
			
			delete={}
			delete[self.home]=[]
			delete[self.net]=[]
			
			info={}
			info[self.students]={}
			
			
			info[self.students][self.home]=self.checkb1.get_active()
			if info[self.students][self.home]:
				delete[self.home].append("students")
			info[self.students][self.net]=self.checkb4.get_active()
			if info[self.students][self.net]:
				delete[self.net].append("students")
			info[self.teachers]={}
			info[self.teachers][self.home]=self.checkb2.get_active()
			if info[self.teachers][self.home]:
				delete[self.home].append("teachers")
			info[self.teachers][self.net]=self.checkb5.get_active()
			if info[self.teachers][self.net]:
				delete[self.net].append("teachers")
			info[self.admins]={}
			info[self.admins][self.home]=self.checkb3.get_active()
			if info[self.admins][self.home]:
				delete[self.home].append("admins")
			info[self.admins][self.net]=self.checkb6.get_active()
			if info[self.admins][self.net]:
				delete[self.net].append("admins")
			
			
			
			for g in info:
				self.dprint(g)
				for d in info[g]:
					self.dprint("\t %s : %s"%(d,info[g][d]))

			self.dprint("Summary to remove this elements: %s"%(delete))
			
			#Are you sure to delete????
			
			if ( len(delete[self.home]) >0 ) or ( len(delete[self.net]) >0 ):
				
				#dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "HOME ERASER")
				#dialog.format_secondary_text(_("Are you sure you want to delete?"))
				
				dialog=Dialog.QuestionDialog(self.main_window,_(u"HOME ERASER"),_(u"Are you sure you want to delete?"))
				response=dialog.run()
				dialog.destroy()
				#if response == Gtk.ResponseType.YES:
				if response == Gtk.ResponseType.OK:
					
					self.apply_button.set_sensitive(False)
					self.checkb1.set_sensitive(False)
					self.checkb2.set_sensitive(False)
					self.checkb3.set_sensitive(False)
					self.checkb4.set_sensitive(False)
					self.checkb5.set_sensitive(False)
					self.checkb6.set_sensitive(False)
					self.txt_apply.set_text(_("Working........"))
					self.apply_delete_methods_thread(delete)
			else:
				#dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "HOME ERASER")
				#dialog.format_secondary_text(_("You didn't select any option to delete."))
				dialog=Dialog.InfoDialog(self.main_window,_(u"HOME ERASER"),_(u"You didn't select any option to delete."))
				response=dialog.run()
				dialog.destroy()
			
			
		except Exception as e:
			self.dprint(e)
			print ("[HomeEraserGUI](apply_button_clicked) %s"%e)
			return [False,str(e)]
		
	#def check_changes
	
	
	
	def apply_delete_methods_thread(self,delete):
		
		t=threading.Thread(target=self.apply_delete_methods,args=(delete,))
		t.daemon=True
		t.start()
		self.spinner.start()
		GLib.timeout_add(500,self.sure_delete,t)
		
	#apply_delete_methods_thread
	
		
	def sure_delete(self,thread):
		
		try:
			if thread.is_alive():
				return True
			
			self.detect_connected_clients_cancelled=True
			self.spinner.stop()
			self.txt_apply.set_markup("<span foreground='blue'>"+_("Finished. Log is found in /var/log/home-eraser.log ")+"</span>")


			#Do you want to execute again? or Exit.
			dialog=Dialog.QuestionDialog(self.main_window,_(u"HOME ERASER"),_(u"Do you want to execute it again?"))
			response=dialog.run()
			dialog.destroy()
			#if response == Gtk.ResponseType.YES:
			if response == Gtk.ResponseType.OK:
				
				self.apply_button.set_sensitive(True)
				self.checkb1.set_sensitive(True)
				self.checkb2.set_sensitive(True)
				self.checkb3.set_sensitive(True)
				self.checkb4.set_sensitive(True)
				self.checkb5.set_sensitive(True)
				self.checkb6.set_sensitive(True)

			else:
				#Gtk.main_quit()
				#sys.exit(0)
				pass
			
		except Exception as e:
			self.dprint(e)
			print ("[HomeEraserGUI](sure_delete) %s"%e)
			return [False,str(e)]
		
	#def_sure_delete
		
	
	
	def apply_delete_methods(self,delete):
		
		try:
			
			
			
			#DELETE LOCAL HOMES IN FAT CLIENTS
			if ( len(delete[self.home] ) > 0 ):
				ips_detele=self.n4d_man.ips_connected
				self.dprint("Apply to clients: %s"%(ips_detele))
				r=self.n4d_man.delete_clients_homes(self.user_val,ips_detele, delete[self.home])
				if r[0]:
					#shared in resume all ips and paths deleted
					self.resume_home={**self.resume_home,**r[1]}
			
			#print resume home deleted in fat clients
			if (  len(self.resume_home) >0 ):
				self.dprint("")
				self.dprint("Summary for HOMES deleted")
				for i in self.resume_home:
					self.dprint("%s : %s"%(i,self.resume_home[i]))
			
			
			#DELETE /NET DIRECTORIES
			if ( len(delete[self.net] ) > 0 ):
				rnet=self.n4d_man.delete_net_homes(self.user_val,delete[self.net])
				if rnet[0]:
					self.resume_net=rnet[1]
					if self.resume_net:
						self.dprint("")
						self.dprint("Summary for paths in /NET deleted:")
						for i in rnet[1]:
							self.dprint(i)
			
			
			
			return[True,self.resume_home,self.resume_net]
					
		except Exception as e:
			self.dprint(e)
			print ("[HomeEraserGUI](apply_delete_methods)%s"%e)
			return [False,str(e)]
		
		
	#def_apply_delete_methods


#class LliurexPerfilreset


if __name__=="__main__":
	
	pass
	

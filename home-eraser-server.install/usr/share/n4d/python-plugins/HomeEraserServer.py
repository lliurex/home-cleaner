import os
import pwd
import logging
import shutil

import n4d.server.core
import n4d.responses

class HomeEraserServer:
	
	logging.basicConfig(format = '%(asctime)s %(message)s',datefmt = '%m/%d/%Y %I:%M:%S %p',filename = '/var/log/home-eraser.log',level=logging.DEBUG)
	
	DEBUG=True
	
	def lprint(self,arg):
		
		logging.debug(arg)
		return n4d.responses.build_successful_call_response(0)
		
	#def_lprint
	
	def dprint(self,arg):
		
		self.lprint("[HomeEraserServer] %s"%arg)
		if HomeEraserServer.DEBUG:
			print("[HomeEraserServer] %s"%arg)
		
	#def dprint
	
	def delete_home(self,groups_delete=[]):
		
		home_dir="/home"
		run_dir="/run"
		home_list={}
		deleted=[]
		
		try:
			self.dprint("****************************")
			self.dprint("*********** APPLY **********")
			self.dprint("")
			self.dprint("Groups to deleted: %s"%groups_delete)

			if ( len(groups_delete) > 0 ):

				for dirname in os.listdir(home_dir):
					 
					dir_path=os.path.join(home_dir,dirname)
					self.dprint("")
					self.dprint("Discover in home: %s"%dir_path)
					self.dprint("-----------------------------")
						
					if ( os.path.islink(dir_path) == False) & ( os.path.isfile(dir_path) == False ):
						run_path=os.path.join(run_dir,dirname)
						run_path_home=os.path.join(run_path,"home")
						run_path_share=os.path.join(run_path,"share")

						if ( os.path.ismount(run_path_home) == False ) & ( os.path.ismount(run_path_share) == False ):

							self.dprint("Directory can be deleted: %s"%(dirname))
							try:
								ownername= pwd.getpwuid(os.stat(dir_path).st_uid).pw_name
							except:
								ownername="unknow"
								self.dprint("Ownername is unknow for %s"%dir_path)
							
							#uid=pwd.getpwuid(os.stat(dir_path).st_uid).pw_uid
							try:
								uid=os.stat(dir_path).st_uid
								
							except:
								uid="0"
								self.dprint("UID is unknow for %s"%dir_path)
								
							self.dprint("Testing group for: %s    with uid: %s"%(dir_path,uid))
							self.dprint("In groups: %s"%groups_delete)
							insert_to_delete_solved=self.insert_to_delete(uid, groups_delete)
							self.dprint('insert_to_delete_solved: %s'%insert_to_delete_solved)
							#self.dprint(type(insert_to_delete_solved['return'][0]))
							insert_to_delete_solved=insert_to_delete_solved['return'][0]
							if insert_to_delete_solved:
								self.dprint("RESUME: +++++...ADDED to delete list")
								home_list[dirname]={}
								home_list[dirname]["path"]=dir_path
								home_list[dirname]["owner"]=ownername
								home_list[dirname]["uid"]=uid
							else:
								self.dprint("RESUME: Cannot be deleted because is not in group allowed")
						else:
							self.dprint("RESUME: Cannot be deleted because this user has folders mounted.")
				
				self.dprint("------------------")
				self.dprint("Resume paths to delete: %s"%home_list)
	
				
				if ( len(home_list) > 0 ):
					deleted=self.delete_home_local(home_list)['return'][1]

			return n4d.responses.build_successful_call_response([True, deleted])
		
		except Exception as e:
			print ("[HomeEraserServer](delete_home) %s"%e)
			self.dprint ("[HomeEraserServer](delete_home) %s"%e)
			return n4d.responses.build_successful_call_response([False, str(e)])
			
	#def_delete_home
		
		
		
		
	def insert_to_delete (self,uid=0,groups_delete=[]):
		
		try:		
			for group in groups_delete:
				self.dprint(group)
				if ( str(group) == "students" ):
					self.dprint("testing group students.....")
					arg1=20000
					arg2=50000
					if self.test_user(uid,arg1,arg2)['return'][0]:
						return n4d.responses.build_successful_call_response([True])
					
				elif ( str(group) == "teachers" ):
					self.dprint("testing group teachers.....")
					arg1=5000
					arg2=10000
					if self.test_user(uid,arg1,arg2)['return'][0]:
						return n4d.responses.build_successful_call_response([True])
					
				elif ( str(group) == "admins" ):
					self.dprint("testing group admins.....")
					arg1=1042
					arg2=5000
					if self.test_user(uid,arg1,arg2)['return'][0]:
						return n4d.responses.build_successful_call_response([True])
				else:
					self.dprint("....this group cannot be deleted")
					
			return n4d.responses.build_successful_call_response([False])
			
		
		except Exception as e:
			print ("[HomeEraserServer](insert_to_delete) %s"%e)
			self.dprint ("[HomeEraserServer](insert_to_delete) %s"%e)
			return n4d.responses.build_successful_call_response([False, str(e)])
			
	#def_insert_to_delete


	
	
	def test_user(self,uid=0,arg1=0,arg2=0):
		
		try:
			if (  uid >= arg1 ) & ( uid  < arg2  ):
				self.dprint("....is include in selected groups to delete")
				return n4d.responses.build_successful_call_response([True])
			else:
				return n4d.responses.build_successful_call_response([False])
			
		except Exception as e:
			print ("[HomeEraserServer](test_user) %s"%e)
			self.dprint ("[HomeEraserServer](test_user) %s"%e)
			return n4d.responses.build_successful_call_response([False, str(e)])
			
	#def_test_user




	def delete_home_local(self, home_list={}):
		
		deleted=[]
		
		try:
			for delete in home_list:
					#INSTRUCCION PARA EL BORRADO DEL DIRECTORIO
					self.dprint("Path deleted: %s"%home_list[delete]["path"] )
					deleted.append(home_list[delete]["path"])
					try:
						shutil.rmtree(home_list[delete]["path"])
					except Exception as r_ex:
						self.dprint("[HomeEraserServer] %s"%r_ex)
					
					
			self.dprint("Deleted this paths: %s"%deleted)
			return n4d.responses.build_successful_call_response([True,deleted])
		
		except Exception as e:
			print ("[HomeEraserServer](delete_home_local) %s"%e)
			self.dprint("[HomeEraserServer](delete_home_local) %s"%e)
			return n4d.responses.build_successful_call_response([False, str(e)])
			
	#def_delete_home_local
	
	
	
	
	
	
	def delete_net_home(self,groups_delete=[]):
		
		net_dir="/net/server-sync/home/"
		net_list={}
		deleted=[]
		
		try:
			self.dprint("*********************")
			self.dprint("*********** DELETING /NET DIRECTORIES **********")
			self.dprint("")
			self.dprint("Groups to deleted: %s"%groups_delete)

			if ( len(groups_delete) > 0 ):
				
				for group in groups_delete:
					
					self.dprint("-----------------------------")
					dir_delete_path=os.path.join(net_dir,group)
					self.dprint("Deleting users from: %s"%(dir_delete_path))
					
					for dirname in os.listdir(dir_delete_path):
						
						dir_path=os.path.join(dir_delete_path,dirname)
						self.dprint("")
						self.dprint("Discover in net: %s"%dir_path)
						if ( os.path.islink(dir_path) == False) & ( os.path.isfile(dir_path) == False ):
							self.dprint("Adding to to delete.....")
							net_list[dirname]={}
							net_list[dirname]["path"]=dir_path
				self.dprint("------------RESUME-------------")			
				self.dprint("Deleting this paths: %s"%net_list)	
				ret=self.delete_home_local(net_list)
				self.dprint('(delete_net_home) self.delete_home_local(net_list): %s'%ret)
				ret_solved=ret['return'][0]
				if ret_solved:
					deleted=deleted+ret['return'][1]
			self.dprint('(delete_net_home) deleted: %s'%deleted)
			if len(deleted)>0:
				self.dprint('(delete_net_home) Executing Golem....')
				#objects["Golem"].regenerate_net_files()
				resolved=n4d.server.core.Core.get_core().get_plugin("Golem").regenerate_net_files()

				self.dprint("(delete_net_home) Golem solved: %s"%resolved)

			return n4d.responses.build_successful_call_response([True, deleted])
		
		except Exception as e:
			print ("[HomeEraserServer](delete_net_home) %s"%e)
			self.dprint ("(delete_net_home) %s"%e)
			return n4d.responses.build_successful_call_response([False, str(e)])
	#def_delete_net_home
		
#class HomeEraserServer

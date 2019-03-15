import xmlrpc.client
import ssl
import threading
import time


class N4dManager:
	
	def __init__(self,server=None):
		
		self.debug=False
		
		self.user_validated=False
		self.client=None
		self.user_val=()
		self.user_groups=[]
		self.validation=None
		self.detected_clients=0
		self.ips_connected=[]

		if server!=None:
			self.set_server(server)
		
	#def init
	
	def lprint(self,validation,arg):
		
		self.client.lprint(validation,"HomeEraserServer", arg)
		
	#def_lprint
	
	
	def mprint(self,msg):
		
		if self.debug:
			print("[HomeEraserN4DManager] %s"%str(msg))
			
	#def mprint
		
	
	def set_server(self,server):
		
		context=ssl._create_unverified_context()	
		self.client=xmlrpc.client.ServerProxy("https://%s:9779"%server,allow_none=True,context=context)
		self.mprint("Proxy: %s"%self.client)
		
	#def set_server
	
	
	def validate_user(self,user,password):
		
		ret=self.client.validate_user(user,password)
		self.user_validated,self.user_groups=ret
			
		
		if self.user_validated:
			self.user_val=(user,password)
		
		return [self.user_validated, self.user_val]
		
	#def validate_user
	
	def delete_net_homes(self,validation,groups_to_delete):
				
		resume=[]
		
		try:
			context=ssl._create_unverified_context()
			tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			resolve=tmp.delete_net_home(validation,"HomeEraserServer", groups_to_delete)
			if resolve[0]:
				resume=resolve[1]
					
			return[True,resume]
	
		except Exception as e:
			print ("[HomeEraserN4DManager] ERROR: %s"%e)
			self.lprint (validation,"[HomeEraserServer] %s"%e)
			return [False,str(e)]	
		
	#def delete_net_homes
	
	
	
	
	
	def delete_clients_homes(self,validation,clients,groups_to_delete):
				
		resume={}
		
		try:
			context=ssl._create_unverified_context()
			#Delete homes in Fat clients
			if ( len(clients) > 0 ):
				for ip in clients:
					self.mprint("Deleting client: %s"%ip)
					tmp=xmlrpc.client.ServerProxy("https://%s:9779"%ip,allow_none=True,context=context)
					resolve=tmp.delete_home(validation,"HomeEraserClient", groups_to_delete)
					if resolve[0]:
						resume[ip]=resolve[1]
				
			#Delete homes in Server
			tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			resolve=tmp.delete_home(validation,"HomeEraserServer", groups_to_delete)
			if resolve[0]:
				resume["server"]=resolve[1]
					
			return[True,resume]
	
		except Exception as e:
			print ("[HomeEraserN4DManager] ERROR: %s"%e)
			self.lprint (validation,"[HomeEraserServer] %s"%e)
			return [False,str(e)]	
		
	#def delete_clients_homes
	
	
	
	def get_client_list(self):
		
		try:
			self.ips_connected=[]
			self.mprint(self.client.manual_client_list_check(self.user_val,"VariablesManager"))
			self.ret=self.client.get_client_list("","VariablesManager")
			
			count=0
			for item in self.ret:
				if self.ret[item]["missed_pings"]<1:
					count+=1
				self.ips_connected.append(self.ret[item]["ip"])
					
			self.detected_clients=count
			self.mprint("Clients connected N4D: %s"%self.detected_clients)
			
		except Exception as e:
			print ("[HomeEraserN4DManager] ERROR: %s"%e)
			return [False,str(e)]	
			
	#def get_client_list
	
	
	def update_client_list_thread(self):
		
		try:
			while True:
				time.sleep(5)
				self.get_client_list()
				self.mprint("Clients connected Thread: %s"%self.detected_clients)
		
		except Exception as e:
			print ("[HomeEraserN4DManager] ERROR: %s"%e)
			return [False,str(e)]
			
	#def update_client_list_thread
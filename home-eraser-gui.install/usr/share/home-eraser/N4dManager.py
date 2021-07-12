import xmlrpc.client
import ssl
import threading
import time
import n4d.client
import n4d.server.core
import os


class N4dManager:

	
	def __init__(self,server=None):
		
		self.debug=True
		
		self.user_validated=False
		self.client=None
		self.user_val=()
		self.user_groups=[]
		self.validation=None
		self.detected_clients=0
		self.ips_connected=[]

		#self.core=n4d.server.core.Core.get_core()

		if server!=None:
			self.set_server(server)
		
	#def init



	
	def lprint(self,validation,arg):
		
		#self.client.lprint(validation,"HomeEraserServer", arg)
		self.client.HomeEraserServer.lprint(arg)
		
	#def_lprint
	
	



	def mprint(self,msg):
		
		if self.debug:
			print("[HomeEraserN4DManager] %s"%str(msg))
			
	#def mprint
		
	



	def set_server(self,server):
		
		#context=ssl._create_unverified_context()	
		#self.client=xmlrpc.client.ServerProxy("https://%s:9779"%server,allow_none=True,context=context)

		self.server="https://%s:9779"%server
		self.mprint("Proxy: %s"%self.client)
		
	#def set_server



	
	
	def validate_user(self,user,password):
		
		'''ret=self.client.validate_user(user,password)
		self.user_validated,self.user_groups=ret
			
		
		if self.user_validated:
			self.user_val=(user,password)
		
		return [self.user_validated, self.user_val]'''
		try:
			self.client=n4d.client.Client(self.server,user,password)

			ret=self.client.validate_user()
			self.user_validated=ret[0]
			self.user_groups=ret[1]
			self.credentials=[user,password]
		
			if self.user_validated:
				session_user=os.environ["USER"]
				self.ticket=self.client.get_ticket()
				if self.ticket.valid():
					self.client=n4d.client.Client(ticket=self.ticket)
					msg_log="Session User: %s"%session_user+" HomeEraser User: %s"%user
					self.mprint(msg_log)
					
					self.local_client=n4d.client.Client("https://localhost:9779",user,password)
					local_t=self.local_client.get_ticket()
					if local_t.valid():
						self.local_client=n4d.client.Client(ticket=local_t)
					else:
						self.user_validated=False	
				else:
					self.user_validated=False
			self.mprint(self.user_groups)

		except Exception as e:
			msg_log="(validate_user)Session User Error: %s"%(str(e))
			self.mprint(msg_log)
			self.user_validated=False
	
		
	#def validate_user




	
	def delete_net_homes(self,validation,groups_to_delete):
				
		resume=[]
		
		try:
			#context=ssl._create_unverified_context()
			#tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			#resolve=tmp.delete_net_home(validation,"HomeEraserServer", groups_to_delete)
			resolve=self.client.HomeEraserServer.delete_net_home(groups_to_delete)
			self.mprint('resolve: %s'%resolve)
			if not resolve[0]:
				print ("[HomeEraserN4DManager](delete_net_homes) ERROR: %s"%resolve[1])
				return [False,resolve[1]]
			else:
				resume=resolve[1]
					
			return[True,resume]
	
		except Exception as e:
			print ("[HomeEraserN4DManager](delete_net_homes) ERROR: %s"%e)
			self.lprint (validation,"[HomeEraserServer](delete_net_homes) %s"%e)
			return [False,str(e)]	
		
	#def delete_net_homes
	
	
	
	
	
	def delete_clients_homes(self,validation,clients,groups_to_delete):
				
		resume={}
		resume_fail={}
		
		try:
			context=ssl._create_unverified_context()
			#Delete homes in Fat clients
			if ( len(clients) > 0 ):
				for ip in clients:
					self.mprint("Deleting client: %s"%ip)
					#ANTIGUA LLAMADA N4D
					try:
						tmp=xmlrpc.client.ServerProxy("https://%s:9779"%ip,allow_none=True,context=context)
						resolve=tmp.delete_home(validation,"HomeEraserClient", groups_to_delete)
					except Exception as e:
						print ("[HomeEraserN4DManager](delete_clients_homes) ERROR: %s"%e)
						self.lprint (validation,"[HomeEraserServer](delete_clients_homes) %s"%e)
					#resolve=self.client.HomeEraserClient.delete_home(groups_to_delete)
					self.mprint("[HomeEraserN4DManager](delete_clients_homes) resolve IP: %s: %s"%(ip,resolve))
					if resolve['return'][0]:
						resume[ip]=resolve['return'][1]
					else:
						resume_fail[ip]=resolve['return'][1]
						
			#Delete homes in Server
			#ANTIGUA LLAMADA N4D
			#tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			#resolve=tmp.delete_home(validation,"HomeEraserServer", groups_to_delete)
			resolve=self.client.HomeEraserServer.delete_home(groups_to_delete)
			self.mprint("[HomeEraserN4DManager](delete_clients_homes) resolve In server: %s"%(resolve))
			if resolve[0]:
				resume["server"]=resolve[1]
					
			return[True,resume,resume_fail]
	
		except Exception as e:
			print ("[HomeEraserN4DManager](delete_clients_homes) ERROR: %s"%e)
			self.lprint (validation,"[HomeEraserServer](delete_clients_homes) %s"%e)
			return [False,str(e)]	
		
	#def delete_clients_homes
	
	


	
	def get_client_list(self):
		
		try:
			self.ips_connected2=[]
			#Forzar la lectura del listado de clientes
			#self.mprint(self.client.manual_client_list_check("","VariablesManager"))
			self.mprint(self.client.check_clients(True))
			#self.ret=self.client.get_client_list("","VariablesManager")
			self.ret=self.client.get_client_list()
			
			
			count=0
			for item in self.ret:
				if self.ret[item]["missed_pings"]<1:
					count+=1
				self.ips_connected2.append(self.ret[item]["ip"])
			
			self.ips_connected=self.ips_connected2		
			self.detected_clients=count
			self.mprint("Clients connected N4D: %s"%self.detected_clients)
			
		except Exception as e:
			print ("[HomeEraserN4DManager](get_client_list) ERROR: %s"%e)
			return [False,str(e)]	
			
	#def get_client_list
	
	



	def update_client_list_thread(self):
		
		try:
			while True:
				time.sleep(5)
				self.get_client_list()
				self.mprint("Clients connected Thread: %s"%self.detected_clients)
		
		except Exception as e:
			print ("[HomeEraserN4DManager](update_client_list_thread) ERROR: %s"%e)
			return [False,str(e)]
			
	#def update_client_list_thread
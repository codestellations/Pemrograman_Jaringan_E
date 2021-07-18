import sys
import os
import json
import base64
import uuid
import logging
from queue import  Queue

class Chat:
	def __init__(self):
		self.sessions={}
		self.users = {}
		self.users['messi']={ 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming' : {}, 'outgoing': {}}
		self.users['henderson']={ 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
		self.users['lineker']={ 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya','incoming': {}, 'outgoing':{}}
		self.group = {}
		self.group['grup3'] = ['messi', 'henderson', 'lineker']
	def proses(self,data):
		j=data.split(" ")
		try:
			command=j[0].strip()
			if (command=='auth'):
				username=j[1].strip()
				password=j[2].strip()
				logging.warning("AUTH: auth {} {}" . format(username,password))
				return self.autentikasi_user(username,password)
			elif (command=='send'):
				sessionid = j[1].strip()
				usernameto = j[2].strip()
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,usernameto))
				return self.send_message(sessionid,usernamefrom,usernameto,message)
			elif (command=='inbox'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				logging.warning("INBOX: {}" . format(sessionid))
				return self.get_inbox(username)
			# create group message
			elif (command=='creategroup'):
				sessionid = j[1].strip()
				groupname = j[2].strip()
				usernamelist = []
				for u in j[3:]:
					usernamelist.append(u)
				usernamefrom = self.sessions[sessionid]['username']
				usernamelist.append(usernamefrom)
				if('\r\n' in usernamelist):
					usernamelist.remove('\r\n')
				logging.warning("CREATE: session {} group message {} with {}" . format(sessionid, groupname, usernamelist))
				return self.create_group_message(sessionid, groupname, usernamelist)
			# send group message
			elif (command=='sendgroup'):
				sessionid = j[1].strip()
				groupname = j[2].strip()
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send group message from {} to {}" . format(sessionid, usernamefrom,groupname))
				return self.send_group_message(sessionid, usernamefrom, groupname, message)
			# send file
			elif (command=='sendfile'):
				sessionid = j[1].strip()
				usernameto = j[2].strip()
				filename = j[3].strip()
				filedata = str.encode(j[4].strip())
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send file from {} to {}".format(sessionid, usernamefrom, usernameto))
				return self.send_file(sessionid, usernamefrom, usernameto, filename, filedata)
			# get all users
			elif (command=='getallusers'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				logging.warning("GET ALL USERS: {}" . format(sessionid))
				return self.get_all_users()
			# get all groups
			elif (command=='getallgroups'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				logging.warning("GET ALL GROUPS: {}" . format(sessionid))
				return self.get_all_groups(username)
			else:
				return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}
		except KeyError:
			return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
		except IndexError:
			return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}
	def autentikasi_user(self,username,password):
		if (username not in self.users):
			return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
		if (self.users[username]['password']!= password):
			return { 'status': 'ERROR', 'message': 'Password Salah' }
		tokenid = str(uuid.uuid4()) 
		self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
		return { 'status': 'OK', 'tokenid': tokenid }
	def get_user(self,username):
		if (username not in self.users):
			return False
		return self.users[username]
	def send_message(self,sessionid,username_from,username_dest,message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)
		
		if (s_fr==False or s_to==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
		outqueue_sender = s_fr['outgoing']
		inqueue_receiver = s_to['incoming']
		try:	
			outqueue_sender[username_from].put(message)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message)
		try:
			inqueue_receiver[username_from].put(message)
		except KeyError:
			inqueue_receiver[username_from]=Queue()
			inqueue_receiver[username_from].put(message)
		return {'status': 'OK', 'message': 'Message Sent'}

	# create group message
	def create_group_message(self, sessionid, group_name, username_list):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}

		group_username_list = []
		for u in username_list:
			if(self.get_user(u) == False):
				print(self.get_user(u))
				return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
			group_username_list.append(u)

		self.group[group_name] = group_username_list

		return {'status': 'OK', 'message': 'Group Created'}

	# send group message
	def send_group_message(self, sessionid, username_from, groupname, message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_group_user(groupname)

		if (s_fr == False or s_to == False):
			return {'status': 'ERROR', 'message': 'User atau Group Tidak Ditemukan'}

		message = {'msg_from': s_fr['nama'], 'msg_to': groupname, 'msg': message}
		for u in s_to:
			if(u != s_fr):
				outqueue_sender = s_fr['outgoing']
				u = self.get_user(u)
				inqueue_receiver = u['incoming']
				try:
					outqueue_sender[username_from].put(message)
				except KeyError:
					outqueue_sender[username_from] = Queue()
					outqueue_sender[username_from].put(message)
				try:
					inqueue_receiver[username_from].put(message)
				except KeyError:
					inqueue_receiver[username_from] = Queue()
					inqueue_receiver[username_from].put(message)

		return {'status': 'OK', 'message': 'Group Message Sent'}

	# get group user
	def get_group_user(self,groupname):
		if (groupname not in self.group):
			return False
		return self.group[groupname]

	# send file
	def send_file(self, sessionid, username_from, username_dest, filename, filedata):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)

		if (s_fr == False or s_to == False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		dirname = './file/' + username_dest

		if (os.path.isdir(dirname) == False):
			os.mkdir(dirname)
			# print('Direktori file/' + username_dest + ' berhasil dibuat')

		name = dirname + '/from_' + username_from + '_' + filename
		file_to = open(name, 'wb')

		decoded = base64.b64decode(filedata)
		file_to.write(decoded)

		file_message = "Kamu menerima file " + filename + " dari " + username_from
		self.send_message(sessionid, username_from, username_dest, file_message)

		return {'status': 'OK', 'message': 'File Sent'}

	def get_inbox(self,username):
		s_fr = self.get_user(username)
		incoming = s_fr['incoming']
		msgs={}
		for users in incoming:
			msgs[users]=[]
			while not incoming[users].empty():
				msgs[users].append(s_fr['incoming'][users].get_nowait())

		return {'status': 'OK', 'messages': msgs}

	def get_all_users(self):
		users = [*self.users]
		return {'status': 'OK', 'message': 'All Users Get', 'userlist': users}
	
	def get_all_groups(self, username):
		#group_list = {}
		groups = []
		for key, value in self.group.items():
			if username in value:
				groups.append(key)
				print(groups)
				#group_list[key] = value
				#print(group_list)

		return {'status': 'OK', 'message': 'All Groups Get', 'grouplist': groups}


if __name__=="__main__":
	j = Chat()
	sesi = j.proses("auth messi surabaya")
	print(sesi)
	tokenid = sesi['tokenid']

	# filename = './chat_client.py'
	# data = open(filename, 'rb').read()
	# encoded = base64.b64encode(data)
	# encoded = encoded.decode('utf-8') # convert from bytes to str
	#
	# print(j.proses("sendfile {} henderson {} {} ".format(tokenid,os.path.basename(filename),encoded)))

	# group message test
	# create group message
	# print(j.proses("creategroup {} tesgroup henderson lineker" . format(tokenid)))
	# print(j.get_group_user("grup3"))
	# # send group message
	# print(j.proses("sendgroup {} grup3 halo semua" . format(tokenid)))
	# sesi = j.proses("auth henderson surabaya")
	# tokenid = sesi['tokenid']
	# print(j.proses("sendgroup {} grup3 halo juga".format(tokenid)))
	# print("isi mailbox dari messi")
	# print(j.get_inbox('messi'))
	# print("isi mailbox dari henderson")
	# print(j.get_inbox('henderson'))
	# print("isi mailbox dari lineker")
	# print(j.get_inbox('lineker'))
	# print(j.get_all_users())
	# print(j.get_all_groups('messi'))

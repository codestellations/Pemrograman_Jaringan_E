import socket
import os
import json
import base64

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889


class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""

    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmessage(usernameto,message)
            elif (command=='inbox'):
                return self.inbox()
            # create group message
            elif (command=='creategroup'):
                groupname = j[1].strip()
                usernamelist = []
                for u in j[2:]:
                    usernamelist.append(u)
                # if(usernamelist):
                #     usernamefrom = self.username
                #     usernamelist.append(usernamefrom)
                print(usernamelist)
                return self.creategroup(groupname, usernamelist)
            # send group message
            elif (command=='sendgroup'):
                groupname = j[1].strip()
                message = ""
                for w in j[2:]:
                    message = "{} {}".format(message, w)
                return self.sendgroup(groupname, message)
            # send file
            elif (command=='sendfile'):
                usernameto = j[1].strip()
                filepath = j[2].strip()
                for w in j[3:]:
                    filepath = "{} {}".format(filepath, w)

                filename = os.path.basename(filepath)
                filename = filename.replace(" ", "-")
                print(filepath)

                data = open(filepath, 'rb').read()
                # print(data)
                filedata = base64.b64encode(data)       # convert to base64
                filedata = filedata.decode('utf-8')     # convert to str from bytes

                return self.sendfile(usernameto, filename, filedata)
            elif (command == 'getallusers'):
                return self.getallusers()
            elif (command == 'getallgroups'):
                return self.getallgroups()
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                print("diterima dari server",data)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}
    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])

    # create group message
    def creategroup(self,groupname="xxx",usernamelist=[]):
        if(usernamelist==[]):
            return "Error, no user added"
        usernameTo = ' '.join(map(str, usernamelist))
        if (self.tokenid==""):
            return "Error, not authorized"
        string="creategroup {} {} {} \r\n" . format(self.tokenid,groupname,usernameTo)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Group {} created" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])

    # send group message
    def sendgroup(self,groupname="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgroup {} {} {} \r\n" . format(self.tokenid,groupname,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])

    # send file
    def sendfile(self,usernameto="xxx",filename="xxx", filedata="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendfile {} {} {} {}\r\n" . format(self.tokenid,usernameto,filename,filedata)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])

    # get all users
    def getallusers(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="getallusers {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['userlist']))
        else:
            return "Error, {}" . format(result['message'])

    # get all groups
    def getallgroups(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="getallgroups {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['grouplist']))
        else:
            return "Error, {}" . format(result['message'])

if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))


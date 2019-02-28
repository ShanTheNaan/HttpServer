#CS560 Programming Assignment 1
#server.py - an implementation of a web server using sockets
#Michael Price and Shan Lalani

import socket
import os
import sys

def create_dir_html(dir_name):
    #generates http response for a directory
    cwd = os.getcwd()
    if(dir_name[-1] != '/'):
        dir_name += '/'
    
    curr_path = dir_name.replace(cwd, '')
    f = "<html>\n<head>\n<title>Directory: "+curr_path+"</title>\n</head>\n<body>\n"
    f += "Directory of "+curr_path+"<br><br>\n"
    f += "<a href = \""+ "../" + "\">..</a><br>\n"
    for file in os.listdir(dir_name):
        filename = os.fsdecode(file)
        if (os.path.isdir(dir_name+'/'+filename)):
            filename += '/'
        f += "<a href = \"" + filename+"\">"+filename+"</a><br>\n"
    f += "</body>\n</html>"
    return f.encode('utf-8')


HOST, PORT = '',6969
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind ((HOST, PORT))
    
    s.listen (10)
    print ('Serving piping hot HTTP on port %s' % PORT)
    
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        if not data:
            continue
        
        data = data.decode('utf-8')
        print(data)
        
        data = data.split(' ')
        rqfile = data[1]
        
        if (data[0] == "POST"): 
            try:
                first = True
                while True:
                    conn.settimeout(1)
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    if (first):
                        data = data.strip().split(b'\r\n\r\n')
                        fileName = data[0].split(b'\r\n')[-2].decode('utf-8').split("\"")[-2]
                        boundry = data[0].decode('utf-8').split('\r\n')[0]
                        fileData = data[1]
                        first = False
                    else:
                        fileData += data


            except socket.timeout:
                boundry = ("\r\n" + boundry).encode('utf-8')
                fileData = fileData.split(boundry)[0]

                f = open("uploads/"+fileName, "wb")
                f.write(fileData)
                f.close()

                header = 'HTTP/1.1 200 OK\n\n'
                http_response = create_dir_html(os.getcwd()+'/uploads')


        else:
            if (rqfile == '/'):
                rqfile = '/index.html'

            try:
                rqfile = sys.path[0] + rqfile
                if (os.path.isdir(rqfile)):
                    header = 'HTTP/1.1 200 OK\n\n'
                    http_response = create_dir_html(rqfile)
                else:
                    f = open(rqfile,'rb')
                    http_response = f.read()
                    f.close()
                
                    header = 'HTTP/1.1 200 OK\n'
                    if(rqfile.endswith('.jpg')):
                        mime  = "image/jpg"
                    elif(rqfile.endswith('.png')):
                        mime = 'image/png'
                    elif(rqfile.endswith('.txt')):
                        mime = 'text/txt'
                    else:
                        mime = "text/html"
                    
                    header += 'Content-Type: '+str(mime)+'\n\n'
            
            except Exception:
                #default to 404 for invalid requests
                header = 'HTTP/1.1 404 Not Found\n\n'
                http_response = """<html><body><center><h3>Error 404: File not found</h3>
                <p>Go home user, you\'re drunk.</p></center></body></html>"""
                http_response = http_response.encode('utf-8')
    
        response = header.encode('utf-8')
        response += http_response
        conn.send(response)
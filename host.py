import socket

s = socket.socket()
port = 1247
host = "127.0.0.1"
s.bind((host, port))
s.listen(5)
while True:
    c, addr = s.accept()
    print("Connection accepted from " + repr(addr[1]))
    msg = c.recv(4096)
    print(msg.decode())
    c.send("Server approved connection\n".encode())
    # print(repr(addr[1]) + ": " + c.recv(1026))
    c.close()

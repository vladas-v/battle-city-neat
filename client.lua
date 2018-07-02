local host, port = "127.0.0.1", 1247
local socket = require("socket")
local tcp = assert(socket.tcp())

tcp:connect(host, port);
tcp:send("hello\n")
line = tcp:receive()
print(line)
tcp:close()

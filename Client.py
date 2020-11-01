import socket
import json

# Server Addresses
serverAAddressPort = ("127.0.0.1", 1000)
serverBAddressPort = ("127.0.0.1", 1001)
bufferSize = 1024

# Client info
ip_address = "127.0.0.1"
socket_number = "22"

registerMessage = {"request_type": "REGISTER", "rq_number": 1, "name": "Khendek", "ip": ip_address, "socket": socket_number}
registerMessageJson = json.dumps(registerMessage)
registerMessageBytes = str.encode(registerMessageJson)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send register request to both servers
UDPClientSocket.sendto(registerMessageBytes, serverAAddressPort)
#UDPClientSocket.sendto(registerMessageBytes, serverBAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from Server {}".format(msgFromServer[0])
print(msg)

# TODO: setup while for more actions client side
# TODO: add client de-registering


# x = 0
# while x < 2:
#     if x == 0:
#
#     else:
#         UDPClientSocket.sendto(bytesToSend2, serverAddressPort)
#
#     msgFromServer = UDPClientSocket.recvfrom(bufferSize)
#     msg = "Message from Server {}".format(msgFromServer[0])
#     print(msg)
#     x+=1
#

import socket

msgFromClient = "hello"
msgFromClient2 = "192.128.22.11, GregPC"

bytesToSend = str.encode(msgFromClient)
bytesToSend2 = str.encode(msgFromClient2)

serverAddressPort = ("127.0.0.1", 20001)

bufferSize = 1024

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
x = 0
while x < 2:
    if x == 0:
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    else:
        UDPClientSocket.sendto(bytesToSend2, serverAddressPort)

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Message from Server {}".format(msgFromServer[0])
    print(msg)
    x+=1


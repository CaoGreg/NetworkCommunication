import socket

localIP = "127.0.0.1"

localPort = 20001

bufferSize = 1024

msgFromServer = "Please enter your ip and hostname"
msgFromServer2 = "Thx bruh"

bytesToSend = str.encode(msgFromServer)
bytesToSend2 = str.encode(msgFromServer2)

# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams

while (True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP = "Client IP Address:{}".format(address)
    print(str(message))
    if str(message) == "b'hello'":
        UDPServerSocket.sendto(bytesToSend, address)
    else:
        UDPServerSocket.sendto(bytesToSend2, address)

    print(clientMsg)
    print(clientIP)

    # Sending a reply to client


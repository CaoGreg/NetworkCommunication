import socket
import threading
import time
import logging
import json

# Server A information
serverIP = "127.0.0.1"
serverPort = 1000
bufferSize = 1024

# msgFromServer = "Please enter your ip and hostname"
# msgFromServer2 = "Thx bruh"
#
# bytesToSend = str.encode(msgFromServer)
# bytesToSend2 = str.encode(msgFromServer2)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((serverIP, serverPort))

#Log server A is up
f = open("ServerALog.txt", "w")
f.write("Server A is up and listening")
f.close()


# Listen for incoming messages
def listen_for_messages():
    logging.info("Thread %s: starting", "Message Listener")
    thread_list = []
    tempcount = 0
    while tempcount < 2:
        bytes_address_pair = UDPServerSocket.recvfrom(bufferSize)
        message = (bytes_address_pair[0].decode())
        message_dict = json.loads(message)

        print("Tempcount: " + str(tempcount))
        if message_dict["request_type"] == "REGISTER":
            register_thread = threading.Thread(target=user_registration, args=(message_dict,))
            thread_list.append(register_thread)
            register_thread.start()
            tempcount += 1
        client_msg = "Message from Client: {}".format(str(message_dict))

        # write message to log file
        file = open("ServerALog.txt", "a")
        file.write("\n"+client_msg)
        file.close()

    for element in thread_list:
        print("Joining thread with id: " + str(element.ident))
        element.join()


def user_registration(reg_message):
    # Test talk to serverB from serverA
    server_b_address_port = ("127.0.0.1", 1001)
    register_message_json = json.dumps(reg_message)
    register_message_bytes = str.encode(register_message_json)
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.sendto(register_message_bytes, server_b_address_port)
    print(reg_message)


if __name__ == "__main__":
    messageThread = threading.Thread(target=listen_for_messages, args=())
    messageThread.start()
    messageThread.join()

# while (True):
#     bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
#
#     message = bytesAddressPair[0]
#
#     address = bytesAddressPair[1]
#
#     clientMsg = "Message from Client:{}".format(message)
#     clientIP = "Client IP Address:{}".format(address)
#     print(str(message))
#     if str(message) == "b'hello'":
#         UDPServerSocket.sendto(bytesToSend, address)
#     else:
#         UDPServerSocket.sendto(bytesToSend2, address)
#
#     print(clientMsg)
#     print(clientIP)

    # Sending a reply to client

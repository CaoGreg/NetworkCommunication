import socket
import json
import threading
import select
import datetime
import time

import Gui

# Server Addresses
serverAAddressPort = ""
serverBAddressPort = ""
bufferSize = 1024
currentServerAddressPort = ""

# Client info
client_name = ""
ip_address = ""
socket_number = 2000    # Random number for initialization, will get overwritten later
subjects_of_interest = []
isListening = False
count_time_out = 10     # Random number for initialization, will get overwritten later

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.connect(("8.8.8.8",80))
ip_address = str(UDPClientSocket.getsockname()[0])
UDPClientSocket.close()
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.bind((ip_address, socket_number))


def listen_for_messages(stop_event):
    global currentServerAddressPort
    global serverAAddressPort
    global serverBAddressPort
    global subjects_of_interest
    print("starting message")
    # Wait for messages
    while not stop_event.is_set():
        read, write, errors = select.select([UDPClientSocket], [], [], 1)
        for read_socket in read:
            server_message = UDPClientSocket.recvfrom(bufferSize)
            print(str(server_message[0].decode()))
            # TODO: Check si ca marche
            if "SUBJECTS-UPDATED" in str(server_message[0]):
                subject_info = str(server_message[0].decode()).split(' ')
                subjects_of_interest = subject_info[3]
                print("New subject of interests: " + subjects_of_interest)
            if "CHANGE-SERVER" in str(server_message[0]):
                server_info = str(server_message[0].decode()).split(',')
                nextServerAddressPort = (server_info[1], int(server_info[2]))
                if currentServerAddressPort == serverAAddressPort:
                    serverBAddressPort = nextServerAddressPort
                else:
                    serverAAddressPort = nextServerAddressPort
                currentServerAddressPort = nextServerAddressPort
                print("Current host: " + str(currentServerAddressPort))


def isValidIpAddress(ip):
    ipArr = ip.split(".")
    if len(ipArr) != 4:
        return False
    for x in ipArr:
        if x.lower().islower():
            return False
        if int(x) > 255:
            return False
    return True


def isValidPort(port):
    if not port.isnumeric():
        return False
    if str(port).lower().islower():
        return False
    if int(port) == 0 or int(port) > 65535:
        return False
    return True


def getAddressAndPort(server):
    validInput = False
    while not validInput:
        ipInput = input("What is the " + server + " server's IP address?\n")
        if isValidIpAddress(ipInput):
            serverAddress = ipInput
            validInput = True
        else:
            print("Incorrect IP address format\n")

    validInput = False
    while not validInput:
        portInput = input("What is the " + server + " server's port?\n")
        if isValidPort(portInput):
            serverPort = int(portInput)
            validInput = True
        else:
            print("Incorrect port number\n")
    return (serverAddress, int(serverPort))


if __name__ == "__main__":
    # Get the servers information
    serverAAddressPort = getAddressAndPort("first")
    serverBAddressPort = getAddressAndPort("second")
    count_time_out = int(input("How long should I wait for a response before timing out?\n"))

    while True:
        # Get user input
        print("What would you like to do today?")
        print("0: Register to the server\n1: De-register from server\n2: Update ip/socket"
              "\n3: Update subjects of interest\n4: Publish subjects of interest")
        user_action = input()
        # Register
        if user_action == '0':
            # Send register request to both servers
            name = input("What is your name?\n")
            registerMessage = {"request_type": "REGISTER", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                               "name": name, "ip": ip_address, "socket": str(socket_number)}
            registerMessageJson = json.dumps(registerMessage)
            registerMessageBytes = str.encode(registerMessageJson)

            UDPClientSocket.sendto(registerMessageBytes, serverAAddressPort)
            UDPClientSocket.sendto(registerMessageBytes, serverBAddressPort)
            count = count_time_out
            while count > 0:
                read, write, errors = select.select([UDPClientSocket], [], [], 1)
                for read_socket in read:
                    msg = UDPClientSocket.recvfrom(bufferSize)
                    if "REGISTERED" in str(msg):
                        client_name = name
                    if not isListening:
                        if "REGISTERED" in str(msg):
                            currentServerAddressPort = msg[1]
                            # Start listening to the server
                            isListening = True
                            t_message_event = threading.Event()
                            t_message = threading.Thread(target=listen_for_messages, args=(t_message_event,))
                            t_message.start()
                        print(msg)
                    break
                else:
                    count = count - 1
                    continue
                break
            else:
                print("Timed out. No response from the server. Please try again.")

        # De-register
        elif user_action == '1':
            if currentServerAddressPort == "" or not isListening or client_name == "":
                print("You need to register or update your information first")
            else:
                print("Starting De-registering")

                # Create de-register message
                de_register_message = {"request_type": "DE-REGISTER", "rq_number":
                                       int(datetime.datetime.utcnow().timestamp()), "name": client_name}
                de_register_message_json = json.dumps(de_register_message)
                de_register_message_bytes = str.encode(de_register_message_json)

                # Send message to current active server
                UDPClientSocket.sendto(de_register_message_bytes, currentServerAddressPort)
                currentServerAddressPort = ""
                client_name = ""
                subjects_of_interest = []
                # Stop the listening thread
                try:
                    isListening = False
                    t_message_event.set()
                    t_message.join()
                    t_message_event.clear()
                except NameError:
                    print("Client wasn't registered, nothing to de-register")
                else:
                    print("Client was de-registered")
        # Update
        elif user_action == '2':
            print("Starting ip/socket update")
            if currentServerAddressPort == "":
                # Send current request to both servers
                current_message = {"request_type": "CURRENT", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                                   "ip": ip_address, "socket": socket_number}
                current_message_json = json.dumps(current_message)
                current_message_bytes = str.encode(current_message_json)

                # Send message to both servers
                UDPClientSocket.sendto(update_message_bytes, serverAAddressPort)
                UDPClientSocket.sendto(update_message_bytes, serverBAddressPort)

                msg = UDPClientSocket.recvfrom(bufferSize)
                currentServerAddressPort = msg[1]

            # Send update request to current server
            name = input("What is your name?\n")
            update_message = {"request_type": "UPDATE", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                              "name": name, "ip": ip_address, "socket": socket_number}
            update_message_json = json.dumps(update_message)
            update_message_bytes = str.encode(update_message_json)

            # Send message to current active server
            UDPClientSocket.sendto(update_message_bytes, currentServerAddressPort)
            msg = UDPClientSocket.recvfrom(bufferSize)
            if "UPDATE-CONFIRMED" in str(msg):
                client_name = name
            if not isListening:
                if "UPDATE-CONFIRMED" in str(msg):
                    # Start listening to the server
                    isListening = True
                    t_message_event = threading.Event()
                    t_message = threading.Thread(target=listen_for_messages, args=(t_message_event,))
                    t_message.start()

                print(msg)
        # Subject of interest
        elif user_action == '3':
            if currentServerAddressPort == "" or not isListening or client_name == "":
                print("You need to register or update your information first")
            else:
                print("Starting subjects of interest update")
                subjects_list = ["AI", "Cloud", "Networking", "Micro controllers", "Micro processors"]
                subj = []
                subject_done = False
                while not subject_done:
                    print("This is the list of subjects: " + str(subjects_list))
                    subj.append(input("Select a subject you wish to subscribe to (This is case sensitive): "))
                    again = input("Do you wish to add another subject? 1 for No, anything else for Yes ")
                    if again == "1":
                        subject_done = True
                print("List to be sent to the server: " + str(subj))
                # Create subjects message
                subjects_message = {"request_type": "SUBJECTS", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                                    "name": client_name, "subjects": subj}
                subjects_message_json = json.dumps(subjects_message)
                subjects_message_bytes = str.encode(subjects_message_json)

                try:
                    t_message_event.clear()
                    # Send message to current active server
                    UDPClientSocket.sendto(subjects_message_bytes, currentServerAddressPort)
                except NameError:
                    print("Client wasn't registered, cannot update subjects")
        # Publish
        elif user_action == '4':
            if currentServerAddressPort == "" or not isListening or client_name == "":
                print("You need to register or update your information first")
            else:
                print("Starting subjects of interest publish")
                print("These are you subjects of interest: " + subjects_of_interest)
                subject = input("To which subject do you want to publish? (This is case sensitive)")
                print("Please enter the text you want to publish")
                text = input()

                # Create publish message
                publish_message = {"request_type": "PUBLISH", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                                   "name": client_name, "subject": subject, "text": text}
                publish_message_json = json.dumps(publish_message)
                publish_message_bytes = str.encode(publish_message_json)

                try:
                    t_message_event.clear()
                    # Send message to current active server
                    UDPClientSocket.sendto(publish_message_bytes, currentServerAddressPort)
                except NameError:
                    print("Client wasn't registered, cannot publish messages")

        else:
            print("Invalid input. Please try again")

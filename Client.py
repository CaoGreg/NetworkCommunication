import socket
import json
import threading
import select
import datetime
import Gui

# Server Addresses
serverAAddressPort = ("192.168.2.28", 38708)
serverBAddressPort = ("192.168.2.29", 56552)
bufferSize = 1024
currentServerAddressPort = serverBAddressPort

# Client info
client_name = "Khendek"
ip_address = ""
socket_number = 2000
subjects_of_interest = []
isListening = False

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.connect(("8.8.8.8",80))
ip_address = str(UDPClientSocket.getsockname()[0])
UDPClientSocket.close()
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.bind((ip_address, socket_number))


def listen_for_messages(stop_event):
    global currentServerAddressPort
    print("starting message")
    # Wait for messages
    while not stop_event.is_set():
        read, write, errors = select.select([UDPClientSocket], [], [], 1)
        for read_socket in read:
            server_message = UDPClientSocket.recvfrom(bufferSize)
            print(str(server_message[0].decode()))

            if "CHANGE-SERVER" in str(server_message[0]):
                server_info = str(server_message[0].decode()).split(',')
                currentServerAddressPort = (server_info[1], int(server_info[2]))
                print("Current host: " + str(currentServerAddressPort))


if __name__ == "__main__":
    # TODO: 1) client does not get answer from the server if not registered, is this ok?
    # TODO: 2) user input for subjects of interest and publishing

    while True:
        # Get user input
        print("What would you like to do today?")
        print("0: Register to the server\n1: De-register from server\n2: Update ip/socket"
              "\n3: Update subjects of interest\n4: Publish subjects of interest")
        user_action = input()
        if user_action == '0':
            # Send register request to both servers
            registerMessage = {"request_type": "REGISTER", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                               "name": input("What is your name?\n"), "ip": ip_address, "socket": str(socket_number)}
            registerMessageJson = json.dumps(registerMessage)
            registerMessageBytes = str.encode(registerMessageJson)

            UDPClientSocket.sendto(registerMessageBytes, serverAAddressPort)
            UDPClientSocket.sendto(registerMessageBytes, serverBAddressPort)

            if not isListening:
                msg = UDPClientSocket.recvfrom(bufferSize)
                if "REGISTERED" in str(msg):
                    # Start listening to the server
                    isListening = True
                    t_message_event = threading.Event()
                    t_message = threading.Thread(target=listen_for_messages, args=(t_message_event,))
                    t_message.start()

                print(msg)

        elif user_action == '1':
            if currentServerAddressPort == "" or not isListening:
                print("You need to register or update your information first")
            else:
                print("Starting De-registering")

                # Create de-register message
                de_register_message = {"request_type": "DE-REGISTER", "rq_number":
                                       int(datetime.datetime.utcnow().timestamp()), "name": input("What is your name?\n")}
                de_register_message_json = json.dumps(de_register_message)
                de_register_message_bytes = str.encode(de_register_message_json)

                # Send message to current active server
                UDPClientSocket.sendto(de_register_message_bytes, currentServerAddressPort)

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

        elif user_action == '2':
            print("Starting ip/socket update")
            if currentServerAddressPort == "":
                # Send update request to current server
                update_message = {"request_type": "UPDATE", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                                  "name": input("What is your name?\n"), "ip": ip_address, "socket": socket_number}
                update_message_json = json.dumps(update_message)
                update_message_bytes = str.encode(update_message_json)

                # Send message to current active server
                UDPClientSocket.sendto(update_message_bytes, currentServerAddressPort)
            else:
                # Send update request to current server
                update_message = {"request_type": "UPDATE", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                                  "name": input("What is your name?\n"), "ip": ip_address, "socket": socket_number}
                update_message_json = json.dumps(update_message)
                update_message_bytes = str.encode(update_message_json)

                # Send message to current active server
                UDPClientSocket.sendto(update_message_bytes, currentServerAddressPort)
                if not isListening:
                    msg = UDPClientSocket.recvfrom(bufferSize)
                    if "UPDATE-CONFIRMED" in str(msg):
                        # Start listening to the server
                        isListening = True
                        t_message_event = threading.Event()
                        t_message = threading.Thread(target=listen_for_messages, args=(t_message_event,))
                        t_message.start()

                    print(msg)

        elif user_action == '3':
            if currentServerAddressPort == "" or not isListening:
                print("You need to register or update your information first")
            else:
                print("Starting subjects of interest update")
                # TODO: make this user input
                subj = ["AI", "Cloud"]
                # Create subjects message
                subjects_message = {"request_type": "SUBJECTS", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                                    "name": input("What is your name?\n"), "subjects": subj}
                subjects_message_json = json.dumps(subjects_message)
                subjects_message_bytes = str.encode(subjects_message_json)

                try:
                    t_message_event.clear()
                    # Send message to current active server
                    UDPClientSocket.sendto(subjects_message_bytes, currentServerAddressPort)
                except NameError:
                    print("Client wasn't registered, cannot update subjects")

        elif user_action == '4':
            if currentServerAddressPort == "" or not isListening:
                print("You need to register or update your information first")
            else:
                print("Starting subjects of interest publish")
                # TODO: add user input here for subject
                print("Please enter the text you want to publish")
                text = input()

                # Create publish message
                publish_message = {"request_type": "PUBLISH", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                                   "name": input("What is your name?\n"), "subject": "AI", "text": text}
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
            
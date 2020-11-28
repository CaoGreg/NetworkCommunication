#!/usr/bin/python3
import socket
import threading
import time
import json
import select

# Server information
serverIP = ""   # To be set later on
serverPort = 0  # To be set later on
bufferSize = 1024
thread_list = []
user_list = []
subjects_list = ["AI", "Cloud", "Networking", "Micro controllers", "Micro processors"]
t_message_stop = threading.Event()
global t_message

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.connect(("8.8.8.8", 80))
serverIP = str(UDPServerSocket.getsockname()[0])
UDPServerSocket.close()
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((serverIP, serverPort))
serverPort = UDPServerSocket.getsockname()[1]
print("Starting server")
print("My IP address is " + serverIP + " and my port is " + str(serverPort))

# Clear log file
f = open("ServerLog.txt", "w")
f.write("Server " + serverIP + ": Beginning of Execution")
f.close()


# Listen for incoming messages
def listen_for_messages(stop_event):
    global isServerActive
    global user_list
    global other_server_address
    global other_server_port
    global other_server_address_port

    while not stop_event.is_set():
        # Wait for messages from clients
        read, write, errors = select.select([UDPServerSocket], [], [], 1)
        for read_socket in read:
            bytes_address_pair = UDPServerSocket.recvfrom(bufferSize)
            message = (bytes_address_pair[0].decode())
            print(message)

            # Only answer if the server is serving
            if isServerActive:
                message_dict = json.loads(message)

                if message_dict["request_type"] == "REGISTER":
                    # write message to log file
                    client_msg = "Client to Server " + serverIP + ": " + message_dict["request_type"] + " " + str(
                        message_dict["rq_number"]) \
                                 + " " + message_dict["name"] + " " + message_dict["ip"] + " " + str(message_dict["socket"])
                    add_to_server_log(client_msg)

                    register_thread = threading.Thread(target=user_registration, args=(message_dict,))
                    thread_list.append(register_thread)
                    add_to_server_log("Server " + serverIP + ": Starting Registration for client " + message_dict["name"])
                    register_thread.start()

                if message_dict["request_type"] == "DE-REGISTER":
                    # write message to log file
                    client_msg = "Client to Server " + serverIP + ": " + message_dict["request_type"] + " " + str(
                        message_dict["rq_number"]) + " " + message_dict["name"]
                    add_to_server_log(client_msg)

                    de_register_thread = threading.Thread(target=user_de_registration, args=(message_dict,))
                    thread_list.append(de_register_thread)
                    add_to_server_log("Server " + serverIP + ": Starting De-Registration for client " + message_dict["name"])
                    de_register_thread.start()

                if message_dict["request_type"] == "UPDATE":
                    # write message to log file
                    client_msg = "Client to Server " + serverIP + ": " + message_dict["request_type"] + " " + str(
                        message_dict["rq_number"]) \
                                 + " " + message_dict["name"] + " " + message_dict["ip"] + " " + str(message_dict["socket"])
                    add_to_server_log(client_msg)

                    update_user_thread = threading.Thread(target=user_update, args=(message_dict,))
                    thread_list.append(update_user_thread)
                    add_to_server_log("Server " + serverIP + ": Starting user update for client " + message_dict["name"])
                    update_user_thread.start()

                if message_dict["request_type"] == "SUBJECTS":
                    # write message to log file
                    client_msg = "Client to Server " + serverIP + ": " + message_dict["request_type"] + " " + str(
                        message_dict["rq_number"]) + " " + message_dict["name"] + " " + str(message_dict["subjects"])
                    add_to_server_log(client_msg)

                    update_subjects_thread = threading.Thread(target=subjects_update,
                                                              args=(message_dict, bytes_address_pair[1]))
                    thread_list.append(update_subjects_thread)
                    add_to_server_log("Server " + serverIP + ": Starting subjects update for client " + message_dict["name"])
                    update_subjects_thread.start()

                if message_dict["request_type"] == "PUBLISH":
                    # write message to log file
                    client_msg = "Client to Server " + serverIP + ": " + message_dict["request_type"] + " " + str(
                        message_dict["rq_number"]) + " " + message_dict["name"] + " " + str(message_dict["subject"])\
                                 + " " + message_dict["text"]
                    add_to_server_log(client_msg)

                    user_publish_thread = threading.Thread(target=user_publish, args=(message_dict,bytes_address_pair[1]))
                    thread_list.append(user_publish_thread)
                    add_to_server_log("Server " + serverIP + ": Starting publish for client " + message_dict["name"])
                    user_publish_thread.start()
                #
                # if message_dict["request_type"] == "UPDATE-SERVER":
                #     server_b_address = message_dict["ip"]
                #     server_b_port = message_dict["socket"]
                #     server_b_address_port = (server_b_address, int(server_b_port))
                #     add_to_server_log("Server " + other_server_address + " to Server " + serverIP + ": " + message_dict["request_type"] + " " +
                #                       str(server_b_address_port))

                if message_dict["request_type"] == "CURRENT":
                    # write message to log file
                    client_msg = "Client to Server " + serverIP + ": " + message_dict["request_type"] + " " + str(
                        message_dict["rq_number"]) + " " + message_dict["name"]
                    add_to_server_log(client_msg)

                    current_server_thread = threading.Thread(target=current_server,
                                                           args=(message_dict, bytes_address_pair[1]))
                    thread_list.append(current_server_thread)
                    add_to_server_log("Server " + serverIP + ": Signaling current server for client " + message_dict["name"])
                    current_server_thread.start()
            else:
                # Wait for messages from Other Server
                if other_server_address in message and str(other_server_port) in message:
                    print("Message from Other Server: " + message)
                    if "SERVER UP" in message:
                        add_to_server_log("Server " + serverIP + " Resuming Service")
                        print("Server " + serverIP + " Resuming Service")
                        isServerActive = True
                    else:
                        other_server_client_msg = "Server " + other_server_address + " to Server " + serverIP + ": " + str(message).split(',' + other_server_address)[0]
                        add_to_server_log(other_server_client_msg)

                        # Check if it is a memory update
                        if '[{' in message:
                            user_list = json.loads(str(message).split(',' + other_server_address)[0])


def user_registration(reg_message):
    # Check if the user already exists
    user_exists = False
    denial_reason = ""
    status = ""
    client_address = (reg_message["ip"], int(reg_message["socket"]))

    for registered_user in user_list:
        if registered_user["name"] == reg_message["name"]:
            user_exists = True
            denial_reason = "Name already exists"
            break
        if registered_user["ip"] == reg_message["ip"] and registered_user["socket"] == reg_message["socket"]:
            user_exists = True
            denial_reason = "IP and socket already registered"
            break

    if user_exists:
        # Send response to the Client
        denial_message = "REGISTER-DENIED: " + str(reg_message["rq_number"]) + ", " + denial_reason
        register_message_bytes = str.encode(denial_message)
        UDPServerSocket.sendto(register_message_bytes, client_address)

        # Log the message
        add_to_server_log("Server " + serverIP + ": " + str(reg_message["rq_number"]) +
                          " " + reg_message["name"] + ", " + denial_message)
        print(reg_message["name"] + ", " + denial_message)
        status = "REGISTER-DENIED"
    else:
        # Add registered user to the list
        registered_message = "REGISTERED: " + str(reg_message["rq_number"])
        reg_user = {"name": reg_message["name"], "ip": reg_message["ip"],
                    "socket": reg_message["socket"], "subjects": []}
        user_list.append(reg_user)

        # Send response to the Client
        register_message_bytes = str.encode(registered_message)
        UDPServerSocket.sendto(register_message_bytes, client_address)

        # Log the message
        add_to_server_log("Server " + serverIP + ": " + str(reg_message["rq_number"]) + " "
                          + reg_message["name"] + ", " + registered_message)
        print(reg_message["name"] + ", " + registered_message)
        status = "REGISTERED"

    # Send Result to Other Server and update its memory
    server_msg = status + " " + str(reg_message["rq_number"]) + " " + reg_message["name"] + " " + \
                 reg_message["ip"] + " " + str(reg_message["socket"]) + "," + serverIP + "," + str(serverPort)

    register_message_bytes = str.encode(server_msg)
    UDPClientSocket.sendto(register_message_bytes, other_server_address_port)

    new_reg_memory = str.encode(json.dumps(user_list) + "," + serverIP + "," + str(serverPort))
    UDPClientSocket.sendto(new_reg_memory, other_server_address_port)
    print(reg_message)
    print(new_reg_memory)


def user_de_registration(de_reg_message):
    user_removed = False

    for registered_user in user_list:
        if registered_user["name"] == de_reg_message["name"]:
            user_removed = True
            user_list.remove(registered_user)
            print("Removing " + str(registered_user))

    if user_removed:
        # Send Result to Other Server and update its memory
        server_msg = "DE-REGISTER" + " " + str(de_reg_message["name"]) + "," + serverIP + "," + str(serverPort)
        register_message_bytes = str.encode(server_msg)
        UDPClientSocket.sendto(register_message_bytes, other_server_address_port)

        new_reg_memory = str.encode(json.dumps(user_list) + "," + serverIP + "," + str(serverPort))
        UDPClientSocket.sendto(new_reg_memory, other_server_address_port)
        add_to_server_log("Server " + serverIP + ": " + str(de_reg_message["rq_number"]) + " "
                          + de_reg_message["name"] + ", " + "DE-REGISTERED")
        print(de_reg_message)
        print(new_reg_memory)


def user_update(update_message):
    client_address = (str(update_message["ip"]), int(update_message["socket"]))
    user_exists = False
    denial_reason = ""

    for registered_user in user_list:
        if registered_user["ip"] == update_message["ip"] and registered_user["socket"] == update_message["socket"] and registered_user["name"] != update_message["name"]:
            denial_reason = "Requested ip/socket combination already exists"
            break
        if registered_user["name"] == update_message["name"]:
            user_exists = True
            registered_user["ip"] = update_message["ip"]
            registered_user["socket"] = update_message["socket"]
            print("Updating " + registered_user["name"])
            break

    if denial_reason == "" and user_exists is False:
        denial_reason = "User " + update_message["name"] + " does not exist"

    if user_exists and denial_reason == "":
        # Send response to the Client
        message = "UPDATE-CONFIRMED: " + str(update_message["rq_number"]) + " " + update_message["name"] \
                  + " " + update_message["ip"] + " " + str(update_message["socket"])
        update_message_bytes = str.encode(message)
        UDPServerSocket.sendto(update_message_bytes, client_address)

        # Log the message
        add_to_server_log("Server " + serverIP + ": " + str(update_message["rq_number"]) + " "
                          + update_message["name"] + ", updated: " + update_message["ip"] + ": " + str(update_message["socket"]))
        print(update_message["name"] + ", updated socket")

        # Send result to Other Server
        server_msg = message + "," + serverIP + "," + str(serverPort)
        update_message_bytes = str.encode(server_msg)
        UDPClientSocket.sendto(update_message_bytes, other_server_address_port)

        new_reg_memory = str.encode(json.dumps(user_list) + "," + serverIP + "," + str(serverPort))
        UDPClientSocket.sendto(new_reg_memory, other_server_address_port)
        print(message)
        print(new_reg_memory)
    else:
        # Send response to the Client
        denial_message = "UPDATE-DENIED: " + str(update_message["rq_number"]) + ", " + denial_reason
        update_message_bytes = str.encode(denial_message)
        UDPServerSocket.sendto(update_message_bytes, client_address)

        # Log the message
        add_to_server_log("Server " + serverIP + ": " + str(update_message["rq_number"]) + " " + update_message["name"]
                          + ", " + denial_message)
        print(update_message["name"] + ", " + denial_message)


def subjects_update(subjects_message, client_address):
    user_exists = False
    subject_exists = True
    status = ""

    for subject in subjects_message["subjects"]:
        if subject not in subjects_list:
            subject_exists = False

    if subject_exists:
        for registered_user in user_list:
            if registered_user["name"] == subjects_message["name"]:
                user_exists = True
                registered_user["subjects"] = subjects_message["subjects"]
                print("Updating " + str(registered_user))

    if user_exists and subject_exists:
        status = "SUBJECTS-UPDATED"

        # Send response to the Client
        message = status + ": " + str(subjects_message["rq_number"]) + " " + subjects_message["name"] \
                         + " " + str(subjects_message["subjects"])
        subj_message_bytes = str.encode(message)
        UDPServerSocket.sendto(subj_message_bytes, client_address)

        # Send Result to Other Server and update its memory
        server_msg = status + " " + str(subjects_message["rq_number"]) + " " + str(
            subjects_message["name"]) + " " + str(subjects_message["subjects"]) + "," + serverIP + "," + str(serverPort)
        subject_message_bytes = str.encode(server_msg)
        UDPClientSocket.sendto(subject_message_bytes, other_server_address_port)

        new_reg_memory = str.encode(json.dumps(user_list) + "," + serverIP + "," + str(serverPort))
        UDPClientSocket.sendto(new_reg_memory, other_server_address_port)

        # log the message
        add_to_server_log("Server " + serverIP + ": " + str(subjects_message["rq_number"]) + " "
                          + subjects_message["name"] + ", updated: " + str(subjects_message["subjects"]) + " " + status)

        print(subjects_message)
        print(new_reg_memory)
    else:
        status = "SUBJECTS-REJECTED"

        # Send response to the Client
        message = status + ": " + str(subjects_message["rq_number"]) + " " + subjects_message["name"] \
                  + " " + str(subjects_message["subjects"])
        update_message_bytes = str.encode(message)
        UDPServerSocket.sendto(update_message_bytes, client_address)

        # log the message
        add_to_server_log("Server " + serverIP + ": " + str(subjects_message["rq_number"]) + " "
                          + subjects_message["name"] + ", updated: " + str(subjects_message["subjects"]) + " " + status)
        print(subjects_message)
        print(message)


def user_publish(publish_message, client_address):
    user_exists = False
    subject_exists = False
    status = ""

    for registered_user in user_list:
        if registered_user["name"] == publish_message["name"]:
            user_exists = True
            if publish_message["subject"] in registered_user["subjects"]:
                subject_exists = True
            break

    if user_exists and subject_exists:
        status = "MESSAGE"

        # Send response to clients with the subject in their interests
        message = status + ": " + publish_message["name"] + " " + publish_message["subject"]\
                         + " " + publish_message["text"]
        publish_message_bytes = str.encode(message)
        for user in user_list:
            if publish_message["subject"] in user["subjects"]:
                UDPServerSocket.sendto(publish_message_bytes, (user["ip"], int(user["socket"])))

        # log the message
        add_to_server_log("Server " + serverIP + ": " + str(publish_message["rq_number"]) + " "
                          + publish_message["name"] + " MESSAGE: " + publish_message["subject"]
                          + ", " + publish_message["text"])
        print(message)
    else:
        status = "PUBLISH-DENIED"
        denial_reason = ""
        if not subject_exists:
            denial_reason = "The provided subject is either invalid or not in your interests"
        if not user_exists:
            denial_reason = "User does not exist"

        # Send response to the Client
        denial_message = status + ": " + str(publish_message["rq_number"]) + " " + denial_reason
        publish_denial_message_bytes = str.encode(denial_message)
        UDPServerSocket.sendto(publish_denial_message_bytes, client_address)

        # log the message
        add_to_server_log("Server " + serverIP + ": " + str(publish_message["rq_number"]) +
                          " " + publish_message["name"] + ", PUBLISH-DENIED: " + denial_reason)
        print(denial_message)


def current_server(current_message, client_address):
    # Send to client if active
    server_msg = "CURRENT" + " " + serverIP + " " + str(serverPort)
    server_message_bytes = str.encode(server_msg)

    UDPServerSocket.sendto(server_message_bytes, client_address)
    add_to_server_log("Server " + serverIP + ": " + str(current_message["rq_number"]) + " "
                      + current_message["name"] + ", " + "CURRENT")
    print(server_msg)


def change_server():
    # Change server message
    change_message = "CHANGE-SERVER," + other_server_address + "," + str(other_server_port)
    change_message_bytes = str.encode(change_message)

    # Send the message to each registered user
    for registered_user in user_list:
        user_address_port = (registered_user["ip"], int(registered_user["socket"]))
        UDPClientSocket.sendto(change_message_bytes, user_address_port)

    add_to_server_log("Server " + serverIP + ": " + change_message)


def add_to_server_log(log):
    file = open("ServerLog.txt", "a")
    file.write("\n" + log)
    file.close()


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


if __name__ == "__main__":
    # Start the message thread
    t_message = threading.Thread(target=listen_for_messages, args=(t_message_stop,))
    # t_input = threading.Thread(target=update_server_ip, args=())
    t_message.start()
    # t_input.start()

    # Get other server information
    validInput = False
    while not validInput:
        ipInput = input("What is the other server's IP address?\n")
        if isValidIpAddress(ipInput):
            other_server_address = ipInput
            validInput = True
        else:
            print("Incorrect IP address format\n")

    validInput = False
    while not validInput:
        portInput = input("What is the other server's port?\n")
        if isValidPort(portInput):
            other_server_port = int(portInput)
            validInput = True
        else:
            print("Incorrect port number\n")

    other_server_address_port = (other_server_address, other_server_port)
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    activeInput = input("Am I the serving server? 1 for Yes, anything else for No\n")
    if activeInput == "1":
        isServerActive = True
    else:
        isServerActive = False

    validInput = False
    while not validInput:
        activeTimeInput = input("How long should I serve before switching to other server?\n")
        if activeTimeInput.isnumeric():
            validInput = True
        else:
            print("Incorrect number\n")

    validInput = False
    while not validInput:
        timeOutInput = input("How long should I wait before switching back in case of time out?\n")
        if timeOutInput.isnumeric():
            validInput = True
        else:
            print("Incorrect number\n")

    while True:
        if isServerActive:
            # Serving time
            print("Server Listening")
            time.sleep(int(activeTimeInput))

            # TODO
            # isChanging = True
            # save users to user file

            # Join all the threads that were started during the serving time and clear the list
            for element in thread_list:
                print("Joining thread with id: " + str(element.ident))
                element.join()
            thread_list = []

            # Send messages to all connected clients that the server is changing
            change_server()

            # Update Other Server and Tell it to start serving
            new_memory = str.encode(json.dumps(user_list) + "," + serverIP + "," + str(serverPort))
            UDPClientSocket.sendto(new_memory, other_server_address_port)

            up_message_bytes = str.encode("SERVER UP," + serverIP + "," + str(serverPort))
            UDPClientSocket.sendto(up_message_bytes, other_server_address_port)
            print("Sent server up to " + other_server_address)
            isServerActive = False
        else:
            # If Other Server takes to long to respond, timeout and start serving again
            timeout_count = 0
            while not isServerActive:
                if timeout_count >= int(timeOutInput):
                    isServerActive = True
                    print("Time out")
                else:
                    time.sleep(1)
                    timeout_count += 1

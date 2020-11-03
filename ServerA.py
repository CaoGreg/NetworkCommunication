import socket
import threading
import time
import json

# Server A information
serverIP = "127.0.0.1"
serverPort = 1000
bufferSize = 1024
isServerActive = 1
thread_list = []
client_list = []
subjects_list = ["AI", "Cloud", "Networking", "Micro controllers", "Micro processors"]

# Server B information
server_b_address = "127.0.0.1"
server_b_port = 1001
server_b_address_port = (server_b_address, server_b_port)
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((serverIP, serverPort))

# Clear log file
f = open("ServerALog.txt", "w")
f.write("Server A: Beginning of Execution")
f.close()


# Listen for incoming messages
def listen_for_messages(stop_event):
    global isServerActive
    global client_list
    while True:
        # Wait for messages from clients
        bytes_address_pair = UDPServerSocket.recvfrom(bufferSize)
        message = (bytes_address_pair[0].decode())

        # Only answer if the server is serving
        if not stop_event.is_set():
            message_dict = json.loads(message)

            if message_dict["request_type"] == "REGISTER":
                # write message to log file
                client_msg = "Client to Server A: " + message_dict["request_type"] + " " + str(
                    message_dict["rq_number"]) \
                             + " " + message_dict["name"] + " " + message_dict["ip"] + " " + str(message_dict["socket"])
                add_to_server_log(client_msg)

                register_thread = threading.Thread(target=user_registration, args=(message_dict,))
                thread_list.append(register_thread)
                add_to_server_log("Server A: Starting Registration for client " + message_dict["name"])
                register_thread.start()

            if message_dict["request_type"] == "DE-REGISTER":
                # write message to log file
                client_msg = "Client to Server A: " + message_dict["request_type"] + " " + str(
                    message_dict["rq_number"]) + " " + message_dict["name"]
                add_to_server_log(client_msg)

                de_register_thread = threading.Thread(target=user_de_registration, args=(message_dict,))
                thread_list.append(de_register_thread)
                add_to_server_log("Server A: Starting De-Registration for client " + message_dict["name"])
                de_register_thread.start()

            if message_dict["request_type"] == "UPDATE":
                # write message to log file
                client_msg = "Client to Server A: " + message_dict["request_type"] + " " + str(
                    message_dict["rq_number"]) \
                             + " " + message_dict["name"] + " " + message_dict["ip"] + " " + str(message_dict["socket"])
                add_to_server_log(client_msg)

                update_user_thread = threading.Thread(target=user_update, args=(message_dict,))
                thread_list.append(update_user_thread)
                add_to_server_log("Server A: Starting user update for client " + message_dict["name"])
                update_user_thread.start()

            if message_dict["request_type"] == "SUBJECTS":
                # write message to log file
                client_msg = "Client to Server A: " + message_dict["request_type"] + " " + str(
                    message_dict["rq_number"]) + " " + message_dict["name"] + " " + str(message_dict["subjects"])
                add_to_server_log(client_msg)

                update_subjects_thread = threading.Thread(target=subjects_update,
                                                          args=(message_dict, bytes_address_pair[1]))
                thread_list.append(update_subjects_thread)
                add_to_server_log("Server A: Starting subjects update for client " + message_dict["name"])
                update_subjects_thread.start()

        else:
            # Wait for messages from Server B
            if server_b_address in message and str(server_b_port) in message:
                print("Message from Server A: " + message)
                if "SERVER UP" in message:
                    add_to_server_log("Server A Resuming Service")
                    print("Server A Resuming Service")
                    isServerActive = 1
                else:
                    server_b_client_msg = "Server B to Server A: " + str(message).split(',' + serverIP)[0]
                    add_to_server_log(server_b_client_msg)

                    # Check if it is a memory update
                    if '[' in message:
                        client_list = json.loads(str(message).split(',' + serverIP)[0])


def user_registration(reg_message):
    # Check if the user already exists
    user_exists = False
    denial_reason = ""
    status = ""
    client_address = (reg_message["ip"], int(reg_message["socket"]))

    for registered_user in client_list:
        if registered_user["name"] == reg_message["name"]:
            user_exists = True
            denial_reason = "Name already exists"
        if registered_user["ip"] == reg_message["ip"] and registered_user["socket"] == reg_message["socket"]:
            user_exists = True
            denial_reason = "IP and socket already registered"

    if user_exists:
        # Send response to the Client
        denial_message = "REGISTER-DENIED: " + str(reg_message["rq_number"]) + ", " + denial_reason
        register_message_bytes = str.encode(denial_message)
        UDPServerSocket.sendto(register_message_bytes, client_address)

        # Log the message
        add_to_server_log("Server A: " + reg_message["name"] + ", " + denial_message)
        print(reg_message["name"] + ", " + denial_message)
        status = "REGISTER-DENIED"
    else:
        # Add registered user to the list
        registered_message = "REGISTERED: " + str(reg_message["rq_number"])
        reg_user = {"name": reg_message["name"], "ip": reg_message["ip"],
                    "socket": reg_message["socket"], "subjects": []}
        client_list.append(reg_user)

        # Send response to the Client
        register_message_bytes = str.encode(registered_message)
        UDPServerSocket.sendto(register_message_bytes, client_address)

        # Log the message
        add_to_server_log("Server A: " + reg_message["name"] + ", " + registered_message)
        print(reg_message["name"] + ", " + registered_message)
        status = "REGISTERED"

    # Send Result to Server B and update its memory
    server_msg = status + " " + str(reg_message["rq_number"]) + " " + reg_message["name"] + " " + \
                 reg_message["ip"] + " " + str(reg_message["socket"]) + "," + serverIP + "," + str(serverPort)

    register_message_bytes = str.encode(server_msg)
    UDPClientSocket.sendto(register_message_bytes, server_b_address_port)

    new_reg_memory = str.encode(json.dumps(client_list) + "," + serverIP + "," + str(serverPort))
    UDPClientSocket.sendto(new_reg_memory, server_b_address_port)
    print(reg_message)
    print(new_reg_memory)


def user_de_registration(de_reg_message):
    user_removed = False

    for registered_user in client_list:
        if registered_user["name"] == de_reg_message["name"]:
            user_removed = True
            client_list.remove(registered_user)
            print("Removing " + str(registered_user))

    if user_removed:
        # Send Result to Server B and update its memory
        server_msg = "DE-REGISTER" + " " + str(de_reg_message["name"]) + "," + serverIP + "," + str(serverPort)
        register_message_bytes = str.encode(server_msg)
        UDPClientSocket.sendto(register_message_bytes, server_b_address_port)

        new_reg_memory = str.encode(json.dumps(client_list) + "," + serverIP + "," + str(serverPort))
        UDPClientSocket.sendto(new_reg_memory, server_b_address_port)
        add_to_server_log("Server A: " + de_reg_message["name"] + ", " + "DE-REGISTERED")
        print(de_reg_message)
        print(new_reg_memory)


def user_update(update_message):
    client_address = (str(update_message["ip"]), int(update_message["socket"]))
    user_exists = False
    denial_reason = ""

    for registered_user in client_list:
        if registered_user["name"] == update_message["name"]:
            user_exists = True
            registered_user["ip"] = update_message["ip"]
            registered_user["socket"] = update_message["socket"]
            print("Updating " + registered_user["name"])
        if registered_user["ip"] == update_message["ip"] and registered_user["socket"] == update_message["socket"] and registered_user["name"] != update_message["name"]:
            denial_reason = "Requested ip/socket combination already exists"
            break

    if denial_reason == "" and user_exists is False:
        denial_reason = "User " + update_message["name"] + " does not exist"

    if user_exists:
        # Send response to the Client
        message = "UPDATE-CONFIRMED: " + str(update_message["rq_number"]) + " " + update_message["name"] \
                  + " " + update_message["ip"] + " " + str(update_message["socket"])
        update_message_bytes = str.encode(message)
        UDPServerSocket.sendto(update_message_bytes, client_address)

        # Log the message
        add_to_server_log("Server A: " + update_message["name"] + ", updated: " +
                          update_message["ip"] + ": " + str(update_message["socket"]))
        print(update_message["name"] + ", updated socket")

        # Send result to Server B
        server_msg = message + "," + serverIP + "," + str(serverPort)
        update_message_bytes = str.encode(server_msg)
        UDPClientSocket.sendto(update_message_bytes, server_b_address_port)

        new_reg_memory = str.encode(json.dumps(client_list) + "," + serverIP + "," + str(serverPort))
        UDPClientSocket.sendto(new_reg_memory, server_b_address_port)
        print(message)
        print(new_reg_memory)
    else:
        # Send response to the Client
        denial_message = "UPDATE-DENIED: " + str(update_message["rq_number"]) + ", " + denial_reason
        update_message_bytes = str.encode(denial_message)
        UDPServerSocket.sendto(update_message_bytes, client_address)

        # Log the message
        add_to_server_log("Server A: " + update_message["name"] + ", " + denial_message)
        print(update_message["name"] + ", " + denial_message)


def subjects_update(subjects_message, client_address):
    user_exists = False
    status = ""

    for registered_user in client_list:
        if registered_user["name"] == subjects_message["name"]:
            user_exists = True
            registered_user["subjects"] = subjects_message["subjects"]
            print("Updating " + str(registered_user))
    if user_exists:
        status = "SUBJECTS-UPDATED"

        # Send response to the Client
        message = status + ": " + str(subjects_message["rq_number"]) + " " + subjects_message["name"] \
                  + " " + str(subjects_message["subjects"])
        update_message_bytes = str.encode(message)
        UDPServerSocket.sendto(update_message_bytes, client_address)

        # Send Result to Server B and update its memory
        server_msg = status + " " + str(subjects_message["rq_number"]) + " " + str(
            subjects_message["name"]) + " " + str(subjects_message["subjects"]) + "," + serverIP + "," + str(serverPort)
        register_message_bytes = str.encode(server_msg)
        UDPClientSocket.sendto(register_message_bytes, server_b_address_port)

        new_reg_memory = str.encode(json.dumps(client_list) + "," + serverIP + "," + str(serverPort))
        UDPClientSocket.sendto(new_reg_memory, server_b_address_port)
        add_to_server_log("Server A: " + subjects_message["name"] + ", " + "SUBJECTS-UPDATED")

        # log the message
        add_to_server_log("Server A: " + subjects_message["name"] + ", updated: " +
                          str(subjects_message["subjects"]) + " " + status)

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
        add_to_server_log("Server A: " + subjects_message["name"] + ", updated: " +
                          str(subjects_message["subjects"]) + " " + status)
        print(subjects_message)
        print(message)


def change_server():
    # Change server message
    change_message = "CHANGE-SERVER," + server_b_address + "," + str(server_b_port)
    change_message_bytes = str.encode(change_message)

    # Send the message to each registered user
    for registered_user in client_list:
        user_address_port = (registered_user["ip"], int(registered_user["socket"]))
        UDPClientSocket.sendto(change_message_bytes, user_address_port)

    add_to_server_log("Server A: " + change_message)


def add_to_server_log(log):
    file = open("ServerALog.txt", "a")
    file.write("\n" + log)
    file.close()


if __name__ == "__main__":
    # Start the message thread
    t_message_stop = threading.Event()
    t_message = threading.Thread(target=listen_for_messages, args=(t_message_stop,))
    t_message_stop.set()
    t_message.start()
    # TODO: make listening thread like in client?
    while True:
        if isServerActive == 1:
            t_message_stop.clear()
            # Serving time
            print("Server A Listening")
            time.sleep(60)
            t_message_stop.set()

            # Join all the threads that were started during the serving time
            for element in thread_list:
                print("Joining thread with id: " + str(element.ident))
                element.join()

            # Send messages to all connected clients that the server is changing
            change_server()

            # Update Server B and Tell it to start serving
            new_memory = str.encode(json.dumps(client_list) + "," + serverIP + "," + str(serverPort))
            UDPClientSocket.sendto(new_memory, server_b_address_port)

            up_message_bytes = str.encode("SERVER UP," + serverIP + "," + str(serverPort))
            UDPClientSocket.sendto(up_message_bytes, server_b_address_port)
            print("Sent server up to B")
            isServerActive = 0
        else:
            # If Server B takes to long to respond, timeout and start serving again
            timeout_count = 0
            while isServerActive == 0:
                if timeout_count >= 13:
                    isServerActive = 1
                else:
                    time.sleep(5)
                    timeout_count += 1

    # Join the serving thread
    t_message.join()

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
        address = bytes_address_pair[1]

        # Only answer if the server is serving
        if not stop_event.is_set():
            message_dict = json.loads(message)

            # write message to log file
            client_msg = "Client to Server A: " + message_dict["request_type"] + " " + str(message_dict["rq_number"]) \
                         + " " + message_dict["name"] + " " + message_dict["ip"] + " " + str(message_dict["socket"])
            add_to_server_log(client_msg)

            if message_dict["request_type"] == "REGISTER":
                register_thread = threading.Thread(target=user_registration, args=(message_dict, address,))
                thread_list.append(register_thread)
                register_thread.start()
                add_to_server_log("Server A: Starting Registration for client " + message_dict["name"])
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


def user_registration(reg_message, client_address):
    # Check if the user already exists
    user_exists = False
    denial_reason = ""
    status = ""

    for registered_user in client_list:
        if registered_user.name == reg_message["name"]:
            user_exists = True
            denial_reason = "Name already exists"
        if registered_user.ip_address == reg_message["ip"] and registered_user.socket_num == reg_message["socket"]:
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
        reg_user = {"name": reg_message["name"], "ip": reg_message["ip"], "socket": reg_message["socket"]}
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

            # TODO: send messages to all connected clients that the server is changing + log
            # TODO: add timeout on server side in case the server gets shut down

            # Update Server B and Tell it to start serving
            new_memory = str.encode(json.dumps(client_list) + "," + serverIP + "," + str(serverPort))
            UDPClientSocket.sendto(new_memory, server_b_address_port)

            up_message_bytes = str.encode("SERVER UP," + serverIP + "," + str(serverPort))
            UDPClientSocket.sendto(up_message_bytes, server_b_address_port)
            print("Sent server up to B")
            isServerActive = 0

    # Join the serving thread
    t_message.join()

import socket
import threading
import time
import json
import RegisteredUser

# Server A information
serverIP = "127.0.0.1"
serverPort = 1000
bufferSize = 1024
isServerActive = 1
thread_list = []
client_list = []

# Server B information
server_b_address_port = ("127.0.0.1", 1001)
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
    while True:
        # Wait for messages from clients
        bytes_address_pair = UDPServerSocket.recvfrom(bufferSize)
        message = (bytes_address_pair[0].decode())
        address = bytes_address_pair[1]
        message_dict = json.loads(message)

        # Only answer if the server is serving
        if not stop_event.is_set():
            # write message to log file
            client_msg = "Client to Server A: " + message_dict["request_type"] + " " + str(message_dict["rq_number"]) \
                         + " " + message_dict["name"] + " " + message_dict["ip"] + " " + str(message_dict["socket"])
            add_to_server_log(client_msg)

            if message_dict["request_type"] == "REGISTER":
                register_thread = threading.Thread(target=user_registration, args=(message_dict, address,))
                thread_list.append(register_thread)
                register_thread.start()
                add_to_server_log("Server A: Starting Registration for client " + message_dict["name"])


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
        reg_user = RegisteredUser.RegisteredUser(reg_message["name"], reg_message["ip"], reg_message["socket"])
        client_list.append(reg_user)

        # Send response to the Client
        register_message_bytes = str.encode(registered_message)
        UDPServerSocket.sendto(register_message_bytes, client_address)

        # Log the message
        add_to_server_log("Server A: " + reg_message["name"] + ", " + registered_message)
        print(reg_message["name"] + ", " + registered_message)
        status = "REGISTERED"

    # Send Result to Server B
    server_msg = reg_message
    server_msg["request_type"] = status
    register_message_json = json.dumps(server_msg)
    register_message_bytes = str.encode(register_message_json)
    UDPClientSocket.sendto(register_message_bytes, server_b_address_port)
    print(reg_message)


def add_to_server_log(log):
    file = open("ServerALog.txt", "a")
    file.write("\n" + log)
    file.close()


if __name__ == "__main__":
    while True:
        if isServerActive == 1:
            t_message_stop = threading.Event()
            t_message = threading.Thread(target=listen_for_messages, args=(t_message_stop,))
            t_message.start()

            # Serving time
            time.sleep(100)
            t_message_stop.set()

            # Join all the threads that were started during the serving time
            for element in thread_list:
                print("Joining thread with id: " + str(element.ident))
                element.join()

            # TODO: send messages to all connected clients that the server is changing + log
            # TODO: tell server B that it can starting serving
            isServerActive = 0
        else:
            # Wait for messages from Server B
            print("Waiting for logs from Server B")
            server_b_bytes_address_pair = UDPServerSocket.recvfrom(bufferSize)
            server_b_message = (server_b_bytes_address_pair[0].decode())
            server_b_message_dict = json.loads(server_b_message)

            if server_b_message_dict["request_type"] == "SERVER":
                # TODO: reactivate the server
                isServerActive = 1
            else:
                # TODO: make this log properly
                server_b_client_msg = "Client to Server B: {}".format(str(server_b_message_dict))
                add_to_server_log("Starting Registration for client " + server_b_message_dict["name"])

    # Join the serving thread
    t_message.join()

class RegisteredUser:
    name = ""
    ip_address = ""
    socket_num = 0

    def __init__(self, name, ip_address, socket_num):
        self.name = name
        self.ip_address = ip_address
        self.socket_num = socket_num

    def to_string(self):
        return self.name + self.ip_address + str(self.socket_num)
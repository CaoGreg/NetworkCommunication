import socket
import json
import threading
import select
import datetime
from tkinter import *
from PIL import ImageTk, Image
import urllib.request
import xml.etree.ElementTree as  ElementTree
from tkinter import messagebox


#Global Variables for GUI
global userInput
name = "Please Enter Your Name"
postTopicID = 0
newsFeedTopics = {"AI" : False, "Cloud" : False, "Networking" : False, "Micro controllers" : False, "Micro processors" : False} 
userInputCommands = {"REGISTER" : 0, "DELETE ACCOUNT" : 1, "UPDATE IP ADDRESS" : 2, "UPDATE TOPICS LIST" : 3, "SUBMIT" : 4} 



#Global variable for Client
# Server Addresses
serverAAddressPort = ("127.0.0.1", 1000)
serverBAddressPort = ("127.0.0.1", 1001)
bufferSize = 1024
currentServerAddressPort = serverAAddressPort

# Client info
client_name = "Khendek"
ip_address = "127.0.0.1"
socket_number = 2000
subjects_of_interest = []

# Create a UDP socket at client side



class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.t_message_event = None
        self.t_message = None
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        #Pop up window Settings
        self.popUp = False
        self.entryNewIP = None
        self.entryNewSocket = None
        self.UserConnectionStatus = "Offline"

        #TODO Fix this socket issue (un comment line 52 to observe)
        #self.UDPClientSocket.bind((ip_address, socket_number))
    def show(self):
        self.lift()

    def listen_for_messages(self, stop_event):
        global currentServerAddressPort
        print("starting message")
        # Wait for messages
        while not stop_event.is_set():
            read, write, errors = select.select([self.UDPClientSocket], [], [], 1)
            for read_socket in read:
                server_message = self.UDPClientSocket.recvfrom(bufferSize)
                print(str(server_message[0].decode()))

                if "CHANGE-SERVER" in str(server_message[0]):
                    server_info = str(server_message[0].decode()).split(',')
                    currentServerAddressPort = (server_info[1], int(server_info[2]))
                    print("Current host: " + str(currentServerAddressPort))





    #User's functions
    #Button Execution
    def registrationClick(self):

        #TODO: Investigate crash (crashes when servers are offline)

        # Send register request to both servers
        registerMessage = {"request_type": "REGISTER", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                            "name": client_name, "ip": ip_address, "socket": str(socket_number)}
        registerMessageJson = json.dumps(registerMessage)
        registerMessageBytes = str.encode(registerMessageJson)

        self.UDPClientSocket.sendto(registerMessageBytes, serverAAddressPort)
        self.UDPClientSocket.sendto(registerMessageBytes, serverBAddressPort)

        msg = self.UDPClientSocket.recvfrom(bufferSize)
        if "REGISTERED" in str(msg):
            #messagebox.showinfo(title="Operation Result", message="The account has been registered")
            # Start listening to the server
            self.t_message_event = threading.Event()
            self.t_message.start()

        print(msg)
        





    def updateTopicsListClick(self):
            print("Starting subjects of interest update")
            # TODO: make this user input
            # TODO Implement and link global dictionnary (line 17)
            subj = ["AI", "Cloud"]
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
    
    



    def updateIPAddressClick(self):

        print("Starting ip/socket update")

        #TODO Fetch and restart new IP
        # Get new ip/socket info
        #print("Please enter your new ip")
        new_ip = input()

        #print("Please enter your new socket")
        new_socket = input()


        # Update ip/socket info
        ip_address = str(new_ip)
        socket_number = int(new_socket)
        try:
            # Stop the listening thread
            self.t_message_event.set()
            self.t_message.join()
            self.t_message_event.clear()

            # Starting new listening thread with new socket
            self.UDPClientSocket.close()
            self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.UDPClientSocket.bind((ip_address, socket_number))
            self.t_message = threading.Thread(target=listen_for_messages, args=(t_message_event,))
            self.t_message.start()

            # Create update message
            update_message = {"request_type": "UPDATE", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                                "name": client_name, "ip": ip_address, "socket": socket_number}
            update_message_json = json.dumps(update_message)
            update_message_bytes = str.encode(update_message_json)

            # Send message to current active server
            UDPClientSocket.sendto(update_message_bytes, currentServerAddressPort)
        except NameError:
            print("Client wasn't registered, cannot update ip/socket")
        else:
            print("Client was de-registered")







    def refreshClick(self):
        #TODO
        pass





    def accountDeletionClick(self):
        response = messagebox.askokcancel("ACCOUNT DELETION ", "Do you wish to delete this account ?")
        if response == True:
            print("OK button clicked")
            print("Starting De-registering")

            # Create de-register message
            de_register_message = {"request_type": "DE-REGISTER", "rq_number":
                                    int(datetime.datetime.utcnow().timestamp()), "name": client_name}
            de_register_message_json = json.dumps(de_register_message)
            de_register_message_bytes = str.encode(de_register_message_json)

            # Send message to current active server
            self.UDPClientSocket.sendto(de_register_message_bytes, currentServerAddressPort)

            # Stop the listening thread
            try:
                t_message_event.set()
                self.t_message.join()
                t_message_event.clear()
            except NameError:
                messagebox.showerror(title="ACCOUNT DELETION ", message="Error: Client wasn't registered, nothing to de-register")
                print("Client wasn't registered, nothing to de-register")
            else:
                print("Client was de-registered")
        elif response == False:
            print("Cancel button clicked")
    def submissionClick(self):
            print("Starting subjects of interest publish")
            # TODO: add user input here for subject
            print("Please enter the text you want to publish")
            text = input()

            # Create publish message
            publish_message = {"request_type": "PUBLISH", "rq_number": int(datetime.datetime.utcnow().timestamp()),
                                "name": client_name, "subject": "AI", "text": text}
            publish_message_json = json.dumps(publish_message)
            publish_message_bytes = str.encode(publish_message_json)

            try:
                t_message_event.clear()
                # Send message to current active server
                UDPClientSocket.sendto(publish_message_bytes, currentServerAddressPort)
            except NameError:
                print("Client wasn't registered, cannot publish messages")






class Page1(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       # create a canvas to show image on
       canvas_for_image = Canvas(self, bg='white', height=194, width=259, borderwidth=0, highlightthickness=0)
       canvas_for_image.grid(row=1, column=3, columnspan=4, sticky='nesw', padx=0, pady=0)
       image = Image.open('Registration.png')
       canvas_for_image.image = ImageTk.PhotoImage(image.resize((259, 194), Image.ANTIALIAS))
       canvas_for_image.create_image(0, 0, image=canvas_for_image.image, anchor='nw')
       

       #Left Side
       #texts
       Label (self, text='\nUser Connection Status: ' + self.UserConnectionStatus, bg="white", fg="black", font="non 12 bold").grid(row=0, column=7, sticky=W)
       Label (self, text='\n\nUser ID:', bg="white", fg="black", font="non 12 bold").grid(row=2, column=0, sticky=W)
       Label (self, text='\nPassword:', bg="white", fg="black", font="non 12 bold").grid(row=5, column=0, sticky=W)


        #Textbox
       textentry_UserID = Entry(self, width=50,bg="white")
       textentry_UserID.grid(row=4,column=0, columnspan=3, sticky=W)

       textentry_Password = Entry(self, width=50,bg="white")
       textentry_Password.grid(row=6,column=0, columnspan=3, sticky=W)


       
       Button(self, command=self.registrationClick,text="REGISTER", width=8,state="active").grid(row=7, column=3, sticky=W)
       Button(self, command=self.accountDeletionClick,text="DELETE \nACCOUNT", width=8,state="active").grid(row=7, column=5, sticky=W)
       Button(self, command=self.updateIPAddressClick,text="UPDATE IP \nADDRESS", width=8,state="active").grid(row=7, column=7, sticky=W)


class Page2(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       # create a canvas to show image on
       canvas_for_image = Canvas(self, bg='white', height=200, width=200, borderwidth=0, highlightthickness=0)
       canvas_for_image.grid(row=0, column=1, columnspan=3, sticky='nesw', padx=0, pady=0)
       image = Image.open('udp.png')
       canvas_for_image.image = ImageTk.PhotoImage(image.resize((400, 200), Image.ANTIALIAS))
       canvas_for_image.create_image(0, 0, image=canvas_for_image.image, anchor='nw')
       #texts and 
       Label (self, text='\n\nSelect your News Feed Topics:', bg="white", fg="black", font="non 12 bold").grid(row=1, column=0, sticky=W)
       Label (self, text="\n\nSelect post's Topic:", bg="white", fg="black", font="non 12 bold").grid(row=4, column=0, sticky=W)
       Label (self, text='\nType the description:', bg="white", fg="black", font="non 12 bold").grid(row=6, column=0, sticky=W)

       CheckVar1 = IntVar()
       CheckVar2 = IntVar()
       CheckVar3 = IntVar()
       CheckVar4 = IntVar()
       CheckVar5 = IntVar()
       Checkbutton(self, text = "AI", variable = CheckVar1,onvalue = 1, offvalue = 0, height=5, width = 20, ).grid(row=2, column=0, sticky=W)
       Checkbutton(self, text = "Cloud", variable = CheckVar2, onvalue = 1, offvalue = 0, height=5, width = 20).grid(row=2, column=1, sticky=W)
       Checkbutton(self, text = "Networking", variable = CheckVar3,onvalue = 1, offvalue = 0, height=5, width = 20, ).grid(row=2, column=2, sticky=W)
       Checkbutton(self, text = "Micro controllers", variable = CheckVar4, onvalue = 1, offvalue = 0, height=5, width = 20).grid(row=2, column=3, sticky=W)
       Checkbutton(self, text = "Micro processors", variable = CheckVar5,onvalue = 1, offvalue = 0, height=5, width = 20, ).grid(row=2, column=4, sticky=W)





        #Topics List
       v = StringVar(self, "0") 
       values = {"AI" : "1", 
               "Cloud" : "2", 
               "Networking" : "3", 
               "Micro controllers" : "4", 
               "Micro processors" : "5"} 
       counter = 0
       for (text, value) in values.items(): 
           Radiobutton(self, text = text, variable = v, 
               value = value).grid(row=5,column=counter, sticky=W) 
           counter = counter + 1
        #Textbox
       textentry_Description = Entry(self, width=50,bg="white")
       textentry_Description.grid(row=7,column=0, columnspan=3, sticky=W)

       #Button
       Button(self, command=self.updateTopicsListClick, text="UPDATE NEWS FEED\nTOPICS LIST", width=25).grid(row=3, column=2, sticky=W)
       Button(self, command=self.submissionClick, text="SUBMIT", width=25).grid(row=8, column=2, sticky=W)

class Page3(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       LB1 = Listbox(
           master=self,
           selectmode='single',
           width=600,
           height=35,
           fg='black',
           bg='skyblue')
       SB = Scrollbar(self, orient='vertical')
       SB.pack(side=RIGHT, fill=Y)
       LB1.configure(yscrollcommand=SB.set)
       SB.configure(command=LB1.yview)
       SB2 = Scrollbar(self, orient='horizontal')
       SB2.pack(side=BOTTOM, fill=X)
       LB1.configure(xscrollcommand=SB2.set)
       SB2.configure(command=LB1.xview)
       LB1.pack()
       
       LB1.insert('end', "NEWS HEADLINES ")
       LB1.itemconfig('end', {'bg': 'white'})
       self.get_news(LB1)
       LB1.insert('end', "_____________________________________ END")

       Button(self, command=self.refreshClick, text="REFRESH", width=25, bg='#0052cc', fg='#ffffff').pack()

   def get_news(self, LB1):
       #TODO Modify this function to take in .json files and read news feed
       URL = "http://feeds.bbci.co.uk/news/rss.xml"
       REQ = urllib.request.urlopen(URL)
       PAGE = REQ.read()
       DOC = ElementTree.fromstring(PAGE)

       for item in DOC.iter('item'):
           title = item.find('title').text
           pubDate = item.find('pubDate').text
           LB1.insert('end', pubDate)
           LB1.insert('end', title)
           link = item.find('link').text
           LB1.insert('end', link)
           LB1.itemconfig('end', {'fg': 'blue'})
           LB1.insert('end', "-------------------------------------------------")

class MainView(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        p1 = Page1(self)
        p2 = Page2(self)
        p3 = Page3(self)

        buttonframe = Frame(self)
        container = Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)


        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)


        b1 = Button(buttonframe, text="Registration", command=p1.lift)
        b2 = Button(buttonframe, text="Topic List/Publish", command=p2.lift)
        b3 = Button(buttonframe, text="News Feed", command=p3.lift)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")

        p1.show()


if __name__ == "__main__":

    # TODO: 1) client does not get answer from the server if not registered, is this ok?
    # TODO: 2) user input for subjects of interest and publishing
    # TODO: 3) link all button and text entry

    window = Tk()
    main = MainView(window)
    window.title("Netwok and Communication Project - Client")
    main.pack(side="top", fill="both", expand=True)
    window.wm_geometry("950x700")
    window.configure(bg="white")
    window.mainloop()
    

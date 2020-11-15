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

class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()
    
    #Button Execution
    def registrationClick(self):
        pass
    def updateTopicsListClick(self):
        pass
    def updateIPAddressClick(self):
        pass
    def refreshClick(self):
        #TODO
        pass
    def accountDeletionClick(self, result):
        #if account exist
        if(result):
            #messagebox.showerror(title="ACCOUNT DELETION ", message="Error, No Account")
            pass
        else:
            response = messagebox.askokcancel("ACCOUNT DELETION ", "Do you wish to delete this account ?")
            if response == True:
                pass
                print("OK button clicked")
            elif response == False:
                print("Cancel button clicked")
    def submissionClick(self):
        pass


class Page1(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       # create a canvas to show image on
       canvas_for_image = Canvas(self, bg='green', height=194, width=259, borderwidth=0, highlightthickness=0)
       canvas_for_image.grid(row=0, column=2, columnspan=3, sticky='nesw', padx=0, pady=0)
       image = Image.open('Registration.png')
       canvas_for_image.image = ImageTk.PhotoImage(image.resize((259, 194), Image.ANTIALIAS))
       canvas_for_image.create_image(0, 0, image=canvas_for_image.image, anchor='nw')
       

       #Left Side
       #texts
       Label (self, text='\n\nUser ID:', bg="white", fg="black", font="non 12 bold").grid(row=1, column=0, sticky=W)
       Label (self, text='\nPassword:', bg="white", fg="black", font="non 12 bold").grid(row=4, column=0, sticky=W)
       Label (self, text='\nConfirm Password:', bg="white", fg="black", font="non 12 bold").grid(row=6, column=0, sticky=W)

        #Textbox
       textentry_UserID = Entry(self, width=50,bg="white")
       textentry_UserID.grid(row=3,column=0, columnspan=3, sticky=W)

       textentry_Password = Entry(self, width=50,bg="white")
       textentry_Password.grid(row=5,column=0, columnspan=3, sticky=W)

       textentry_ConfirmPassword = Entry(self, width=50,bg="white")
       textentry_ConfirmPassword.grid(row=7,column=0, columnspan=3, sticky=W)

       

       #Button
       Button(self, command=self.registrationClick,text="REGISTER", width=8).grid(row=8, column=1, sticky=W)
       Button(self, command=self.accountDeletionClick,text="DELETE \nACCOUNT", width=8).grid(row=8, column=3, sticky=W)
       Button(self, command=self.updateIPAddressClick,text="UPDATE IP \nADDRESS", width=8).grid(row=8, column=5, sticky=W)


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
       Button(self, command=self.updateTopicsListClick, text="UPDATE NEWS FEED\nTOPICS LIST", width=25).grid(row=3, column=1, sticky=W)
       Button(self, command=self.submissionClick, text="SUBMIT", width=6).grid(row=8, column=2, sticky=W)

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
       #TODO Modify this function to take in .json files
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
    userInput = 5 #5 = No input Entered
    window = Tk()
    main = MainView(window)
    window.title("Netwok and Communication Project - Client")
    main.pack(side="top", fill="both", expand=True)
    window.wm_geometry("900x700")
    window.configure(bg="white")
    window.mainloop()
    print("Debug test______Hmmmmm")
    


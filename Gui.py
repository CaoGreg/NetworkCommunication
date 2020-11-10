from tkinter import *
from PIL import ImageTk, Image

class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()

class Page1(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       
       # create a canvas to show image on
       canvas_for_image = Canvas(self, bg='green', height=200, width=200, borderwidth=0, highlightthickness=0)
       canvas_for_image.grid(row=0, column=3, columnspan=3, sticky='nesw', padx=0, pady=0)
       image = Image.open('account.png')
       canvas_for_image.image = ImageTk.PhotoImage(image.resize((200, 200), Image.ANTIALIAS))
       canvas_for_image.create_image(0, 0, image=canvas_for_image.image, anchor='nw')
       
       #texts
       Label (self, text='\n\nUser ID:', bg="white", fg="black", font="non 12 bold").grid(row=1, column=0, sticky=W)
       Label (self, text='\nPassword:', bg="white", fg="black", font="non 12 bold").grid(row=4, column=0, sticky=W)

        #Textbox
       textentry_LogIn = Entry(self, width=50,bg="white")
       textentry_LogIn.grid(row=3,column=0, columnspan=3, sticky=W)

       textentry_Description = Entry(self, width=50,bg="white")
       textentry_Description.grid(row=5,column=0, columnspan=3, sticky=W)

       #Button
       Button(self, text="SIGN IN", width=7).grid(row=6, column=0, sticky=W)

class Page2(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       # create a canvas to show image on
       canvas_for_image = Canvas(self, bg='green', height=200, width=500, borderwidth=0, highlightthickness=0)
       canvas_for_image.grid(row=0, column=2, columnspan=3, sticky='nesw', padx=0, pady=0)
       image = Image.open('signup.png')
       canvas_for_image.image = ImageTk.PhotoImage(image.resize((500, 200), Image.ANTIALIAS))
       canvas_for_image.create_image(0, 0, image=canvas_for_image.image, anchor='nw')
       
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
       Button(self, text="REGISTER", width=8).grid(row=8, column=0, sticky=W)


class Page3(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       # create a canvas to show image on
       canvas_for_image = Canvas(self, bg='green', height=200, width=400, borderwidth=0, highlightthickness=0)
       canvas_for_image.grid(row=0, column=1, columnspan=3, sticky='nesw', padx=0, pady=0)
       image = Image.open('udp.png')
       canvas_for_image.image = ImageTk.PhotoImage(image.resize((400, 200), Image.ANTIALIAS))
       canvas_for_image.create_image(0, 0, image=canvas_for_image.image, anchor='nw')
       #texts and 
       Label (self, text='\n\nSelect your Topics:', bg="white", fg="black", font="non 12 bold").grid(row=1, column=0, sticky=W)
       Label (self, text='\nType the description:', bg="white", fg="black", font="non 12 bold").grid(row=4, column=0, sticky=W)

        #Topics List
       v = StringVar(self, "1") 
       values = {"AI" : "1", 
               "Cloud" : "2", 
               "Networking" : "3", 
               "Micro controllers" : "4", 
               "Micro processors" : "5"} 
       counter = 0
       for (text, value) in values.items(): 
           Radiobutton(self, text = text, variable = v, 
               value = value).grid(row=3,column=counter, sticky=W) 
           counter = counter + 1
        #Textbox
       textentry_Description = Entry(self, width=50,bg="white")
       textentry_Description.grid(row=5,column=0, columnspan=3, sticky=W)

       #Button
       Button(self, text="SUBMIT", width=6).grid(row=6, column=0, sticky=W)

class Page4(Page):
   def __init__(self, *args, **kwargs):
       Page.__init__(self, *args, **kwargs)
       label = Label(self, text="This is page 4")
       label.pack(side="top", fill="both", expand=True)

class MainView(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        p1 = Page1(self)
        p2 = Page2(self)
        p3 = Page3(self)
        p4 = Page4(self)

        buttonframe = Frame(self)
        container = Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p4.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = Button(buttonframe, text="Log In", command=p1.lift)
        b2 = Button(buttonframe, text="Register", command=p2.lift)
        b3 = Button(buttonframe, text="Publish", command=p3.lift)
        b4 = Button(buttonframe, text="News Feed", command=p4.lift)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")
        b4.pack(side="left")

        p1.show()

if __name__ == "__main__":
    window = Tk()
    main = MainView(window)
    window.title("Netwok and Communication Project - Client")
    main.pack(side="top", fill="both", expand=True)
    window.wm_geometry("800x500")
    window.configure(bg="white")
    window.mainloop()


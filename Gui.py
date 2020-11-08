from tkinter import *
import tkinter.ttk as ttk


#key functions
#Collect the text from the text box
def click_SUBMIT():
    entered_Description=textentry_Description.get()
    #TODO send the textbox information to the server here

#Creating blank window
window = Tk()
window.title("Netwok and CommunicationProject - Client")
window.geometry('800x500')
window.configure(bg="white")

#Logo/ Photo
photo = PhotoImage(file="udp.png")
Label (window, image=photo, bg="white").grid(row=0,column=1,columnspan=3, sticky=W)


#texts and 
Label (window, text='\n\nSelect your Topics:', bg="white", fg="black", font="non 12 bold").grid(row=1, column=0, sticky=W)
Label (window, text='\nType the description:', bg="white", fg="black", font="non 12 bold").grid(row=4, column=0, sticky=W)

#Topics List
v = StringVar(window, "1") 
values = {"AI" : "1", 
          "Cloud" : "2", 
          "Networking" : "3", 
          "Micro controllers" : "4", 
          "Micro processors" : "5"} 
counter = 0
for (text, value) in values.items(): 
    Radiobutton(window, text = text, variable = v, 
        value = value).grid(row=3,column=counter, sticky=W) 
    counter = counter + 1

#Textbox
textentry_Description = Entry(window, width=50,bg="white")
textentry_Description.grid(row=5,column=0, columnspan=3, sticky=W)

#Button
Button(window, text="SUBMIT", width=6, command=click_SUBMIT).grid(row=6, column=0, sticky=W)

window.mainloop() 
from tkinter import *           #We need EVERYTHING from tkinter
from tkinter import ttk         #For shorter terms, just use ttk
import inspect                  #Inspect is used for getting the path of the script and the directory
import os   
import apod_desktop                         #We need APOD desktop for its functions
import image_lib            #Image library for downloading new APODs
import ctypes                       #Ctypes is used to make our window a process
from PIL import ImageTk, Image          #Pillow is only used for two functions to create specific label frames and such
from tkcalendar import DateEntry            #DateEntry is the calender used when selecting dates
from datetime import date                           #And with this in mind, we also need datetime

script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)        #Get the full path of the script
script_dir = os.path.dirname(script_path)                       #Get the full directory of script

apod_desktop.init_apod_cache(script_dir)        #And initalize the cache in case it does not already exist


#This is a neat lil function I put together to clear the cache
#Sadly, it goes unused due to time constraints
def flush():
    image_apod.configure(image="default.png")       #Not exactly finished
    apod_desktop.init_apod_cache(script_dir)
    return


#This function activates whenever an APOD has been selected
def apod_selection(event):
    select_apod = box_image_selection.current() + 1     #Increase choice by 1 (change it)

    info = apod_desktop.get_apod_info(select_apod)      #Get APOD info
    imagepath = info['file_path']               #Get the file path from the info received


    #For image scaling, we scale the provided image to its width and height dimensions before any changes are made.
    #This will create a resized image
    unsized_image = Image.open(imagepath)           #Get the given picture from the image path                
    size = image_lib.scale_image(image_size=(unsized_image.width, unsized_image.height))      #The size is the the image scaled down
    global resize
    resize = unsized_image.resize(size)

    #To be modified by other functions, make the apod image global
    global image_apod
    image_apod = ImageTk.PhotoImage(resize)     #The image apod will be the resized photo in question
    label_image.configure(image=image_apod)         #Configure the current image (default.png) to become the image
    label_description.configure(text=info['explanation'], wraplength=root.winfo_width(), justify="left")    #Display the explanation with a wraplength to match the window length of the screen. It will stick to the left so it does not trail off
    return


#This function is what happens when Set as Desktop is pressed

def setdesktop():
    select_apod = box_image_selection.current() + 1

    info = apod_desktop.get_apod_info(select_apod)      #Get the APOD info
    imagepath = info['file_path']                           #Grab the file path
    image_lib.set_desktop_background_image(imagepath)       #And set as background using it


#This function runs when a date is grabbed that responds with an APOD date, it will download
#the image requested and add it to the cache

def download_image():
    date = date_entry_dateselect.get_date()     #We get the current date by using the date_entry get_date function

    if date < date.fromisoformat("1995-06-16"):     #If it is too far back, print an error
        print("Error! Date is too far back!")
        return
    elif date > date.today():           #If the date exceeds today, print error and cease
        print("Error! Date exceeds the current date")
        return
    apod_desktop.add_apod_to_cache(date)                        #Add the APOD to the cache
    box_image_selection.configure(values=apod_desktop.get_all_apod_titles())      #Change the selection box to match recently downloaded images
    return

#This function resizes the image
#it goes unused since I didn't figure it out in time
def resize(event):
    #event.grid(row=0, column=1, padx=5, pady=15)
    return


#Here is where we create the window as well as the process that holds it

root = Tk()                                 #Initalize our window
root.title("APOD Viewer")           #Give it the title
root.rowconfigure(0, weight=1)              #Configure the weight for row 0
root.rowconfigure(1, weight=1)                 #same with 1 and 2
root.rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)               #And column 0 will have a weight of 1
root.bind("<Configure>", resize)            #Configure the image and resize it (doesn't resize it)

app_id = "APOD"     #Give the app an ID name
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)   #Set it as a process
root.iconbitmap(os.path.join(script_dir, "poke.ico"))           #Include our icon


#Here is where we create our frames, which keep the window organized and are meant to be user friendly
frame_top = ttk.Frame(root)         #Create the Top frame which hosts our image, and add it to row 0
frame_top.grid(row=0, column=0, columnspan=3, padx=5, pady=5)       #It is meant to span 3 columns

frame_mid = ttk.Frame(root) #Create our middle frame, which will span 3 columns as well.
frame_mid.grid(row=1, column=0, columnspan=3, padx=0, pady=0, sticky=NSEW)
frame_mid.columnconfigure(0, weight=1)
frame_mid.rowconfigure(0, weight=1)         #Configure both the row and column of 0 to have a weight of 1

frame_bot_left = ttk.LabelFrame(root, text="View Cached Image") #Create our first label frame which contains the text to view the cache image
frame_bot_left.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=W) #Put it in the second frame so it does not overlap with anything
frame_bot_left.columnconfigure(0, weight=1)         #Configure the columns and rows to our liking
frame_bot_left.rowconfigure(0, weight=1)
frame_bot_left.rowconfigure(1, weight=1)
frame_bot_left.rowconfigure(2, weight=1)

#Create the label frame to get more images
frame_bot_right = ttk.LabelFrame(root, text="Get more Images")
frame_bot_right.grid(row=2, column=2, padx=5, pady=5, sticky=W) #Set up our parameters
frame_bot_right.columnconfigure(0, weight=1)
frame_bot_right.rowconfigure(0, weight=1)

#Setup the default image which will replace the image with whatever APOD is selected. By default it uses the NASA logo
image_apod = ImageTk.PhotoImage(file=os.path.join(script_dir, "default.png"))
label_image = ttk.Label(frame_top, image=image_apod)    #The label for the image is on the top of the frame and consists of the image
label_image.grid(padx=0, pady=0)


label_description = ttk.Label(frame_mid, text="") #Create the description label which holds the explanation. By default, it is blank
label_description.grid(padx=20, pady=0, sticky=NSEW)

#Create our image selector label
label_imageselect = ttk.Label(frame_bot_left, text="Select an Image: ", width=12)
label_imageselect.grid(row=0, column=0, padx=5, pady=5, sticky=W)

#And right beside it, create a combobox that is read only on the left frame, which holds the value of all the apod_titles
box_image_selection = ttk.Combobox(frame_bot_left, width=40, state="readonly", values=apod_desktop.get_all_apod_titles())
box_image_selection.grid(row=0, column=1, padx=5, pady=5, stick=W)
box_image_selection.set("Select an Image")
box_image_selection.bind("<<ComboboxSelected>>", apod_selection)

#Create a button to set an image as the desktop
btn_imageselect = ttk.Button(frame_bot_left, text="Set as Desktop", command=setdesktop) #The command will run the desktop function
btn_imageselect.grid(row=0, column=0, padx=5, pady=5, sticky=W)

#Create a label that is near the calender
label_dateselect = ttk.Label(frame_bot_right, text= "Select Date: ")
label_dateselect.grid(row=0, column=0, padx=5, pady=5)

#Create a calendar widget using DateEntry. It is on the right frame and hosts in the format of YYYY-MM-DD. The calendar cannot be edited
date_entry_dateselect = DateEntry(frame_bot_right, date_pattern="YYYY-MM-DD", state="readonly")
date_entry_dateselect.grid(row=0, column=1, padx=5, pady=5)

#Create a button to download a selected image. The command will run the download image function
btn_imagedownload = ttk.Button(frame_bot_right, text="Download Image", command=download_image)
btn_imagedownload.grid(row=0, column=2, padx=5, pady=5)

root.mainloop()     #loop until the window is closed
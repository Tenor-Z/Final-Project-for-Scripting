'''
Library of useful functions for working with images.
'''

import requests #Requests is used to download the images needed
import ctypes    #Ctypes is used to use user32.dll to set the background

#The main function is used for testing purposes only. The functions are called individually in apod_desktop
#For testing purposes, I downloaded a jpg I hosted on a web server from a Kali Linux VM

def main():
    #download_image("192.168.2.114/test.jpg") 
    return


#This function downloads whatever image is specified in the parameter. It does not save it to the disk, rather it grabs the request contents of said file, which it can later use to write to a file

def download_image(image_url):
    """Downloads an image from a specified URL.
    DOES NOT SAVE THE IMAGE FILE TO DISK.
    Args:
        image_url (str): URL of image
    Returns:
        bytes: Binary image data, if succcessful. None, if unsuccessful.
    """
    
    request = requests.get(image_url) #Get the image data with requests.get
    
    if request.ok: #If we recieve the OK signal, then return the contents
        return request.content
    else: #Otherwise, something screwed up
        return None
    

#This function will save the contents of the images downloaded. It will specify a path to save it in and the data sent to it. It is essentially binary data of the image

def save_image_file(image_data, image_path):
    """Saves image data as a file on disk.
    
    DOES NOT DOWNLOAD THE IMAGE.
    Args:
        image_data (bytes): Binary image data
        image_path (str): Path to save image file
    Returns:
        bytes: True, if succcessful. False, if unsuccessful
    """
    
    #print(f'the path is {image_path}')
    #print("GO FIND IT!!")
    
    with open(image_path, 'wb') as f:  #Create a file with the image path that was specified
        f.write(image_data) #Write the contents of the image data to a binary file
        f.close() #Close it and exit
        return True


#This function will set the image as the background. Remember that these functions will be frequently called individually by apod_desktop and mainly serves as a library of functions

def set_desktop_background_image(image_path):
    """Sets the desktop background image to a specific image.
    Args:
        image_path (str): Path of image file
    Returns:
        bytes: True, if succcessful. False, if unsuccessful        
    """

    #The strategy is to use Ctypes to set the background since it allows us to operate Windows drivers, especially user32.dll which manages the Desktop. By specifying the SETDESKWALLPAPER, we can specify the height and width of the image (not relevant since it will be scaled later). User32.dll will set the Desktop background using the image_path. If we recieve any type of error, just return False
  
    try:
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)   #Set the image as the Desktop Background
        return True
    except:          #If any error, return False and get outta there!
        return False
    
    return


#This function scales the image automatically by calculating the dimensions of said image. I did not write this function

def scale_image(image_size, max_size=(800, 600)):
    """Calculates the dimensions of an image scaled to a maximum width
    and/or height while maintaining the aspect ratio  
    Args:
        image_size (tuple[int, int]): Original image size in pixels (width, height) 
        max_size (tuple[int, int], optional): Maximum image size in pixels (width, height). Defaults to (800, 600).
    Returns:
        tuple[int, int]: Scaled image size in pixels (width, height)
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    # NOTE: This function is only needed to support the APOD viewer GUI
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size

if __name__ == '__main__':
    main()
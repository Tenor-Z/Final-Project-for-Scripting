""" 
COMP 593 - Final Project
Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.
Usage:
  python apod_desktop.py [apod_date]
Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""

from datetime import date       #We need datetime for selecting APOD dates
import hashlib                  #Hashlib generates hashes for comparison and for our database tables
import os        
import re               #We only use re for a small regex for seperating a name from the file extension
from apod_api import get_apod_image_url         #We need this function to get the URL specifically
from apod_api import get_apod_info as get_apod_info_api     #Need this for apod info gathering
import image_lib                #Image library is needed for all of our image needs
import inspect                  #inspect is only used a few times to get the full path of the script
import sys
import sqlite3                  #Sqlite3 is for interacting with our database


# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])


#This function gets the APOD date. It is then tossed to other python functions in order
#to get more data as to where to download it and the info it contains. It queries the API
#for the selective date given in argv1 in which it will later be stored into the Database

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.
    Returns:
        date: APOD date
    """

    apod_date = date.today()        #If no date is specified, just use today's date
    

    #First we need to check how much arguments were passed. This is important so we don't get
    #errors for list indexes out of range and such

    if len(sys.argv) == 2:          #Try this if the amount of arguments equals to 2
        try:
            apod_date = date.fromisoformat(sys.argv[1])     #Try to format the first argument to a date format
        except ValueError:          #If it doesn't work, just print that it is an invalid string
            print("Error: Invalid date string: " + str(sys.argv[1]))
            sys.exit()      #And exit
    

    if apod_date > date.today():            #If the date exceeds today's date, print the error and exit
        print("Error: The date must be in the past or today: " + apod_date.isoformat())
        sys.exit()
    
    return apod_date                #Return the date we get nonetheless


#This function merely just gets the full path of the script using inspect
#I did not write this

def get_script_dir():
    """Determines the path of the directory in which this script resides
    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)


#Once arguments have been validated, we can begin to initalize the apod cache. If it does not exit
#we can simply create it and format it to our liking. It will reside in its own folder 'imgcache'

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.
    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir  #Since the cache dir might be modified in the future, let's global it
    global image_cache_db       #Same with the database

    image_cache_dir = os.path.join(parent_dir, "imgcache\\") #Get the full path of the cache directory
    
    #If the cache folder does not exist, create it

    if os.path.isdir(image_cache_dir) == False:
        os.mkdir(image_cache_dir)
        print("Image cache directory created: " + image_cache_dir)
    else:
        print("Image cache directory already exists: " + image_cache_dir)
        
    image_cache_db = os.path.join(image_cache_dir, "image_cache.db")  #Get the full path of the cache directory
    
    
    #If the cache DB does not exist, create it

    if os.path.exists(image_cache_db) == False:
        connectus = sqlite3.connect(image_cache_db)     #Set up our connection using sqlite3
        cursor = connectus.cursor()         #initalize our cursor
        

        #For our apod_table, we need to make sure we get the title, explanation (description), the ID (for identification)
        #and the hash. The values must not be blank

        create_apod_table_sql = """
        CREATE TABLE IF NOT EXISTS apod_image
        (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            explanation TEXT NOT NULL,
            path TEXT NOT NULL,
            sha256 TEXT NOT NULL
        );
        """
        
        cursor.execute(create_apod_table_sql)           #Execute our query
        
        connectus.commit()                      #Commit the changes and exit
        connectus.close()
        print("Image cache DB created: " + image_cache_db) 
    else:
        print("Image cache DB already exists: " + image_cache_db)
    return
        


#Here is where we take the selected APOD_date from earlier and add it to the cache
#We download using the apod_api and image_lib. The hashes are compared to check if the
#file is already in the cache. After that, it is added to the cache

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.
    Args:
        apod_date (date): Date of the APOD image
    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    
    
    print("APOD date:", apod_date.isoformat())  #Print the date from argv 1 (for debugging)

    apod_info = get_apod_info_api(apod_date)            #Get info about it
    
    apod_image_url = get_apod_image_url(apod_info)       #Use the image_url function to download the image
    image_data = image_lib.download_image(apod_image_url)       #Download the image using image_lib with the url
    print("Downloaded image from " + apod_image_url) 
    
    

    #Now we must compare the hashes to ensure we actually have the file and it doesn't match something already in the cache
    
    image_hash = hashlib.sha256(image_data).hexdigest()         #To do, we generate a hash for the data from the image
    print("APOD SHA-256: " + str(image_hash))       #Print it for debugging
    


    apod_id = get_apod_id_from_db(image_hash)  #Search the database for a matching hash to what was generated
    if  apod_id == 0:                               #If it doesn't exist, create it
        
        apod_image_path = determine_apod_file_path(     #Get the file path of the downloaded file using the title from gathered info, as well as the url
                apod_info['title'],
                apod_image_url
                )
        # Save the APOD file to the image cache directory
        print("APOD does not exist in cache")
        image_lib.save_image_file(image_data, apod_image_path)  #Save the image using image.lib
        
        #For the APOD ID, we combine everything we have found into an entry for the DB
        apod_id = add_apod_to_db(
            apod_info['title'],
            apod_info['explanation'],
            apod_image_path,
            image_hash
        )
        
        return apod_id  #Return the ID we created
        
        
    else:
        print("APOD already exists in cache")
        return apod_id


#This function will add apod data to the database using other functions to gather each of the parameter data
#It gets the information from the apod_date which is found on the URL, and is saved to cover for the file_path

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image
    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    
    apod_id = get_apod_id_from_db(sha256)   #Get the apod ID from the function
    if apod_id != 0:        #If it is not empty
        return apod_id      #Just return the id
    
    connectus = sqlite3.connect(image_cache_db)     #Initalize our connection
    cursor = connectus.cursor()                     #Initalize our cursor
    
    
    #For the APOD query, we just fill in the title, explanation, etc.
    #The wildcards (?) mean any data suited for the type can be inputted as the value

    add_apod_query = """
    INSERT INTO apod_image (title, explanation, path, sha256)
    VALUES (?, ?, ?, ?);
    """
    
    apod = (title, explanation, file_path, sha256)  #We use this data to get the apod data
    
    cursor.execute(add_apod_query, apod)        #Execute the query and add our apod to the cache
    
    connectus.commit()      #commit and exit
    connectus.close() 
    
    
    return cursor.lastrowid #Return the ID
    

#Since we gather information to add to the cache, we need to get the id
#from the database when needed. This function is an easily method of this

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.
    Args:
        image_sha256 (str): SHA-256 hash value of APOD image
    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    connectus = sqlite3.connect(image_cache_db) #Initiate our connection
    cursor = connectus.cursor()         #Initialize our cursor
    
    #To find the ID, we find at least one that matches a hash. This
    #is to make sure there are no malformed or duplicates (there shouldn't be)
    
    find_apod_query = """
    SELECT id FROM apod_image WHERE sha256 = ?;
    """

    cursor.execute(find_apod_query, (image_sha256,)) #Execute our query using the hash passed to it as a search term
    result = cursor.fetchone()  #Get the results
    connectus.close()       #And close connection
    
    
    if result is not None:      #If there is something in the result (it isn't null)
        return result[0]        #Return the result for further use
    
    return 0


#This function determines the APOD file path, using the title of the image and url passed to it
#To get the title of the file, we strip it of the extension, whitespace, etc and store it in a variable
#It is then returned to use for the cache. It determines where the image in question is saed

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed
    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '
    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'
    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    
    #Regex isn't my best subject so there were a lot of failed attempts.
    #Decided to remove them to conserve space, but this one works AND its self-explanatory
    #We look for anything in the title that represents any letter or number at the start
    #Created using Regex101

    image_title = image_title.strip().replace(' ', '_') #Replace all blank spaces with underscores
    image_title = re.sub('[^A-Za-z0-9_]+', '', image_title) #Look for the name by finding any letter or numbers at the start of the file name
    image_title = image_title + '.' + image_url.split('.')[-1] #Next, we split the name and extension by the '.'   
    image_title =  os.path.join(image_cache_dir, image_title)       #And then, we join the cache irectory and the image title together
    
    #This determines where the file will be saved and with what name
    
    return image_title #Return the results


#This function is the entrypoint for gaining information, as it gets the title, explanation and the path of an ID in the database
#The format of return will be through a dictionary, similar to the apod_api

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.
    Args:
        image_id (int): ID of APOD in the DB
    Returns:
        dict: Dictionary of APOD information
    """
    connectus = sqlite3.connect(image_cache_db)     #Initialize our connection and cursor
    cursor = connectus.cursor()
    
    #Start a query to match a potential APOD ID in the database
    select_apod_query = """ SELECT title, explanation, path FROM apod_image WHERE id = ? """
    
    cursor.execute(select_apod_query, (image_id,))      #Execute our search with the image id in hand
    result = cursor.fetchone()          #Get the results (in a dictionary)
    connectus.close()                                   #And close connection
    
    #For the APOD info, it is the tile locating in index 0 and the explanation in index 1 with the file path in index 2. It matches the format of our
    #query

    apod_info = {
        'title': result[0], 
        'explanation': result[1],
        'file_path': result[2],
    }
    return apod_info        #Return the info


#This function gets all of the titles for APOD data in the cache.

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache
    Returns:
        list: Titles of all images in the cache
    """
    connectus = sqlite3.connect(image_cache_db)         #Initialize our connection and cursor
    cursor = connectus.cursor()
    
    select_apod_query = """ SELECT title FROM apod_image"""                 #Get each title in the cache
    

    cursor.execute(select_apod_query)       #Execute our query
    result = cursor.fetchall()              #Store it in a dictionary
    connectus.close()               #And close connection
    
    if result is not None:              #If there is actual content in the result variable, return it
        return result
    
    return None

if __name__ == '__main__':
    main()
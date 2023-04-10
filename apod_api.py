'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
#We need requests for sending queries to the API to get the URL for our images
import requests

key = 'e5luxCvnXI0Ld5bH2IRJgqtgblFdPoyOtziLDo5K' #This is the key we need in order to interact with the API (API key)

#The main function is used to test out parts of the script. For example I made a query to get the apod info for 2012-09-29

def main():
  apod_info = get_apod_info('2012-09-29') #Query the date
  print(apod_info)    #Print the results (for testing)
  return

#The get_apod_info function will get the url for the corresponding image date we provide it, in the form of yyyy-mm-dd. The results are brought in the form of a dictionary which we can get the url with the 'url' and 'thumbnail_url' keys respectively

def get_apod_info(apod_date):
  """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.
    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)
    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """

  #When getting information from the API, we require the correct parameters in order to get what we wish. We want to specify the date we ware looking for is the one provided to us, and the api_key to do so. 'Thumbs' is used to get thumbnails in case the date provided comes in the form of a video.
  
  header_params = {                                               
      'date': apod_date,
      'thumbs': 'True',
      'api_key': key,
  }

  #Now that we have the parameters, send the request to the APOD api with them
  request = requests.get('https://api.nasa.gov/planetary/apod',
                     params=header_params)

  #An 'ok' signal implies that the connection and request were valid so we can use the signal to determine if something went correctly. If so, we can convert the data into a list and use it
  if request.ok:
    body_dict = request.json()  #Put the data into a list
    print("Success!!")
    print(body_dict)            #Print it (debugging only)
    return body_dict            #And return it so it can be used

  else:
    print('Failed!') #If it failed, print the requests status code and the reason why it failed (good for more info)
    print(f'{request.status_code} ({request.reason})')
    print(f'Error: {request.text}')
  return None


#This function will get the actual URL associated with the dictionary we once got with the request to the API. It is passed as the parameter so any dictionary with it can be used

def get_apod_image_url(apod_info_dict):
  """Gets the URL of the APOD image from the dictionary of APOD information.
    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.
    Args:
        apod_info_dict (dict): Dictionary of APOD info from API
    Returns:
        str: APOD image URL
    """

  #Here is where I messed up the first time, since I tried first to convert the url key into a string and pass it as that, it had no idea what the string 'url' was and could not further parse it. 
#By returning just the key itself with return it parses it properly and can be used further (was messing around with sending the key) I left it for documentation so be warned that uncommenting it will not work
  
  #Images can be identified with the media_type key
  #The key we want to return is url for an image and thumbnail_url for a video
  
  if apod_info_dict['media_type'] == 'image': #If the value of the media_type key is image, then it is an image
    print("It's an image!")
    #print(type())
    #photo = str(['url'])
        #print("It's a url")
        #return photo
    
    return apod_info_dict['url'] #Return the URL key (it contains the url for the image) Since return sends the result of the contents of url, the content returned will be whatever is in 'url'
    
  elif apod_info_dict['media_type'] == 'video': #Otherwise, if it is a video, just return the thumbnail_url contents
    
    #if "thumbnail_url" in apod_info_dict:
        #thumbnail = str(['thumbnail_url'])
        #print(type(thumbnail))
        #print("bob")
        #return thumbnail
    
    return apod_info_dict['thumbnail_url']

  return None


if __name__ == '__main__':
  main()

#Created on 03/16/2023
#Modified for finalization on 04-09-2023
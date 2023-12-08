#!/usr/bin/python
"""
 Lightweight Motion Detection using python picamera libraries.
 Requires a Raspberry Pi computer with a picamera module.
 This code is based on a raspberry pi forum post by user utpalc
 modified by Claude Pageau for this working example.

 This project can be used for further development
 and is located on GitHub at
 https://github.com/pageauc/picamera-motion

 For a full featured program see my GitHub pi-timolo project at
 https://github.com/pageauc/pi-timolo
"""

import os
import datetime
import time
import glob
import picamera
import picamera.array
from twilio.rest import Client
if not os.path.exists('settings.py'):
    print("ERROR : File Not Found - settings.py")
    print("        Cannot import program variables.")
    print("        To Repair Run menubox.sh UPGRADE menu pick.")
    exit(1)
try:
    from settings import *
except ImportError:
    print("ERROR : Could Not Import settings.py")
    exit(1)

PROG_VER = "ver 2.7"
SCRIPT_PATH = os.path.abspath(__file__)
# get script file name without extension
PROG_NAME = SCRIPT_PATH[SCRIPT_PATH.rfind("/")+1:SCRIPT_PATH.rfind(".")]
SCRIPT_DIR = SCRIPT_PATH[0:SCRIPT_PATH.rfind("/")+1] # get script directory
# conversion from stream coordinate to full image coordinate
X_MO_CONV = imageWidth/float(streamWidth)
Y_MO_CONV = imageHeight/float(streamHeight)
MSG_SENT_AT = 0

#------------------------------------------------------------------------------
def send_msg():
    global MSG_SENT_AT
    # only send text messages every 5 minutes.
    if(time.time() - MSG_SENT_AT > 300):
        # Find your Account SID and Auth Token at twilio.com/console
        # and set the environment variables. See http://twil.io/secure
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        fromPhone = os.environ['TWILIO_FROM_PHONE']
        toPhone = os.environ['TWILIO_TO_PHONE']
        client = Client(account_sid, auth_token)

        message = client.messages \
                        .create(
                            body="Motion detected on water meter.",
                            from_=fromPhone,
                            to=toPhone
                        )
        MSG_SENT_AT = time.time()

        print(message.sid)

#------------------------------------------------------------------------------
def get_now():
    """ Get datetime and return formatted string"""
    right_now = datetime.datetime.now()
    return ("%04d%02d%02d-%02d:%02d:%02d"
            % (right_now.year, right_now.month, right_now.day,
               right_now.hour, right_now.minute, right_now.second))

#------------------------------------------------------------------------------
def check_image_dir(image_dir):
    """ if image_dir does not exist create the folder """
    if not os.path.isdir(image_dir):
        if verbose:
            print("INFO  : Creating Image Storage folder %s" % (image_dir))
        try:
            os.makedirs(image_dir)
        except OSError as err:
            print("ERROR : Could Not Create Folder %s %s" % (image_dir, err))
            exit(1)

#------------------------------------------------------------------------------
def get_file_name(image_dir, image_name_prefix, current_count):
    """
    Create a file name based on settings.py variables
    Note image numbering will not be saved but will be inferred from the
    last image name using get_last_counter() function.
    If the last image file name is not a number sequence file
    then numbering will start from imageNumStart variable and may overwrite
    previous number sequence images. This can happen if you switch between
    number sequence and datetime sequence in the same folder.
    or
    Set imageNumOn=False to save images in datetime format to
    ensure image name is unique and avoid overwriting previous image(s).

    """
    if imageNumOn:
        # you could also use os.path.join to construct image path file_path
        file_path = image_dir+ "/"+image_name_prefix+str(current_count)+".jpg"
    else:
        right_now = datetime.datetime.now()
        file_path = ("%s/%s%04d%02d%02d-%02d%02d%02d.jpg"
                     % (image_dir, image_name_prefix,
                        right_now.year, right_now.month, right_now.day,
                        right_now.hour, right_now.minute, right_now.second))
    return file_path

#------------------------------------------------------------------------------
def get_last_counter():
    """
    glob imagePath for last saved jpg file. Try to extract image counter from
    file name and convert to integer.  If it fails restart number sequence.

    Note: If the last saved jpg file name is not in number sequence name
    format (example was in date time naming format) then previous number
    sequence images will be overwritten.

    Avoid switching back and forth between datetime and number sequences
    per imageNumOn variable in settings.py
    """
    counter = imageNumStart
    if imageNumOn:
        image_ext = ".jpg"
        search_str = imagePath + "/*" + image_ext
        file_prefix_len = len(imagePath + imageNamePrefix)+1
        try:
           # Scan image folder for most recent jpg file
           # and try to extract most recent number counter from file name
            newest = max(glob.iglob(search_str), key=os.path.getctime)
            count_str = newest[file_prefix_len:newest.find(image_ext)]
            print("%s INFO  : Last Saved Image is %s Try to Convert %s"
                  % (get_now(), newest, count_str))
            counter = int(count_str)+1
            print("%s INFO  : Next Image Counter is %i"
                  % (get_now(), counter))
        except:
            print("%s WARN  : Restart Numbering at %i "
                  "WARNING: Previous Files May be Over Written."
                  % (get_now(), counter))
    return counter

#------------------------------------------------------------------------------
def take_day_image(image_path, camera):
    """
    Take a picamera day image. Note: You may need to increase
    sleep for low light conditions
    """

    camera.capture(image_path, use_video_port=True)
    #camera.close()
    return image_path

#------------------------------------------------------------------------------
def get_stream_array(camera):
    """ Take a stream image and return the image data array"""
    with picamera.array.PiRGBArray(camera) as stream:
            camera.capture(stream, format='rgb', use_video_port=True)
            return stream.array

#------------------------------------------------------------------------------
def scan_motion(camera):
    """ Loop until motion is detected """
    data1 = get_stream_array(camera)
    while True:
        data2 = get_stream_array(camera)
        diff_count = 0
        for y in range(scanRange[0][1], scanRange[1][1]):
            for x in range(scanRange[0][0], scanRange[1][0]):
                # get pixel differences. Conversion to int
                # is required to avoid unsigned short overflow.
                diff = abs(int(data1[y][x][1]) - int(data2[y][x][1]))
                if  diff > threshold:
                    diff_count += 1
                    if diff_count > sensitivity:
                        # x,y is a very rough motion position
                        return x, y
        data1 = data2

#------------------------------------------------------------------------------
def do_motion_detection(camera):
    """
    Loop until motion found then take an image,
    and continue motion detection. ctrl-c to exit
    """
    current_count = get_last_counter()
    if not imageNumOn:
        print("%s INFO  : File Naming by Date Time Sequence" % get_now())
    while True:
        x_pos, y_pos = scan_motion(camera)
        send_msg()
        file_name = get_file_name(imagePath, imageNamePrefix, current_count)
        #take_day_image(file_name, camera)
        if imageNumOn:
            current_count += 1
        # Convert xy movement location for full size image
        mo_x = x_pos * X_MO_CONV
        mo_y = y_pos * Y_MO_CONV
        if verbose:
            print("%s INFO  : Motion xy(%d,%d) Saved %s (%ix%i)"
                  % (get_now(), mo_x, mo_y, file_name,
                     imageWidth, imageHeight,))

# Start Main Program Logic
def start(q):
    camera = q

    print("%s %s  written by Claude Pageau" % (PROG_NAME, PROG_VER))
    print("---------------------------------------------")
    check_image_dir(imagePath)
    print("%s INFO  : Scan for Motion "
          "threshold=%i (diff)  sensitivity=%i (num px's)..."
          % (get_now(), threshold, sensitivity))
    if not verbose:
        print("%s WARN  : Messages turned off per settings.py verbose = %s"
              % (get_now(), verbose))
    try:
        do_motion_detection(camera)
    except KeyboardInterrupt:
        print("")
        print("INFO  : User Pressed ctrl-c")
        print("        Exiting %s %s " % (PROG_NAME, PROG_VER))
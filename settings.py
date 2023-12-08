# User Configuration variable settings for webserver
# Done by - Claude Pageau

configTitle = "picamera-motion Default Settings"
configName  = "settings.py"

verbose = True  # True= Enable Logging Messages  False= Disable

# User Image Settings
# -------------------
imagePath = "images"    # Folder path to save images
imageNamePrefix = 'mo-' # Prefix for all image file names. Eg front-
#imageWidth = 1920       # Final image width
#imageHeight = 1088       # Final image height
imageWidth = 640       # Final image width
imageHeight = 480       # Final image height
imageVFlip = True       # Flip image Vertically
imageHFlip = True       # Flip image Horizontally
imagePreview = False    # Set picamera preview False=off True=on
imageNumOn = False      # Image Naming True=Number sequence  False=DateTime
imageNumStart = 1000    # Start of number sequence if imageNumOn=True

# User Motion Detection Settings
# ------------------------------
threshold = 30  # How Much pixel changes
sensitivity = 10  # How many pixels change
#streamWidth = 1920  # motion scan stream Width
#streamHeight = 1088
#scanRange = [[713,456],[986,873]] # scan for motion in the region with the blue dial.
streamWidth = 640  # motion scan stream Width
streamHeight = 480
scanRange = [[309,130],[405,270]] # scan for motion in the region with the blue dial.
# scan full image
#scanRange = [[0,0],[streamWidth,streamHeight]]

#======================================
#       webserver.py Settings
#======================================

# Web Server settings
# -------------------
web_server_port = 8080        # default= 8080 Web server access port eg http://192.168.1.100:8080
web_server_root = "images"    # default= "images" webserver root path to webserver image/video sub-folders
web_page_title = "PICAMERA-MOTION"  # web page title that browser show (not displayed on web page)
web_page_refresh_on = True   # False=Off (never)  Refresh True=On (per seconds below)
web_page_refresh_sec = "180"  # default= "180" seconds to wait for web page refresh  seconds (three minutes)
web_page_blank = False        # True Starts left image with a blank page until a right menu item is selected
                              # False displays second list[1] item since first may be in progressx

# Left iFrame Image Settings
# --------------------------
web_image_height = "768"       # default= "768" px height of images to display in iframe
web_iframe_width_usage = "75%" # Left Pane - Sets % of total screen width allowed for iframe. Rest for right list
web_iframe_width = "100%"      # Desired frame width to display images. can be eg percent "80%" or px "1280"
web_iframe_height = "100%"     # Desired frame height to display images. Scroll bars if image larger (percent or px)

# Right Side Files List
# ---------------------
web_max_list_entries = 500       # 0 = All or Specify Max right side file entries to show (must be > 1)
web_list_height = web_image_height  # Right List - side menu height in px (link selection)
web_list_by_datetime = True      # True=datetime False=filename
web_list_sort_descending = True  # reverse sort order (filename or datetime per web_list_by_datetime setting


# ---------------------------------------------- End of User Variables -----------------------------------------------------
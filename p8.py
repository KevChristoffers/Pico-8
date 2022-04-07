#---INDEX OF LEXALOFFLE SUBDIRECTORIES---
#1: Chat: Chat about anything related to PICO-8.
#2: Cartridges: Cartridges that are finished or unlikely to change. Small experimental carts and curiosities welcome.
#3: Work in Progress: Half-finished carts, prototypes, devlogs, abandoned projects.
#4: Collaboration: Make things together! Collaboration invitations, community projects, snippet requests.
#5: Workshop: The never-ending workshop! Get help with any aspect of PICO-8 creation or using the editing tools.
#6: Bugs: Bug reports and troubleshooting.
#7: Blog: PICO-8-related blog posts / anything that doesn't fit elsewhere.
#8: Jam: Jams, challenges, off-site event threads (e.g. Ludum Dare) and trashcarts.
#9: Code Snippets: Reusable snippets of code and mini-libraries that can be pasted into cartridges.
#10: UNNAMED (logos and titlecards?)
#11: UNNAMED (old music thread?)
#12: Tutorials: Tutorials, HOW-TOs, lessons and other teaching resources.
#13: BLANK
#14: GFX Snippets: Reusable GFX that can be pasted into cartridges.
#15: SFX Snippets: Reusable SFX and music that can be pasted into cartridge

import requests
import os, sys, time
from os.path import exists
from PIL import Image
from io import BytesIO

CART_DOWNLOAD_DIR = "/media/kevin/NTFS 4tb/Games/p8Script/carts/"
PAGES = 1
DOWNLOAD_URL = "https://www.lexaloffle.com/bbs/get_cart.php?cat=7&lid="
SUBSTOGET = [2,3,4,8,9,12,14,15]

def save_cart(sub, cart_info, data):
    print(debug(cart_info)) #DEBUG KC
    filename = "".join(x for x in cart_info[1] if x.isalnum()) #Remove invalid filepath characters
    filename = filename[0:128] #Limit filename to 128 characters (cart ID added below)
    filename += "-" + cart_info[0].split()[1] #Adds CartID to the filename

    full_file_path = f"{CART_DOWNLOAD_DIR}sub{str(sub)}/{filename}.p8.png" #Puts everything together for the file save location
    print(f"Writing to: {full_file_path}")
    
    #Write cart data to file
    with open(full_file_path,"wb") as cd:
        cd.write(data)

def get_cart_listing(sub, start_index):
    #Search cart listings 32 at a time.
        print("Searching carts " + str(32*start_index) + " to " + str((32*start_index)+31) + "...")
        success = 0 #Flag for successful connection to BBS
        while(success == 0): #Try to connect to BBS
            try:
                r = requests.get("https://www.lexaloffle.com/bbs/cpost_lister3.php?max=32&start_index=" + str(32*start_index) + "&cat=7&sub=" + str(sub))
                success = 1 #If we make it here, we have received a response from the BBS.
            except requests.exceptions.ConnectionError as connectErr:
                print(f"Got {connectErr}. Waiting 10 seconds before retry")
                time.sleep(10) #Wait after connection error
        return r.content #This returns one large image that is split later

def parse_cart_info(pixels):
    #Cart listing image is 32 carts in a 4 x 8 grid
    #Metadata about each cart is in the 8 pixel rows under each cart, RGB encoded
    cart_info = []
    for row in range (1, 5):
        for col in range (0, 8):
            cart_data = []
            for y in range (128*row + (8*(row-1)), (128*row) + 8 + (8*(row-1))):
                line = ""
                for x in range (128*col, (128*col) + 128):
                    rgba = pixels[x,y]
                    line += chr(rgba) #decrypt pixel RGB to a character
                cart_data.append(line.replace("\x00","")) #Clean-up empty characters
            cart_info.append(cart_data)
    return cart_info

def download_cart(sub, cart_info):
    dc = requests.get(DOWNLOAD_URL + cart_info[3])
    try:
        save_cart(sub, cart_info, dc.content)
    except IndexError as indErr:
        #Make error directory if it doesn't exist
        if not os.path.isdir(f"{CART_DOWNLOAD_DIR}ERROR"):
            os.mkdir(f"{CART_DOWNLOAD_DIR}ERROR")
        FULL_ERROR_PATH = f"{CART_DOWNLOAD_DIR}ERROR/{cart_info[3]}.p8.png"
        print(f"Got index error. saving file to {FULL_ERROR_PATH}")
        dc.save(FULL_ERROR_PATH)
def main():
    for sub in SUBSTOGET:
        print("Sub: " + str(sub))
        #Make download directory for all the carts if it doesn't exist
        if not os.path.isdir(f"{CART_DOWNLOAD_DIR}sub{str(sub)}"):
            os.mkdir(f"{CART_DOWNLOAD_DIR}sub{str(sub)}")
        for p in range(0, PAGES):
            print("Page: " + str(p+1) + " of " + str(PAGES))
            cart_listing_bytes = get_cart_listing(sub, p)
            if len(cart_listing_bytes) <= 1064:
                break
            cart_listing_image = Image.open(BytesIO(cart_listing_bytes))
            cart_pixels = cart_listing_image.load()
            cart_listing_image.show()#DEBUG KC
            cart_listing_info = parse_cart_info(cart_pixels)
            for i in range(len(cart_listing_info)):
                if cart_listing_info[i][3]:
                    print("Downloading cart "  + str(32*p+i) + "..." + cart_listing_info[i][1])
                    download_cart(sub, cart_listing_info[i])
            print("Waiting 2 secs...")
            time.sleep(2) #Trying not to kill the BBS
    print("Cart downloads complete.")

def debug(cart_info):
    #Return a string of cart information for debugging purposes
    debugString = f"URL: {DOWNLOAD_URL + cart_info[3]}\n\
                    cart_info: {cart_info}\n"
    '''for info in cart_info:
        debugString.join(f"{info}\n")'''
    return debugString

if __name__ == "__main__":
    main()

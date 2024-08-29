#Download Cleanup - searches through all files in current and sub-directories
#renames them to a common scheme, adds definition, track and artist names
#from file metadata, scrapes web for release year.
#Then copies over to new directory and deletes old file.
#
#pip install send2trash
#pip install tinytag - for audio metadata
#pip install opencv-python - for video metadata
#pip install requests
#pip install lxml
#pip install bs4

import os
import shutil
import send2trash
import re
import requests
import bs4
import cv2
from tinytag import TinyTag

#change this to the directory you want to search
download_directory = "/home/deck/downloads/"

#change this to the main directory you want to copy to
storage_directory = "/run/media/ZimmZorek SSD/"


def video_cleanup(vid_file):
  #grab file name with extension
  vid_base_name = os.path.basename(vid_file)
  #split file name into name and extension
  vid_split_name = vid_base_name.split(".")
  #remove non-alphanumeric characters from file name
  clean_name = re.sub(r'[^a-zA-Z0-9]', ' ', vid_split_name[0])
  #rename 'The ...' to '..., The'
  if clean_name.casefold()[0:4] == "The ":
    new_vid_name = clean_name[4:] + ", The"
  else:
    new_vid_name = clean_name
  #get definition from file metadata
  vid_data = cv2.VideoCapture(vid_file)
  height = int(vid_data.get(cv2.CAP_PROP_FRAME_HEIGHT))
  width = int(vid_data.get(cv2.CAP_PROP_FRAME_WIDTH))
  if width <= 640 or height <= 480:
    resolution = " [480p]"
  elif width <= 1280 or height <= 720:
    resolution = " [720p]"
  elif width <= 1920 or height <= 1080:
    resolution = " [1080p]"
  elif width <= 2560 or height <= 1440:
    resolution = " [1440p]"
  elif width <= 3840 or height <= 2160:
    resolution = " [2160p]"
  else:
    resolution = f' [{width}x{height}]'
  #add definition to file name
  new_vid_name += resolution
  #scrape TMDB for release year
  #search TMDB for the movie title
  url = "https://www.themoviedb.org/search/movie?query=" + '%20'.join(
      clean_name) + "&language=en-US"
  #request the page
  result = requests.get(url)
  #parse the page
  soup = bs4.BeautifulSoup(result.text, "lxml")
  #grab the first result
  year = str(soup.select('.release_date')[0])[-11:-7]
  #add year to file name
  new_vid_name += f' ({year})'
  #combine file name with extension
  new_vid_file = new_vid_name + "." + vid_split_name[1]
  new_vid_file_path = storage_directory + "Movies/" + new_vid_file
  #copy file to new directory and delete old file.
  shutil.copy(vid_file, new_vid_file_path)
  send2trash.send2trash(vid_file)


def audio_cleanup(audio_file):
  #grab file name with extension
  audio_base_name = os.path.basename(audio_file)
  #split file name into name and extension
  audio_split_name = audio_base_name.split(".")
  #get file metadata
  audio = TinyTag.get(audio_file)
  #rename file based on artist and title and combine with extension
  new_audio_file = audio.artist + " - " + audio.title + "." + audio_split_name[1]
  new_audio_file_path = storage_directory + "Music/" + new_audio_file
  #copy file to new directory and delete old file.
  shutil.copy(audio_file, new_audio_file_path)
  send2trash.send2trash(audio_file)


def image_cleanup(image_file):
  #grab file name with extension
  image_base_name = os.path.basename(image_file)
  new_image_file_path = storage_directory + "Pictures/" + image_base_name
  #copy file to new directory and delete old file.
  shutil.copy(image_file, new_image_file_path)
  send2trash.send2trash(image_file)


def disk_image_cleanup(disk_file):
  #grab file name with extension
  disk_base_name = os.path.basename(disk_file)
  new_disk_file_path = storage_directory + "ISOs/" + disk_base_name
  #copy file to new directory and delete old file.
  shutil.copy(disk_file, new_disk_file_path)
  send2trash.send2trash(disk_file)


for folder, sub_folders, files in os.walk(download_directory):
  for file in files:
    if re.search(r'(\.mkv|\.mp4|\.m4v|\.avi|\.mov|\.wmv|\.flv|\.mpg|\.mpeg)$',
                 files):
      video_cleanup(file)

    elif re.search(r'(\.mp3|\.wav|\.flac|\.ogg|\.m4a|\.aac)$', files):
      audio_cleanup(file)

    elif re.search(r'(\.jpeg|\.png|\.bmp|\.gif)$', files):
      image_cleanup(file)

    elif re.search(r'(\.iso|\.img|\.zip|\.rar|\.7z|\.tar|\.gz|\.dmg)$', files):
    disk_image_cleanup(file)

    else:
      print("Unknown file type: " + os.path.basename(file) + "\n" +
            "File skipped" + "\n")
      pass
print("Cleanup complete.")

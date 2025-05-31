#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __Author__ = "Michael Yu and Cooper"
# Filename: downloadPic.py
# Date: 2025/5/31

import os
import time
import requests
import hashlib
from operator import itemgetter

# constants
SALT = 'laxiaoheiwu'
COUNT = 9999

# Define the parameters of the request
data = {
    'activityNo': 0,
    'isNew': False,
    'count': COUNT,
    'page': 1,
    'ppSign': 'live',
    'picUpIndex': '',
    '_t': 0,
}

# Sort the object by key
def obj_key_sort(obj):
    sorted_obj = sorted(obj.items(), key=itemgetter(0))
    sorted_obj_dict = {k: str(v) for k, v in sorted_obj if v is not None}
    return '&'.join([f"{k}={v}" for k, v in sorted_obj_dict.items()])

# MD5 encryption
def md5(value):
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()

# Get all images
def get_all_images(id,place):
    
    t = int(time.time() * 1000)
    data['activityNo'] = id
    data['_t'] = t
    data_sort = obj_key_sort(data)
    sign = md5(data_sort + SALT)
    params = {
        **data,
        '_s': sign,
        'ppSign': 'live',
        'picUpIndex': '',
    }
    try:
        res = requests.get('https://live.photoplus.cn/pic/pics', params=params)
        res.raise_for_status()  # If the response status is not 200, actively throw an exception
    except requests.RequestException as err:
        print("Oops: Something Else Happened",err)
        return
    try:
        res_json = res.json()
    except ValueError:
        print("Response content is not valid JSON")
        return

    total_pics = res_json['result']['pics_total']
    camer = res_json['result']['pics_array'][0]['camer']
    album = res_json['result']['pics_array'][0]['activity_name']
    
    if album:
        album_folder = album.replace(" ", "_").replace("/", "_").replace("\\", "_")
        image_path = "../Pics/" + str(album_folder)
    else:
        image_path = "../Pics/" + str(id)
    if not os.path.exists(image_path):
        os.makedirs(image_path)+

    print("Downloading album: {} by {}. Total photos: {}".format(album, camer, total_pics))

    i = total_pics + 1
    j = 0
    for pic in res_json['result']['pics_array']:
        image_name = pic['pic_name']
        download_all_images(("https:" + pic['origin_img']),image_path,image_name)
        i = i - 1
        j = j + 1
        # Progress bar
        progress = int((j / total_pics) * 50) if total_pics else 0
        bar = '[' + '#' * progress + '-' * (50 - progress) + ']'
        print(f"\r{bar} {j}/{total_pics} Downloading: {image_name}", end='', flush=True)
    print("Total Photos:{} - Downloaded:{} - Photographer:{}".format(total_pics,j,camer))

# Download images
def download_all_images(url,image_path,image_name):
    try:
        response = requests.get(url, stream=True)   
        response.raise_for_status()  # If the response status is not 200, actively throw an exception
    except requests.RequestException as err:
        print("Oops: Something Else Happened",err)
        return
    time.sleep(2)
    with open(os.path.join(image_path, image_name), 'wb') as out_file:
        out_file.write(response.content)

id = input("Enter photoplus ID (eg:6483836): ")
if not id:
    id = "6483836"  # Default ID
count = input("Enter number of photos (Default:9999): ")
place = input("Enter the place to save photos (Default:../Pics/Album name or ID): ")
if not place:
    place = id  # Default place is the ID"

if count.isnumeric():
  data['count'] = int(count)
if id.isnumeric():
  get_all_images(int(id),place)
else:
  print('Wrong ID')
  exit()
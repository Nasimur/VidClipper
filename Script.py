#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
import ffmpeg
import pprint
import time
import subprocess
import string
import itertools
import os
import requests
sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries = 20)
sess.mount('http://', adapter)
import json

#this loop just generates a list from a to zzz

strings = [''.join(letters)
           for length in range(1, 3)
           for letters in itertools.product(string.ascii_lowercase,
                                            repeat=length)]

#functions that are used to watermark, ID or both
    
def prub(fn):
    prob = ffmpeg.probe(fn)
    video_streams = [stream for stream in prob["streams"] if stream["codec_type"] == "video"]
    n=float(video_streams[0].get('duration'))
    m=time.strftime("%H:%M:%S", time.gmtime(n))
    return(video_streams[0].get('height'),video_streams[0].get('width'),m)


def Imgur(listoffiles):
    imglinks=[]
    for i in range(len(listoffiles)):
        height, width, duration=prub(listoffiles[i])
        if pd.Timestamp(duration) <= pd.Timestamp('00:01:00'):
            url = "https://api.imgur.com/3/upload"
            payload={}
            files=[
              ('video',(listoffiles[i],open(listoffiles[i],'rb'),'application/octet-stream'))
            ]
            headers = {
              'Authorization': 'Client-ID {{e94983edea98bb0}}'
            }

            response = sess.request("POST", url, headers=headers, data=payload, files=files)

            # Use the json module to load CKAN's response into a dictionary.
            response_dict = json.loads(response.text) 

            imglinks.append(listoffiles[i] + ":     https://imgur.com/" + response_dict['data']['id']) 

    with open('imgurlinks.txt', 'w') as f:
        for item in imglinks:
            f.write("%s\n" % item)


def WM(listoffiles):
    for i in range(len(listoffiles)):
        height, width, duration=prub(listoffiles[i])
        if height==1080 and width==1920:
            wmcmd="ffmpeg -i " + listoffiles[i] +" -loop 1 -i image1080p.png -filter_complex \"[0:v][1:v] overlay=shortest=1:x=0:y=0 [y];[0:a]volume=1[aud0]\" -map \"[y]\" -map \"[aud0]\" -c:v libx264 -preset ultrafast -crf 26 -y wm"+listoffiles[i]
            subprocess.run(wmcmd, stderr=subprocess.STDOUT,shell=True)
        elif height==720 and width==1280:
            wmcmd="ffmpeg -i " + listoffiles[i] +" -loop 1 -i image720p.png -filter_complex \"[0:v][1:v] overlay=shortest=1:x=0:y=0 [y];[0:a]volume=1[aud0]\" -map \"[y]\" -map \"[aud0]\" -c:v libx264 -preset ultrafast -crf 26 -y wm"+listoffiles[i]
            subprocess.run(wmcmd, stderr=subprocess.STDOUT,shell=True)
        else:
            wmcmd="ffmpeg -i " + listoffiles[i] +" -loop 1 -i image720p.png -filter_complex \"[0:v]scale=1280x720[v];[v][1:v] overlay=shortest=1:x=0:y=0 [y];[0:a]volume=1[aud0]\" -map \"[y]\" -map \"[aud0]\" -c:v libx264 -preset ultrafast -crf 26 -y wm"+listoffiles[i]
            subprocess.run(wmcmd, stderr=subprocess.STDOUT,shell=True)
    with open('list.txt', 'w') as f:
        for item in listoffiles:
            f.write("%s\n" % item)     
    subprocess.run("xargs rm < list.txt", stderr=subprocess.STDOUT,shell=True)
    os.remove("list.txt")

def ID(listoffiles):
    for i in range(len(listoffiles)):
        IDbuilder1=listoffiles[i].split(".")
        IDbuilder2=IDbuilder1[0].split("-")
        IDbuilder3=IDbuilder2[1]+"-"+IDbuilder2[2]
        height, width, duration=prub(listoffiles[i])
        if height==1080 and width==1920:
            wmcmd="ffmpeg -i " + listoffiles[i] +" -filter_complex \"[0:v]drawtext=text=\'"+IDbuilder3+"\':x=18:y=1025:fontfile=Montserrat-Bold.ttf:fontsize=65:fontcolor=white:bordercolor=black:borderw=3[y];[0:a]volume=1[aud0]\" -map \"[y]\" -map \"[aud0]\" -c:v libx264 -preset ultrafast -crf 26 -y ID"+listoffiles[i]
            subprocess.run(wmcmd, stderr=subprocess.STDOUT,shell=True)
        elif height==720 and width==1280:
            wmcmd="ffmpeg -i " + listoffiles[i] +" -filter_complex \"[0:v]drawtext=text=\'"+IDbuilder3+"\':x=12:y=674:fontfile=Montserrat-Bold.ttf:fontsize=45:fontcolor=white:bordercolor=black:borderw=3[y];[0:a]volume=1[aud0]\" -map \"[y]\" -map \"[aud0]\" -c:v libx264 -preset ultrafast -crf 26 -y ID"+listoffiles[i]
            subprocess.run(wmcmd, stderr=subprocess.STDOUT,shell=True)
        else:
            wmcmd="ffmpeg -i " + listoffiles[i] +" -filter_complex \"[0:v]scale=1280x720[v];[v]drawtext=text=\'"+IDbuilder3+"\':x=12:y=674:fontfile=Montserrat-Bold.ttf:fontsize=45:fontcolor=white:bordercolor=black:borderw=3[y];[0:a]volume=1[aud0]\" -map \"[y]\" -map \"[aud0]\" -c:v libx264 -preset ultrafast -crf 26 -y ID"+listoffiles[i]
            subprocess.run(wmcmd, stderr=subprocess.STDOUT,shell=True)
    with open('list.txt', 'w') as f:
        for item in listoffiles:
            f.write("%s\n" % item)     
    subprocess.run("xargs rm < list.txt", stderr=subprocess.STDOUT,shell=True)
    os.remove("list.txt")

def WMplusID(listoffiles):
    for i in range(len(listoffiles)):
        IDbuilder1=listoffiles[i].split(".")
        IDbuilder2=IDbuilder1[0].split("-")
        IDbuilder3=IDbuilder2[1]+"-"+IDbuilder2[2]
        height, width, duration=prub(listoffiles[i])
        if height==1080 and width==1920:
            wmcmd="ffmpeg -i " + listoffiles[i] +" -loop 1 -i image1080p.png -filter_complex \"[0:v][1:v] overlay=shortest=1:x=0:y=0 [y];[y]drawtext=text=\'"+IDbuilder3+"\':x=18:y=1025:fontfile=Montserrat-Bold.ttf:fontsize=65:fontcolor=white:bordercolor=black:borderw=3[y];[0:a]volume=1[aud0]\" -map \"[y]\" -map \"[aud0]\" -c:v libx264 -preset ultrafast -crf 26 -y WMID"+listoffiles[i]
            subprocess.run(wmcmd, stderr=subprocess.STDOUT,shell=True)
        elif height==720 and width==1280:
            wmcmd="ffmpeg -i " + listoffiles[i] +" -loop 1 -i image720p.png -filter_complex \"[0:v][1:v] overlay=shortest=1:x=0:y=0 [y];[y]drawtext=text=\'"+IDbuilder3+"\':x=12:y=674:fontfile=Montserrat-Bold.ttf:fontsize=45:fontcolor=white:bordercolor=black:borderw=3[y];[0:a]volume=1[aud0]\" -map \"[y]\" -map \"[aud0]\" -c:v libx264 -preset ultrafast -crf 26 -y WMID"+listoffiles[i]
            subprocess.run(wmcmd, stderr=subprocess.STDOUT,shell=True)
        else:
            wmcmd="ffmpeg -i " + listoffiles[i] +" -loop 1 -i image720p.png -filter_complex \"[0:v]scale=1280x720[v];[v][1:v] overlay=shortest=1:x=0:y=0 [y];[y]drawtext=text=\'"+IDbuilder3+"\':x=12:y=674:fontfile=Montserrat-Bold.ttf:fontsize=45:fontcolor=white:bordercolor=black:borderw=3[y];[0:a]volume=1[aud0]\" -map \"[y]\" -map \"[aud0]\" -c:v libx264 -preset ultrafast -crf 26 -y WMID"+listoffiles[i]
            subprocess.run(wmcmd, stderr=subprocess.STDOUT,shell=True)
    with open('list.txt', 'w') as f:
        for item in listoffiles:
            f.write("%s\n" % item)     
    subprocess.run("xargs rm < list.txt", stderr=subprocess.STDOUT,shell=True)
    os.remove("list.txt")
 
#Checking command line arguments and acting accordingly

if all(x in sys.argv for x in ['watermarkfolder', 'IDfolder']):
    print("adding both watermark and ID code to all the videos in this folder")
    folderscan="for f in *.mp4; do echo \"$f\" >> list.txt; done"
    subprocess.run(folderscan, stderr=subprocess.STDOUT,shell=True)
    filelist=[]
    with open("list.txt") as f:
        for line in f.readlines():
            filelist.append(line.strip())
    os.remove("list.txt")
    WMplusID(filelist)
            
elif sys.argv[1]=="watermarkfolder":
    print("adding branding watermarks to all the videos in the script's folder")
    folderscan="for f in *.mp4; do echo \"$f\" >> list.txt; done"
    subprocess.run(folderscan, stderr=subprocess.STDOUT,shell=True)
    filelist=[]
    with open("list.txt") as f:
        for line in f.readlines():
            filelist.append(line.strip())
    os.remove("list.txt")
    WM(filelist)   
            
    
elif sys.argv[1]=="IDfolder":
    print("adding ID to all the videos in the script's folder")
    folderscan="for f in *.mp4; do echo \"$f\" >> list.txt; done"
    subprocess.run(folderscan, stderr=subprocess.STDOUT,shell=True)
    filelist=[]
    with open("list.txt") as f:
        for line in f.readlines():
            filelist.append(line.strip())
    os.remove("list.txt")
    ID(filelist)
    
elif sys.argv[1]=="imgurfolder":
    print("uploading all the files with the duration of less than 1 minute to imgur")
    folderscan="for f in *.mp4; do echo \"$f\" >> list.txt; done"
    subprocess.run(folderscan, stderr=subprocess.STDOUT,shell=True)
    filelist=[]
    with open("list.txt") as f:
        for line in f.readlines():
            filelist.append(line.strip())
    os.remove("list.txt")
    Imgur(filelist)             

else:	
    fn=sys.argv[1]
    print("The name of the we will be working with is",fn)
    #checking if the file is mp4 or not
    bn,ext=fn.split(".")
    if ("rencode" in set(sys.argv)) or (ext!="mp4"):
        encodeoption="-c:v libx264 -preset ultrafast -crf 25"
        print("encoding turned on and set to", encodeoption)
    else:
        encodeoption="-c copy"
        print("encoding is off and is set to",encodeoption)
    if "splitm" in set(sys.argv):
        print("splitting the file",fn,"into 1 min segments")
        height, width, duration=prub(fn)
        splitDates = pd.date_range(start=pd.Timestamp('00:00:00'), end=pd.Timestamp(duration), freq='T').strftime('%H:%M:%S')
        i = 0
        for value in zip(splitDates, splitDates[1:]):
                start, end =value
                cmd = ["ffmpeg", "-ss", start, "-to", end, "-i", fn,  "-avoid_negative_ts", "1", encodeoption, str(strings[i] + "-" + fn)]
                bmd =' '.join(cmd)
                subprocess.run(bmd, stderr=subprocess.STDOUT,shell=True)
                last=end
                i += 1
        if last != duration:
            start=last
            end=duration
            cmd = ["ffmpeg", "-ss", start, "-to", end, "-i", fn,  "-avoid_negative_ts", "1", encodeoption, str(strings[i] + "-" + fn)]
            bmd =' '.join(cmd)
            subprocess.run(bmd, stderr=subprocess.STDOUT,shell=True)

                
        
    elif "splitn" in set(sys.argv):
        j=sys.argv.index("splitn")+1
        segments=int(sys.argv[j])
        print("split the file",fn,"into",segments,"segments")
        height, width, duration=prub(fn)
        splitDates = pd.date_range(start=pd.Timestamp('00:00:00'), end=pd.Timestamp(duration), periods=segments+1).strftime('%H:%M:%S')
        i = 0
        for value in zip(splitDates, splitDates[1:]):
                start, end =value
                cmd = ["ffmpeg", "-ss", start, "-to", end, "-i", fn,  "-avoid_negative_ts", "1", encodeoption, str(strings[i] + "-" + fn)]
                bmd =' '.join(cmd)
                subprocess.run(bmd, stderr=subprocess.STDOUT,shell=True)
                last=end
                i += 1

    else:
        if "concat" in set(sys.argv):
            print("cutting clips will concat the files after done")
            i = 0
            with open("cuts.txt") as f:
                for line in f.readlines():
                    start, end = line.strip().split(' ')
                    cmd = ["ffmpeg", "-ss", start, "-to", end, "-i", fn,  "-avoid_negative_ts", "1", encodeoption, str(strings[i] + "-" + bn + ".mp4")]
                    bmd =' '.join(cmd)
                    subprocess.run(bmd, stderr=subprocess.STDOUT,shell=True)
                    i += 1
            filelist=[]         
            for x in range(i):
                filelist.append(str(strings[x] + "-" + bn + ".mp4"))
            newlist =[str("file " + item) for item in filelist]    
            with open('list.txt', 'w') as f:
                for item in newlist:
                    f.write("%s\n" % item)     
            concatmd="ffmpeg -f concat -i list.txt -c copy concat-" + bn + ".mp4"
            subprocess.run(concatmd, stderr=subprocess.STDOUT,shell=True)
            with open('list.txt', 'w') as f:
                for item in filelist:
                    f.write("%s\n" % item)     
            subprocess.run("xargs rm < list.txt", stderr=subprocess.STDOUT,shell=True)
            os.remove("list.txt")
            filelist.clear()
            filelist.append(str("concat-"+bn + ".mp4"))
            print(filelist)
            if all(x in sys.argv for x in ['watermark', 'ID']):
                print("Adding watermark and ID code to the concated file")
                WMplusID(filelist)
            elif "watermark" in set(sys.argv):
                print("adding watermark to the concated file")
                WM(filelist)
            elif sys.argv[1]=="ID":
                print("adding ID to the concatted file")
                ID(filelist)
                
        else:
            print("cutting clips with the given options")
            i = 0
            with open("cuts.txt") as f:
                for line in f.readlines():
                    start, end = line.strip().split(' ')
                    cmd = ["ffmpeg", "-ss", start, "-to", end, "-i", fn,  "-avoid_negative_ts", "1", encodeoption, str(strings[i] + "-" + bn + ".mp4")]
                    bmd =' '.join(cmd)
                    subprocess.run(bmd, stderr=subprocess.STDOUT,shell=True)
                    i += 1
            filelist=[]         
            for x in range(i):
                filelist.append(str(strings[x] + "-" + bn + ".mp4"))
            if all(x in sys.argv for x in ['watermark', 'ID']):
                print("Adding watermark and ID code to these files")
                WMplusID(filelist)
            elif "watermark" in set(sys.argv):
                print("adding watermark to these files")
                WM(filelist)                
            elif "ID" in set(sys.argv):
                print("adding ID to these files")
                ID(filelist)


if "imgur" in set(sys.argv):
    print("uploading all the files with the duration of less than 1 minute to imgur")
    folderscan="for f in *.mp4; do echo \"$f\" >> list.txt; done"
    subprocess.run(folderscan, stderr=subprocess.STDOUT,shell=True)
    filelist=[]
    with open("list.txt") as f:
        for line in f.readlines():
            filelist.append(line.strip())
    os.remove("list.txt")
    Imgur(filelist)                 

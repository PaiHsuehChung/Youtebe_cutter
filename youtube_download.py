import argparse
import os
import json
from colorama import Fore, Style, init
import traceback
from pytube import YouTube
from tqdm import tqdm
import datetime
import cv2
import argparse

# Setting argparse tools
parse = argparse.ArgumentParser(description='Download Youtube Video and cut to frame.')
parse.add_argument('--url', type=str, required=True, help='Paste Youtube URL')

# The center of path
main_path = os.path.dirname(os.path.abspath(__file__))

# Defualt setting
storage_folder_name = 'videos'
frame_folder_name = 'frames'
frame_path = os.path.join(main_path, frame_folder_name)
storage_path = os.path.join(main_path, storage_folder_name)
storage_files_by_videos = None
storage_folders_by_frames = None

youtube_record = 'youtube_record.json'
record_data = None


# setting colorama
init(autoreset=True)

def init_factory():
    global storage_files_by_videos
    global record_data
    global storage_folders_by_frames
    
    # Check videos storage path
    if os.path.isdir(storage_path):
        print('|- \"{}\" folder is exist !'.format(storage_folder_name))
        contents = os.listdir(storage_path)
        
        storage_files_by_videos = list(filter(lambda f: os.path.isfile(os.path.join(storage_path, f)), contents))
        
        print(Fore.CYAN+'|- {} video files'.format(len(storage_files_by_videos)))
        
    else:
        try:
            print(Fore.YELLOW+'|- \"{}\" folder did not exists. Make it right now....'.format(storage_folder_name))
            os.mkdir(storage_path)

            if os.path.isdir(storage_path):
                print(Fore.GREEN+'|- Done !')
        except:
            print(traceback.format_exc())
     
    
    # Check videos per frame storage path
    if os.path.isdir(frame_path):
        print('|- \"{}\" folder is exist !'.format(frame_folder_name))
        contents = os.listdir(frame_path)
        storage_folders_by_frames = list(filter(lambda f: os.path.isdir(os.path.join(frame_path, f)), contents))

        print(Fore.CYAN+'|- {} frames folders'.format(len(storage_folders_by_frames)))
        
    else:
        try:
            print(Fore.YELLOW+'|- \"{}\" folder did not exists. Make it right now....'.format(frame_folder_name))
            os.mkdir(frame_path)

            if os.path.isdir(frame_path):
                print(Fore.GREEN, '|- Done !')
        except:
            print(traceback.format_exc())
        
    print("-"*100)
    # Checking record file if exist
    if os.path.isfile(os.path.join(main_path, youtube_record)):
        print('|- Loading record data \"{}\"....'.format(youtube_record))
        with open(youtube_record, 'r') as jsFile:
            record_data = json.load(jsFile)


def file_name_factory():
    global record_data
    print('|- via naming factory')
    
    start_number = 0
    
    if record_data:
        sort_list = sorted(record_data.keys())
        return str(int(sort_list[-1])+1)
    else:
        return str(start_number)



def write_record_data(yt_title, yt_url, file_name):
    global record_data

    data = {}
    data.update({file_name : {'title': yt_title,
                              'url': yt_url}})
    
    print('|- Saving record....')
    if record_data:
        record_data.update(data)
        with open(youtube_record, 'w') as jfile:
            json.dump(record_data, jfile)
    else:
        record_data = data
        with open(youtube_record, 'w') as jfile:
            json.dump(record_data, jfile)

    
    print(Fore.GREEN,'|- Done!')



def download_youtube(yt_url, target_folder, file_name):
    try:
        print('|- Connecting Youtube ... ')
        yt = YouTube(yt_url)
        video = yt.streams.first()
        file_size = video.filesize
        yt_title = video.title
        
        
        print('-'*100+'|')
        print('|-Title : {} '.format(yt_title))
        print('-'*100+'|')
        print('|-URL : {} '.format(yt_url))
        print('-'*100+'|')
        print('|-File Size : {} KB'.format(file_size//(1024*1024)))
        print('-'*100+'|')
        print('|-Storage Path : {}'.format(target_folder))
        print('-'*100+'|')
        print('|-File Name : {}.mp4'.format(file_name))
        print('-'*100+'|')

        for _ in tqdm(yt.streams):
            video.download(target_folder, file_name)
            
            
        # save metadata
        write_record_data(yt_title, yt_url, file_name)
        
        
        now = datetime.datetime.now()
        print('-'*100+'|')
        print(Fore.GREEN+'|- {}.{}.{} {}:{} download successful!! '.format(now.year, now.month, now.day, now.hour, now.minute))

    except:
        print(traceback.format_exc())


def cut_video2frame(src_path, video_name):
    sec = 0
    frameRate = 1

    #FIXME : Check format
    video_format = '.mp4'
    frame_folder_name = 'video{}'.format(video_name)
    
    frames_folder = os.path.join(frame_path, frame_folder_name)
    
    if os.path.isdir(frames_folder):
        raise Exception('The frame by video folder already exist. Please check the target path({}) or the folder name({})'.format(frames_folder, frame_folder_name))
    else:
        print("|- Create \"{}\" folder ...".format(frame_folder_name))
        os.mkdir(frames_folder)
    

    def getFrame(sec):
        image_name = 'video{}_{}.jpg'.format(video_name, str(sec))
        vidcap.set(cv2.CAP_PROP_POS_MSEC, sec*1000)
        hasFrames, image = vidcap.read()
        if hasFrames:
            cv2.imwrite(os.path.join(frames_folder, image_name), image)
        return hasFrames

    print(Fore.GREEN+"|- Capture video {}".format(video_name+video_format))
    vidcap = cv2.VideoCapture(os.path.join(src_path, video_name+video_format))
    success = getFrame(sec)
    while success:
        sec = sec + frameRate
        success = getFrame(sec)
        
    print("|- Cutting video successful!!")



def main():
    args = parse.parse_args()
    yt_url = args.url

    init_factory()
    file_name = file_name_factory()
    download_youtube(yt_url, storage_path, file_name)
    cut_video2frame(storage_path, file_name)


if __name__ == '__main__':
    main()



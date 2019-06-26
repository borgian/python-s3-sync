import os
from os import stat
import time
from io import StringIO
import hashlib
import boto
import boto.s3.connection
from boto.s3.key import Key
from boto3.s3.transfer import  S3Transfer
import boto3
import queue
import threading
from threading import Thread


#########################################

folders_to_sync =  [
'C:/workfolder',
]

file_to_sync = [
'C:/file.txt'
]




#VARS

ACCESS_KEY = "YOUR S3 ACCESS KEY"
SECRET_KEY = "YOUR S3 Secret Key"
BUCKET_NAME = "YOUR S3 Bucket Name"
AWS_REGION = 'YOUR S3 AWS REGION'

q = queue.Queue();
threadLock = threading.Lock()
total_synched = 0
s3 = boto3.resource('s3',
                    aws_access_key_id=ACCESS_KEY,
                     aws_secret_access_key= SECRET_KEY)


#Initiate S3 Objects
client = s3.meta.client
transfer = S3Transfer(client)


#MD5 Functions
def md5(path):
  return hashlib.md5(open(path,'rb').read()).hexdigest()


def get_aws_md5(name,s3_synch):
    #bucket = s3.Bucket(BUCKET_NAME)
    try:
        obj = s3_synch.Object(bucket_name=BUCKET_NAME, key=name)
        return obj.e_tag.replace('"','')
    except:
        return False



#Dir Scan Functions
def recursive_directory_upload(dir,parent = ""):

    dir_file_upload(dir)
    for root, subdirs, files in os.walk(dir):
        for subdir in subdirs:
             new_dir = root+"/"+subdir+"/"
             new_dir = new_dir.replace('//','/')
             new_dir = new_dir.replace('\\','/')
             dir_file_upload(new_dir)


def dir_file_upload(dir):

     print("####### "+'Scanning: '+dir)


     root = dir
     for file in os.scandir(dir):
            if file.is_file():
             new_file = root+"/"+file.name
             #new_file = file.replace('/','')
             new_file = new_file.replace('\\','')
             new_file = new_file.replace('//','/')
             q.put(new_file)



def file_changed(dir,s3_synch):
    aws_md5 = get_aws_md5(dir,s3_synch)
    if aws_md5 == False:
        return True

    local_md5 = md5(dir)

    if(local_md5 == aws_md5):
        return False
    else:
        return True



#Function to Synch Files With S3 Bucket
def sync_file(filename):

    synch_s3 = boto3.resource('s3',
                    aws_access_key_id=ACCESS_KEY,
                     aws_secret_access_key= SECRET_KEY)

    synch_client = synch_s3.meta.client

    synch_transfer = S3Transfer(synch_client)

    if file_changed(filename,synch_s3):
        res = synch_transfer.upload_file(filename,
                         BUCKET_NAME,
                         filename,
                         extra_args={'ServerSideEncryption': 'AES256'})
        print("Synched: "+filename)
        with threadLock:
            global total_synched
            if total_synched is None:
               total_synched = 0

            total_synched += 1
    else:
        print("Unchanged: "+filename)



#MAIN

for folder in folders_to_sync:
    recursive_directory_upload(folder)

for file in file_to_sync:
    q.put(file)


#Start threads
threads = []
num_threads = 50
intitial_count = q.qsize()
def do_work():

      print("Starting to Sync "+str(q.qsize())+ " files.")
      for i in range(num_threads):
         t = threading.Thread(target=worker,args=(q,))
         threads.append(t)
         t.start()
      #Wait On Each Thread
      for tt in threads:
         tt.join()



def worker(q):
   while(not q.empty()):
      if q.empty():
       return
      else:
          try:
               file = q.get()
               sync_file(file)

          except Exception as e:
               print('Error: '+ str(e))
               time.sleep(0.1)





do_work()
print("Sync Complete, Total files synched: "+str(total_synched)+"/"+str(intitial_count))
time.sleep(1000000)

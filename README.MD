# Python S3 Bucket Sync

A multi-threaded python script to sync your files & folders with an S3 Bucket.

## Getting Started

These instructions will help you setup all the variables needed to start synching your files.

### Prerequisites
```
boto
boto3
```


### Setup

First, you need to setup an account with Amazon S3, generate your ACCESS KEY + SECRET KEY and create your bucket.
Once you've got these variables you need to change these variables in the _sync.py file:
* **ACCESS_KEY**
* **SECRET_KEY**
* **BUCKET_NAME**
* **AWS_REGION**

Lastly:
* the directories that need to be synced need to be added to the **folders_to_sync array**
* the specific files that need to be synced need to be added to the **file_to_sync array**



## Authors

* **Ian Borg**



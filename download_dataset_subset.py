import os
import shutil
import time
import requests
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import RequestException
import json
from PIL import Image


def download_dataset_subset(start, end, ids, images_dir, descs_dir, thread_id):
    # Announce the start of the thread (mainly for debugging)
    print('Thread {0} started'.format(thread_id))

    # The url template is 'base_url_prefix - image_id - base_url_suffix'
    base_url_prefix = 'https://isic-archive.com/api/v1/image/'
    base_url_suffix = '/download?contentDisposition=inline'

    # For each id:
    # 1. get the corresponding image and description urls
    # 2. download the image and the description from the urls
    for id, index in zip(ids, range(start, end)):
        print("downloading image ({0} / {1} / {2})".format(start, index, end-1))

        # Get the corresponding image url
        url_image = base_url_prefix + id + base_url_suffix
        # Get the corresponding description url
        url_desc = base_url_prefix + id
        print ("url_image = {0}".format(url_image))

        # Download the image and desctiprion using the urls
        # Sometimes their site isn't responding well, and than an error occurs,
        # So we will retry the same url 5 seconds later, until it succeeds
        succeeded = False
        while not succeeded:
            try:
                response_image = requests.get(url_image, stream=True, timeout=20)
                response_desc = requests.get(url_desc, stream=True, timeout=20)
                response_image.raise_for_status()
                response_desc.raise_for_status()

                # Write the image into a file
                img_path = os.path.join(images_dir, 'ISIC_{0}.jpg'.format(str(index).zfill(7)))
                with open(img_path, 'wb') as imageFile:
                    shutil.copyfileobj(response_image.raw, imageFile)

                # Validate the image was downloaded correctly
                validate_image(img_path)

                # Parse the description and write the description into a file
                parsed_desc = response_desc.json()
                desc_path = os.path.join(descs_dir, 'ISIC_{0}'.format(str(index).zfill(7)))
                with open(desc_path, 'w') as descFile:
                    json.dump(parsed_desc, descFile, indent=2)

                succeeded = True
            except RequestException:
                print("connection error occurred - trying again image number {0}".format(index))
                time.sleep(10)
            except ReadTimeoutError:
                print("connection timed out - trying again image number {0}".format(index))
                time.sleep(10)
            except IOError:
                print("Image wasn't fully downloaded - trying again image number {0}".format(index))
                time.sleep(10)

    print('Thread {0} finished'.format(thread_id))


def validate_image(image_path):
    # We would like to validate the image was fully downloaded and wasn't truncated.
    # To do so, we can open the image file using PIL.Image and try to resize it to the size
    # the file declares it has.
    # If the image wasn't fully downloaded and was trucnated - an error will be raised.
    img = Image.open(image_path)
    img.resize(img.size)

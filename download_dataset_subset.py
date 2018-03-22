from os.path import join
import shutil
import time
import requests
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import RequestException
import json
from PIL import Image


def download_dataset_subset_wrapper(args):
    download_dataset_subset(*args)


def download_dataset_subset(ids, images_dir, descs_dir):
    # The url template for the image is <base url prefix><image id><base url suffix>
    # The url template for the description of the image is: <base url prefix><image id>
    base_url_prefix = 'https://isic-archive.com/api/v1/image/'
    base_url_suffix = '/download?contentDisposition=inline'

    # For each id:
    # 1. get the corresponding image and description urls
    # 2. download the image and the description from the urls
    for id in ids:
        # Build the image url
        url_image = base_url_prefix + id + base_url_suffix
        # Build the description url
        url_desc = base_url_prefix + id

        # Download the image and description using the url
        # Sometimes their site isn't responding well, and than an error occurs,
        # So we will retry 10 seconds later and repeat until it succeeds
        succeeded = False
        while not succeeded:
            try:
                # Download the image and description
                response_image = requests.get(url_image, stream=True, timeout=20)
                response_desc = requests.get(url_desc, stream=True, timeout=20)
                # Validate the download status is ok
                response_image.raise_for_status()
                response_desc.raise_for_status()

                # Parse the description and write it into a file
                parsed_desc = response_desc.json()

                # Write the image into a file
                img_path = join(images_dir, '{0}.jpg'.format(parsed_desc['name']))
                with open(img_path, 'wb') as imageFile:
                    shutil.copyfileobj(response_image.raw, imageFile)

                # Validate the image was downloaded correctly
                validate_image(img_path)

                desc_path = join(descs_dir, parsed_desc['name'])
                with open(desc_path, 'w') as descFile:
                    json.dump(parsed_desc, descFile, indent=2)

                succeeded = True
            except RequestException:
                time.sleep(10)
            except ReadTimeoutError:
                time.sleep(10)
            except IOError:
                time.sleep(10)


def validate_image(image_path):
    # We would like to validate the image was fully downloaded and wasn't truncated.
    # To do so, we can open the image file using PIL.Image and try to resize it to the size
    # the file declares it has.
    # If the image wasn't fully downloaded and was truncated - an error will be raised.
    img = Image.open(image_path)
    img.resize(img.size)

from os.path import join
import shutil
import time
import requests
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import RequestException
import json
from PIL import Image

# The url template for the image is <base url prefix><image id><base url suffix>
# The url template for the description of the image is: <base url prefix><image id>
base_url_prefix = 'https://isic-archive.com/api/v1/image/'
base_url_suffix = '/download?contentDisposition=inline'


def download_and_save_description_wrapper(args):
    return download_and_save_description(*args)


def download_and_save_description(id, descriptions_dir) -> list:
    """

    :param id: Id of the image whose description will be downloaded
    :param descriptions_dir:
    :return: Json
    """
    description = download_description(id)
    save_description(description, descriptions_dir)
    return description


def download_description(id) -> list:
    """

    :param id: Id of the image whose description will be downloaded
    :return: Json
    """
    # Build the description url
    url_desc = base_url_prefix + id

    # Download the image and description using the url
    # Sometimes their site isn't responding well, and than an error occurs,
    # So we will retry 10 seconds later and repeat until it succeeds
    while True:
        try:
            # Download the description
            response_desc = requests.get(url_desc, stream=True, timeout=20)
            # Validate the download status is ok
            response_desc.raise_for_status()
            # Parse the description
            parsed_description = response_desc.json()
            return parsed_description
        except RequestException:
            time.sleep(10)
        except ReadTimeoutError:
            time.sleep(10)
        except IOError:
            time.sleep(10)


def save_description(description, descriptions_dir):
    """

    :param description: Json
    :param descriptions_dir:
    :return:
    """
    desc_path = join(descriptions_dir, description['name'])
    with open(desc_path, 'w') as descFile:
        json.dump(description, descFile, indent=2)


def download_and_save_image_wrapper(args):
    download_and_save_image(*args)


def download_and_save_image(description, images_dir):
    """

    :param description: Json describing the image
    :param images_dir: Directory in which to save the image
    """
    # Build the image url
    url_image = base_url_prefix + description['_id'] + base_url_suffix

    # Download the image and description using the url
    # Sometimes their site isn't responding well, and than an error occurs,
    # So we will retry 10 seconds later and repeat until it succeeds
    while True:
        try:
            response_image = requests.get(url_image, stream=True, timeout=20)
            # Validate the download status is ok
            response_image.raise_for_status()

            # Write the image into a file
            img_path = join(images_dir, '{0}.jpg'.format(description['name']))
            with open(img_path, 'wb') as imageFile:
                shutil.copyfileobj(response_image.raw, imageFile)

            # Validate the image was downloaded correctly
            validate_image(img_path)
            return
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

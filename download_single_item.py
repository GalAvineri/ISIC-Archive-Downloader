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
img_url_prefix = 'https://isic-archive.com/api/v1/image/'
img_url_suffix = '/download?contentDisposition=inline'
seg_url_prefix = 'https://isic-archive.com/api/v1/segmentation'
seg_id_url_prefix = seg_url_prefix + '?limit=1&sort=created&sortdir=-1&imageId='
seg_img_url_prefix = seg_url_prefix + '/'
seg_img_url_suffix = '/mask?contentDisposition=inline'


def imap_wrapper(args):
    """
    :param args: tuple of the form (func, f_arguments)
    :return: result of func(**f_arguments)
    """

    func = args[0]
    f_args = args[1:]
    return func(*f_args)


def download_image_description(id, descriptions_dir) -> list:
    """

    :param id: Id of the image whose description will be downloaded
    :param descriptions_dir:
    :return: Json
    """
    desc_url = img_url_prefix + id
    description = fetch_description(desc_url)
    save_description(description, descriptions_dir)
    return description


def fetch_description(url : str) -> list:
    """

    :param id: Id of the image whose description will be downloaded
    :return: Json
    """
    # Sometimes their site isn't responding well, and than an error occurs,
    # So we will retry 10 seconds later and repeat until it succeeds
    while True:
        try:
            # Download the description
            response_desc = requests.get(url, stream=True, timeout=20)
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


def fetch_img_description(id : str) -> list:
    """

    :param id: Id of the image whose description will be downloaded
    :return: Json
    """
    # Sometimes their site isn't responding well, and than an error occurs,
    # So we will retry 10 seconds later and repeat until it succeeds
    url = img_url_prefix + id
    while True:
        try:
            # Download the description
            response_desc = requests.get(url, stream=True, timeout=20)
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


def download_lesion_image(description, dir):
    """
    :param description: Json describing the image
    :param dir: Directory in which to save the image
    """
    # Build the image url
    img_url = img_url_prefix + description['_id'] + img_url_suffix

    download_image(img_url=img_url, img_name=description['name'], dir=dir)


def download_image(img_url, img_name, dir, type='jpg', max_tries=None):
    """
    Download the image from the given url and save it in the given dir,
    naming it using img_name with an jpg extension
    :param img_name:
    :param img_url: Url to download the image through
    :param dir: Directory in which to save the image
    :return Whether the image was downloaded successfully
    """
    # Sometimes their site isn't responding well, and than an error occurs,
    # So we will retry 10 seconds later and repeat until it succeeds
    tries = 0
    while max_tries is None or tries <= max_tries:
        try:
            # print('Attempting to download image {0}'.format(img_name))
            response_image = requests.get(img_url, stream=True, timeout=20)
            # Validate the download status is ok
            response_image.raise_for_status()

            # Write the image into a file
            img_path = join(dir, '{0}.{1}'.format(img_name, type))
            with open(img_path, 'wb') as imageFile:
                shutil.copyfileobj(response_image.raw, imageFile)

            # Validate the image was downloaded correctly
            validate_image(img_path)

            # print('Finished Downloading image {0}'.format(img_name))
            return True
        except (RequestException, ReadTimeoutError, IOError):
            tries += 1
            time.sleep(5)

    return False


def download_segmentation(description, dir):
    """
    :param description: Json describing the image
    :param dir: Directory in which to save the image
    :return Whether there was a segmentation for the requested image, and it was downloaded
        successfully.
    """
    # Get the id of the segmentation image
    image_id = description['_id']
    seg_desc_url = seg_id_url_prefix + image_id
    seg_description = fetch_description(seg_desc_url)
    # If there are no segmentation available for the image, do nothing
    if len(seg_description) == 0:
        return False
    # Download the first available segmentation
    seg_id = seg_description[0]['_id']
    seg_img_url = seg_img_url_prefix + seg_id + seg_img_url_suffix
    has_downloaded = download_image(img_url=seg_img_url, img_name=description['name'], dir=dir, type='png', max_tries=5)
    return has_downloaded


def validate_image(image_path):
    # We would like to validate the image was fully downloaded and wasn't truncated.
    # To do so, we can open the image file using PIL.Image and try to resize it to the size
    # the file declares it has.
    # If the image wasn't fully downloaded and was truncated - an error will be raised.
    img = Image.open(image_path)
    img.resize(img.size)
from os.path import join
import shutil
import time
import requests
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import RequestException
import json
from PIL import Image
import imghdr


class BasicElementDownloader:
    @classmethod
    def download_img(cls, img_url, img_name, dir, max_tries=None):
        """
        Download the image from the given url and save it in the given dir,
        naming it using img_name with an jpg extension
        :param img_name:
        :param img_url: Url to download the image through
        :param dir: Directory in which to save the image
        :return Whether the image was downloaded successfully
        """
        # Sometimes their site isn't responding well, and than an error occurs,
        # So we will retry a few seconds later and repeat until it succeeds
        tries = 0
        while max_tries is None or tries <= max_tries:
            try:
                # print('Attempting to download image {0}'.format(img_name))
                response = requests.get(img_url, stream=True, timeout=20)
                # Validate the download status is ok
                response.raise_for_status()

                # Find the format of the image
                format = response.headers['Content-Type'].split('/')[1]

                # Write the image into a file
                image_string = response.raw
                img_path = join(dir, '{0}.{1}'.format(img_name, format))
                with open(img_path, 'wb') as imageFile:
                    shutil.copyfileobj(image_string, imageFile)

                # Validate the image was downloaded correctly
                cls.validate_image(img_path)

                # print('Finished Downloading image {0}'.format(img_name))
                return True
            except (RequestException, ReadTimeoutError, IOError):
                tries += 1
                time.sleep(5)

        return False

    @staticmethod
    def fetch_description(url: str) -> list:
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
            except (RequestException, ReadTimeoutError):
                time.sleep(5)

    @staticmethod
    def save_description(desc, dir):
        """

        :param desc: Json
        :param dir:
        :return:
        """
        desc_path = join(dir, desc['name'])
        with open(desc_path, 'w') as descFile:
            json.dump(desc, descFile, indent=2)

    @classmethod
    def download_description(cls, url: str, dir: str) -> list:
        desc = cls.fetch_description(url)
        cls.save_description(desc, dir)

    @staticmethod
    def validate_image(image_path):
        # We would like to validate the image was fully downloaded and wasn't truncated.
        # To do so, we can open the image file using PIL.Image and try to resize it to the size
        # the file declares it has.
        # If the image wasn't fully downloaded and was truncated - an error will be raised.
        img : Image.Image = Image.open(image_path)
        img.resize(img.size)


class LesionImageDownloader():
    url_prefix: str = 'https://isic-archive.com/api/v1/image/'
    url_suffix: str = '/download?contentDisposition=inline'

    @classmethod
    def download_image(cls, desc, dir):
        """
        :param desc: Json describing the image
        :param dir: Directory in which to save the image
        """
        # Build the image url
        img_url = cls.url_prefix + desc['_id'] + cls.url_suffix

        BasicElementDownloader.download_img(img_url=img_url, img_name=desc['name'], dir=dir)

    @classmethod
    def fetch_img_description(cls, id: str) -> list:
        """

        :param id: Id of the image whose description will be downloaded
        :return: Json
        """
        url = cls.url_prefix + id
        return BasicElementDownloader.fetch_description(url)

    @classmethod
    def save_img_description(cls, desc, dir):
        BasicElementDownloader.save_description(desc, dir)

    @classmethod
    def save_description(self,desc, dir) -> list:
        """

        :param desc: Json
        :param dir:
        :return:
        """
        return BasicElementDownloader.save_description(desc, dir)

    @classmethod
    def download_image_description(cls, id, dir) -> list:
        """

        :param id: Id of the image whose description will be downloaded
        :param dir:
        :return: Json
        """
        desc = cls.fetch_img_description(id)
        BasicElementDownloader.save_description(desc, dir)
        return desc


class SegmentationDownloader:
    url_prefix: str = 'https://isic-archive.com/api/v1/segmentation'
    id_url_prefix: str = url_prefix + '?limit=0&imageId='
    img_url_prefix: str = url_prefix + '/'
    img_url_suffix: str = '/mask?contentDisposition=inline'

    @classmethod
    def download_image(cls, lesion_desc, dir, skill_pref):
        """
        Downloads a segmentation for a lesion image, if available.
        If skill_pref is not None, and a segmentation is of the preferred skill level is available,
        it will be downloaded.
        If a segmentation of the preferred skill level is not available, the method will download
        the first segmentation available.

        :param lesion_desc: Json describing the lesion image
        :param dir: Directory in which to save the image
        :param skill_pref: Preferred skill of segmentation.
        :return Whether there was a segmentation for the requested image, and it was downloaded
            successfully.
        """
        # Get the id of the segmentation image
        image_id = lesion_desc['_id']
        seg_desc_url = cls.id_url_prefix + image_id
        seg_desc = BasicElementDownloader.fetch_description(seg_desc_url)
        # If there are no segmentation available for the image, do nothing
        if len(seg_desc) == 0:
            return False
        seg_index = 0
        if skill_pref is not None:
            # If there's a segmentation with the preffered skill level, pick it.
            for index, seg in enumerate(seg_desc):
                seg_id, seg_skill = seg['_id'], seg['skill']
                if seg_skill == skill_pref:
                    seg_index = index
        chosen_seg_id = seg_desc[seg_index]['_id']
        skill_level = seg_desc[seg_index]['skill']
        # Download the segmentation
        seg_img_url = cls.img_url_prefix + chosen_seg_id + cls.img_url_suffix
        has_downloaded = BasicElementDownloader.download_img(img_url=seg_img_url,
                                                             img_name='{}_{}'.format(lesion_desc['name'], skill_level),
                                                             dir=dir, max_tries=5)
        return has_downloaded
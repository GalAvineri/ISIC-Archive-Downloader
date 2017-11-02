from download_dataset_subset import download_dataset_subset, validate_image
import re
import os
import shutil
import requests
from os.path import join
from threading import Thread
from PIL import Image


# Required Parameters:
# Specify the current dataset size
size = 13786

# Optional parameters:
# Specify the path to the dir the images will be saved in
images_dir = join(os.pardir, 'Data', 'Images')
# Specify the path to the dir the descriptions will be saved in
descs_dir = join(os.pardir, 'Data', 'Descriptions')
# Choose the number of images each thread will download
thread_subset_size = 300


def main():
    # If any of the images dir, descs dir or ids file exists - remove them so we won't override data
    # and perhaps create corrupted data
    create_or_recreate_dir(images_dir)
    create_or_recreate_dir(descs_dir)

    # 1. Get the ids of all the images
    ids = get_ids()
    # 2. Download all the images using their ids
    download_dataset(ids)
    # 3. Validate all the images
    validate_images()


def get_ids():
    print('Collecting all images ids')

    # Specify the url that lists the meta data about the images (id, name, etc..)
    url = 'https://isic-archive.com/api/v1/image?limit={0}&offset=0&sort=name&sortdir=1'.format(size)
    # Get the images metadata
    response = requests.get(url, stream=True)
    # Parse as json
    meta_data = response.json()
    # Extract all the ids
    ids = [str(meta_data[index]['_id']) for index in range(size)]

    return ids


def download_dataset(ids):
    # Determine the dataset subsets which multiple threads will download
    bins = range(0, size, thread_subset_size)

    # Create the threads to download subsets of the dataset
    # and determine the edges for the current thread
    threads = []
    for idx, left_edge in enumerate(bins):
        # Deretmine the right edge
        right_edge = left_edge + thread_subset_size
        if right_edge >= size:
            right_edge = size
        # Define the thread on the current subset
        thread = Thread(target=download_dataset_subset, kwargs={'start': left_edge, 'end': right_edge, 'ids': ids[left_edge: right_edge],
                                                                'images_dir': images_dir, 'descs_dir': descs_dir, 'thread_id': idx})
        # Start it and add it to the list of threads
        thread.start()
        threads.append(thread)

    # Wait for all the threads to finish
    for thread in threads:
        thread.join()

    print('All threads have finished')


def validate_images():
    # We would like to check that all the images are valid
    try:
        for image in os.listdir(images_dir):
            image_path = join(images_dir, image)
            validate_image(image_path)
    except IOError as e:
        print(e.message)
        print("The image {0} wasn't downloaded successfully. "
              "Please Open an issue in the github repository together with the error".format(image))


def create_or_recreate_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)


if __name__ == '__main__':
    main()

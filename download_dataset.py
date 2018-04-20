from download_single_item import downlad_image_and_desc_wrapper
from progress_bar import progress_bar

import argparse
import os
import shutil
import requests
from os.path import join
from threading import Thread
from multiprocessing import Pool
from itertools import repeat


def main(num_images, offset, images_dir, descs_dir, num_processes):
    # If any of the images dir, descs dir or ids file exists - remove them so we won't override data
    # and perhaps create corrupted data
    create_if_none(images_dir)
    create_if_none(descs_dir)

    print('Collecting the images ids')
    ids = get_images_ids(num_images=num_images, offset=offset)

    num_images_found = len(ids)
    if num_images_found != num_images:
        print('Found {0} images and not the requested {1}'.format(num_images_found, num_images))

    print('Downloading images and descriptions')
    download_dataset(ids=ids, num_images=num_images_found, images_dir=images_dir, descs_dir=descs_dir,
                     num_processes=num_processes)

    print('Finished downloading the data set')


def create_if_none(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def get_images_ids(num_images, offset):
    # Specify the url that lists the meta data about the images (id, name, etc..)
    url = 'https://isic-archive.com/api/v1/image?limit={0}&offset={1}&sort=name&sortdir=1'.format(num_images, offset)
    # Get the images metadata
    response = requests.get(url, stream=True)
    # Parse the metadata
    meta_data = response.json()
    # Extract the ids of the images
    ids = [meta_data[index]['_id'] for index in range(len(meta_data))]
    return ids


def download_dataset(ids, num_images, images_dir, descs_dir, num_processes):
    # Create a thread to provide a progress bar
    prog_thread = Thread(target=progress_bar, kwargs={'target': num_images, 'dir': descs_dir})
    prog_thread.start()

    # Have a process download each data subset
    pool = Pool(processes=num_processes)
    pool.map(downlad_image_and_desc_wrapper, zip(ids, repeat(images_dir), repeat(descs_dir)))

    # The starmap function blocks until all the processes have finished
    # So at this point all the images and descriptions have been downloaded.
    # Collect the progress bar thread
    prog_thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('num_images', type=int, help='The number of images you would like to download from the ISIC Archive')
    parser.add_argument('--offset', type=int, help='The offset of the image index from which to start downloading', default=0)
    parser.add_argument('--images-dir', help='The directory in which the images will be downloaded to',
                        default=join('Data', 'Images'))
    parser.add_argument('--descs-dir', help='The directory in which the descriptions of '
                                            'the images will be downloaded to',
                        default=join('Data', 'Descriptions'))
    parser.add_argument('--p', type=int, help='The number of processes to use in parallel', default=16)
    args = parser.parse_args()

    main(num_images=args.num_images, offset=args.offset, images_dir=args.images_dir, descs_dir=args.descs_dir,
         num_processes=args.p)

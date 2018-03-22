from download_dataset_subset import download_dataset_subset
from progress_bar import progress_bar

import argparse
import os
import shutil
import requests
from os.path import join
from threading import Thread
from multiprocessing import Pool
from itertools import repeat


def main(num_images, images_dir, descs_dir, num_processes):
    # If any of the images dir, descs dir or ids file exists - remove them so we won't override data
    # and perhaps create corrupted data
    create_or_recreate_dir(images_dir)
    create_or_recreate_dir(descs_dir)

    print('Collecting the images ids')
    ids = get_images_ids(num_images=num_images)
    num_images_found = len(ids)

    print('Downloading images and descriptions')
    download_dataset(ids=ids, num_images=num_images_found, images_dir=images_dir, descs_dir=descs_dir,
                     num_processes=num_processes)

    print('Finished downloading the data set')


def create_or_recreate_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)


def get_images_ids(num_images):
    # Specify the url that lists the meta data about the images (id, name, etc..)
    url = 'https://isic-archive.com/api/v1/image?limit={0}&offset=0&sort=name&sortdir=1'.format(num_images)
    # Get the images metadata
    response = requests.get(url, stream=True)
    # Parse the metadata
    meta_data = response.json()
    # Extract the ids of the images
    ids = [meta_data[index]['_id'] for index in range(len(meta_data))]
    return ids


def download_dataset(ids, num_images, images_dir, descs_dir, num_processes):
    # Each process will download a subset of the archive.
    # Infer the size of the subsets
    subset_size = num_images // num_processes
    # Split the data into subsets
    bins = list(range(0, num_images, subset_size))
    bins[-1] = num_images
    bin_starts = bins[:-1]
    bin_ends = bins[1:]

    # Create a thread to provide a progress bar
    prog_thread = Thread(target=progress_bar, kwargs={'target': num_images, 'dir': descs_dir})
    prog_thread.start()

    # Have a process download each data subset
    ids_subsets = [ids[bin_start: bin_end] for bin_start, bin_end in zip(bin_starts, bin_ends)]
    pool = Pool(processes=num_processes)
    pool.starmap(download_dataset_subset, zip(ids_subsets, repeat(images_dir), repeat(descs_dir)))

    # The starmap function blocks until all the processes have finished
    # So at this point all the images and descriptions have been downloaded.
    # Collect the progress bar thread
    prog_thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('num_images', type=int, help='The number of images in the ISIC Archive')
    parser.add_argument('--images-dir', help='The directory in which the images will be downloaded to',
                        default=join('Data', 'Images'))
    parser.add_argument('--descs-dir', help='The directory in which the descriptions of '
                                            'the images will be downloaded to',
                        default=join('Data', 'Descriptions'))
    parser.add_argument('--p', type=int, help='The number of processes to use in parallel', default=16)
    args = parser.parse_args()

    main(num_images=args.num_images, images_dir=args.images_dir, descs_dir=args.descs_dir,
         num_processes=args.p)

from download_dataset_subset import download_dataset_subset, validate_image

import argparse
import os
import shutil
import requests
from os.path import join
from threading import Thread


def main(num_images, images_dir, descs_dir, thread_subset_size):
    # If any of the images dir, descs dir or ids file exists - remove them so we won't override data
    # and perhaps create corrupted data
    create_or_recreate_dir(images_dir)
    create_or_recreate_dir(descs_dir)

    print('Collecting the images ids')
    ids = get_images_ids(num_images=num_images)

    print('Downloading images and descriptions')
    download_dataset(ids=ids, num_images=num_images, images_dir=images_dir, descs_dir=descs_dir,
                     thread_subset_size=thread_subset_size)

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
    ids = [meta_data[index]['_id'] for index in range(num_images)]
    return ids


def download_dataset(ids, num_images, images_dir, descs_dir, thread_subset_size):
    # Split the data into subsets
    bins = list(range(0, num_images, thread_subset_size))
    bins.append(num_images)
    bin_starts = bins[:-1]
    bin_ends = bins[1:]

    # Create threads to download each data subset
    threads = []
    for idx, bin_start, bin_end in enumerate(zip(bin_starts, bin_ends)):
        thread = Thread(target=download_dataset_subset, kwargs={'start': bin_start, 'end': bin_end, 'ids': ids[bin_start: bin_end],
                                                                'images_dir': images_dir, 'descs_dir': descs_dir, 'thread_id': idx})
        thread.start()
        threads.append(thread)

    # Wait for all the threads to finish
    for thread in threads:
        thread.join()

    print('All threads have finished')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('num_images', type=int, help='The number of images in the ISIC Archive')
    parser.add_argument('--images-dir', help='The directory in which the images will be downloaded to',
                        default=join('Data', 'Images'))
    parser.add_argument('--descs-dir', help='The directory in which the descriptions of '
                                            'the images will be downloaded to',
                        default=join('Data', 'Descriptions'))
    parser.add_argument('--tss', type=int, help='The number of images each thread will download', default=300)
    args = parser.parse_args()

    main(num_images=args.num_images, images_dir=args.images_dir, descs_dir=args.descs_dir,
         thread_subset_size=args.tss)

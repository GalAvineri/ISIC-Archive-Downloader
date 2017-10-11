from download_dataset_subset import download_dataset_subset
import re
import os
import shutil
import requests
from os.path import join
from threading import Thread


# Required Parameters:
# Specify the current dataset size
size = 13786

# Optional parameters:
# Specify the path to the dir the images will be saved in
images_dir = join('Data', 'images')
# Specify the path to the dir the descriptions will be saved in
descs_dir = join('Data', 'descriptions')
# Choose the number of images each thread will download
thread_subset_size = 300


def main():

    # Specify the path to the temporary text file which will hold the images ids
    id_file_path = os.path.join(os.getcwd(), 'ids.txt')

    # If any of the images dir, descs dir or ids file exists - remove them so we won't override data
    # and perhaps create corrupted data
    if os.path.isdir(images_dir):
        shutil.rmtree(images_dir)
    if os.path.isdir(descs_dir):
        shutil.rmtree(descs_dir)
    if os.path.isfile(id_file_path):
        os.remove(id_file_path)
    os.makedirs(images_dir)
    os.makedirs(descs_dir)

    # 1. Get the ids of all the images into a txt file
    get_ids(id_file_path)
    # 2. Download all the images using their ids
    download_dataset(id_file_path)
    # 3. Cleanup
    os.remove(id_file_path)


def get_ids(id_file_path):

    print('Collecting all images ids')

    # Specify the url that lists the meta data about the images (id, name, etc..)
    url = 'https://isic-archive.com/api/v1/image?limit={0}&offset=0&sort=name&sortdir=1'.format(size)
    # Get the images metadata
    response = requests.get(url, stream=True)
    # extract all the ids
    ids = []
    for match in re.finditer('_id', response.content):
        id = extract_id_from_line(response.content, match.start())
        ids.append(id)

    # Write the ids into a txt file
    with open(id_file_path, 'w') as f:
        for item in ids:
            f.write("%s\n" % item)


def extract_id_from_line(s, index):
    start_quotes = s.index('"', index+4)
    end_quotes = s.index('"', start_quotes + 1)
    id = s[start_quotes + 1 : end_quotes]
    return id


def download_dataset(id_file_path):
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
        thread = Thread(target=download_dataset_subset, kwargs={'start': left_edge, 'end': right_edge, 'id_file_path': id_file_path,
                                                                'images_dir': images_dir, 'descs_dir': descs_dir, 'thread_id': idx})
        # Start it and add it to the list of threads
        thread.start()
        threads.append(thread)

    # Wait for all the threads to finish
    for thread in threads:
        thread.join()

    print('All threads have finished')


if __name__ == '__main__':
    main()
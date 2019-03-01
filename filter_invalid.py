import os
from os.path import join
import json
import shutil
import argparse
import multiprocessing
from itertools import repeat
from tqdm import tqdm
from auxiliaries import validate_exists_and_dir, create_or_recreate_dir, imap_wrapper


def filter_invalid_images(images_dir, descs_dir, inv_images_dir, inv_descs_dir, num_processes):
    validate_exists_and_dir(images_dir, 'images_dir')
    validate_exists_and_dir(descs_dir, 'descs_dir')
    # Create the result dirs
    create_or_recreate_dir(inv_images_dir)
    create_or_recreate_dir(inv_descs_dir)

    # Find all the descriptions
    images_fnames = os.listdir(images_dir)
    descs_fnames = os.listdir(descs_dir)

    # Find which descriptions are invalid
    # And mark them and their corresponding image for moving
    src_paths = []
    dst_paths = []
    for image_fname, desc_fname in zip(images_fnames, descs_fnames):
        valid_desc = True
        desc_path = join(descs_dir, desc_fname)
        # Load the json
        desc = json.load(open(desc_path))
        # Validate the description
        try:
            label = desc['meta']['clinical']['benign_malignant']
            if label not in {'benign', 'malignant'}:
                valid_desc = False
        except KeyError:
            valid_desc = False
        if not valid_desc:
            # The description is invalid.
            # Mark it and its corresponding image for moving
            image_path = join(images_dir, image_fname)
            src_paths += [image_path, desc_path]
            dst_paths += [join(inv_images_dir, image_fname), join(inv_descs_dir, desc_fname)]

    # Move the invalid descriptions and images to the filtered directories
    p = multiprocessing.Pool(processes=num_processes)
    list(tqdm(p.imap(imap_wrapper, zip(repeat(shutil.move), src_paths, dst_paths)), total=len(src_paths), desc='Filtering invalid images'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--images-dir', type=str, help='Directory which holds the images, and only them', required=True)
    parser.add_argument('--descs-dir', type=str, help='Directory which holds the descriptions of the images and only them', required=True)
    parser.add_argument('--inv-dir', type=str, help='Directory to store the filtered out invalid data', required=True)
    parser.add_argument('--p', type=int, help='Number of processes to use in parallel', default=16)
    args = parser.parse_args()

    inv_images_dir = join(args.inv_dir, 'images')
    inv_descs_dir = join(args.inv_dir, 'descs')

    filter_invalid_images(images_dir=args.images_dir, descs_dir=args.descs_dir, inv_images_dir=inv_images_dir, inv_descs_dir=inv_descs_dir, num_processes=args.p)

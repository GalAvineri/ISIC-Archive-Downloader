import os
import shutil
import time
import requests


def download_dataset_subset(start, end, id_file_path, images_dir, descs_dir, thread_id):
    # Announce the start of the thread (mainly for debugging)
    print('Thread {0} started'.format(thread_id))

    # The url template is 'base_url_prefix - image_id - base_url_suffix'
    base_url_prefix = 'https://isic-archive.com/api/v1/image/'
    base_url_suffix = '/download?contentDisposition=inline'

    with open(id_file_path) as f:
        # get all the ids
        ids = f.readlines()

        # for each id:
        # 1. get the corresponding image and description urls
        # 2. download the image and the description from the urls
        for index, id in enumerate(ids[start:end]):
            # Update the index to the right offset of the bin we're working on
            index = index + start

            print("downloading image ({0}/{1})".format(index, end))
            # strip the id from the \n at the end
            id = id.strip()

            # get the corresponding image url
            url_image = base_url_prefix + id + base_url_suffix
            # get the corresponding description url
            url_desc = base_url_prefix + id
            print ("url_image = {0}".format(url_image))

            # Download the image and desctiprion using the urls
            # Sometimes their site isn't responding well, and than an error occurs,
            # So we will retry the same url 5 seconds later, until it succeeds
            succeeded = False
            while not succeeded:
                try:
                    response_image = requests.get(url_image, stream=True)
                    response_desc = requests.get(url_desc, stream=True)
                    succeeded = True
                except:
                    print "trying again index number ", index
                    time.sleep(5)

            # Write the image into a file
            imgFilePath = os.path.join(images_dir, 'ISIC_{0}.jpg'.format(str(index).zfill(7)))
            with open(imgFilePath, 'wb') as imageFile:
                shutil.copyfileobj(response_image.raw, imageFile)

            # Parse the description and write the description into a file
            parsed_desc = parse_desc(response_desc.content)
            descFilePath = os.path.join(descs_dir, 'ISIC_{0}'.format(str(index).zfill(7)))
            with open(descFilePath, 'w') as descFile:
                for line in parsed_desc:
                    descFile.write("%s\n" % line)

    print('Thread {0} finished'.format(thread_id))


def parse_desc(desc):
    line_start_index = 0
    line_end_index = 0
    lines = []
    indentation = 0

    while line_end_index < len(desc):
        if desc[line_end_index:line_end_index+2] == '},':
            line = desc[line_start_index: line_end_index + 2]
            # indent the line
            line = ' ' * indentation + line
            lines.append(line)
            line_start_index = line_end_index + 2
            line_end_index = line_start_index
            # update indentation
            indentation -= 4

        elif desc[line_end_index] in ['{', '}', ',', '[', ']']:
            line = desc[line_start_index: line_end_index + 1]
            # indent the line
            line = ' '*indentation + line
            lines.append(line)

            # update indentation
            if desc[line_end_index] in ['{', '[']:
                indentation += 4
            elif desc[line_end_index] in ['}', ']']:
                indentation -= 4

            # update pointers
            line_start_index = line_end_index + 1
            line_end_index = line_start_index

        else:
            line_end_index += 1

    return lines


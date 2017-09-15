import shutil
import requests
import os
import time
import re

# Specify the current dataset size
size = 13776
# specify the path to the dir the images will be saved in
imagesDir = os.path.join(os.getcwd(), 'images')
# specify the path to the dir the descriptions will be saved in
descsDir = os.path.join(os.getcwd(), 'descriptions')


def getIds():
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
    with open(idFile, 'w') as f:
        for item in ids:
            f.write("%s\n" % item)

def extract_id_from_line(s, index):
    start_quotes = s.index('"', index+4)
    end_quotes = s.index('"', start_quotes + 1)
    id = s[start_quotes + 1 : end_quotes]
    return id

def download_dataset():
    # The url template is 'base_url_prefix - image_id - base_url_suffix'
    baseUrlPrefix = 'https://isic-archive.com/api/v1/image/'
    baseUrlSuffix = '/download?contentDisposition=inline'


    with open(idFile) as f:
        # get all the ids
        ids = f.readlines()

        # for each id:
        # 1. get the corresponding image and description urls
        # 2. download the image and the description from the urls
        for index, id in enumerate(ids):
                print("downloading image {0}".format(index))
                # strip the id from the \n at the end
                id = id.strip()

                # get the corresponding image url
                url_image = baseUrlPrefix + id + baseUrlSuffix
                # get the corresponding description url
                url_desc = baseUrlPrefix + id
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
                imgFilePath = os.path.join(imagesDir, 'ISIC_{0}.jpg'.format(str(index).zfill(7)))
                with open(imgFilePath, 'wb') as imageFile:
                    shutil.copyfileobj(response_image.raw, imageFile)

                # Parse the description and write the description into a file
                parsed_desc = parse_desc(response_desc.content)
                descFilePath = os.path.join(descsDir, 'ISIC_{0}'.format(str(index).zfill(7)))
                with open(descFilePath, 'w') as descFile:
                    for line in parsed_desc:
                        descFile.write("%s\n" % line)

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


# Main

# the path to the temporary text file which will hold the images ids
idFile = os.path.join(os.getcwd(), 'ids.txt')

# If the imagesDir or descsDir exist - remove them so we won't override data
# and perhaps create corrupted data
if os.path.isdir(imagesDir):
    shutil.rmtree(imagesDir)
if os.path.isdir(descsDir):
    shutil.rmtree(descsDir)
os.mkdir(imagesDir)
os.mkdir(descsDir)

# 1. Get the ids of all the images into a txt file
getIds()
# 2. Download all the images using their ids
download_dataset()
# 3. Cleanup
os.remove(idFile)


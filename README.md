# ISIC Archive Downloader
The ISIC Archive contains over 23k images of skin lesions, labeled as 'benign' or 'malignant'.  
The archive can be found here:
https://www.isic-archive.com/#!/onlyHeaderTop/gallery

The current ways to download the archive, provided by the ISIC foundation and which are known to me, are the following:
1. Download the entire archive via the direct download button on their website.
2. Download all the partitions of the archive, called 'datasets' one by one
3. Downloading the images one by one via the Grider API provided in the site

The first option (which is the easiest and most comfortable way) doesn't always finish successfully for some reason.  
We suspect this is happening due to the large file size.
  
The second option seems rather good if you plan to download the archive only a few times  
and the third option seems unfeasible.  

If you find the options above too laborious or unavailable, this script provides a comfortable alternative.  
This script can download the entire ISIC archive ([or parts of it](#optional-download-abilities))  
all you have to do is run `python download_archive.py`

# Requirements
1. Python 3.6 or later
2.  requests  `pip install requests`
3.  PIL  `pip install Pillow`
4.  tqdm  `pip install tqdm`

Or you could just `pip install -r requirements.txt`

# Instructions
1.  download or clone the repository
2.  run download_archive.py `python download_archive.py`

#### Notes
1.  By default if you call the script in the following way:  
    `python <root>/.../download_archive.py`  
    images will be download to \<root\>/Data/Images  
    their descriptions will be downloaded to \<root\>/Data/Descriptions
    
2.  In case you choose to download segmentations of images,
    Note that some images have multiple segmentations of different expertise levels.
    This script currently downloads one in random, and unnecessarily one of the highest
    expertise.


#### Warnings
1. Make sure you have enough space in the download destination.
Otherwise the download will run into errors.
2. The download might take a few hours.

# Optional download abilities
1. You can download a subset of the archive by specifying how many images you would like.  
`python download_archive.py --num-images 1000`  
If this option isn't present, the program will download all the available images.  

2. You can start downloading images from an offset.  
   `python download_archive.py --offset 100`  
   This is useful for example if you would like to append upon a prior download.  
   
3. You can choose to download either only benign or malignant images.  
   `python download_archive.py --filter benign`  
   Note: If you would like k benign images instead of all the benign images, you could do  
   `python download_archive.py --num-images k --filter benign`
   
4. You can choose to download the segmentation of the images  
   `python download_archive.py -s`  
   and the directory which they will be downloaded to.  
   `python download_archive.py -s --seg-dir /Data/Segmentations`  
   Some images have multiple segmentations offered, made with different skill level.  
   You can choose a preferred skill level (e.g expert).  
   `python download_archive.py -s --seg-level novice`  
   That means that, when available, the script will download a segmentation with the preferred
   skill level.  
   If no preference was given, the first available segmentation will be downloaded.  
   Note: It has been suggested that sometimes segmentations tagged as 'novice' skill are more accurate
   than there 'expert' alternative. So perhaps relying the the 'expert' segmentations are always better
   can be incorrect.   
   
5. You can choose not to download the lesion images.  
   `python download_archive.py --no-images`  
   This might be useful if you would like to download only the descriptions of segmentation images.
   
6. You can change the default directories the images and the descriptions will be downloaded into.  
`python download_archive.py --images-dir /Data/Images --descs-dir /Data/Descriptions`  

7. You can also change the default amount of processes that will work in parallel to download the archive.  
`python download_archive.py --p 16`  
But if you have no knowledge about this one, the default will be fine.

# How does it work
Searching for a few images using the API provided by the website, we found that the images are stored  
at a url which is in the template of \<prefix>  \<image id>  \<suffix>  
and that their description are stored in \<prefix> \<image id>  
while the prefix and suffix parts are the same for all the images. 

The website API also provides a way to request all the ids of all the images.

So the basic portion of the script is:
1. Request the ids of all the images
2. Build the urls by the given template
3. Download the images and descriptions from the built urls

##### Note
As mentioned above, we assume that the urls of the images and descriptions are built by a certain template.  
If the template ever changes (and you start getting errors for example)  
just let us know and we will change it accordingly :)  
Feel free to use the issues tab for that.


# Finally
We hope this script will allow researchers, who had similliar difficulties
accessing ISIC's archive, to have easier access and enable them to provide further work on this field,
as the ISIC foundation wishes :)

If you stumble into any issues - let us know in the issues section!

In addition, Any contributions or improvement ideas to our code that will improve the comfort of the users 
will be dearly appreciated :)


# Written By
Oren Talmor & Gal Avineri


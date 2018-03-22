# ISIC Archive Downloader
The ISIC Archive contains over 13k images of skin lesions, labeled as 'benign' or 'malignant'.  
The archive can be found here:
https://isic-archive.com/#images

The current ways to download the archive, provided by the ISIC foundation and which are known to me, are the following:
1. Download the entire archive via the direct download button on their website.
2. Download all the partitions of the archive, called 'datasets' one by one
3. Downloading the images one by one via the Grider API provided in the site

The first option (which is the easiest and most comfortable way) doesn't always work for some reason.  
The download doesn't always finish successfully,  
and  we suspect this is happening due to the large file size.
  
The second option seems rather good if you plan to download the archive only a few times  
and the third option seems unfeasible.  

If you find the options above too laborious or unavailable, this script provides a comfortable alternative.  
This script can download the entire ISIC archive,  
all you have to do is run it with the amount of images you'd like to download:  
`python download_dataset <num of images>`

# Requirements
Python: Python 3.3 and beyond

Packages:
1.  requests  `pip install requests`
2.  PIL  `pip install Pillow`
3.  progressbar2  `pip install progressbar2`

Or you could just `pip install -r requirements.txt`

# Instructions
1.  download or clone the repository
2.  run download_dataset.py with the number of images you would like to download.  
    e.g `python download_dataset 13000`  
    If you would like to download the entire ISIC archive, just enter the current
    number of images the archive possess.
    
    Warning: Make sure you have enough space in the download destination.  
    Otherwise the download will run into errors. 
    
3.  (optional)  
    You can change the default directories which the images and their descriptions will be downloaded to.  
    `python download_dataset 13000 --images-dir /Data/Images --descs-dir /Data/Descriptions`
      
    You can also change the default amount of processes that will work in parallel to download  
    the dataset
    `python download_dataset 13000 --p 16`  
    But if you don't have a clue about this one, the default will be fine.

# How does it work
Searching for a few images using the API provided by the website, we found that the images are stored
at a url which is in the template of \<prefix>  \<image id>  \<suffix>  
and that their description are stored in \<prefix> \<image id>  
while the prefix and suffix parts are the same for all the images. 

The website API also provides a way to request all the ids of all the images.

So we wrote a script that:
1. Requests the ids of all the images
2. Builds the urls by the given template
3. Downloads the images and descriptions from the built urls 

# Note
As mentioned above, we assume that the urls of the images and descriptions are built by a certain template.  
If the template ever changes (and you start getting errors for example)  
just let us know and we will change it accordingly :)  
Feel free to use the issues tab for that.


# Finally
We hope this script will allow researchers who had similliar difficulties
accessing ISIC's Archive to have easier access and enable them to provide further work on this field,
as the ISIC foundation wishes :)

If you stumble into any issues - let us know in the issues section!

In addition, Any contributions or improvement ideas to our code that will improve the comfort of the users 
will be dearly appreciated :)


# Written By
Oren Talmor & Gal Avineri


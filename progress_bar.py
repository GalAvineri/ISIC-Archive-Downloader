import os
import time
import progressbar


def progress_bar(target, dir):
    """
    Will print a progress bar of the images downloading.
    The progress bar will contain the number of images that have been downloaded so far
    next to the number of images in the data set.

    The progress bar will be updated every second

    :param target: The number of elements that should finally be in the directory
    :param dir: The directory into which items will be downloaded
    """

    with progressbar.ProgressBar(max_value=target) as bar:
        num_elems_cur = len(os.listdir(dir))
        while num_elems_cur < target:
            bar.update(num_elems_cur)
            time.sleep(5)
            num_elems_cur = len(os.listdir(dir))

import cv2
import numpy as np
import Quartz


# Function to retrieve a list of all windows with their titles
def get_screen_window_list():
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    return Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)


# Function to get a window with a specific title
def get_screen_window_with_title(title):
    for window in get_screen_window_list():
        # need to improve, currently only capture one window
        owner_name = window.get('kCGWindowOwnerName', 'No title')
        if owner_name == title:
            return window
    return None


# Function to capture the screen of a given window
def get_screen_image(window):
    window_id = window['kCGWindowNumber']
    core_graphics_image = Quartz.CGWindowListCreateImage(
        Quartz.CGRectNull,
        Quartz.kCGWindowListOptionIncludingWindow,
        window_id,
        Quartz.kCGWindowImageDefault
    )
    bytes_per_row = Quartz.CGImageGetBytesPerRow(core_graphics_image)
    width = Quartz.CGImageGetWidth(core_graphics_image)
    height = Quartz.CGImageGetHeight(core_graphics_image)
    core_graphics_data_provider = Quartz.CGImageGetDataProvider(core_graphics_image)
    core_graphics_data = Quartz.CGDataProviderCopyData(core_graphics_data_provider)
    np_raw_data = np.frombuffer(core_graphics_data, dtype=np.uint8)
    numpy_data = np.lib.stride_tricks.as_strided(np_raw_data,
                                                 shape=(height, width, 3),
                                                 strides=(bytes_per_row, 4, 1),
                                                 writeable=False)
    return np.ascontiguousarray(numpy_data, dtype=np.uint8)


def is_screen_window_change(img1, img2, threshold=0.99):
    if img1 is None:
        return True
    # Ensure images have the same size and number of channels
    if img1.shape != img2.shape:
        return True

    # Calculate difference between the two images
    diff = cv2.absdiff(img1, img2)
    diff_norm = cv2.norm(diff, cv2.NORM_L2)

    # Calculate similarity
    similarity = 1 - (diff_norm / (img1.shape[0] * img1.shape[1] * img1.shape[2]))

    # If similarity exceeds threshold, consider them almost similar
    if similarity >= threshold:
        return False
    else:
        return True
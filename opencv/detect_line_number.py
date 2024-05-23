import cv2

from collections import defaultdict
import pytesseract as tess



def get_number_position_from_image(image):
    # Binarize the image
    avg_pixel_value = image.mean()
    if avg_pixel_value < 127:
        ret, binary = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY)
    else:
        ret, binary = cv2.threshold(image, 205, 255, cv2.THRESH_BINARY)
    binary = cv2.GaussianBlur(binary, (3, 3), 0)
    config = '--tessdata-dir ../tessdata --psm 6 -c tessedit_char_whitelist=0123456789 -c tessedit_create_boxfile=1'
    return tess.image_to_boxes(binary, lang='eng-fast', config=config)


def remove_line_number(image):
    # Get the dimensions of the image
    hImg, wImg, _ = image.shape

    # Get the position information of the numbers
    data = get_number_position_from_image(image)

    # Group the rectangle data by the x-coordinate of the center point
    rectangles_by_center = defaultdict(list)
    positions_removed = []
    for box in data.splitlines():
        box = box.split()
        if box[0] == '~' or int(box[3]) - int(box[1]) > 50:
            continue
        x, y, w, h = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        p1 = (x, hImg - y)
        p2 = (w, hImg - h)
        positions_removed.append((p1, p2))
        center_x, _ = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        key = round(center_x)
        rectangles_by_center[key].append((p1, p2))
    # Remove numbers area that meet the criteria
    for center_x, rectangles_in_group in rectangles_by_center.items():
        # Line number area is always at the left of the code, that's why I used 1/10
        if len(rectangles_in_group) >= 4 and center_x / wImg < 1 / 10:
            #left_boundary = min(rectangle[0][0] for rectangle in rectangles_in_group)
            right_boundary = max(rectangle[1][0] for rectangle in rectangles_in_group)
            # Cover the number area with average pixel value
            image[:, 0:right_boundary] = image.mean()
    return image, positions_removed
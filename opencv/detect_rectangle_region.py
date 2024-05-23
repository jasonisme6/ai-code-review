import cv2
import numpy as np


# Function to calculate the area of a rectangle
def area(rect):
    return rect[2] * rect[3]


# Function to check if two rectangles are similar within a threshold
def is_similar(rect1, rect2, threshold=15):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return abs(x1 - x2) <= threshold and \
        abs(y1 - y2) <= threshold and \
        abs(w1 - w2) <= threshold and \
        abs(h1 - h2) <= threshold


# Function to check if one rectangle is inside another
def is_contained(small, big):
    return (small[0] >= big[0] and small[1] >= big[1] and
            small[2] <= big[2] and
            small[3] <= big[3])


def is_intersect(small, big):
    x1, y1, x2, y2 = small  # Coordinates of the first rectangle
    x3, y3, x4, y4 = big  # Coordinates of the second rectangle
    area_small = (x2 - x1) * (y2 - y1)
    # Check if there is horizontal overlap
    horizontal_overlap = max(x1, x3) < min(x2, x4)
    # Check if there is vertical overlap
    vertical_overlap = max(y1, y3) < min(y2, y4)
    # If there is both horizontal and vertical overlap, then the rectangles intersect
    if horizontal_overlap and vertical_overlap:
        # Calculate the area of intersection
        intersection_width = min(x2, x4) - max(x1, x3)
        intersection_height = min(y2, y4) - max(y1, y3)
        intersection_area = intersection_width * intersection_height
        if intersection_area / area_small > 1 / 3:
            return True
    return False


# Function to detect regions in an image
def detect_region(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 5, 2)

    # Define kernel for dilation (you can adjust the size according to your requirement)
    kernel = np.ones((3, 3), np.uint8)

    # Apply dilation
    binary_dilated = cv2.dilate(binary, kernel, iterations=1)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    # Get image dimensions and calculate the image area
    img_h = image.shape[0]
    img_w = image.shape[1]

    # Extract potential rectangles from the contours
    rectangles = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Filter out small rectangles and rectangles covering most of the image
        if w / img_w > 1 / 5 and h / img_h > 1 / 27:
            rectangles.append((x, y, x + w, y + h))

    rectangles_remain = []
    skip_index_set = set()

    # Merge similar rectangles
    for i, item1 in enumerate(rectangles):
        if i in skip_index_set:
            continue
        tmp_rectangle = rectangles[i]
        for j, item2 in enumerate(rectangles[i + 1:], start=i + 1):
            if j in skip_index_set:
                continue
            if is_similar(tmp_rectangle, rectangles[j]):
                skip_index_set.add(j)
                if area(tmp_rectangle) < area(rectangles[j]):
                    tmp_rectangle = rectangles[j]
        rectangles_remain.append(tmp_rectangle)
    rectangles = rectangles_remain

    # Sort rectangles by area from smallest to largest
    rectangles.sort(key=lambda rect: (rect[2] - rect[0]) * (rect[3] - rect[1]))

    # List to hold the final set of rectangles
    final_rectangles = []

    # Iterate over the sorted list of rectangles
    for current_rect in rectangles:
        # Assume the current rectangle is not contained by any other rectangle
        contained_or_intersected = False

        #Check if the current rectangle contains any of the previously added rectangles
        for rect in final_rectangles:
            if is_contained(rect, current_rect):
                # If the current rectangle contains another, it will be skipped
                contained_or_intersected = True
                break

        # If the current rectangle does not contain any other rectangle, add it to the final list
        if not contained_or_intersected:
            final_rectangles.append(current_rect)

    rectangles = final_rectangles
    region_list = []
    # Draw bounding rectangles on the image
    for (x1, y1, x2, y2) in rectangles:
        region_list.append(((x1, y1), (x2, y2), (x2-x1) * (y2-y1)))

    if len(region_list) == 0:
        region_list.append(((0, 0), (img_w, img_h), img_w * img_h))

    return region_list

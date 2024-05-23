import cv2
import numpy as np

horizontal_area_templates = ['../symbol/symbol1.jpg', '../symbol/symbol2.jpg',
                             '../symbol/symbol3.jpg', '../symbol/symbol4.jpg']
horizontal_area_images = [cv2.imread(url, 0) for url in horizontal_area_templates]


def remove_the_detected_horizontal_area(image):
    positions_removed = []
    for template in horizontal_area_images:
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        template_h, template_w = template.shape[:2]
        img_h, img_w = image.shape[:2]
        # If template is bigger, stop the match
        if img_h < template_h or img_w < template_w:
            return image, positions_removed
        template_h, template_w = template.shape[:2]
        # Match the template and find out the position
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.85
        loc = np.nonzero(res >= threshold)
        for top_left in zip(*loc[::-1]):
            bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
            image[top_left[1]:bottom_right[1], :] = image[top_left[1]][0]
            positions_removed.append((top_left, bottom_right))
    return image, positions_removed


rectangle_area_templates = ['../symbol/symbol5.jpg', '../symbol/symbol6.jpg',
                            '../symbol/symbol7.jpg', '../symbol/symbol8.jpg',
                            '../symbol/symbol9.jpg', '../symbol/symbol13.jpg']
rectangle_area_images = [cv2.imread(url, 0) for url in rectangle_area_templates]


def remove_the_detected_rectangle_area(image):
    positions_removed = []
    for template in rectangle_area_images:
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        template_h, template_w = template.shape[:2]
        img_h, img_w = image.shape[:2]
        # If template is bigger, stop the match
        if img_h < template_h or img_w < template_w:
            return image, positions_removed
        template_h, template_w = template.shape[:2]
        # Match the template and find out the position
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.85
        loc = np.nonzero(res >= threshold)
        for top_left in zip(*loc[::-1]):
            bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
            image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = image[top_left[1]][top_left[0]]
            positions_removed.append((top_left, bottom_right))
    return image, positions_removed


partial_horizontal_area_templates = ['../symbol/symbol10.jpg', '../symbol/symbol11.jpg', '../symbol/symbol12.jpg']
partial_horizontal_area_images = [cv2.imread(url, 0) for url in partial_horizontal_area_templates]


def remove_the_detected_partial_horizontal_area(image):
    positions_removed = []
    for template in partial_horizontal_area_images:
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        template_h, template_w = template.shape[:2]
        img_h, img_w = image.shape[:2]
        # If template is bigger, stop the match
        if img_h < template_h or img_w < template_w:
            return image, positions_removed
        template_h, template_w = template.shape[:2]
        # Match the template and find out the position
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.nonzero(res >= threshold)
        for top_left in zip(*loc[::-1]):
            bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
            image[top_left[1]:bottom_right[1], top_left[0]:] = image[top_left[1]][0]
            positions_removed.append((top_left, bottom_right))
    return image, positions_removed
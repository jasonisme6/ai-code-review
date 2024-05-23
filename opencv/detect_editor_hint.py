import cv2
import numpy as np
import pytesseract as tess

hint_image_start_1_template = cv2.imread('../hint/hint_start_1.jpg', 0)

hint_image_start_2_template = cv2.imread('../hint/hint_start_2.jpg', 0)

hint_image_end_template = cv2.imread('../hint/hint_end.jpg', 0)


def get_text_from_image(image):
    binary = cv2.GaussianBlur(image, (3, 3), 0)
    config = '--tessdata-dir ../tessdata --psm 6'
    return tess.image_to_string(binary, lang='eng-best', config=config)

# Function to calculate the area of a rectangle
def area(rect):
    return rect[2] * rect[3]


# Function to check if two rectangles are similar within a threshold
def is_similar(rect1, rect2, threshold=5):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return abs(x1 - x2) <= threshold and \
        abs(y1 - y2) <= threshold and \
        abs(w1 - w2) <= threshold and \
        abs(h1 - h2) <= threshold


def remove_similar_rectangle(rectangles):
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
    return rectangles_remain


def get_detected_hint_area_for_code_snippet(image, image_template):
    hints_edge_detected = []
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_h, template_w = image_template.shape[:2]
    img_h, img_w = image.shape[:2]
    # If template is bigger, stop the match
    if img_h < template_h or img_w < template_w:
        return image, []
    # Match the template and find out the position
    res = cv2.matchTemplate(img_gray, image_template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.nonzero(res >= threshold)
    for top_left in zip(*loc[::-1]):
        bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
        hints_edge_detected.append((top_left[0], top_left[1], bottom_right[0], bottom_right[1]))
    # Remove similar rectangles
    hints_edge_detected = remove_similar_rectangle(hints_edge_detected)
    # Hints in one line is in the same group
    grouped_hints_detected = []
    for rect in hints_edge_detected:
        group_found = False
        for group in grouped_hints_detected:
            # Calculate the center of rect1
            center1_y = (rect[1] + rect[3]) / 2
            # Calculate the center of the first rectangle in the group
            center2_y = (group[0][1] + group[0][3]) / 2
            # Check if the center of rect1 is close to the center of the first rectangle in the group
            if abs(center1_y - center2_y) <= 10:
                group.append(rect)
                group_found = True
                break
        if not group_found:
            grouped_hints_detected.append([rect])
    grouped_hints_detected.sort(key=lambda element: (element[0][1] + element[0][3]) / 2)
    return image, grouped_hints_detected


# Function to detect code hint in a code area
def detect_the_code_hint_area(image):
    position_removed = []
    # Get the end of code hints of the code snippet
    image, grouped_hints_end_detected = get_detected_hint_area_for_code_snippet(image, hint_image_end_template)
    if len(grouped_hints_end_detected) == 0:
        return image, position_removed, [], []
    # Get the start 1 of code hints of the code snippet
    image, grouped_hints_start_1_detected = get_detected_hint_area_for_code_snippet(image, hint_image_start_1_template)
    # Get the start 2 of code hints of the code snippet
    image, grouped_hints_start_2_detected = get_detected_hint_area_for_code_snippet(image, hint_image_start_2_template)
    hint_code_for_each_line = []
    hint_num_for_each_line = []
    # Find out the start hints in each line, also match the start and end
    for hint_end_group in grouped_hints_end_detected:
        code = get_text_from_image(image[hint_end_group[0][1]:hint_end_group[0][3], :])
        hint_code = code.strip().replace(" ", "").replace("_", "").replace("%", "").replace("*", "")
        hint_code_for_each_line.append(hint_code)
        hint_num_for_each_line.append(len(hint_end_group))
        # sort it by position
        hint_end_group = sorted(hint_end_group, key=lambda rect: rect[0])
        number_of_hint_end = len(hint_end_group)
        hints_start_detected = []
        y1 = hint_end_group[0][1]
        y2 = hint_end_group[0][3]
        end_center_height = (y2 + y1)/2
        # get start 1 hints in the same line
        for hint_start_1_group in grouped_hints_start_1_detected:
            y1 = hint_start_1_group[0][1]
            y2 = hint_start_1_group[0][3]
            start_1_center_height = (y2 + y1) / 2
            # use height to judge whether it is in one line
            if abs(end_center_height - start_1_center_height) < 10:
                hints_start_detected.extend(hint_start_1_group)
        # get start 2 hints in the same line
        for hint_start_2_group in grouped_hints_start_2_detected:
            y1 = hint_start_2_group[0][1]
            y2 = hint_start_2_group[0][3]
            start_2_center_height = (y2 + y1) / 2
            # use height to judge whether it is in one line
            if abs(end_center_height - start_2_center_height) < 10:
                hints_start_detected.extend(hint_start_2_group)
        # If start and end hint number not matched, then skip and continue for next line
        if len(hints_start_detected) != number_of_hint_end:
            continue
        for hint_start_position in hints_start_detected:
            hint_x1 = hint_start_position[0]
            hint_y1 = hint_start_position[1]
            hint_x2 = hint_start_position[2]
            middle_hint_x = (hint_x1 + hint_x2)/2
            # Find out the corresponding nearest end hint
            nearest_end_hint_list = [rect for rect in hint_end_group if rect[0] > hint_x2]
            if len(nearest_end_hint_list) == 0:
                continue
            nearest_end_hint = nearest_end_hint_list[0]
            final_hint_x1 = int(middle_hint_x)
            final_hint_y1 = int(hint_y1)
            final_hint_x2 = int(nearest_end_hint[2])
            final_hint_y2 = int(nearest_end_hint[3])
            position_removed.append(((final_hint_x1+2, final_hint_y1-2), (final_hint_x2+2, final_hint_y2)))
    return image, position_removed, hint_code_for_each_line, hint_num_for_each_line

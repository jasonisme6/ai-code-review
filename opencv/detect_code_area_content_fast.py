import time

import cv2

import pytesseract as tess
from opencv.detect_code_area import check_text_is_code_or_not
from opencv.detect_code_content import add_indentation_to_detected_code, optimize_code_ocr_result
from opencv.detect_editor_hint import get_detected_hint_area_for_code_snippet, \
    hint_image_end_template, hint_image_start_1_template, hint_image_start_2_template
from opencv.detect_editor_symbol import remove_the_detected_horizontal_area, remove_the_detected_rectangle_area, \
    remove_the_detected_partial_horizontal_area
from opencv.detect_line_number import remove_line_number

from concurrent.futures import ThreadPoolExecutor, as_completed

def get_text_from_image_hint(image):
    binary = cv2.GaussianBlur(image, (3, 3), 0)
    config = '--tessdata-dir ../tessdata --psm 6'
    return tess.image_to_string(binary, lang='eng-fast', config=config)

def get_text_from_image(image):
    binary = cv2.GaussianBlur(image, (3, 3), 0)
    config = '--tessdata-dir ../tessdata --psm 6'
    return tess.image_to_string(binary, lang='eng-best', config=config)


def get_character_from_image(image):
    binary = cv2.GaussianBlur(image, (3, 3), 0)
    config = '--tessdata-dir ../tessdata --psm 6 -c tessedit_create_boxfile=1'
    return tess.image_to_boxes(binary, lang='eng-best', config=config)


def process_region(image, region):
    x1, y1 = region[0]
    x2, y2 = region[1]
    cropped_img = image[y1:y2, x1:x2].copy()
    time1 = time.time()
    cropped_img, _ = remove_the_detected_horizontal_area(cropped_img)
    time2 = time.time()
    print("remove_the_detected_horizontal_area time:" + str(time2-time1))
    cropped_img, _ = remove_the_detected_rectangle_area(cropped_img)
    time3 = time.time()
    print("remove_the_detected_rectangle_area time:" + str(time3-time2))
    cropped_img, _ = remove_the_detected_partial_horizontal_area(cropped_img)
    time4 = time.time()
    print("remove_the_detected_partial_horizontal_area time:" + str(time4-time3))
    cropped_img, _ = remove_line_number(cropped_img)
    time5 = time.time()
    print("remove_line_number time:" + str(time5-time4))
    raw_code_result = get_text_from_image(cropped_img)
    time6 = time.time()
    print("get_text_from_image time:" + str(time6-time5))
    if raw_code_result is None or raw_code_result == "" or check_text_is_code_or_not(raw_code_result) is False:
        return None, None, None
    p1 = region[0]
    p2 = region[1]
    code_region = (p1, p2, region[2])
    cropped_img, _, code_hint_set = detect_the_code_hint_area_fast(cropped_img)
    time7 = time.time()
    print("detect_the_code_hint_area_fast time:" + str(time7-time6))
    boxes = get_character_from_image(cropped_img)
    time8 = time.time()
    print("get_character_from_image time:" + str(time8-time7))
    code_with_space, code_line_position, max_end_position, max_line_length \
        = add_indentation_to_detected_code(cropped_img, raw_code_result, boxes)
    time9 = time.time()
    print("add_indentation_to_detected_code time:" + str(time9-time8))
    revised_code_result = post_process_code_fast(image, region, code_with_space, max_end_position, max_line_length,
                                                 code_line_position, code_hint_set)
    time10 = time.time()
    print("post_process_code_fast time:" + str(time10-time9))
    return code_region, raw_code_result, revised_code_result


def get_code_area_and_content(image, region_list):
    code_region_list = []
    code_list = []
    final_code = ''
    original_code = ''
    time1 = time.time()
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_region, image, region) for region in region_list]
        for future in as_completed(futures):
            code_region, raw_code_result, revised_code_result = future.result()
            if code_region and raw_code_result and revised_code_result:
                code_region_list.append(code_region)
                code_list.append(revised_code_result)
                final_code += revised_code_result
                original_code += raw_code_result
    time2 = time.time()
    print("get_code_area_and_content time:" + str(time2-time1))
    return code_region_list, code_list, final_code, original_code


def post_process_code_fast(image, region, code_with_space, max_end_position, max_line_length, code_line_position,
                           code_hint_set):
    x1, y1 = region[0]
    previous_line = ''
    bracket_flag = False
    code_result = ''
    for i, line in enumerate(code_with_space.splitlines()):
        if not line.strip():
            continue
        if "{" in line or "}" in line:
            bracket_flag = True
        line = optimize_code_ocr_result(line, previous_line, bracket_flag)
        for code_hint in code_hint_set:
            if code_hint in line:
                line = line.replace(code_hint, "")
        # remove the hint of the editor
        if len(line.strip()) > 0 and line.strip()[0].isdigit() and " usage" in line:
            continue
        previous_line = line
        strip_flag = False
        if (x1 + max_end_position + max_line_length) > image.shape[1]:
            strip_flag = True
            x = code_line_position[i][0] + x1 + 2
        else:
            x = max_end_position + x1 + 2
        y = code_line_position[i][1] + y1
        code_result += line + '\n'
        if strip_flag is True:
            line = line.strip()
        cv2.putText(image, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, 1)
    return code_result


def process_hint_start_position(hint_start_position, hint_end_group, image):
    hint_x1 = hint_start_position[0]
    hint_y1 = hint_start_position[1]
    hint_x2 = hint_start_position[2]
    middle_hint_x = (hint_x1 + hint_x2) / 2
    # Find out the corresponding nearest end hint
    nearest_end_hint_list = [rect for rect in hint_end_group if rect[0] > hint_x2]
    if len(nearest_end_hint_list) == 0:
        return None, None

    nearest_end_hint = nearest_end_hint_list[0]
    final_hint_x1 = int(middle_hint_x)
    final_hint_y1 = int(hint_y1)
    final_hint_x2 = int(nearest_end_hint[2])
    final_hint_y2 = int(nearest_end_hint[3])

    hint_code = get_text_from_image_hint(image[final_hint_y1 - 2:final_hint_y2, final_hint_x1 + 2:final_hint_x2 + 2])
    code_variants = {
        hint_code.strip(),
        hint_code.strip().replace("_", ""),
        hint_code.strip().replace("_", " "),
        hint_code.strip().replace("_", ".")
    }
    position = ((final_hint_x1 + 2, final_hint_y1 - 2), (final_hint_x2 + 2, final_hint_y2))
    return code_variants, position


def detect_the_code_hint_area_fast(image):
    position_removed = []
    code_removed = set()
    # Get the end of code hints of the code snippet
    image, grouped_hints_end_detected = get_detected_hint_area_for_code_snippet(image, hint_image_end_template)
    if len(grouped_hints_end_detected) == 0:
        return image, position_removed, code_removed
    # Get the start 1 of code hints of the code snippet
    image, grouped_hints_start_1_detected = get_detected_hint_area_for_code_snippet(image, hint_image_start_1_template)
    # Get the start 2 of code hints of the code snippet
    image, grouped_hints_start_2_detected = get_detected_hint_area_for_code_snippet(image, hint_image_start_2_template)
    # Find out the start hints in each line, also match the start and end
    for hint_end_group in grouped_hints_end_detected:
        # sort it by position
        hint_end_group = sorted(hint_end_group, key=lambda rect: rect[0])
        number_of_hint_end = len(hint_end_group)
        hints_start_detected = []
        y1 = hint_end_group[0][1]
        y2 = hint_end_group[0][3]
        end_center_height = (y2 + y1) / 2
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
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_hint_start_position, hint_start_position, hint_end_group, image)
                for hint_start_position in hints_start_detected
            ]
            for future in as_completed(futures):
                code_variants, position = future.result()
                if code_variants and position:
                    code_removed.update(code_variants)
                    position_removed.append(position)
    return image, position_removed, code_removed

import time

import cv2

from opencv.detect_code_area_content_fast import get_code_area_and_content
from opencv.detect_rectangle_region import detect_region


def find_source_code_url(url):
    # Find the index of the last slash
    last_slash_index = url.rfind('/')

    # Find the index where the filename starts
    filename_start_index = last_slash_index + 1

    # Find the index where the filename ends
    filename_end_index = url.rfind('.')

    # Extract the filename and file extension
    filename = url[filename_start_index:filename_end_index]

    # Build the new filename by adding "_result" and then adding back the extension
    source_filename = filename + "_source" + ".txt"
    # Replace the filename in the original URL with the new filename
    source_code_url = url[:filename_start_index] + source_filename
    return source_code_url


def add_result_to_image_filename(url):
    # Find the index of the last slash
    last_slash_index = url.rfind('/')

    # Find the index where the filename starts
    filename_start_index = last_slash_index + 1

    # Find the index where the filename ends
    filename_end_index = url.rfind('.')

    # Extract the filename and file extension
    filename = url[filename_start_index:filename_end_index]
    extension = url[filename_end_index:]

    # Build the new filename by adding "_result" and then adding back the extension
    new_image_filename = filename + "_result" + extension
    new_text_filename = filename + "_result" + ".txt"
    # Replace the filename in the original URL with the new filename
    new_image_url = url[:filename_start_index] + new_image_filename
    new_txt_url = url[:filename_start_index] + new_text_filename
    return new_image_url, new_txt_url


def clean_line(line):
    # Remove all spaces and strip the line.
    return line.replace(" ", "").strip()


def calculate_accuracy(file_path, code):
    # Compare file content and text at character level after cleaning lines.
    with open(file_path, 'r', encoding='utf-8') as file:
        file_lines = [line.strip() for line in file if line.strip()
                      and line.strip() != '"""']
    code_lines = [line.strip() for line in code.splitlines() if line.strip()]
    min_length = min(len(file_lines), len(code_lines))
    if len(file_lines) != len(code_lines):
        print("not accurate, file_lines length is " + str(len(file_lines)) + ", code_lines length is "
              + str(len(code_lines)))
    total_chars = 0
    matches = 0
    for index, file_line in enumerate(file_lines):
        if index == min_length:
            break
        code_line = code_lines[index]
        file_line_without_space = file_line.replace(" ", "")
        code_line_without_space = code_line.replace(" ", "")
        match_number = sum(1 for i in range(min(len(file_line_without_space), len(code_line_without_space)))
                           if file_line_without_space[i] == code_line_without_space[i])
        matches += match_number
        if match_number != min(len(file_line_without_space), len(code_line_without_space)):
            print("source_line: " + file_line)
            print("result_line: " + code_line)
        total_chars += min(len(file_line_without_space), len(code_line_without_space))
    accuracy = (matches / total_chars) * 100 if total_chars > 0 else 0
    return accuracy


# # test_code code area and show code
if __name__ == "__main__":
    start_time = time.time()
    url = "../test_image/editor/pycharm/pycharm_code_1.jpg"
    image = cv2.imread(url)
    region_list = detect_region(image)
    code_region_list, _, final_code, original_code = get_code_area_and_content(image, region_list)
    # for code_region in code_region_list:
    #      cv2.rectangle(image, code_region[0], code_region[1], (0, 255, 0), 2)
    new_image_url, new_txt_url = add_result_to_image_filename(url)
    end_time = time.time()
    total_time = end_time - start_time
    print("total execution time is " + str(total_time) + "s")
    # Need source code file to check accuracy, if no source code file than set enable_accuracy to False
    enable_accuracy = False
    if enable_accuracy is True:
        source_code_url = find_source_code_url(url)
        original_accuracy = calculate_accuracy(source_code_url, original_code)
        print("accuracy before postprocessing is " + str(original_accuracy))
        preprocessing_accuracy = calculate_accuracy(source_code_url, final_code)
        print("accuracy after postprocessing is " + str(preprocessing_accuracy))
    print(final_code)
    cv2.imwrite(new_image_url, image)
    with open(new_txt_url, 'w') as file:
        file.write(final_code)

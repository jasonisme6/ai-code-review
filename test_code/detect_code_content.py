import cv2

from opencv.detect_code_area import remove_non_code_area
from opencv.detect_code_content import get_code_content_with_space_for_image
from opencv.detect_rectangle_region import detect_region

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


# # test_code code area and show code
if __name__ == "__main__":
    url = "../test_image/editor/idea/idea_code_1.jpg"
    image = cv2.imread(url)
    region_list = detect_region(image)
    code_region_list = remove_non_code_area(image, region_list)
    image, code, _ = get_code_content_with_space_for_image(image, code_region_list)
    new_image_url, new_txt_url = add_result_to_image_filename(url)
    cv2.imwrite(new_image_url, image)
    with open(new_txt_url, 'w') as file:
        file.write(code)

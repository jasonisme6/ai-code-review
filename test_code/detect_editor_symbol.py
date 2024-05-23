import cv2
import numpy as np

from opencv.detect_code_area_content_fast import get_character_from_image
from opencv.detect_editor_symbol import remove_the_detected_horizontal_area, remove_the_detected_rectangle_area, \
    remove_the_detected_partial_horizontal_area

# remove editor symbol
if __name__ == "__main__":
    image = cv2.imread("../test_image/blog/blog_code_1.jpg")[242:2024, 1138:2010]
    image = cv2.GaussianBlur(image, (3, 3), 0)

    # image, positions_removed_horizontal = remove_the_detected_horizontal_area(image)
    # image, positions_removed_rectangle = remove_the_detected_rectangle_area(image)
    # image, positions_removed_partial_rectangle = remove_the_detected_partial_horizontal_area(image)
    # boxes = get_character_from_image(image)
    # line_box_array = boxes.splitlines()
    # hImg = image.shape[0]
    # for index in range(len(line_box_array)):
    #     box = line_box_array[index].split()
    #     x, y, w, h = int(box[1]), int(box[2]), int(box[3]), int(box[4])
    #     p1 = (x, hImg - y)
    #     p2 = (w, hImg - h)
    #     cv2.rectangle(image, p1, p2, (0, 0, 255), 3)
    # for position in positions_removed_horizontal:
    #     cv2.rectangle(image, position[0], position[1], (0, 0, 255), 3)
    # for position in positions_removed_rectangle:
    #     cv2.rectangle(image, position[0], position[1], (0, 0, 255), 3)
    # for position in positions_removed_partial_rectangle:
    #     cv2.rectangle(image, position[0], position[1], (0, 0, 255), 3)
    cv2.imshow('123', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
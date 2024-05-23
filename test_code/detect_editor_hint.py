import cv2

from opencv.detect_editor_hint import detect_the_code_hint_area

# remove editor code hint
if __name__ == "__main__":
    image = cv2.imread('../test_image/editor/pycharm/pycharm_code_1.jpg')
    image, position_removed, hint_code_for_each_line, hint_num_for_each_line = detect_the_code_hint_area(image)
    for position in position_removed:
        cv2.rectangle(image, position[0], position[1], (0, 0, 255), 3)
    cv2.imshow('123', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

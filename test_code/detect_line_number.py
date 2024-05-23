import cv2
import numpy as np

from opencv.detect_line_number import remove_line_number

# remove line number
if __name__ == "__main__":
    image = cv2.imread("../test_image/github/go/go_code_1.jpg")
    image = image[480:2140, 979:2006]
    new_image, positions_removed = remove_line_number(image)
    #for position in positions_removed:
        #cv2.rectangle(image, position[0], position[1], (0, 0, 255), 2)
    cv2.imshow('123', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
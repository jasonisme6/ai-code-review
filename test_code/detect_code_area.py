import cv2

from opencv.detect_code_area import remove_non_code_area
from opencv.detect_rectangle_region import detect_region


# test_code locate code area
if __name__ == "__main__":
    image = cv2.imread("../test_image/blog/blog_code_1.jpg")
    region_list = detect_region(image)
    code_region_list = remove_non_code_area(image, region_list)
    for region in code_region_list:
        cv2.rectangle(image, region[0], region[1], (0, 255, 0), 2)
    cv2.imshow('123', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

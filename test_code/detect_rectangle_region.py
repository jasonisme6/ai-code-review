from paddle.dataset.image import cv2

from opencv.detect_rectangle_region import detect_region

# detect rectangle regions(including code blocks)
if __name__ == "__main__":
    image = cv2.imread("/Users/minghao/Desktop/CV-Project-Fast/test_code/img.png")
    region_list = detect_region(image)
    for region in region_list:
        cv2.rectangle(image, region[0], region[1], (0, 0, 255), 5)
    cv2.imshow('123', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
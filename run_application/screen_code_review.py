import time

import cv2
import numpy as np

from gpt.gpt_review_code import start_gpt_review_code
from opencv.detect_code_area_content_fast import get_code_area_and_content
from opencv.detect_mac_screen import get_screen_window_with_title, get_screen_image, is_screen_window_change
from opencv.detect_rectangle_region import detect_region



def draw_code_and_review(code_list, gpt_answer, gpt_image):
    # Set the initial position for text
    x = 10
    y = 30
    line_height = 40
    for i, code_snippet in enumerate(code_list):
        cv2.putText(gpt_image, f"### Code Block {i + 1}:", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        y += line_height
        lines = code_snippet.splitlines()
        for line in lines:
            cv2.putText(gpt_image, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            y += line_height
        # Draw each line of text on the image
    for line in gpt_answer.splitlines():
        if '. ' in line:
            sentences = line.split('. ')
            for sentence in sentences:
                if sentence.strip().isdigit():
                    continue
                cv2.putText(gpt_image, sentence, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                y += line_height
        else:
            cv2.putText(gpt_image, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            y += line_height


def show_screen_with_code_region(target_window_title, enable_gpt):
    global original_show_image
    global show_image
    global gpt_image
    global already_detected
    global code_list
    global code_region_list
    window = get_screen_window_with_title(target_window_title)
    if window:
        cv2.namedWindow(target_window_title)
        old_image = None
        gpt_image = None
        while True:
            window_image = get_screen_image(window)
            new_image = cv2.cvtColor(window_image, cv2.COLOR_RGBA2RGB)
            if is_screen_window_change(old_image, new_image):
                old_image = new_image
                region_list = detect_region(new_image)
                code_region_list, code_list, final_code, original_code = get_code_area_and_content(new_image, region_list)
                show_image = new_image.copy()
                for code_region in code_region_list:
                    cv2.rectangle(show_image, code_region[0], code_region[1], (0, 255, 0), 2)
                height = show_image.shape[0]
                width = show_image.shape[1]
                gpt_image = np.full((height, width, 3), (255, 255, 255), dtype=np.uint8)
                time1 = time.time()
                if enable_gpt is True:
                    gpt_answer = start_gpt_review_code(code_list)
                else:
                    gpt_answer = ""
                time2 = time.time()
                print("start_gpt_review_code time:" + str(time2 - time1))
                draw_code_and_review(code_list, gpt_answer, gpt_image)
                time3 = time.time()
                print("draw_code_and_review time:" + str(time3 - time2))
                original_show_image = show_image.copy()
                already_detected = False
                # for non_code_region in region_list:
                #     if non_code_region not in code_region_list:
                #         cv2.rectangle(show_image, non_code_region[0], non_code_region[1], (0, 0, 255), 1)
            cv2.imshow('GPT Code review', gpt_image)
            cv2.imshow('Mac Screen Capture', show_image)
            key = cv2.waitKey(25)
            if key & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break



if __name__ == "__main__":
    # Replace 'target_window_title' with the title of the window you're looking for
    target_window_title = "Google Chrome"
    #target_window_title = "PyCharm"
    #target_window_title = "Safari"
    #target_window_title = "IntelliJ IDEA"
    enable_gpt = True
    show_screen_with_code_region(target_window_title, enable_gpt)

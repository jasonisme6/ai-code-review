
import cv2
import numpy as np

from gpt.gpt_review_code import start_gpt_review_code
from opencv.detect_code_area import remove_non_code_area
from opencv.detect_code_content import get_code_content_with_space_for_screen
from opencv.detect_mac_screen import get_screen_window_with_title, get_screen_image, is_screen_window_change
from opencv.detect_rectangle_region import detect_region

original_show_image = None
show_image = None
gpt_image = None
already_detected = True
code_list = []
code_region_list = []
text_window = None

def draw_code_and_review(code_list, gpt_answer):
    global gpt_image
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
        while True:
            window_image = get_screen_image(window)
            new_image = cv2.cvtColor(window_image, cv2.COLOR_RGBA2RGB)
            if is_screen_window_change(old_image, new_image):
                code_list = []
                old_image = new_image
                region_list = detect_region(new_image)
                show_image = new_image.copy()
                code_region_list = remove_non_code_area(new_image, region_list)
                for code_region in code_region_list:
                    cv2.rectangle(show_image, code_region[0], code_region[1], (0, 255, 0), 2)
                original_show_image = show_image.copy()
                height = show_image.shape[0]
                width = show_image.shape[1]
                gpt_image = np.full((height, width, 3), (255, 255, 255), dtype=np.uint8)
                already_detected = False
                # for non_code_region in region_list:
                #     if non_code_region not in code_region_list:
                #         cv2.rectangle(show_image, non_code_region[0], non_code_region[1], (0, 0, 255), 1)
            cv2.imshow('Mac Screen Capture', show_image)
            cv2.imshow('GPT Code review', gpt_image)
            key = cv2.waitKey(25)
            if key & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            elif key & 0xFF == ord('w'):
                cv2.destroyWindow('GPT Code review')
            elif key & 0xFF == ord(' '):  # Handle spacebar press
                if not already_detected:
                    print("start detection")
                    show_image, code_list = get_code_content_with_space_for_screen(show_image, code_region_list)
                    already_detected = True
                    # If it is true then enable gpt
                    if enable_gpt is True:
                        gpt_answer = start_gpt_review_code(code_list)
                        draw_code_and_review(code_list, gpt_answer)



if __name__ == "__main__":
    # Replace 'target_window_title' with the title of the window you're looking for
    #target_window_title = "Google Chrome"
    #target_window_title = "PyCharm"
    target_window_title = "Safari"
    #target_window_title = "IntelliJ IDEA"
    enable_gpt = True
    show_screen_with_code_region(target_window_title, enable_gpt)

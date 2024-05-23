# COSC428 Project
Name: Utilizing Computer Vision for AI Real-Time Code Review on Computer Screen \
Author: Minghao Li \
Modified: 04/05/2024

## Description:
This project presents a method for real-time AI code review on computer screen, including code region detection 
and classification, region image preprocessing, code content OCR and postprocessing, GPT code review. AI tools created 
from studies in this area are often integrated with Github or certain code editors, making them confined to specific 
programming language and dependent on other systems or platforms. This paper combines computer vision techniques with 
GPT to create a novel way for AI code review that is applicable to all programming languages and operates as a 
standalone application, unaffected by other systems.

And the project is developed in Python 3.7 using PyCharm with OpenCV 4.9.0.80. The processing time is about from 4 to 17 
seconds for each image depending on the code complexity. And it is capable for reviewing code with various programming 
languages from all kinds of websites or code editors.

## Project Structure
Main Functions is in the opencv folder \
Editor inlay hint templates is in the hint folder \
Editor symbol templates is in the symbol folder \
GPT api is in the gpt folder \
Tesseract traindata is in the tessdata folder\
The test data and result is in the test_image folder \
Code for testing main functions is under the test_code folder \
Code for starting the application is under the run_application folder. 

## Start Application
image_code_ocr is for image code ocr only, no code review function in it. \
screen_code_review is for only Mac live screen capture and code review. If you want to enable 
GPT, you need to use your own API_KEY and change the key in gpt_review_code.
you can also check the cv_demo.mp4 and cv_presentation.pptx for more information.
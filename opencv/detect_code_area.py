import cv2
import pytesseract as tess
from pygments.lexers import guess_lexer, ClassNotFound

def is_code(text):
    try:
        lexer = guess_lexer(text)
        print(lexer.name)
        return lexer.name not in ['Text only', 'Carbon', 'ECL', 'Tera Term macro', 'Brainfuck', 'CBM BASIC V2',
                                  'Transact-SQL', 'scdoc', 'verilog', 'GAS', 'Objective-C', 'World of Warcraft TOC',
                                  'GDScript', 'Maxima', 'CSS+Lasso']
    except ClassNotFound:
        return False

def get_text_from_image(image):
    binary = cv2.GaussianBlur(image, (3, 3), 0)
    config = '--tessdata-dir ../tessdata --psm 6'
    return tess.image_to_string(binary, lang='eng', config=config)


all_contain_symbol_list = [("def ", "(", "):"), ("interface ", "{"), ("(", ");"), ("for ", " in ", ":"),
                           ("public ", "{"), ("private ", "{"), ("if (", "{"), ("while (", "{"), ("for (", "{"),
                           ("fun ", "(", ") {"), ("implements ", "{"), ("function ", "{"), ("class ", "{"),
                           ("int ", "="), ("char ", "="), (" = ", "[0]"), (" = ", "[1]"), ("if ", ":"),
                           ("_", ".", "=", "(", ")"), " = '"]

single_contain_symbol_list = ["<h2>", " self.", "float(", "len(", "var ", "public static", "private static ",
                              " = null;", "this.", "super(", "else {", "catch (", "try {", " != ", " += ", "== ",
                              " = false;", "#include ", "List<", ".class", " = [", " = {", "print(", "printf(", "echo ",
                              " = true;", "String ", ".equals(", ".orElse(", " = None", " = False", " = True", " = []",
                              "<?php", "<h1>", "</tr>", "</form>", "<html>", "<body>", "</html>", "</body>", "</table>",
                              "</td>", "</script>", "</div>", "<title>", "</title>", "<!DOCTYPE html>", "<style>",
                              "</style>", "var ", "val ", "</head>", "<head>", " := ", "import (", "struct {", "func (",
                              "#include \"", "#include <", "#elif ", "#ifdef ", "unsigned ", "static void ",
                              "static int ", "static bool ", "const ", "instanceof ", ".append(", "is None ", "is True",
                              "import ", "@Override", "@Autowired", "else:", "return False", "return True", "break",
                              "continue", "throw e;", "cv2.", "global "]

start_with_symbol_list = ["# "]


def check_line_is_code_or_not(line):
    line = line.strip()
    for in_symbol in single_contain_symbol_list:
        if in_symbol in line:
            return True
    for in_symbol_tuple in all_contain_symbol_list:
        all_contain = True
        for in_symbol in in_symbol_tuple:
            if in_symbol not in line:
                all_contain = False
        if all_contain is True:
            return True
    for start_with_symbol in start_with_symbol_list:
        if line.startswith(start_with_symbol):
            return True
    return False


def check_text_is_code_or_not(text):
    lines = text.splitlines()
    code_line_count = 0
    for line in lines:
        if check_line_is_code_or_not(line) is True:
            code_line_count += 1
            if code_line_count >= 2:
                return True
    return is_code(text)


def remove_non_code_area(image, region_list):
    code_region_list = []
    skip_list = []
    for region in region_list:
        if region in skip_list:
            continue
        x1, y1 = region[0]
        x2, y2 = region[1]
        cropped_img = image[y1:y2, x1:x2].copy()
        text = get_text_from_image(cropped_img)
        if text is None or text == "":
            continue
        if check_text_is_code_or_not(text) is True:
            p1 = region[0]
            p2 = region[1]
            code_region_list.append((p1, p2, region[2]))
    return code_region_list

import cv2
import pytesseract as tess

from opencv.detect_editor_hint import detect_the_code_hint_area
from opencv.detect_editor_symbol import remove_the_detected_horizontal_area, remove_the_detected_rectangle_area, \
    remove_the_detected_partial_horizontal_area
from opencv.detect_line_number import remove_line_number


def get_text_from_image(image):
    binary = cv2.GaussianBlur(image, (3, 3), 0)
    config = '--tessdata-dir ../tessdata --psm 6'
    return tess.image_to_string(binary, lang='eng-best', config=config)


def get_character_from_image(image):
    binary = cv2.GaussianBlur(image, (3, 3), 0)
    config = '--tessdata-dir ../tessdata --psm 6 -c tessedit_create_boxfile=1'
    return tess.image_to_boxes(binary, lang='eng-best', config=config)


def add_indentation_to_detected_code(image, code, boxes):
    # Get the dimensions of the image
    hImg, wImg, _ = image.shape
    lines_without_space = [line.replace(" ", "") for line in code.splitlines()]
    line_indent = []
    line_box_array = boxes.splitlines()
    tmp_start_index = 0
    tmp_end_index = -1
    code_line_positions = []
    end_positions = []
    max_end_position = 0
    for index in range(len(lines_without_space)):
        tmp_end_index += len(lines_without_space[index])
        end_box = line_box_array[tmp_end_index].split()
        end_y, end_w = int(end_box[2]), int(end_box[3])
        max_end_position = max(max_end_position, end_w)
        end_positions.append(int(end_w))
        code_line_positions.append((end_w, hImg - end_y))
        if index != 0:
            tmp_start_index = tmp_start_index + len(lines_without_space[index - 1])
        start_box = line_box_array[tmp_start_index].split()
        start_x = int(start_box[1])
        # Add the x position of the first character of each line
        line_indent.append(start_x)
    differences = [x - y for x, y in zip(end_positions, line_indent)]
    max_line_length = max(differences)
    # Grouping the indentation array based on proximity
    groups = [[]]  # Initialize the first group
    for num in sorted(line_indent):
        if groups[-1] and num - groups[-1][-1] > 5:
            groups.append([])  # Create a new group
        groups[-1].append(num)
    # Create a mapping dictionary
    mapping = {}
    for i, group in enumerate(groups):
        for indent in group:
            mapping[indent] = i

    # Replace elements in the first array with group numbers
    space_number_array = [mapping[indent] for indent in line_indent]

    # Combine each line of code with its corresponding element from space_number_array
    lines_with_space = code.splitlines()
    for i, space_number in enumerate(space_number_array):
        space = "    " * space_number
        if len(lines_with_space[i].strip()) != 0 and lines_with_space[i].strip()[0] == '*':
            space = "    " * max(space_number - 1, 0) + " "
        # Add the corresponding number of spaces at the beginning of each line based on the group data
        lines_with_space[i] = space + lines_with_space[i]

    # Combine the modified lines back into a single code
    code_with_space = '\n'.join(lines_with_space)
    return code_with_space, code_line_positions, max_end_position, max_line_length


single_replace_list = [("‘", "'"), ("(  ", "("), ("( ", "("), ('“', '"'), (" )", ")"), (" ;", ";"),
                       ("(%"," (%"), ("minl","min1"), ("maxl","max1"), ("prodl","prod1"), ("[list[strl]","[list[str]]"),
                       (")(", ") ("), ("||(", "|| ("), ("&&(", "&& ("), (" and(", " and ("), (" or(", " or ("),
                       ("elses", "else:"), ("-—", "-"), ("—", "-"), ("[@]", "[0]"), ("’ ", " ' "), (" j= tt", " = ''"),
                         ("7?>", "?>"), ("]1/", "]/"), (" [", "["), ("[]lbyte", "[]byte"), ("[]byte", " []byte"),
                       (" if (1", " if (!"), ("/[~", "/[^"), ("-->", "->"), ("rts '1,", "'r' = '1'"),
                       (". ", "."), ("(e,", "(0,"), ("/%%", "/**"), (" 1i;", " i;"),
                       ("r= '1Y,", "'r' = '1',"), ("iy", "}"), ("vielL", "vieL"), ("7:", "?:"), (": sw\"", ": %w\""),
                       ("[lb", "[]b"), ("[stringl", "[string]"), ("!'=", "!="), ("[ls", "[]s"), (" n.", " ln."),
                       ("xhttp.", "*http."), ("Ment", "\"err\","), ("Men", "err"), ("ys,", "s,"),
                       (" on)", " n"), ("\"input,", "\"input\","), ("\"7\";", "\"?\";"), ("G6aussian", "Gaussian"),
                       ("0utput", "Output"), ("ixi", "i*i"), ("re]=", "rel="), (" Preturn", " @return"),
                       (" * (", " * ("), (" x (", " * ("), ("\"n\",", "nt"), (" |] ", " || "), ("[il.", "[i]."),
                       ("©", '0'), ("(e, 0", "(0, 0"), ("({'", "('"), ("Exception (", "Exception("), ("’", "'"),
                       ("'*'", "''"), ("°'", "'"), ("WwW", "W"), ("Error (", "Error("), ("(]", "[]"), ("{('", "('"),
                       ("£", ""), ("«", ""), (" =[", " = ["), (",(", ", ("), ("l:,", "[:,"),
                       (" Qauthor"," @author"), (" yl1)"," y1)"), ("for(1 =","for(i ="), ("for(int 1 =","for(int i ="),
                       (",  ", ", "), ("'')", "')"), ("(yrl)", "(url)"), (" X = ", " x = "), ("xdtype", "*dtype"),
                       ("returns=scs", "return \"'S'\""), (" x= ", " *= "), (" FILEx ", " FILE* "), ("\"?7\"", "\"?\""),
                       ("I H", "};"), ("™", ""), ("®", "0"), ("\"%s'", "'%s'"), ("\"”", "\""), ("}H", "})"),
                       ("Isbir", "IsDir"), ("HO)", "}()"), (",01}", ", 1}"), (" ¢ ", " c "), ("]l[", "]["),
                       ("]1[", "]["), ("[1[]", "[][]"), ("TI]", "T[]"), ("[il,", "[i],"), ("]([", "]["),
                       ("]1 ", "] "), ("3e,", "30,"), ("l[il]", "[i]"), ("= ' *'", "= ' '"), ("= '*", "= ''"),
                       ("/%*", "/**"), ("max1l ", "max1 "), ("tlL", "tL"), ("{H\\n", "{}\\n"), ("'S%Y", "'%Y"),
                       (":[1}", ":[]}"), ("__init_ ", "__init__ "), ("]l ", "] "), ("@O0verride", "@Override"),
                       ("/ Xx", "/**"), ("Xx ", "x "), ("super (", "super("), (".stripQ", ".strip()"),
                       ("contig", "config")]

equal_replace_list = [("L", "}"), ("ats", "try:"), ("Ip", "}"), ("iF", "}"), ("elise:", "else:"), ("elise", "else"),
                      ("[kk", "/**"), ("VEST", "/**"), ("VESS", "/**"), ("'/", "*/"), ("I", "}"), ("if", "{"),
                      ("by", "{"), ("¥", "}"), ("1)", "])"), ("0", "}()"), ("ens =iniled", "}); err != nil {"),
                      ("Yi", "};"), ("hH", "})"), ("J", ""), ("/*%", "/**"), ("/XX", "/**"), ("@0verride", "@Override"),
                      ("Visa", "/**")]


start_with_replace_list = [("' @", "* @"), (".>", "->"), ("1,", "],"), ("* @aram", "* @param"), ("»", "."),
                           ("return(", "return ("), ("if(", "if ("), ("for(", "for ("), ("while(", "while ("),
                           ("import(", "import ("),("@lvm", "@Jvm"), ("if not(", "if not (")]

def optimize_code_ocr_result(line, previous_line, bracket_flag):
    for single_replace_item in single_replace_list:
        line = line.replace(single_replace_item[0], single_replace_item[1])
    if " =" in line and "= " not in line:
        line = line.replace(" =", " = ")
    if " +=" in line and "+= " not in line:
        line = line.replace(" +=", " += ")
    if " -=" in line and "-= " not in line:
        line = line.replace(" -=", " -= ")
    for equal_replace_item in equal_replace_list:
        if line.strip() == equal_replace_item[0]:
            line = line.replace(equal_replace_item[0], equal_replace_item[1])
    for start_with_replace_item in start_with_replace_list:
        if line.strip().startswith(start_with_replace_item[0]):
            line = line.replace(start_with_replace_item[0], start_with_replace_item[1], 1)
    if " ." in line and " .=" not in line and " .." not in line:
        line = line.replace(" .", ".")
    if "import " in line and ".x;" in line:
        line = line.replace(".x;", ".*;")
    if "([" in line and line.count("(") > line.count(")"):
        line = line.replace("([", "[")
    if line.strip().startswith("-") and not line.strip().startswith("->"):
        line = line.replace("-", ".", 1)
    if line.strip() == "]" and ("[" not in previous_line or line.count('[') == line.count(']')):
        line = line.replace("]", "}")
    if "@" in line and not line.strip().startswith("@") and not line.strip().startswith("*") and "(@Check" not in line:
        line = line.replace("@", "0")
    if line.strip().startswith(".") and "(" not in line and ")" not in line and "__" in line:
        line = line.replace(".", "__", 1)
    if line.strip().startswith(".") and ":" in line and previous_line.strip().endswith("{"):
        line = line.replace(".", "-", 1)
    if line.strip().startswith(".-") and ":" in line and previous_line.strip().startswith("-"):
        line = line.replace(".-", "-", 1)
    if line.strip().startswith(".") and ":" in line and previous_line.strip().startswith("-"):
        line = line.replace(".", "-", 1)
    if line.strip().endswith("7>"):
        last_index = line.rfind("7>")
        line = line[:last_index] + "?>" + line[last_index + 2:]
    if (" :" in line and "for " not in line and "return " not in line and " :=" not in line and "? " not in line
            and ", :" not in line):
        line = line.replace(" :", ":")
    if ": " in line and "::" in line:
        line = line.replace(": ", ":")
    if "l$" in line and "l;" in line:
        line = line.replace("l$", "[")
        line = line.replace("l;", "];")
    if line.strip() == "{" and (previous_line.strip() == "}" or previous_line.strip().endswith(";")):
        line = line.replace("{", "}")
    if "ll" in line and "[" in line and "]" in line and "ll " not in line:
        line = line.replace("ll", "][")
    if "*," in line and ", '" in line:
        line = line.replace("*,", "',")
    if "\"'" in line and line.strip().endswith("\""):
        line = line.replace("\"'", "\"")
    if "\"'" in line and line.strip().endswith("\","):
        line = line.replace("\"'", "\"")
    if "\"'" in line and line.strip().endswith("'"):
        line = line.replace("\"'", "'")
    if "\"'" in line and line.strip().endswith("',"):
        line = line.replace("\"'", "'")
    if "\"')" in line and "('" in line:
        line = line.replace("\"')", "')")
    if "\"')" in line and "='" in line:
        line = line.replace("\"')", "')")
    if "\")" in line and "='" in line:
        line = line.replace("\")", "')")
    if "¥" in line:
        line = line.replace("¥", "")
    if "while (" in line and "--" not in line and "-)" in line:
        line = line.replace("-", "--")
    if "'" in line and line.count("'") % 2 != 0 and ": '" in previous_line and ": " in line and ": '" not in line:
        line = line.replace(": ", ": '")
    if (0 < len(line.strip()) <= 2 and "}" not in line and "{" not in line and "[" not in line
            and "]" not in line and "(" not in line and ")" not in line and "*" not in line):
        if bracket_flag is True:
            space_prefix_length = len(line) - len(line.lstrip())
            line = space_prefix_length * " " + "}"
        else:
            line = ""
    if ("l " in line and "ll " not in line and "nil " not in line and "ail " not in line and "el " not in line
            and "ol " not in line and "al " not in line and "url " not in line and "html " not in line):
        line = line.replace("l ", "1 ")
    if ("l, " in line and "ll," not in line and "nil, " not in line and "ail, " not in line and "el, " not in line
            and "ol," not in line and "al," not in line and "url," not in line and "html," not in line):
        line = line.replace("l,", "1,")
    if ("l;" in line and "ll;" not in line and "nil; " not in line and "ail; " not in line and "el; " not in line
            and "ol;" not in line and "al;" not in line and "url;" not in line and "html;" not in line):
        line = line.replace("l;", "1;")
    if ("l:" in line and "ll:" not in line and "nil: " not in line and "ail: " not in line and "el: " not in line
            and "ol:" not in line and "al:" not in line  and "url:" not in line and "html:" not in line):
        line = line.replace("l:", "1:")
    if ("l]" in line and "ll]" not in line and "nil]" not in line and "ail]" not in line and "el]" not in line
            and "ol]" not in line and "al]" not in line and "url]" not in line and "html]" not in line):
        line = line.replace("l]", "1]")
    if ("l)" in line and "ll)" not in line and "nil)" not in line and "ail)" not in line and "el)" not in line
            and "ol)" not in line and "al)" not in line and "url)" not in line and "html)" not in line):
        line = line.replace("l)", "1)")
    if (line.strip().endswith("l") and "ll" not in line and "nil" not in line and "mail" not in line
            and "ol" not in line and "el" not in line and "al" not in line and "url" not in line and "html" not in line):
        line = line.replace("l", "1")

    return line


def remove_hint_from_code_line(line, hint_num):
    result_line = ''
    if line.count(":") == hint_num:
        replace_flag = False
        for index in range(len(line)):
            if line[len(line) - 1 - index] == ':':
                replace_flag = True
                continue
            if (line[len(line) - 1 - index] == '(' or line[len(line) - 1 - index] == ',') and replace_flag is True:
                result_line = line[len(line) - 1 - index] + result_line
                replace_flag = False
                continue
            if replace_flag is False or line[len(line) - 1 - index] == ' ':
                result_line = line[len(line) - 1 - index] + result_line
                continue
            if replace_flag is True:
                continue
    return result_line


def post_process_code(image, region, code_with_space, hint_code_for_each_line, hint_num_for_each_line, max_end_position, max_line_length, code_line_position):
    x1, y1 = region[0]
    previous_line = ''
    bracket_flag = False
    code_result = ''
    for i, line in enumerate(code_with_space.splitlines()):
        if not line.strip():
            continue
        if "{" in line or "}" in line:
            bracket_flag = True
        hint_code = (line.strip()
                     .replace(" ", "")
                     .replace("_", "")
                     .replace("%", "")
                     .replace("*", ""))
        if hint_code in hint_code_for_each_line:
            line = remove_hint_from_code_line(line, hint_num_for_each_line[hint_code_for_each_line.index(hint_code)])
        line = optimize_code_ocr_result(line, previous_line, bracket_flag)
        # remove the hint of the editor
        if len(line.strip()) > 0 and line.strip()[0].isdigit() and " usage" in line:
            continue
        previous_line = line
        strip_flag = False
        if (x1 + max_end_position + max_line_length) > image.shape[1]:
            strip_flag = True
            x = code_line_position[i][0] + x1 + 2
        else:
            x = max_end_position + x1 + 2
        y = code_line_position[i][1] + y1
        code_result += line + '\n'
        if strip_flag is True:
            line = line.strip()
        cv2.putText(image, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, 1)
    return code_result

def get_code_from_image(image, region):
    x1, y1 = region[0]
    x2, y2 = region[1]
    cropped_img = image[y1:y2, x1:x2].copy()
    cropped_img, _ = remove_the_detected_horizontal_area(cropped_img)
    cropped_img, _ = remove_the_detected_rectangle_area(cropped_img)
    cropped_img, _ = remove_the_detected_partial_horizontal_area(cropped_img)
    cropped_img, _ = remove_line_number(cropped_img)
    cropped_img, _, hint_code_for_each_line, hint_num_for_each_line = detect_the_code_hint_area(cropped_img)
    original_code = get_text_from_image(cropped_img)
    #print(code)
    boxes = get_character_from_image(cropped_img)
    code_with_space, code_line_position, max_end_position, max_line_length \
        = add_indentation_to_detected_code(cropped_img, original_code, boxes)
    code_result = post_process_code(image, region, code_with_space, hint_code_for_each_line, hint_num_for_each_line,
                                    max_end_position, max_line_length, code_line_position)
    return code_result, original_code


def get_code_content_with_space_for_image(image, code_region_list):
    final_code = ''
    original_code = ''
    for region in code_region_list:
        post_processed_code, raw_code = get_code_from_image(image, region)
        final_code += post_processed_code
        original_code += raw_code
    #print(final_code)
    return image, final_code, original_code


def get_code_content_with_space_for_screen(image, code_region_list):
    code_list = []
    final_code = ''
    for region in code_region_list:
        post_processed_code, _ = get_code_from_image(image, region)
        code_result = post_processed_code
        final_code += code_result
        code_list.append(code_result)
    #print(final_code)
    return image, code_list
import re


def replace_color_in_text(text: str, old_color: str, new_color: str):
    return text.replace(old_color, new_color)


def swap_color_in_text(text: str, color_1: str, color_2: str):
    temp_placeholder = "__TEMP__"
    text = replace_color_in_text(text, color_1, temp_placeholder)
    text = replace_color_in_text(text, color_2, color_1)
    text = replace_color_in_text(text, temp_placeholder, color_2)
    return text


def create_kickback(pregunta_in, respuesta_in):
    # Define the font style and size
    op_b = r"""{"""
    cl_b = r"""}"""
    question_style = r"""\\fnComic Sans MS\\u1"""
    normal_style = r"""\\fnAria\\u0"""
    yellow = r"""\\c&H00FFFF&"""
    white = r"""\\c&HFFFFFF&"""

    pregunta_out = re.sub(yellow, yellow + question_style, pregunta_in)
    pregunta_out = re.sub(op_b + white, r"\\N\\N\\N\\N" + op_b + white, pregunta_out) + r"\N\N\N\N\N"

    list_ask = re.split(r"\\N\\N", pregunta_out)
    list_res = re.split(r"\\N\\N", respuesta_in)

    respuesta_out = (list_ask[0] + re.sub(yellow + cl_b, normal_style + cl_b + r"\\N", list_res[0])).rstrip(
        op_b + white + cl_b)
    respuesta_out += (re.sub(cl_b, question_style + cl_b, list_ask[1]) +
                      r"\N\N" + list_ask[2] + re.sub(white, normal_style, list_ask[1]) + r"\N" + list_res[1])

    return pregunta_out, respuesta_out


if __name__ == '__main__':
    # Example usage:
    pass

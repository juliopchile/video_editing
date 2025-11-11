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


def replace_colors_regex(text: str, palette_from: dict, palette_to: dict) -> str:
    """Reemplaza usando regex sobre los códigos completos presentes en palette_from."""
    # Mapeo de código completo -> nuevo código
    mapping = {
        old_code: palette_to[key]
        for key, old_code in palette_from.items()
        if key in palette_to
    }
    if not mapping:
        return text
    # Crear patrón (OR) escapado
    pattern = re.compile("|".join(sorted((re.escape(c) for c in mapping.keys()), key=len, reverse=True)))
    return pattern.sub(lambda m: mapping[m.group(0)], text)


# Ejemplo de uso
palette_1 = {'U1': '{\c&HB124F7&}', 'AI': '{\c&HB57846&}', 'O1': '{\c&H7995D1&}', 'E1': '{\c&H20DBF8&}', 'A1': '{\c&H86D61D&}', 'ENCIA': '{\c&HD65AA1&}', 'IE': '{\c&H062CF6&}', 'E2': '{\c&H09F53C&}', 'E3': '{\c&HF9E03F&}', 'A2': '{\c&HF8161F&}', 'E4': '{\c&H6547CE&}'}

palette_2 = {'U1': '{\c&HB124F7&}', 'AI': '{\c&HB57846&}', 'O1': '{\c&HF8161F&}', 'E1': '{\c&H20DBF8&}', 'A1': '{\c&H86D61D&}', 'ENCIA': '{\c&HD65AA1&}', 'IE': '{\c&H062CF6&}', 'E2': '{\c&H09F53C&}', 'E3': '{\c&HF9E03F&}', 'A2': '{\c&H7995D1&}', 'E4': '{\c&H6547CE&}'}

TEXT = r"""Dialogue: 0,0:05:22.75,0:05:33.17,Batallas HD,,0,0,0,,Ve poniendo atención a mi estilo en {\c&HB124F7&}Blu{\c&HFFFFFF&}-{\c&HB57846&}ray{\c&HFFFFFF&}, estas que haces este estilo en {\c&HB124F7&}tu {\c&HB57846&}life{\c&HFFFFFF&}.\NPor mucho que quieras alargarme las estructuras, se nota que está a to' pensado el {\c&HB124F7&}punch{\c&HB57846&}line{\c&HFFFFFF&}.
Dialogue: 0,0:05:34.57,0:05:43.70,Batallas HD,,0,0,0,,Ya está de{\c&HF9E03F&}vuel{\c&HF8161F&}ta{\c&HFFFFFF&}, el estilo con la e{\c&HD65AA1&}sencia{\c&HFFFFFF&} fresca co{\c&HF9E03F&}nec{\c&HF8161F&}ta{\c&HFFFFFF&}.\NNo puedes hacerlo porque tu e{\c&HD65AA1&}sencia{\c&HFFFFFF&} no tiene perma{\c&HD65AA1&}nencia{\c&HFFFFFF&} y no es la co{\c&HF9E03F&}rrec{\c&HF8161F&}ta{\c&HFFFFFF&}.
Dialogue: 0,0:05:44.92,0:05:54.36,Batallas HD,,0,0,0,,La mía {\c&H062CF6&}siem{\c&H09F53C&}pre {\c&HF9E03F&}en{\c&HF8161F&}tra{\c&HFFFFFF&}, sabes que el estilo aquí {\c&H062CF6&}sí{\rsinalefa\c&H062CF6&}~{\r\c&H062CF6&}in{\c&H09F53C&}cre{\c&HF9E03F&}men{\c&HF8161F&}ta{\c&HFFFFFF&}\Ny no puedes hacerlo al {\c&H062CF6&}cien{\c&HFFFFFF&} por {\c&H062CF6&}cien{\c&HFFFFFF&}, por eso en la {\c&H062CF6&}sien{\c&H09F53C&} te {\c&HF9E03F&}en{\c&HF8161F&}tra{\c&HFFFFFF&}.
Dialogue: 0,0:05:55.66,0:06:04.87,Batallas HD,,0,0,0,,Me queda {\c&H20DBF8&}diez {\c&HF9E03F&}se{\c&HB124F7&}gun{\c&H7995D1&}dos{\c&HFFFFFF&}, ya lo {\c&H20DBF8&}ves{\c&HF9E03F&} te {\c&HB124F7&}fun{\c&H7995D1&}do{\c&HFFFFFF&}, como un ovulo {\c&H20DBF8&}te{\c&HF9E03F&} fe{\c&HB124F7&}cun{\c&H7995D1&}do{\c&HFFFFFF&}.\NNo puedes hacer este estilo porque yo soy el más cabrón y el más loco de {\c&H20DBF8&}es{\c&HF9E03F&}te {\c&HB124F7&}mun{\c&H7995D1&}do{\c&HFFFFFF&}."""

if __name__ == "__main__":
    nuevo_texto = replace_colors_regex(TEXT, palette_1, palette_2)
    print(nuevo_texto)
    
    #swap_color_in_text(TEXT, r"{\c&HEA18C9&}", r"{\c&H2C8C75&}")

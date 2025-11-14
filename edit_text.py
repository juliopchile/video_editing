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


def _strip_braces(code: str) -> str:
    """Devuelve el código sin llaves externas si vienen presentes: '{...}' -> '...'"""
    m = re.match(r"^\{(.+)\}$", code)
    return m.group(1) if m else code


def replace_colors_regex(text: str, palette_from: dict, palette_to: dict) -> str:
    """Reemplaza SOLO la parte del código de color sin corchetes '{ }'.

    Ejemplo: reemplaza '\\c&H8E3DEF&' por '\\c&H2C8C75&' manteniendo las llaves
    existentes en el texto sin tocarlas.
    """
    # Construir mapeo entre códigos internos (sin llaves)
    mapping = {}
    for key, old_full in palette_from.items():
        if key not in palette_to:
            continue
        new_full = palette_to[key]
        old_inner = _strip_braces(old_full)
        new_inner = _strip_braces(new_full)
        mapping[old_inner] = new_inner

    if not mapping:
        return text

    # Crear patrón (OR) escapado sobre los códigos internos
    pattern = re.compile(
        "|".join(sorted((re.escape(c) for c in mapping.keys()), key=len, reverse=True))
    )
    return pattern.sub(lambda m: mapping[m.group(0)], text)


# Ejemplo de uso
palette_1 = {
    'A1': r'{\c&H8E3DEF&}', 'E1': r'{\c&HFF8F64&}', 'O1': r'{\c&HFFFF00&}',
    'AO': r'{\c&H6A83C0&}', 'EE': r'{\c&HBD9E5E&}', 'OI': r'{\c&HF05E78&}',
    'E2': r'{\c&H88BEE1&}', 'A2': r'{\c&H0061FE&}', 'O2': r'{\c&H45AB6D&}',
    'OE': r'{\c&H00B0FF&}', 'EI': r'{\c&H00FF00&}', 'I1': r'{\c&H0CEACD&}'
}
palette_2 = {
    'A1': r'{\c&H2C8C75&}', 'E1': r'{\c&H7995D1&}', 'O1': r'{\c&HCC8FD9&}',
    'AO': r'{\c&HD65AA1&}', 'EA': r'{\c&HF9E03F&}', 'EE': r'{\c&H86D61D&}',
    'AA': r'{\c&HB124F7&}', 'OIE': r'{\c&HB57846&}', 'O2': r'{\c&H062CF6&}',
    'E2': r'{\c&H20DBF8&}', 'OO': r'{\c&H6547CE&}', 'EI': r'{\c&HF8161F&}',
    'I1': r'{\c&H09F53C&}'
}


TEXT = r"""Dialogue: 0,0:09:56.13,0:10:06.86,Batallas HD,,0,0,0,,[Section]En la {\c&H8E3DEF&}cla{\c&HFF8F64&}ve {\c&HFFFF00&}son{\c&HFFFFFF&} de rap el {\c&H6A83C0&}canto{\c&HD170EF&} deja {\c&HBD9E5E&}siempre{\c&HFFFFFF&}. Tú sabes que te entrega {\c&H6A83C0&}hardcore alto{\c&HFFFFFF&} y {\c&HD170EF&}deja {\c&HBD9E5E&}muerte{\c&HFFFFFF&}.\NNo sé dónde yo lo busco {\c&HBD9E5E&}siempre{\c&HFFFFFF&}. Se llama {\c&H8E3DEF&\i1\fnVerdana}A{\c&HFF8F64&}de{\c&HFFFF00&}song{\c&HFFFFFF&\i0\fnArial}, yo soy tu {\c&H8E3DEF&\i1\fnVerdana}Ha{\c&HFF8F64&}des'{\c&HFFFF00&} song{\c&HFFFFFF&\i0\fnArial}, o tu {\c&H6A83C0&}canto{\c&HD170EF&} de la {\c&HBD9E5E&}muerte{\c&HFFFFFF&}.
Dialogue: 0,0:10:07.35,0:10:17.36,Batallas HD,,0,0,0,,Que mira solo tengo todo el nivel. Voy rimando compañero que {\c&H0061FE&}saca ya as{\c&HFFFFFF&}te{\c&HF05E78&}roi{\c&H88BEE1&}des{\c&HFFFFFF&}.\NYa te {\c&H0061FE&}ataca{\c&HFFFFFF&}, {\c&HF05E78&}hoy{\c&H88BEE1&} ves{\c&H00FF00&} con {\c&HFFFF00&}el {\c&H00FF00&}co{\c&HFFFF00&}nec{\c&H00FF00&}tor {\c&HFFFFFF&}ya te afectan mis {\c&H0061FE&}canna{\c&HFFFFFF&}bi{\c&HF05E78&}noi{\c&H88BEE1&}des{\c&HFFFFFF&}.
Dialogue: 0,0:10:18.99,0:10:27.94,Batallas HD,,0,0,0,,Así ya se saca, ¿querí ganarme? inyecta este{\c&HF05E78&}roi{\c&H88BEE1&}des{\c&HFFFFFF&}.\NTengo todos los tonos, soy el golpe de Meteoro, te topaste en los aste{\c&HF05E78&}roi{\c&H88BEE1&}des{\c&HFFFFFF&}."""


if __name__ == "__main__":
    nuevo_texto = replace_colors_regex(TEXT, palette_1, palette_2)
    print(nuevo_texto)
    
    #swap_color_in_text(TEXT, r"{\c&HEA18C9&}", r"{\c&H2C8C75&}")

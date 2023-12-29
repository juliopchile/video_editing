import json
import re

import numpy as np
import openai

from functions import open_AI


class Subtitulo:
    def __init__(self, spanish, clean_spanish, english="", done_translating=False):
        self.spanish = spanish
        self.clean_spanish = clean_spanish
        self.english = english
        self.done_translating = done_translating

    def to_dict(self):
        return {
            "spanish": self.spanish,
            "clean_spanish": self.clean_spanish,
            "english": self.english,
            "done_translating": self.done_translating
        }

    def translate(self, prompt, api_key, model):
        if not self.done_translating:
            try:
                self.english = open_AI.translate_gpt(_api_key=api_key,
                                                     _message=self.clean_spanish,
                                                     _prompt=prompt,
                                                     _model=model)
                self.done_translating = True
            except openai.OpenAIError as error:  # Replace with the actual exception
                print(f"OpenAIError {error}")
                self.done_translating = False
            finally:
                pass
        else:
            print("Skip (already translated)")

    @classmethod
    def from_dict(cls, data):
        return cls(
            spanish=data["spanish"],
            clean_spanish=data["clean_spanish"],
            english=data["english"],
            done_translating=data["done_translating"]
        )


# --- TRANSCRIPTION --- #
def read_file(filename, chunk_size):
    with open(filename, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data


def read_file_with_progress(filename, chunk_size, progress):
    with open(filename, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            progress.update(len(data))
            yield data
    progress.close()


def save_transcript(data, title):
    filename = title + '.txt'
    with open(filename, 'w') as text_file:
        text_file.write(data['text'])
    print('Transcript saved')


def save_words(data, title):
    filename = title + '.json'
    with open(filename, 'w') as json_file:
        json.dump(data['words'], json_file, indent=4)
    print('Words saved')


def save_data(data, title):
    filename = title + '.json'
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print('Data saved\n')


# --- AEGIS SUB PARSING --- #
def extract_timestamps_from_file(file_path: str) -> list[tuple[str, str]]:
    """
    Extract and parse timestamps from a text file containing subtitles.

    This function reads the subtitles from the specified text file, searches for timestamps
    in its contents, and returns a list of tuples representing the start and end timestamps
    of each subtitle entry.

    :param file_path: The path to the subtitles text file.
    :type file_path: str

    :return: A list of timestamp tuples in the format (start_time, end_time).
    :rtype: list[tuple[str, str]]

    :raises FileNotFoundError: If the specified file is not found.
        """
    timestamps = []
    in_events_section = False
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if in_events_section:
                    timestamps.append((line[12:22], line[23:33]))
                elif line[:8] == '[Events]':
                    in_events_section = True
        return timestamps[1::]
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("Error occurred:", str(e))

    file.close()
    return timestamps[1::]


def calculate_milliseconds(byte_array: bytes):
    horas = byte_array[0] * 3600000
    minutos = byte_array[2] * 600000 + byte_array[3] * 60000
    segundos = byte_array[5] * 10000 + byte_array[6] * 1000
    milisegundos = byte_array[8] * 100 + byte_array[9] * 10

    # Add them all
    return horas + minutos + segundos + milisegundos - 205013280


def str2bytes(time_stamps: list[tuple[str, str]]):
    time_bytes = np.array([[ts[0].encode(), ts[1].encode()] for ts in time_stamps], dtype=object)
    return time_bytes


def time_stamps_to_milliseconds(time_stamps: list[tuple[str, str]]) -> list[tuple[int, int]]:
    time_bytes = str2bytes(time_stamps)
    return [(calculate_milliseconds(start), calculate_milliseconds(end)) for start, end in time_bytes]


def save_timestamps_to_json(_time_stamps: list[tuple], _filename: str):
    """
    Save a list of timestamps to a JSON file.

    This function takes a list of timestamps, represented as tuples, and
    saves them to a JSON file specified by the `filename` parameter.

    :param _time_stamps: A list of timestamp tuples, where each tuple contains
                       information about a specific timestamp.
    :type _time_stamps: list[tuple]

    :param _filename: The name of the JSON file to save the timestamps to. If
                     the filename does not end with '.json', it will be
                     automatically added.
    :type _filename: str

    :return: None

    Example:
        >>> time_stamps = [('0:00:19.87', '0:00:30.20'), ('0:00:30.20', '0:00:40.85')]
        >>> save_timestamps_to_json(time_stamps, 'examples/time_stamps.json')
    """

    # Convert the list of tuples to a list of lists
    timestamps_list = [list(t) for t in _time_stamps]

    # Specify the filename with a .json extension
    if not _filename.endswith(".json"):
        _filename += ".json"

    # Write the list to a JSON file
    with open(_filename, "w") as json_file:
        json.dump(timestamps_list, json_file, indent=4)


def load_words(file_path: str) -> list[dict]:
    """
    Load a list of words dictionaries.

    This function takes a list of words, represented as dictionaries, and return them.

    :param file_path: str

    :return: list[dict]

    Example:
        >>> words = load_words('examples/data.json')
        >>> print(words)
        [{'text': 'Más', 'start': 1645, 'end': 1745, 'confidence': 0.3, 'speaker': None}, {'text': 'arriba', 'start': 1785, 'end': 2025, 'confidence': 0.42, 'speaker': None}, {'text': 'con', 'start': 2085, 'end': 2185, 'confidence': 0.787, 'speaker': None}, {'text': 'Policarpo', 'start': 2206, 'end': 2666, 'confidence': 0.635, 'speaker': None}, {'text': 'Juacho', 'start': 15958, 'end': 16277, 'confidence': 0.458, 'speaker': None}, {'text': 'venía', 'start': 16318, 'end': 16639, 'confidence': 0.755, 'speaker': None}, {'text': 'a', 'start': 16659, 'end': 16679, 'confidence': 0.025, 'speaker': None}, {'text': 'mirarme', 'start': 16739, 'end': 17219, 'confidence': 0.702, 'speaker': None}, {'text': 'los', 'start': 17239, 'end': 17339, 'confidence': 0.545, 'speaker': None}, {'text': 'ojos', 'start': 17399, 'end': 17679, 'confidence': 0.678, 'speaker': None}, {'text': 'sangrientos,', 'start': 17719, 'end': 18300, 'confidence': 0.524, 'speaker': None}, {'text': 'entonces', 'start': 18400, 'end': 18840, 'confidence': 0.49, 'speaker': None}, {'text': 'mírame', 'start': 18880, 'end': 19200, 'confidence': 0.467, 'speaker': None}, {'text': 'a', 'start': 19220, 'end': 19300, 'confidence': 0.814, 'speaker': None}, {'text': 'los', 'start': 19320, 'end': 19420, 'confidence': 0.466, 'speaker': None}, {'text': 'ojos,', 'start': 19540, 'end': 19761, 'confidence': 0.721, 'speaker': None}, {'text': 'vengo', 'start': 19821, 'end': 20081, 'confidence': 0.695, 'speaker': None}, {'text': 'terrible,', 'start': 20121, 'end': 20521, 'confidence': 0.841, 'speaker': None}, {'text': 'violento.', 'start': 20581, 'end': 21082, 'confidence': 0.921, 'speaker': None}, {'text': 'Tuviera', 'start': 21322, 'end': 21622, 'confidence': 0.761, 'speaker': None}, {'text': 'elegido', 'start': 21662, 'end': 21962, 'confidence': 0.446, 'speaker': None}, {'text': 'en', 'start': 21982, 'end': 22022, 'confidence': 0.018, 'speaker': None}, {'text': 'primera', 'start': 22082, 'end': 22442, 'confidence': 0.639, 'speaker': None}, {'text': 'para', 'start': 22482, 'end': 22743, 'confidence': 0.544, 'speaker': None}, {'text': 'ganarte', 'start': 22783, 'end': 23183, 'confidence': 0.812, 'speaker': None}, {'text': 'directo,', 'start': 23243, 'end': 23663, 'confidence': 0.894, 'speaker': None}, {'text': 'pero', 'start': 23723, 'end': 23903, 'confidence': 0.849, 'speaker': None}, {'text': 'los', 'start': 24004, 'end': 24084, 'confidence': 0.629, 'speaker': None}, {'text': 'depredadores', 'start': 24164, 'end': 24964, 'confidence': 0.731, 'speaker': None}, {'text': 'no', 'start': 25024, 'end': 25124, 'confidence': 0.694, 'speaker': None}, {'text': 'se', 'start': 25164, 'end': 25244, 'confidence': 0.334, 'speaker': None}, {'text': 'alimentan', 'start': 25264, 'end': 25765, 'confidence': 0.883, 'speaker': None}, {'text': 'de', 'start': 25785, 'end': 25885, 'confidence': 0.68, 'speaker': None}, {'text': 'insectos.', 'start': 25945, 'end': 27566, 'confidence': 0.709, 'speaker': None}, {'text': 'Loco,', 'start': 27606, 'end': 27886, 'confidence': 0.696, 'speaker': None}, {'text': 'yo', 'start': 27926, 'end': 28046, 'confidence': 0.703, 'speaker': None}, {'text': 'sí', 'start': 28106, 'end': 28206, 'confidence': 0.41, 'speaker': None}, {'text': 'sueno', 'start': 28226, 'end': 28547, 'confidence': 0.606, 'speaker': None}, {'text': 'fresco,', 'start': 28607, 'end': 28967, 'confidence': 0.783, 'speaker': None}, {'text': 'que', 'start': 29147, 'end': 29227, 'confidence': 0.414, 'speaker': None}, {'text': 'quiere', 'start': 29267, 'end': 29467, 'confidence': 0.356, 'speaker': None}, {'text': 'hablarme', 'start': 29487, 'end': 29888, 'confidence': 0.864, 'speaker': None}, {'text': 'de', 'start': 29908, 'end': 29948, 'confidence': 0.003, 'speaker': None}, {'text': 'fracaso,', 'start': 30268, 'end': 30768, 'confidence': 0.852, 'speaker': None}, {'text': 'de', 'start': 30808, 'end': 30888, 'confidence': 0.907, 'speaker': None}, {'text': 'sufrimiento,', 'start': 30968, 'end': 31609, 'confidence': 0.722, 'speaker': None}, {'text': 'que', 'start': 31789, 'end': 31869, 'confidence': 0.397, 'speaker': None}, {'text': 'es', 'start': 31889, 'end': 31929, 'confidence': 0.48, 'speaker': None}, {'text': 'sabio', 'start': 31949, 'end': 32189, 'confidence': 0.635, 'speaker': None}, {'text': 'el', 'start': 32249, 'end': 32308, 'confidence': 0.452, 'speaker': None}, {'text': 'freestyle,', 'start': 32348, 'end': 32930, 'confidence': 0.56, 'speaker': None}, {'text': 'que', 'start': 32950, 'end': 33030, 'confidence': 0.536, 'speaker': None}, {'text': 'es', 'start': 33070, 'end': 33110, 'confidence': 0.754, 'speaker': None}, {'text': 'sabio', 'start': 33130, 'end': 33390, 'confidence': 0.483, 'speaker': None}, {'text': 'el', 'start': 33450, 'end': 33510, 'confidence': 0.544, 'speaker': None}, {'text': 'universo,', 'start': 33550, 'end': 34110, 'confidence': 0.78, 'speaker': None}, {'text': 'que', 'start': 34170, 'end': 34271, 'confidence': 0.42, 'speaker': None}, {'text': 'después', 'start': 34291, 'end': 34551, 'confidence': 0.534, 'speaker': None}, {'text': 'de', 'start': 34571, 'end': 34671, 'confidence': 0.502, 'speaker': None}, {'text': 'mi', 'start': 34731, 'end': 34831, 'confidence': 0.559, 'speaker': None}, {'text': 'peor', 'start': 34891, 'end': 35011, 'confidence': 0.585, 'speaker': None}, {'text': 'caída', 'start': 35051, 'end': 35511, 'confidence': 0.703, 'speaker': None}, {'text': 'es', 'start': 35671, 'end': 35772, 'confidence': 0.829, 'speaker': None}, {'text': 'mi', 'start': 35792, 'end': 35912, 'confidence': 0.556, 'speaker': None}, {'text': 'mejor', 'start': 35972, 'end': 36232, 'confidence': 0.914, 'speaker': None}, {'text': 'momento.', 'start': 36332, 'end': 36832, 'confidence': 0.954, 'speaker': None}, {'text': 'El', 'start': 38153, 'end': 38233, 'confidence': 0.661, 'speaker': None}, {'text': 'mejor', 'start': 38273, 'end': 38513, 'confidence': 0.877, 'speaker': None}, {'text': 'de', 'start': 38573, 'end': 38654, 'confidence': 0.887, 'speaker': None}, {'text': 'todos', 'start': 38714, 'end': 38854, 'confidence': 0.639, 'speaker': None}, {'text': 'los', 'start': 38894, 'end': 39014, 'confidence': 0.663, 'speaker': None}, {'text': 'tiempos.', 'start': 39094, 'end': 39654, 'confidence': 0.525, 'speaker': None}, {'text': 'Ahora', 'start': 39694, 'end': 39974, 'confidence': 0.748, 'speaker': None}, {'text': 'lo', 'start': 40035, 'end': 40135, 'confidence': 0.774, 'speaker': None}, {'text': 'demuestro,', 'start': 40195, 'end': 40715, 'confidence': 0.892, 'speaker': None}, {'text': 'yo', 'start': 40735, 'end': 40775, 'confidence': 0.03, 'speaker': None}, {'text': 'sí', 'start': 40935, 'end': 41055, 'confidence': 0.352, 'speaker': None}, {'text': 'que', 'start': 41075, 'end': 41295, 'confidence': 0.528, 'speaker': None}, {'text': 'represento.', 'start': 41355, 'end': 42156, 'confidence': 0.911, 'speaker': None}, {'text': 'Lo', 'start': 42676, 'end': 42756, 'confidence': 0.891, 'speaker': None}, {'text': 'mío', 'start': 42836, 'end': 42997, 'confidence': 0.344, 'speaker': None}, {'text': 'es', 'start': 43057, 'end': 43117, 'confidence': 0.216, 'speaker': None}, {'text': 'como', 'start': 43157, 'end': 43377, 'confidence': 0.785, 'speaker': None}, {'text': 'pisar', 'start': 43417, 'end': 43797, 'confidence': 0.801, 'speaker': None}, {'text': 'cemento', 'start': 43837, 'end': 44358, 'confidence': 0.74, 'speaker': None}, {'text': 'fresco.', 'start': 44458, 'end': 44858, 'confidence': 0.737, 'speaker': None}, {'text': 'Estoy', 'start': 44878, 'end': 45098, 'confidence': 0.57, 'speaker': None}, {'text': 'dejando', 'start': 45138, 'end': 45638, 'confidence': 0.598, 'speaker': None}, {'text': 'una', 'start': 45679, 'end': 45819, 'confidence': 0.809, 'speaker': None}, {'text': 'huella', 'start': 45899, 'end': 46199, 'confidence': 0.7, 'speaker': None}, {'text': 'a', 'start': 46219, 'end': 46239, 'confidence': 0.025, 'speaker': None}, {'text': 'través', 'start': 46359, 'end': 46679, 'confidence': 0.75, 'speaker': None}, {'text': 'del', 'start': 46719, 'end': 46879, 'confidence': 0.552, 'speaker': None}, {'text': 'tiempo.', 'start': 46999, 'end': 47380, 'confidence': 0.917, 'speaker': None}, {'text': '¡Oye!', 'start': 47400, 'end': 48721, 'confidence': 0.529, 'speaker': None}, {'text': 'Ese', 'start': 48761, 'end': 48921, 'confidence': 0.675, 'speaker': None}, {'text': 'sí', 'start': 49001, 'end': 49081, 'confidence': 0.466, 'speaker': None}, {'text': 'fue', 'start': 49141, 'end': 49241, 'confidence': 0.777, 'speaker': None}, {'text': 'el', 'start': 49261, 'end': 49321, 'confidence': 0.25, 'speaker': None}, {'text': 'momento,', 'start': 49361, 'end': 49922, 'confidence': 0.617, 'speaker': None}, {'text': 'lo', 'start': 49942, 'end': 50002, 'confidence': 0.774, 'speaker': None}, {'text': 'intento.', 'start': 50042, 'end': 50562, 'confidence': 0.666, 'speaker': None}, {'text': 'Vos', 'start': 50802, 'end': 50942, 'confidence': 0.52, 'speaker': None}, {'text': 'querías', 'start': 50962, 'end': 51162, 'confidence': 0.208, 'speaker': None}, {'text': 'armar', 'start': 51182, 'end': 51443, 'confidence': 0.778, 'speaker': None}, {'text': 'minutos', 'start': 51483, 'end': 51843, 'confidence': 0.79, 'speaker': None}, {'text': 'perfectos.', 'start': 51943, 'end': 52463, 'confidence': 0.868, 'speaker': None}, {'text': 'Eres', 'start': 52804, 'end': 53004, 'confidence': 0.662, 'speaker': None}, {'text': 'la', 'start': 53044, 'end': 53104, 'confidence': 0.662, 'speaker': None}, {'text': 'estrategia', 'start': 53144, 'end': 53644, 'confidence': 0.837, 'speaker': None}, {'text': 'del', 'start': 53704, 'end': 53824, 'confidence': 0.761, 'speaker': None}, {'text': 'pushline', 'start': 53884, 'end': 54345, 'confidence': 0.598, 'speaker': None}, {'text': 'con', 'start': 54385, 'end': 54505, 'confidence': 0.844, 'speaker': None}, {'text': 'contexto.', 'start': 54565, 'end': 55105, 'confidence': 0.836, 'speaker': None}, {'text': 'Y', 'start': 55125, 'end': 55145, 'confidence': 0.047, 'speaker': None}, {'text': 'yo', 'start': 55465, 'end': 55626, 'confidence': 0.655, 'speaker': None}, {'text': 'soy', 'start': 55686, 'end': 55866, 'confidence': 0.498, 'speaker': None}, {'text': 'la', 'start': 55886, 'end': 55966, 'confidence': 0.718, 'speaker': None}, {'text': 'magia', 'start': 56006, 'end': 56286, 'confidence': 0.795, 'speaker': None}, {'text': 'del', 'start': 56326, 'end': 56406, 'confidence': 0.674, 'speaker': None}, {'text': 'freestyle', 'start': 56486, 'end': 57027, 'confidence': 0.505, 'speaker': None}, {'text': 'al', 'start': 57067, 'end': 57147, 'confidence': 0.57, 'speaker': None}, {'text': 'momento.', 'start': 57207, 'end': 57687, 'confidence': 0.916, 'speaker': None}, {'text': '¡Oyelo!', 'start': 57707, 'end': 58468, 'confidence': 0.42, 'speaker': None}, {'text': '¡Minuto', 'start': 59368, 'end': 59748, 'confidence': 0.593, 'speaker': None}, {'text': 'perfecto!', 'start': 59788, 'end': 60469, 'confidence': 0.702, 'speaker': None}, {'text': '¡Órale,', 'start': 60829, 'end': 61049, 'confidence': 0.515, 'speaker': None}, {'text': 'hermano!', 'start': 61069, 'end': 61509, 'confidence': 0.666, 'speaker': None}, {'text': '¡Guacho,', 'start': 61549, 'end': 61849, 'confidence': 0.598, 'speaker': None}, {'text': 'sientan', 'start': 61889, 'end': 62249, 'confidence': 0.652, 'speaker': None}, {'text': 'el', 'start': 62309, 'end': 62389, 'confidence': 0.714, 'speaker': None}, {'text': 'esfuerzo!', 'start': 62429, 'end': 63070, 'confidence': 0.794, 'speaker': None}, {'text': 'Si', 'start': 63470, 'end': 63550, 'confidence': 0.412, 'speaker': None}, {'text': 'entre', 'start': 63570, 'end': 63770, 'confidence': 0.305, 'speaker': None}, {'text': 'a', 'start': 63790, 'end': 63810, 'confidence': 0.012, 'speaker': None}, {'text': 'mí', 'start': 63830, 'end': 63930, 'confidence': 0.528, 'speaker': None}, {'text': 'me', 'start': 63970, 'end': 64090, 'confidence': 0.59, 'speaker': None}, {'text': 'siento', 'start': 64129, 'end': 64370, 'confidence': 0.774, 'speaker': None}, {'text': 'una', 'start': 64450, 'end': 64530, 'confidence': 0.94, 'speaker': None}, {'text': 'pintura', 'start': 64610, 'end': 64989, 'confidence': 0.764, 'speaker': None}, {'text': 'antigua,', 'start': 65010, 'end': 65531, 'confidence': 0.741, 'speaker': None}, {'text': '¿sabéis', 'start': 65591, 'end': 65891, 'confidence': 0.455, 'speaker': None}, {'text': 'por', 'start': 65951, 'end': 66091, 'confidence': 0.869, 'speaker': None}, {'text': 'qué?', 'start': 66171, 'end': 66311, 'confidence': 0.442, 'speaker': None}, {'text': '¡Porque', 'start': 66331, 'end': 66591, 'confidence': 0.474, 'speaker': None}, {'text': 'estoy', 'start': 66671, 'end': 66911, 'confidence': 0.542, 'speaker': None}, {'text': 'en', 'start': 66931, 'end': 67071, 'confidence': 0.653, 'speaker': None}, {'text': 'el', 'start': 67111, 'end': 67171, 'confidence': 0.807, 'speaker': None}, {'text': 'renacimiento!', 'start': 67251, 'end': 68212, 'confidence': 0.86, 'speaker': None}, {'text': '¡Última!', 'start': 68412, 'end': 69652, 'confidence': 0.705, 'speaker': None}, {'text': '¡Eso', 'start': 69772, 'end': 69972, 'confidence': 0.614, 'speaker': None}, {'text': 'fue', 'start': 70012, 'end': 70172, 'confidence': 0.412, 'speaker': None}, {'text': 'perfecto!', 'start': 70212, 'end': 70773, 'confidence': 0.816, 'speaker': None}, {'text': "Pa'", 'start': 71053, 'end': 71173, 'confidence': 0.556, 'speaker': None}, {'text': 'que', 'start': 71193, 'end': 71273, 'confidence': 0.436, 'speaker': None}, {'text': 'ahora', 'start': 71333, 'end': 71573, 'confidence': 0.485, 'speaker': None}, {'text': 'no', 'start': 71653, 'end': 71733, 'confidence': 0.835, 'speaker': None}, {'text': 'digan', 'start': 71793, 'end': 72113, 'confidence': 0.824, 'speaker': None}, {'text': 'que', 'start': 72173, 'end': 72293, 'confidence': 0.686, 'speaker': None}, {'text': 'no', 'start': 72333, 'end': 72433, 'confidence': 0.79, 'speaker': None}, {'text': 'tengo', 'start': 72473, 'end': 72753, 'confidence': 0.657, 'speaker': None}, {'text': 'talento', 'start': 72793, 'end': 73354, 'confidence': 0.769, 'speaker': None}, {'text': "Pa'", 'start': 73654, 'end': 73774, 'confidence': 0.526, 'speaker': None}, {'text': 'que', 'start': 73794, 'end': 73874, 'confidence': 0.403, 'speaker': None}, {'text': 'ya', 'start': 73894, 'end': 73934, 'confidence': 0.04, 'speaker': None}, {'text': 'ahora', 'start': 73974, 'end': 74194, 'confidence': 0.645, 'speaker': None}, {'text': 'nadie', 'start': 74214, 'end': 74534, 'confidence': 0.609, 'speaker': None}, {'text': 'nos', 'start': 74554, 'end': 74654, 'confidence': 0.606, 'speaker': None}, {'text': 'diga', 'start': 74694, 'end': 75014, 'confidence': 0.787, 'speaker': None}, {'text': 'que', 'start': 75054, 'end': 75154, 'confidence': 0.68, 'speaker': None}, {'text': 'no', 'start': 75194, 'end': 75274, 'confidence': 0.78, 'speaker': None}, {'text': 'soy', 'start': 75314, 'end': 75495, 'confidence': 0.605, 'speaker': None}, {'text': 'ejemplo', 'start': 75535, 'end': 75895, 'confidence': 0.96, 'speaker': None}, {'text': 'Y', 'start': 75915, 'end': 75935, 'confidence': 0.022, 'speaker': None}, {'text': "pa'", 'start': 76215, 'end': 76335, 'confidence': 0.626, 'speaker': None}, {'text': 'que', 'start': 76355, 'end': 76475, 'confidence': 0.382, 'speaker': None}, {'text': 'nunca', 'start': 76495, 'end': 76775, 'confidence': 0.59, 'speaker': None}, {'text': 'más', 'start': 76815, 'end': 76975, 'confidence': 0.609, 'speaker': None}, {'text': 'digan', 'start': 76995, 'end': 77235, 'confidence': 0.579, 'speaker': None}, {'text': 'que', 'start': 77295, 'end': 77355, 'confidence': 0.52, 'speaker': None}, {'text': 'el', 'start': 77375, 'end': 77455, 'confidence': 0.496, 'speaker': None}, {'text': 'Freestyle', 'start': 77475, 'end': 77815, 'confidence': 0.385, 'speaker': None}, {'text': 'está', 'start': 77855, 'end': 78096, 'confidence': 0.758, 'speaker': None}, {'text': 'muerto', 'start': 78176, 'end': 78556, 'confidence': 0.757, 'speaker': None}, {'text': '¡Tiempo!', 'start': 79696, 'end': 80577, 'confidence': 0.535, 'speaker': None}, {'text': '¡Muya!', 'start': 80617, 'end': 81317, 'confidence': 0.617, 'speaker': None}, {'text': '¡Muya!', 'start': 81357, 'end': 81497, 'confidence': 0.278, 'speaker': None}, {'text': '¡Muya!', 'start': 81537, 'end': 81897, 'confidence': 0.403, 'speaker': None}, {'text': 'Hermano...', 'start': 82217, 'end': 83778, 'confidence': 0.557, 'speaker': None}, {'text': 'Sí,', 'start': 84841, 'end': 84981, 'confidence': 0.975, 'speaker': None}, {'text': 'como', 'start': 85041, 'end': 85202, 'confidence': 0.738, 'speaker': None}, {'text': 'al', 'start': 85242, 'end': 85302, 'confidence': 0.869, 'speaker': None}, {'text': 'principio', 'start': 85342, 'end': 85722, 'confidence': 0.858, 'speaker': None}, {'text': 'de', 'start': 85762, 'end': 85842, 'confidence': 0.526, 'speaker': None}, {'text': 'mi', 'start': 85902, 'end': 85962, 'confidence': 0.942, 'speaker': None}, {'text': 'carrera.', 'start': 86022, 'end': 86383, 'confidence': 0.899, 'speaker': None}, {'text': 'Tanto', 'start': 86903, 'end': 87124, 'confidence': 0.896, 'speaker': None}, {'text': 'le', 'start': 87184, 'end': 87284, 'confidence': 0.903, 'speaker': None}, {'text': 'duele', 'start': 87304, 'end': 87564, 'confidence': 0.906, 'speaker': None}, {'text': 'que', 'start': 87584, 'end': 87684, 'confidence': 0.492, 'speaker': None}, {'text': 'cuando', 'start': 87724, 'end': 87924, 'confidence': 0.824, 'speaker': None}, {'text': 'aparecí', 'start': 87944, 'end': 88285, 'confidence': 0.894, 'speaker': None}, {'text': 'yo,', 'start': 88305, 'end': 88445, 'confidence': 0.553, 'speaker': None}, {'text': 'el', 'start': 88485, 'end': 88565, 'confidence': 0.746, 'speaker': None}, {'text': 'favorito', 'start': 88585, 'end': 89006, 'confidence': 0.96, 'speaker': None}, {'text': 'dejó', 'start': 89066, 'end': 89286, 'confidence': 0.888, 'speaker': None}, {'text': 'de', 'start': 89326, 'end': 89406, 'confidence': 0.772, 'speaker': None}, {'text': 'ser', 'start': 89466, 'end': 89606, 'confidence': 0.966, 'speaker': None}, {'text': 'Teorema.', 'start': 89666, 'end': 90207, 'confidence': 0.92, 'speaker': None}, {'text': 'Este', 'start': 92569, 'end': 92710, 'confidence': 0.774, 'speaker': None}, {'text': 'hace', 'start': 92750, 'end': 92890, 'confidence': 0.835, 'speaker': None}, {'text': 'tantas', 'start': 92930, 'end': 93150, 'confidence': 0.791, 'speaker': None}, {'text': 'flexiones', 'start': 93210, 'end': 93590, 'confidence': 0.653, 'speaker': None}, {'text': 'en', 'start': 93631, 'end': 93711, 'confidence': 0.923, 'speaker': None}, {'text': 'el', 'start': 93751, 'end': 93831, 'confidence': 0.984, 'speaker': None}, {'text': 'escenario', 'start': 93871, 'end': 94351, 'confidence': 0.926, 'speaker': None}, {'text': 'que', 'start': 94371, 'end': 94431, 'confidence': 0.001, 'speaker': None}, {'text': 'va', 'start': 94872, 'end': 94952, 'confidence': 0.866, 'speaker': None}, {'text': 'más', 'start': 94992, 'end': 95072, 'confidence': 0.392, 'speaker': None}, {'text': 'al', 'start': 95132, 'end': 95192, 'confidence': 0.966, 'speaker': None}, {'text': 'gym', 'start': 95212, 'end': 95392, 'confidence': 0.536, 'speaker': None}, {'text': 'que', 'start': 95432, 'end': 95493, 'confidence': 0.984, 'speaker': None}, {'text': 'a', 'start': 95513, 'end': 95533, 'confidence': 0.0, 'speaker': None}, {'text': 'la', 'start': 95553, 'end': 95613, 'confidence': 0.518, 'speaker': None}, {'text': 'escuela.', 'start': 95633, 'end': 95993, 'confidence': 0.941, 'speaker': None}, {'text': 'Así', 'start': 96834, 'end': 97014, 'confidence': 0.955, 'speaker': None}, {'text': 'que,', 'start': 97074, 'end': 97174, 'confidence': 0.861, 'speaker': None}, {'text': 'para', 'start': 97254, 'end': 97354, 'confidence': 0.508, 'speaker': None}, {'text': 'que', 'start': 97375, 'end': 97455, 'confidence': 0.912, 'speaker': None}, {'text': 'no', 'start': 97475, 'end': 97535, 'confidence': 0.818, 'speaker': None}, {'text': 'te', 'start': 97635, 'end': 97695, 'confidence': 0.972, 'speaker': None}, {'text': 'duela', 'start': 97735, 'end': 97935, 'confidence': 0.719, 'speaker': None}, {'text': 'tanto,', 'start': 97975, 'end': 98195, 'confidence': 0.843, 'speaker': None}, {'text': 'yo', 'start': 98235, 'end': 98336, 'confidence': 0.684, 'speaker': None}, {'text': 'te', 'start': 98376, 'end': 98436, 'confidence': 0.838, 'speaker': None}, {'text': 'traje', 'start': 98496, 'end': 98736, 'confidence': 0.829, 'speaker': None}, {'text': 'rodillera.', 'start': 98836, 'end': 99337, 'confidence': 0.936, 'speaker': None}, {'text': '¡Puro,', 'start': 99377, 'end': 101018, 'confidence': 0.794, 'speaker': None}, {'text': 'puro!', 'start': 101058, 'end': 101279, 'confidence': 0.348, 'speaker': None}, {'text': '3,', 'start': 101289, 'end': 102150, 'confidence': 0.5, 'speaker': None}, {'text': '2,', 'start': 102150, 'end': 103011, 'confidence': 0.5, 'speaker': None}, {'text': '1,', 'start': 103011, 'end': 103872, 'confidence': 0.5, 'speaker': None}, {'text': 'tiempo.', 'start': 103882, 'end': 105384, 'confidence': 0.639, 'speaker': None}, {'text': 'Te', 'start': 105424, 'end': 105544, 'confidence': 0.588, 'speaker': None}, {'text': 'voy', 'start': 105604, 'end': 105744, 'confidence': 0.681, 'speaker': None}, {'text': 'a', 'start': 105804, 'end': 105864, 'confidence': 0.623, 'speaker': None}, {'text': 'ganar,', 'start': 105904, 'end': 106164, 'confidence': 0.762, 'speaker': None}, {'text': 'guacho,', 'start': 106204, 'end': 106565, 'confidence': 0.668, 'speaker': None}, {'text': 'y', 'start': 106765, 'end': 106825, 'confidence': 0.64, 'speaker': None}, {'text': 'no', 'start': 106865, 'end': 106925, 'confidence': 0.564, 'speaker': None}, {'text': 'es', 'start': 106965, 'end': 107025, 'confidence': 0.627, 'speaker': None}, {'text': 'nada', 'start': 107065, 'end': 107305, 'confidence': 0.526, 'speaker': None}, {'text': 'personal.', 'start': 107385, 'end': 107846, 'confidence': 0.811, 'speaker': None}, {'text': 'Vos', 'start': 108026, 'end': 108146, 'confidence': 0.617, 'speaker': None}, {'text': 'mismo', 'start': 108186, 'end': 108446, 'confidence': 0.523, 'speaker': None}, {'text': 'sabías', 'start': 108486, 'end': 108787, 'confidence': 0.573, 'speaker': None}, {'text': 'que', 'start': 108907, 'end': 109007, 'confidence': 0.336, 'speaker': None}, {'text': 'esto', 'start': 109047, 'end': 109207, 'confidence': 0.844, 'speaker': None}, {'text': 'ya', 'start': 109247, 'end': 109367, 'confidence': 0.651, 'speaker': None}, {'text': 'tenía', 'start': 109427, 'end': 109748, 'confidence': 0.719, 'speaker': None}, {'text': 'que', 'start': 109828, 'end': 109928, 'confidence': 0.885, 'speaker': None}, {'text': 'pasar.', 'start': 109988, 'end': 110468, 'confidence': 0.699, 'speaker': None}, {'text': 'Por', 'start': 110528, 'end': 110668, 'confidence': 0.808, 'speaker': None}, {'text': 'ahí', 'start': 110688, 'end': 110789, 'confidence': 0.229, 'speaker': None}, {'text': 'es', 'start': 110829, 'end': 110909, 'confidence': 0.568, 'speaker': None}, {'text': 'que', 'start': 110969, 'end': 111089, 'confidence': 0.711, 'speaker': None}, {'text': 'ellos', 'start': 111149, 'end': 111329, 'confidence': 0.574, 'speaker': None}, {'text': 'quieren', 'start': 111449, 'end': 111729, 'confidence': 0.844, 'speaker': None}, {'text': 'que', 'start': 111789, 'end': 111890, 'confidence': 0.781, 'speaker': None}, {'text': 'gane', 'start': 111970, 'end': 112250, 'confidence': 0.689, 'speaker': None}, {'text': 'la', 'start': 112270, 'end': 112370, 'confidence': 0.762, 'speaker': None}, {'text': 'nacional.', 'start': 112430, 'end': 112870, 'confidence': 0.948, 'speaker': None}, {'text': 'Yo', 'start': 113071, 'end': 113211, 'confidence': 0.592, 'speaker': None}, {'text': 'soy', 'start': 113231, 'end': 113391, 'confidence': 0.58, 'speaker': None}, {'text': 'el', 'start': 113431, 'end': 113531, 'confidence': 0.594, 'speaker': None}, {'text': 'que', 'start': 113551, 'end': 113671, 'confidence': 0.358, 'speaker': None}, {'text': 'necesitan', 'start': 113691, 'end': 114252, 'confidence': 0.614, 'speaker': None}, {'text': 'para', 'start': 114372, 'end': 114532, 'confidence': 0.775, 'speaker': None}, {'text': 'la', 'start': 114592, 'end': 114672, 'confidence': 0.666, 'speaker': None}, {'text': 'internacional.', 'start': 114732, 'end': 116854, 'confidence': 0.74, 'speaker': None}, {'text': 'Acabo', 'start': 116934, 'end': 117294, 'confidence': 0.702, 'speaker': None}, {'text': 'con', 'start': 117334, 'end': 117495, 'confidence': 0.596, 'speaker': None}, {'text': 'tu', 'start': 117515, 'end': 117655, 'confidence': 0.726, 'speaker': None}, {'text': 'carrera.', 'start': 117695, 'end': 118155, 'confidence': 0.772, 'speaker': None}, {'text': 'Desde', 'start': 118475, 'end': 118736, 'confidence': 0.615, 'speaker': None}, {'text': 'ahora', 'start': 118796, 'end': 118976, 'confidence': 0.822, 'speaker': None}, {'text': 'es', 'start': 119136, 'end': 119196, 'confidence': 0.638, 'speaker': None}, {'text': 'menor,', 'start': 119276, 'end': 119717, 'confidence': 0.781, 'speaker': None}, {'text': 'ya', 'start': 119757, 'end': 119857, 'confidence': 0.859, 'speaker': None}, {'text': 'no', 'start': 119897, 'end': 119957, 'confidence': 0.896, 'speaker': None}, {'text': 'es', 'start': 120017, 'end': 120057, 'confidence': 0.498, 'speaker': None}, {'text': 'teorema.', 'start': 120097, 'end': 120718, 'confidence': 0.709, 'speaker': None}, {'text': 'Hasta', 'start': 121018, 'end': 121298, 'confidence': 0.804, 'speaker': None}, {'text': 'vos', 'start': 121338, 'end': 121518, 'confidence': 0.639, 'speaker': None}, {'text': 'lo', 'start': 121578, 'end': 121698, 'confidence': 0.8, 'speaker': None}, {'text': 'sabías', 'start': 121779, 'end': 122199, 'confidence': 0.653, 'speaker': None}, {'text': 'y', 'start': 122239, 'end': 122279, 'confidence': 0.509, 'speaker': None}, {'text': 'te', 'start': 122319, 'end': 122399, 'confidence': 0.812, 'speaker': None}, {'text': 'desesperas.', 'start': 122439, 'end': 123100, 'confidence': 0.646, 'speaker': None}, {'text': 'Hasta', 'start': 123120, 'end': 123300, 'confidence': 0.263, 'speaker': None}, {'text': 'mis', 'start': 123320, 'end': 123460, 'confidence': 0.647, 'speaker': None}, {'text': 'compañeros', 'start': 123480, 'end': 124021, 'confidence': 0.507, 'speaker': None}, {'text': 'quieren', 'start': 124101, 'end': 124401, 'confidence': 0.625, 'speaker': None}, {'text': 'que', 'start': 124421, 'end': 124521, 'confidence': 0.704, 'speaker': None}, {'text': 'represente', 'start': 124561, 'end': 125061, 'confidence': 0.874, 'speaker': None}, {'text': 'la', 'start': 125142, 'end': 125202, 'confidence': 0.744, 'speaker': None}, {'text': 'bandera.', 'start': 125262, 'end': 125662, 'confidence': 0.559, 'speaker': None}, {'text': '¡Oye!', 'start': 133864, 'end': 133924, 'confidence': 0.024, 'speaker': None}, {'text': 'Hermano,', 'start': 158216, 'end': 159417, 'confidence': 0.713, 'speaker': None}, {'text': 'eso', 'start': 159457, 'end': 159637, 'confidence': 0.774, 'speaker': None}, {'text': 'es', 'start': 159717, 'end': 159777, 'confidence': 0.428, 'speaker': None}, {'text': 'una', 'start': 159817, 'end': 159917, 'confidence': 0.853, 'speaker': None}, {'text': 'ironía,', 'start': 159997, 'end': 160397, 'confidence': 0.9, 'speaker': None}, {'text': 'si', 'start': 160417, 'end': 160457, 'confidence': 0.0, 'speaker': None}, {'text': 'hasta', 'start': 160477, 'end': 161057, 'confidence': 0.55, 'speaker': None}, {'text': 'vos', 'start': 161097, 'end': 161257, 'confidence': 0.82, 'speaker': None}, {'text': 'sabí', 'start': 161277, 'end': 161698, 'confidence': 0.66, 'speaker': None}, {'text': 'que', 'start': 161918, 'end': 162018, 'confidence': 0.269, 'speaker': None}, {'text': 'yo', 'start': 162058, 'end': 162198, 'confidence': 0.708, 'speaker': None}, {'text': 'tenía', 'start': 162258, 'end': 162578, 'confidence': 0.697, 'speaker': None}, {'text': 'que', 'start': 162638, 'end': 162718, 'confidence': 0.625, 'speaker': None}, {'text': 'ir', 'start': 162758, 'end': 162858, 'confidence': 0.615, 'speaker': None}, {'text': 'a', 'start': 162878, 'end': 162898, 'confidence': 0.892, 'speaker': None}, {'text': 'Trilogía,', 'start': 162958, 'end': 163558, 'confidence': 0.846, 'speaker': None}, {'text': 'yo', 'start': 163578, 'end': 163618, 'confidence': 0.015, 'speaker': None}, {'text': 'mejor', 'start': 164079, 'end': 164299, 'confidence': 0.921, 'speaker': None}, {'text': 'que', 'start': 164339, 'end': 164419, 'confidence': 0.827, 'speaker': None}, {'text': 'el', 'start': 164439, 'end': 164499, 'confidence': 0.579, 'speaker': None}, {'text': 'Kaiser', 'start': 164539, 'end': 164879, 'confidence': 0.363, 'speaker': None}, {'text': 'lo', 'start': 164919, 'end': 165159, 'confidence': 0.544, 'speaker': None}, {'text': 'representaría,', 'start': 165219, 'end': 165999, 'confidence': 0.862, 'speaker': None}, {'text': 'devuélvete', 'start': 166140, 'end': 166680, 'confidence': 0.476, 'speaker': None}, {'text': 'al', 'start': 166700, 'end': 166760, 'confidence': 0.18, 'speaker': None}, {'text': 'anterior', 'start': 166840, 'end': 167160, 'confidence': 0.761, 'speaker': None}, {'text': 'que', 'start': 167260, 'end': 167340, 'confidence': 0.275, 'speaker': None}, {'text': 'esta', 'start': 167360, 'end': 167600, 'confidence': 0.517, 'speaker': None}, {'text': 'generación', 'start': 167620, 'end': 168260, 'confidence': 0.663, 'speaker': None}, {'text': 'es', 'start': 169461, 'end': 169541, 'confidence': 0.323, 'speaker': None}, {'text': 'mía.', 'start': 169581, 'end': 170822, 'confidence': 0.768, 'speaker': None}, {'text': 'Y', 'start': 170902, 'end': 170922, 'confidence': 0.073, 'speaker': None}, {'text': 'era', 'start': 171062, 'end': 171182, 'confidence': 0.658, 'speaker': None}, {'text': 'compañero,', 'start': 171282, 'end': 171882, 'confidence': 0.901, 'speaker': None}, {'text': 'la', 'start': 172242, 'end': 172322, 'confidence': 0.512, 'speaker': None}, {'text': 'verdad', 'start': 172342, 'end': 172642, 'confidence': 0.63, 'speaker': None}, {'text': 'le', 'start': 172702, 'end': 172802, 'confidence': 0.925, 'speaker': None}, {'text': 'ganó', 'start': 172822, 'end': 173022, 'confidence': 0.725, 'speaker': None}, {'text': 'en', 'start': 173062, 'end': 173163, 'confidence': 0.45, 'speaker': None}, {'text': 'un', 'start': 173223, 'end': 173283, 'confidence': 0.217, 'speaker': None}, {'text': 'segundo,', 'start': 173303, 'end': 173783, 'confidence': 0.662, 'speaker': None}, {'text': 'te', 'start': 173803, 'end': 173843, 'confidence': 0.003, 'speaker': None}, {'text': 'creía', 'start': 174223, 'end': 174463, 'confidence': 0.426, 'speaker': None}, {'text': 'el', 'start': 174503, 'end': 174563, 'confidence': 0.814, 'speaker': None}, {'text': 'mejor', 'start': 174603, 'end': 174843, 'confidence': 0.912, 'speaker': None}, {'text': 'de', 'start': 174883, 'end': 175003, 'confidence': 0.64, 'speaker': None}, {'text': 'Chile,', 'start': 175063, 'end': 175303, 'confidence': 0.39, 'speaker': None}, {'text': 'pero', 'start': 175323, 'end': 175564, 'confidence': 0.529, 'speaker': None}, {'text': 'fuiste', 'start': 175604, 'end': 175864, 'confidence': 0.322, 'speaker': None}, {'text': 'absurdo,', 'start': 175884, 'end': 176304, 'confidence': 0.745, 'speaker': None}, {'text': 'el', 'start': 176324, 'end': 176364, 'confidence': 0.007, 'speaker': None}, {'text': 'mejor', 'start': 176784, 'end': 177044, 'confidence': 0.945, 'speaker': None}, {'text': 'de', 'start': 177064, 'end': 177244, 'confidence': 0.682, 'speaker': None}, {'text': 'Chile', 'start': 177284, 'end': 177604, 'confidence': 0.38, 'speaker': None}, {'text': 'contra', 'start': 177624, 'end': 177885, 'confidence': 0.503, 'speaker': None}, {'text': 'el', 'start': 177925, 'end': 177965, 'confidence': 0.024, 'speaker': None}, {'text': 'mejor', 'start': 178005, 'end': 178265, 'confidence': 0.934, 'speaker': None}, {'text': 'del', 'start': 178305, 'end': 178465, 'confidence': 0.802, 'speaker': None}, {'text': 'mundo.', 'start': 178505, 'end': 178865, 'confidence': 0.52, 'speaker': None}, {'text': 'Se', 'start': 181626, 'end': 181786, 'confidence': 0.621, 'speaker': None}, {'text': 'lo', 'start': 181826, 'end': 181926, 'confidence': 0.36, 'speaker': None}, {'text': 'damos', 'start': 181986, 'end': 182266, 'confidence': 0.592, 'speaker': None}, {'text': 'en', 'start': 182326, 'end': 182446, 'confidence': 0.702, 'speaker': None}, {'text': 'tres,', 'start': 183087, 'end': 183187, 'confidence': 0.168, 'speaker': None}, {'text': 'dos,', 'start': 183247, 'end': 183367, 'confidence': 0.391, 'speaker': None}, {'text': 'uno.', 'start': 183387, 'end': 183627, 'confidence': 0.295, 'speaker': None}, {'text': 'Donde', 'start': 194865, 'end': 195625, 'confidence': 0.536, 'speaker': None}, {'text': 'las', 'start': 195705, 'end': 195786, 'confidence': 0.279, 'speaker': None}, {'text': 'vacas', 'start': 195826, 'end': 196106, 'confidence': 0.509, 'speaker': None}, {'text': 'queman,', 'start': 196126, 'end': 196446, 'confidence': 0.536, 'speaker': None}, {'text': 'rima', 'start': 196546, 'end': 196746, 'confidence': 0.775, 'speaker': None}, {'text': 'Julián', 'start': 196806, 'end': 197166, 'confidence': 0.688, 'speaker': None}, {'text': 'de', 'start': 197186, 'end': 197266, 'confidence': 0.276, 'speaker': None}, {'text': 'la', 'start': 197286, 'end': 197386, 'confidence': 0.7, 'speaker': None}, {'text': 'perra', 'start': 197426, 'end': 197686, 'confidence': 0.667, 'speaker': None}, {'text': 'Y', 'start': 197706, 'end': 197726, 'confidence': 0.086, 'speaker': None}, {'text': 'he', 'start': 198047, 'end': 198127, 'confidence': 0.316, 'speaker': None}, {'text': 'perdido', 'start': 198167, 'end': 198507, 'confidence': 0.81, 'speaker': None}, {'text': 'batallas,', 'start': 198567, 'end': 198987, 'confidence': 0.634, 'speaker': None}, {'text': 'pero', 'start': 199187, 'end': 199307, 'confidence': 0.472, 'speaker': None}, {'text': 'he', 'start': 199327, 'end': 199427, 'confidence': 0.371, 'speaker': None}, {'text': 'ganado', 'start': 199447, 'end': 199767, 'confidence': 0.869, 'speaker': None}, {'text': 'la', 'start': 199787, 'end': 199867, 'confidence': 0.557, 'speaker': None}, {'text': 'guerra', 'start': 199967, 'end': 200168, 'confidence': 0.23, 'speaker': None}, {'text': 'Donde', 'start': 200348, 'end': 200768, 'confidence': 0.73, 'speaker': None}, {'text': 'las', 'start': 200808, 'end': 200888, 'confidence': 0.651, 'speaker': None}, {'text': 'papas', 'start': 200948, 'end': 201168, 'confidence': 0.57, 'speaker': None}, {'text': 'queman,', 'start': 201188, 'end': 201528, 'confidence': 0.482, 'speaker': None}, {'text': 'se', 'start': 201648, 'end': 201788, 'confidence': 0.556, 'speaker': None}, {'text': 'las', 'start': 201808, 'end': 201888, 'confidence': 0.579, 'speaker': None}, {'text': 'dije', 'start': 201928, 'end': 202128, 'confidence': 0.702, 'speaker': None}, {'text': 'en', 'start': 202148, 'end': 202228, 'confidence': 0.316, 'speaker': None}, {'text': 'Al', 'start': 202268, 'end': 202328, 'confidence': 0.922, 'speaker': None}, {'text': 'Martín', 'start': 202369, 'end': 202769, 'confidence': 0.83, 'speaker': None}, {'text': '¿No', 'start': 202889, 'end': 202969, 'confidence': 0.81, 'speaker': None}, {'text': 'te', 'start': 203009, 'end': 203089, 'confidence': 0.436, 'speaker': None}, {'text': 'acordas', 'start': 203109, 'end': 203429, 'confidence': 0.613, 'speaker': None}, {'text': 'que', 'start': 203469, 'end': 203629, 'confidence': 0.587, 'speaker': None}, {'text': 'ganaste', 'start': 203649, 'end': 204089, 'confidence': 0.726, 'speaker': None}, {'text': 'FMS', 'start': 204109, 'end': 204550, 'confidence': 0.499, 'speaker': None}, {'text': 'gracias', 'start': 204590, 'end': 204910, 'confidence': 0.806, 'speaker': None}, {'text': 'a', 'start': 204970, 'end': 205010, 'confidence': 0.492, 'speaker': None}, {'text': 'mí?', 'start': 205130, 'end': 205310, 'confidence': 0.367, 'speaker': None}, {'text': 'y', 'start': 214088, 'end': 214128, 'confidence': 0.448, 'speaker': None}, {'text': 'el', 'start': 214148, 'end': 214348, 'confidence': 0.671, 'speaker': None}, {'text': 'próximo', 'start': 214388, 'end': 214728, 'confidence': 0.485, 'speaker': None}, {'text': 'te', 'start': 214828, 'end': 214929, 'confidence': 0.546, 'speaker': None}, {'text': 'descendí.', 'start': 214969, 'end': 215889, 'confidence': 0.73, 'speaker': None}, {'text': 'Me', 'start': 216610, 'end': 216690, 'confidence': 0.305, 'speaker': None}, {'text': 'descendiste,', 'start': 216730, 'end': 217290, 'confidence': 0.605, 'speaker': None}, {'text': 'te', 'start': 217550, 'end': 217650, 'confidence': 0.747, 'speaker': None}, {'text': 'salió', 'start': 217690, 'end': 217970, 'confidence': 0.828, 'speaker': None}, {'text': 'mal.', 'start': 218050, 'end': 218311, 'confidence': 0.892, 'speaker': None}, {'text': 'Vos', 'start': 218611, 'end': 218771, 'confidence': 0.552, 'speaker': None}, {'text': 'me', 'start': 218811, 'end': 218911, 'confidence': 0.404, 'speaker': None}, {'text': 'descendiste,', 'start': 218931, 'end': 219531, 'confidence': 0.68, 'speaker': None}, {'text': 'pero', 'start': 219591, 'end': 219812, 'confidence': 0.77, 'speaker': None}, {'text': 'yo', 'start': 219852, 'end': 219992, 'confidence': 0.786, 'speaker': None}, {'text': 'te', 'start': 220052, 'end': 220152, 'confidence': 0.66, 'speaker': None}, {'text': 'gané', 'start': 220192, 'end': 220452, 'confidence': 0.586, 'speaker': None}, {'text': 'igual.', 'start': 220492, 'end': 221012, 'confidence': 0.877, 'speaker': None}, {'text': 'Al', 'start': 221933, 'end': 222013, 'confidence': 0.314, 'speaker': None}, {'text': 'final', 'start': 222053, 'end': 222333, 'confidence': 0.787, 'speaker': None}, {'text': 'no', 'start': 222373, 'end': 222473, 'confidence': 0.426, 'speaker': None}, {'text': 'le', 'start': 222513, 'end': 222593, 'confidence': 0.613, 'speaker': None}, {'text': 'sale', 'start': 222653, 'end': 222893, 'confidence': 0.728, 'speaker': None}, {'text': 'tan', 'start': 222954, 'end': 223114, 'confidence': 0.746, 'speaker': None}, {'text': 'mal.', 'start': 223174, 'end': 223434, 'confidence': 0.856, 'speaker': None}, {'text': 'Tú', 'start': 223794, 'end': 223834, 'confidence': 0.001, 'speaker': None}, {'text': 'eres', 'start': 223854, 'end': 224054, 'confidence': 0.608, 'speaker': None}, {'text': 'referente,', 'start': 224114, 'end': 224675, 'confidence': 0.961, 'speaker': None}, {'text': 'para', 'start': 224755, 'end': 224935, 'confidence': 0.93, 'speaker': None}, {'text': 'mí', 'start': 225015, 'end': 225155, 'confidence': 0.764, 'speaker': None}, {'text': 'no', 'start': 225175, 'end': 225275, 'confidence': 0.737, 'speaker': None}, {'text': 'eres', 'start': 225295, 'end': 225475, 'confidence': 0.467, 'speaker': None}, {'text': 'rival.', 'start': 225555, 'end': 226176, 'confidence': 0.843, 'speaker': None}, {'text': 'Menor', 'start': 226236, 'end': 226596, 'confidence': 0.777, 'speaker': None}, {'text': 'decreta', 'start': 226616, 'end': 226936, 'confidence': 0.69, 'speaker': None}, {'text': 'el', 'start': 226976, 'end': 227036, 'confidence': 0.939, 'speaker': None}, {'text': 'éxito', 'start': 227076, 'end': 227436, 'confidence': 0.559, 'speaker': None}, {'text': 'y', 'start': 227456, 'end': 227476, 'confidence': 0.007, 'speaker': None}, {'text': 'luego', 'start': 227636, 'end': 227877, 'confidence': 0.717, 'speaker': None}, {'text': 'lo', 'start': 227957, 'end': 228057, 'confidence': 0.838, 'speaker': None}, {'text': 'concreta.', 'start': 228137, 'end': 228677, 'confidence': 0.942, 'speaker': None}, {'text': 'Así', 'start': 228697, 'end': 229217, 'confidence': 0.434, 'speaker': None}, {'text': 'de', 'start': 229257, 'end': 229358, 'confidence': 0.826, 'speaker': None}, {'text': 'fácil,', 'start': 229418, 'end': 229778, 'confidence': 0.759, 'speaker': None}, {'text': 'guacho,', 'start': 229838, 'end': 230158, 'confidence': 0.588, 'speaker': None}, {'text': 'yo', 'start': 230198, 'end': 230338, 'confidence': 0.616, 'speaker': None}, {'text': 'llego', 'start': 230378, 'end': 230618, 'confidence': 0.701, 'speaker': None}, {'text': 'a', 'start': 230658, 'end': 230698, 'confidence': 0.446, 'speaker': None}, {'text': 'la', 'start': 230718, 'end': 230778, 'confidence': 0.444, 'speaker': None}, {'text': 'meta.', 'start': 230918, 'end': 231259, 'confidence': 0.855, 'speaker': None}, {'text': 'Pon', 'start': 231679, 'end': 231819, 'confidence': 0.66, 'speaker': None}, {'text': 'la', 'start': 231879, 'end': 231959, 'confidence': 0.861, 'speaker': None}, {'text': 'bandera,', 'start': 232019, 'end': 232499, 'confidence': 0.773, 'speaker': None}, {'text': 'eres', 'start': 232740, 'end': 232940, 'confidence': 0.694, 'speaker': None}, {'text': 'terrible,', 'start': 233000, 'end': 233340, 'confidence': 0.813, 'speaker': None}, {'text': 'jueta.', 'start': 233460, 'end': 233740, 'confidence': 0.591, 'speaker': None}, {'text': 'No', 'start': 233780, 'end': 233880, 'confidence': 0.764, 'speaker': None}, {'text': 'soy', 'start': 233900, 'end': 234060, 'confidence': 0.486, 'speaker': None}, {'text': 'ni', 'start': 234100, 'end': 234181, 'confidence': 0.51, 'speaker': None}, {'text': 'vieja', 'start': 234221, 'end': 234541, 'confidence': 0.736, 'speaker': None}, {'text': 'ni', 'start': 234561, 'end': 234641, 'confidence': 0.54, 'speaker': None}, {'text': 'nueva,', 'start': 234701, 'end': 234961, 'confidence': 0.652, 'speaker': None}, {'text': 'es', 'start': 235001, 'end': 235041, 'confidence': 0.123, 'speaker': None}, {'text': 'la', 'start': 235081, 'end': 235161, 'confidence': 0.732, 'speaker': None}, {'text': 'generación', 'start': 235221, 'end': 235782, 'confidence': 0.899, 'speaker': None}, {'text': 'completa.', 'start': 235902, 'end': 236482, 'confidence': 0.97, 'speaker': None}, {'text': '¡Tiempo!', 'start': 245960, 'end': 246421, 'confidence': 0.532, 'speaker': None}]
        """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data.get("words", {})


def create_paragraphs_for_timestamps(_transcript_words: list[dict], _time_stamps: list[tuple]):
    """
    Create a list of paragraphs (lines) using a list of words and pairing it to corresponding time stamps.
    :param _transcript_words: List o words
    :param _time_stamps: List of the time stamps to match the words.
    :return: list of paragraphs (lines)
    """
    paragraphs = []

    # Create a copy of the word list to keep track of used words
    remaining_words = _transcript_words.copy()

    for start_time, end_time in _time_stamps:
        paragraph_words = []

        # Iterate over the copy of the word list to avoid modifying the original list
        for word in remaining_words[:]:
            if start_time - 50 <= word['start'] <= end_time and start_time <= word['end'] <= end_time + 40:
                paragraph_words.append(word['text'])
                remaining_words.remove(word)  # Remove the used word from the copy

        paragraph = ' '.join(paragraph_words)
        paragraphs.append(paragraph)

    return paragraphs


def load_timestamps(_time_stamps_path) -> list[tuple[str, str]]:
    # Read the time-stamps from the JSON file
    with open(_time_stamps_path, 'r') as json_file:
        time_stamps = json.load(json_file)

    return time_stamps

def create_composed_subtitles(_time_stamps: list[tuple[str, str]], _transcription_path: str, _subtitles_path: str):
    """
    Create composed subtitles with the AEGIS SUB format.
    :param _time_stamps: Time stamps as a list of tuples of strings.
    :param _transcription_path: Path of the clean and parsed transcription.
    :param _subtitles_path: Path to save the composed subtitles.
    :return:
    """

    # Read the transcription from the text file
    with open(_transcription_path, 'r', encoding="utf-8") as transcription_file:
        transcription_lines = transcription_file.read().splitlines()

    # Initialize variables
    subtitles = []
    index = 0

    # Iterate through the time-stamps and create subtitles
    for start_time, end_time in _time_stamps:
        # Ensure there is a corresponding transcription line
        if index < len(transcription_lines):
            subtitle = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,," + transcription_lines[index]
            subtitles.append(subtitle)
            index += 1
        else:
            # If there's no corresponding transcription, create an empty subtitle
            subtitle = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,"
            subtitles.append(subtitle)

    # Write the subtitles to the subtitles file
    with open(_subtitles_path, 'w', encoding="utf-8") as subtitles_file:
        for subtitle in subtitles:
            subtitles_file.write(subtitle + '\n')


def save_paragraphs_to_file(paragraphs, file_path):
    with open(file_path, 'w', encoding="utf-8") as file:
        for line in paragraphs:
            file.write(line + '\n')


def replace_subs(original_path, parsed_path, output_path):
    # Read original file
    with open(original_path, 'r', encoding="utf-8") as f:
        original_lines = f.readlines()

    # Read parsed file
    with open(parsed_path, 'r', encoding="utf-8") as f:
        parsed_lines = f.readlines()

    # Replace subtitle lines in original file with parsed lines
    original_dialogue_start = next(i for i, line in enumerate(original_lines) if line.startswith('Dialogue:'))
    original_dialogue_end = original_dialogue_start + len(parsed_lines)
    original_lines[original_dialogue_start:original_dialogue_end] = parsed_lines

    # Write to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(original_lines)


def parse_aegis_subs(_ass_file: str, _txt_file: str = None) -> str:
    """
    Extract the subtitles from an Aegis Sub file and return them as a formatted string.
    Files with a non Aegis Sub format will still be parsed through, but avoid for potential issues.

    :param _ass_file: Path to the Aegis Sub file.
    :type _ass_file: str
    :param _txt_file: Path to the text file (optional, if you want to save the extracted text).
    :type _txt_file: str, optional

    :return: Formatted subtitles as a string.
    :rtype: str

    Example:
        >>> result = parse_aegis_subs('subtitles.ass')
        >>> print(result)
        Dialogue: 0,0:02:09.13,0:02:12.94,Default,,0,0,0,,Ey, en verdad que tu rima para hacerme bullying no sale tan chida.
        Dialogue: 0,0:02:12.94,0:02:16.81,Default,,0,0,0,,En serio que meterse contra El Menor en batalla es la misión suicida.
    """

    # Define initial values for the utility variables
    extracted_text = ""
    found_dialogues = False

    with open(_ass_file, "r", encoding="utf-8") as file:
        for line in file:
            # If we have found dialogues, continue adding lines to extracted_text
            if found_dialogues:
                extracted_text += line[50::]
            # If the line starts with "Dialogue:", start extracting dialogues
            elif line.strip().startswith("Dialogue:"):
                found_dialogues = True
                extracted_text += line[50::]

    if _txt_file is not None:
        # Save the extracted text to the .txt file if _txt_file is provided
        with open(_txt_file, "w", encoding="utf-8") as output_file:
            output_file.write(extracted_text)
    else:
        # If _txt_file is not provided, do nothing (pass)
        pass

    return extracted_text


# --- PREPARE FOR TRANSLATION --- #
def clean_text(_unparsed_text: str) -> str:
    """
    Cleans the subtitle text and returns only the text.
    :param _unparsed_text: The text to be cleaned. It directly receives the str, not the path.
    :return: clean text
    """
    # Regular expression to match the unwanted parts
    pattern1 = r'\{[^}]*\}'

    # Regular expression to match the entire "Dialogue:" line
    pattern2 = r'Dialogue: \d+,\d+:\d+:\d+\.\d+,\d+:\d+:\d+\.\d+,Default,,\d+,\d+,\d+,,'

    # Remove the unwanted parts from the text using regex
    cleaned_text = re.sub(pattern1, '', _unparsed_text)
    cleaned_text = re.sub(pattern2, '', cleaned_text)
    cleaned_text = cleaned_text.replace("\\N", " ")

    return cleaned_text


def extract_sections_from_subs(spanish_subs) -> tuple[list[str], list[str]]:
    """
    Extract the different sections from subtitles and return them as list of strings, each string is an AegisSub line.
    :param spanish_subs: Path for the subtitles in spanish.
    :return: sections, sections_clean
    """
    # Extract the subtitles
    texto = parse_aegis_subs(spanish_subs)
    texto_limpio = clean_text(texto)

    # List of sections
    sections = re.split(r'\[Section]', texto)
    sections = [section.strip() for section in sections if section.strip()]

    # List of same sections, cleaned and parsed
    sections_clean = re.split(r'\[Section]', texto_limpio)
    sections_clean = [section.strip() for section in sections_clean if section.strip()]

    return sections, sections_clean


def create_subtitulos_object_list(sections, sections_clean) -> list[Subtitulo]:
    subtitulos = []
    for i in range(len(sections_clean)):
        sub = Subtitulo(sections[i], sections_clean[i], "", False)
        subtitulos.append(sub)

    return subtitulos


def save_subtitulos_json(subtitulos: list[Subtitulo], subtitulos_json: str):
    # Convert the list of objects to a list of dictionaries
    subtitulos_dict = [subtitulo.to_dict() for subtitulo in subtitulos]

    # Save to JSON
    with open(subtitulos_json, 'w') as f:
        json.dump(subtitulos_dict, f, indent=4)


def load_subtitulos_json(subtitulos_json) -> list[Subtitulo]:
    # Load from JSON
    with open(subtitulos_json, 'r') as f:
        subtitulos_dict = json.load(f)

    # Convert the list of dictionaries to a list of objects
    subtitulos = [Subtitulo.from_dict(subtitulo) for subtitulo in subtitulos_dict]

    return subtitulos


def check_subtitulos_done(subtitulos: list[Subtitulo]) -> bool:
    """
    Checks whether all the Subtitulo instances inside the subtitulos list are already done.
    :param subtitulos: he list of Subtitulo objects to be checked.
    :return:
    """
    for subtitulo in subtitulos:
        if not subtitulo.done_translating:
            return False
    return True


def combine_subtitles(subtitulos: list[Subtitulo]) -> list[str]:
    """
    It combines the spanish and english subtitles into a single list of strings.
    :param subtitulos: The list of Subtitulo objects that contains all the subtitle sections in both languages.
    :return: A list of strings representing the combined and final subtitles to use.
    """
    subtitulos_finales = []
    count = 0
    flag = False

    if not check_subtitulos_done(subtitulos):
        print("Not all subtitles are translated yet!!")
        exit(0)

    for subtitulo in subtitulos:
        section_spanish = re.split("\n", subtitulo.spanish)  # spanish lines for that section of subs
        section_english = re.split("\n", subtitulo.english)  # english lines for that section of subs
        count = count + 1

        if len(section_spanish) is not len(section_english):
            flag = True
            subtitulo.done_translating = False
            print(f"Flag in position: {count}")

        for i in range(len(section_spanish)):
            if subtitulo.done_translating:
                texto = r"{\c&H00FFFF&}" + section_english[i] + r"{\c&HFFFFFF&}" + "\\N\\N" + section_spanish[i]
            else:
                texto = section_spanish[i]
            subtitulos_finales.append(texto)

    if flag:
        print("Warning: Some subtitles were not correctly translated!")

    return subtitulos_finales


if __name__ == "__main__":
    words = load_words("examples/data.json")
    print(words)

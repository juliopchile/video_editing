import json
import re

import numpy as np
import openai

from functions import open_AI

INITIAL_INSTRUCTION = "Translate the given transcription"

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

    def translate(self):
        if not self.done_translating:
            try:
                #self.english = open_AI.translate_gpt(_api_key=api_key, _message=self.clean_spanish, _prompt=prompt, _model=model)
                self.english = open_AI.translate_text(message=self.clean_spanish, initial_instruction=INITIAL_INSTRUCTION)
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

    #file.close()
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
    recovered_text = []
    found_dialogues = False

    with open(_ass_file, "r", encoding="utf-8") as file:
        for line in file:
            # If we have found dialogues, continue adding lines to extracted_text
            if found_dialogues:
                parts = line.split(",")
                if len(parts) >= 10:  # Ensure that the line has at least 10 parts
                    text = ",".join(parts[9:])  # Join the text parts
                    recovered_text.append(text.strip())
            # If the line starts with "Dialogue:", start extracting dialogues
            elif line.strip().startswith("Dialogue:"):
                found_dialogues = True
                parts = line.split(",")
                if len(parts) >= 10:  # Ensure that the line has at least 10 parts
                    text = ",".join(parts[9:])  # Join the text parts
                    recovered_text.append(text.strip())
                    
    recovered_text_str = "\n".join(recovered_text)

    if _txt_file is not None:
        # Save the extracted text to the .txt file if _txt_file is provided
        with open(_txt_file, "w", encoding="utf-8") as output_file:
            output_file.write(recovered_text_str)
    else:
        # If _txt_file is not provided, do nothing (pass)
        pass

    return recovered_text_str


# --- PREPARE FOR TRANSLATION --- #
def clean_text(_unparsed_text: str) -> str:
    """
    Cleans the subtitle text and returns only the text.
    :param _unparsed_text: The text to be cleaned. It directly receives the str, not the path.
    :return: clean text
    """
    # Regular expression to match the unwanted parts
    pattern = r'\{[^}]*\}'

    # Remove the unwanted parts from the text using regex
    cleaned_text = re.sub(pattern, '', _unparsed_text)
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

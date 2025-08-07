import os

from tqdm import tqdm

import functions.ffmpeg_functions as ffmpeg
import functions.utility_functions as util
from functions.assembly_AI import AssemblyAI


# ? PASO 0: CONVERTIR VIDEO A AUDIO
def video2audio(video="bin/video", audio="bin/audio", extension="wav"):
    """
    Convierte todos los videos en la carpeta **video** a audios en la
    carpeta **audio**. Se salta a los archivos que ya existen en la
    carpeta **audio**.

    :param str video: directorio de los videos a procesar.
    :param str audio: directorio donde guardar los audios procesados.
    :param str extension: extensión del audio a guardar.
    """
    video_path = os.path.normpath(video)
    audio_path = os.path.normpath(audio)
    ffmpeg.process_videos(video_path, audio_path, extension)


# ? PASO 1: TRANSCRIBIR AUDIO
def manage_transcribe(file, audio_file, data_path, extant_transcripts):
    """
    Gestiona el proceso de transcripción de un audio.
    Usado por manage_transcriptions()
    """
    audio_name, _ = os.path.splitext(file)  # get only the audio name
    data_file = os.path.join(data_path, audio_name)  # use that name
    data_file = util.limpiar_nombre_archivo(data_file)

    # Check if the audio file have already been transcribed
    if os.path.basename(data_file + '.json') not in extant_transcripts:
        print(f"Transcribing audio: {file}")
        transcribe_and_save_data(audio_file, data_file + '.json')
    else:
        print(f"Skipped: {file} (Audio already transcribed)")
        # TODO preguntar si quiere realizar la transcripción nuevamente


def manage_transcriptions(audio_path, data_path):
    """
    Gestiona el proceso de transcripción de los audios en **audio_path**
    y son guardados en el directorio **data_path**.
    :param audio_path:
    :param data_path:
    :return:
    """
    # Ensure the paths are valid
    audio_path = os.path.normpath(audio_path)
    data_path = os.path.normpath(data_path)

    # Ensure the data_path directory exists, or create it if necessary
    os.makedirs(data_path, exist_ok=True)

    # Get a list of existing data files in the data_path
    extant_transcripts = set(os.listdir(data_path))

    # Check whether the audio_path corresponds to a directory or a single file
    if os.path.isfile(audio_path):
        file = os.path.basename(audio_path)  # get the audio name + extension
        audio_file = audio_path
        manage_transcribe(file, audio_file, data_path, extant_transcripts)

    elif os.path.isdir(audio_path):
        # Iterate through files in the audio_path directory
        for file in os.listdir(audio_path):
            audio_file = os.path.join(audio_path, file)
            manage_transcribe(file, audio_file, data_path, extant_transcripts)

    else:
        print("No audio file given.")


def transcribe_and_save_data(audio_file, transcription_data):
    """
    Transcribe el audio en **audio_file** y guarda esta data en un archivo JSON **transcription_data**.
    :param audio_file:
    :param transcription_data:
    :return:
    """
    assembly_ai = AssemblyAI()
    assembly_ai.transcribe(audio_file=audio_file)
    assembly_ai.save_words(filename=transcription_data)



def create_transcription_using_timestamps(original_subs, time_stamps_file, transcription_data, transcription_text):
    """
    Se hacen 4 cosas:
        - Se extraen los "time stamps" desde **original_subs** y se guardan en el archivo JSON **time_stamps_file**.
        - Se convierten los tiempos a milisegundos.
        - Se extraen las palabras guardadas anteriormente en **transcription_data**.
        - Se guardan en **transcription_text** los párrafos con las palabras unidas en sus correspondientes tiempos.
    :param original_subs:
    :param time_stamps_file:
    :param transcription_data:
    :param transcription_text:
    :return:
    """
    # Extract the time stamps from aegis sub and save them for later
    time_stamps_str = util.extract_timestamps_from_file(original_subs)
    #util.save_timestamps_to_json(time_stamps_str, time_stamps_file)

    # Convert time_stamps to milliseconds.
    time_stamps_int = util.time_stamps_to_milliseconds(time_stamps_str)

    # Extract the words from the transcription data
    words = util.load_words(transcription_data)

    # Create the paragraphs using the words and time stamps, and save them
    paragraphs = util.create_paragraphs_for_timestamps(words, time_stamps_int)
    util.save_paragraphs_to_file(paragraphs, transcription_text)


def create_updated_subs_ass(time_stamps_file, transcription_text, original_subs, parsed_text, updated_subs):
    """
    Se hacen 3 cosas:
        - Se cargan los "time stamps" en una lista, desde **time_stamps_file**.
        - Se crea un archivo de texto con los subtitles ajustados a los tiempos.
        - Se remplazan los subtítulos originales con los ajustados al tiempo.
    :param time_stamps_file:
    :param transcription_text:
    :param original_subs:
    :param parsed_text:
    :param updated_subs:
    :return:
    """
    # Load time_stamps into a list.
    time_stamps = util.load_timestamps(time_stamps_file)

    # Create a text file with the time-parsed subtitles.
    util.create_composed_subtitles(time_stamps, transcription_text, parsed_text)

    # Replace the original_subs with the new time-parsed ones.
    util.replace_subs(original_subs, parsed_text, updated_subs)


# Paso 2
def create_save_return_subtitles(sections, sections_clean, subtitulos_json):
    """
    Se hacen 2 cosas:
        - Se crea una lista de clase Subtitulo usando las secciones.
        - Se guardan los subtítulos en formato JSON.
    :param list[str] sections: Líneas de los subtítulos, sin limpiar.
    :param list[str] sections_clean: Líneas de subtítulos limpias
    :param str subtitulos_json: Path donde guardar los subtítulos
    :return: Una lista de objetos de la clase Subtitulo.
    """
    # Check if the file already exists
    if os.path.exists(subtitulos_json):
        overwrite = input(
            f"The file {os.path.basename(subtitulos_json)} already exists. Do you want to overwrite it? (yes/no): ").lower()
        if overwrite != 'yes':
            print("Subtitles were not saved.")
            return

    print("Creating and saving Subtitulo objects")

    # Create list of Subtitulo using sections
    subtitulos = util.create_subtitulos_object_list(sections, sections_clean)

    # Save subtitulos list into a file
    util.save_subtitulos_json(subtitulos, subtitulos_json)

    return subtitulos


def translate_subtitles(subtitulos_json: str):
    # Load subtitulos
    subtitulos = util.load_subtitulos_json(subtitulos_json)

    # Attempt translation for each one
    for subtitulo in tqdm(subtitulos, unit='B', unit_scale=True):
        subtitulo.translate()

    # Save subtitulos
    util.save_subtitulos_json(subtitulos, subtitulos_json)


def combine_subtitles_to_text(subtitulos_json, transcription_text):
    """
    - Se cargan los subtitles desde archivo el JSON *subtitulos_json* a una lista.
    - Combina los subtitles en español e inglés correspondiente.
    - Guarda nuevamente el JSON, para guardar los checks de flags.
    - Guarda la transcripción en un archivo de texto.
    :param str subtitulos_json: Path a los subtítulos en JSON.
    :param str transcription_text: Path donde guardar la transcripción.
    :return:
    """
    print("Combining subtitles")

    # Load from JSON
    subtitulos = util.load_subtitulos_json(subtitulos_json)

    # Clean the translation of extra spaces and normalize apostrophes
    clean_spaces(subtitulos)

    # Combine the subtitles
    subtitulos_finales = util.combine_subtitles(subtitulos)

    # Save subtitles
    util.save_subtitulos_json(subtitulos, subtitulos_json)

    # Save the final transcription in a txt file
    with open(transcription_text, "w", encoding="utf-8") as file:
        for line in subtitulos_finales:
            file.write(line + "\n")


def normalize_apostrophes(text):
    # Replace different types of single apostrophes with '
    text = text.replace('’', "'")
    text = text.replace('‘', "'")
    text = text.replace('`', "'")
    # Replace different types of double apostrophes with "
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    text = text.replace('„', '"')
    return text


def clean_spaces(subtitulos: list[util.Subtitulo]):
    for subtitulo in subtitulos:
        # Split the English string into lines
        lines = subtitulo.english.split('\n')

        # Remove extra spaces from each line and join them back with '\n'
        cleaned_lines = [' '.join(line.strip().split()) for line in lines]

        # Join the lines back to form the cleaned English string
        cleaned_english = '\n'.join(cleaned_lines)

        # Update the English string in the object
        subtitulo.english = normalize_apostrophes(cleaned_english)


def create_final_aegis_subs(time_stamps_file, transcription_text, parsed_text, original_subs, definitive_subs):
    """
    Se crea el archivo *subtitulos_definitivos.ass*. En principio sin errores y bien ordenado.
        - Extraer los timestamps desde el aegis sub.
        -
    :param str time_stamps_file: Path de los timestamps.
    :param str transcription_text: Path de la transcripción en texto.
    :param str parsed_text: Path donde guardar los subtítulos definitivos como texto.
    :param str original_subs: Path del subtítulo aegis sub usado.
    :param str definitive_subs: Path donde guardar los subtítulos definitivos como aegis sub.
    :return:
    """
    # Extract the time stamps from aegis sub and save them for later
    time_stamps_str = util.extract_timestamps_from_file(original_subs)
    util.save_timestamps_to_json(time_stamps_str, time_stamps_file)

    print("Creating final Aegis Sub File")

    time_stamps = util.load_timestamps(time_stamps_file)
    util.create_composed_subtitles(time_stamps, transcription_text, parsed_text)
    util.replace_subs(original_subs, parsed_text, definitive_subs)


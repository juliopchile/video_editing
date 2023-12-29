import os

from tqdm import tqdm

import functions.ffmpeg_functions as ffmpeg
import functions.utility_functions as util
from functions.api_secrets import API_KEY_ASSEMBLYAI, API_KEY_OPENAI
from functions.assembly_AI import AssemblyAI


# Paso 0
def video2audio(video="bin/video", audio="bin/audio", extension="wav"):
    """
    Convierte todos los archivos dentro del directorio video a audios en el directorio audio.
    :return:
    """
    video_path = os.path.normpath(video)
    audio_path = os.path.normpath(audio)
    ffmpeg.process_videos(video_path, audio_path, extension)


def manage_transcriptions(audio_path, data_path):
    """
    Gestiona el proceso de transcripción de los audios en **audio_path** y son guardados en el directorio **data_path**.
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
    existing_data_transcriptions = set(os.listdir(data_path))

    # Check whether the audio_path corresponds to a directory or a single file
    if os.path.isfile(audio_path):
        file = os.path.basename(audio_path)                     # get the audio name + extension
        audio_name, _ = os.path.splitext(file)                  # get only the audio name
        data_file = os.path.join(data_path, audio_name)         # use that name for the full path of data_file

        # Check if the corresponding audio file have already been transcribed
        if os.path.basename(data_file+'.json') not in existing_data_transcriptions:
            print(f"Transcribing audio: {file}")
            transcribe_and_save_data(audio_path, data_file)
        else:
            print(f"Skipped: {file} (Audio already transcribed)")
            # TODO preguntar si quiere realizar la transcripción nuevamente

    elif os.path.isdir(audio_path):
        # Iterate through files in the audio_path directory
        for file in os.listdir(audio_path):
            audio_name, _ = os.path.splitext(file)
            data_file = os.path.join(data_path, audio_name)
            audio_file = os.path.join(audio_path, file)

            # Check if the corresponding audio file have already been transcribed
            if os.path.basename(data_file+'.json') not in existing_data_transcriptions:
                print(f"Transcribing audio: {file}")
                transcribe_and_save_data(audio_file, data_file)
            else:
                print(f"Skipped: {file} (Audio already transcribed)")
                # TODO preguntar si quiere realizar la transcripción nuevamente

    else:
        print("No audio file given.")


# Paso 1
def transcribe_and_save_data(audio_file, transcription_data):
    """
    Transcribe el audio en **audio_file** y guarda esta data en un archivo JSON **transcription_data**.
    :param audio_file:
    :param transcription_data:
    :return:
    """
    transcript = AssemblyAI(api_key=API_KEY_ASSEMBLYAI)
    configuration = {'language_code': 'es',
                    'punctuate': True,
                    'format_text': False,
                    'speaker_labels': False}

    transcript.config(audio_file=audio_file, configuration=configuration)
    transcript.make_and_save_transcription(transcription_data)



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
    util.save_timestamps_to_json(time_stamps_str, time_stamps_file)

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
        overwrite = input(f"The file {os.path.basename(subtitulos_json)} already exists. Do you want to overwrite it? (yes/no): ").lower()
        if overwrite != 'yes':
            print("Subtitles were not saved.")
            return

    print("Creating and saving Subtitulo objects")

    # Create list of Subtitulo using sections
    subtitulos = util.create_subtitulos_object_list(sections, sections_clean)

    # Save subtitulos list into a file
    util.save_subtitulos_json(subtitulos, subtitulos_json)

    return subtitulos


def translate_subtitles(subtitulos_json: str, prompt: str):
    # Load subtitulos
    subtitulos = util.load_subtitulos_json(subtitulos_json)

    # Attempt translation for each one
    for subtitulo in tqdm(subtitulos, unit='B', unit_scale=True):
        subtitulo.translate(prompt, API_KEY_OPENAI, "gpt-4-1106-preview")

    # Save subtitulos
    util.save_subtitulos_json(subtitulos, subtitulos_json)


def combine_subtitles_to_text(subtitulos_json, transcription_text):
    """
    - Carga los subtitles desde archivo el JSON *subtitulos_json* a una lista.
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

    # Combine the subtitles
    subtitulos_finales = util.combine_subtitles(subtitulos)

    # Save subtitulos
    util.save_subtitulos_json(subtitulos, subtitulos_json)

    # Save the final transcription in a txt file
    with open(transcription_text, "w", encoding="utf-8") as file:
        for line in subtitulos_finales:
            file.write(line + "\n")


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


def step_0():
    """
    - Prepara el audio del video para usarla en el video
    :return:
    """
    video = "bin/video"
    audio = "bin/audio"
    extension = "flac"
    video2audio(video, audio, extension)


def step_1():
    """
    - Transcripción del audio haciendo uso de la API de AssemblyAI.
    - Guardado de la data de la transcripción.
    :return:
    """
    audio_path = 'bin/audio'
    data_path = 'bin/transcription/src'

    manage_transcriptions(audio_path, data_path)

def step_2():
    """
    - Se usa la transcripción de AssemblyAI y se ordenan usando los **timestamps** del archivo *.ass*
    - Se crea un nuevo archivo *.ass* con los subtítulos automáticos añadidos.
    :return:
    """
    # Source
    transcription_data = 'bin/transcription/src/example_video_(Vocals).json'   # Debe ser especificado
    timing_subs = 'bin/transcription/src/timing_subs.ass'                      # Define cuando irán los subtítulos

    # Temporales
    time_stamps_file = 'bin/transcription/temp/time_stamps.json'
    transcription_text = 'bin/transcription/temp/transcription_text.txt'
    parsed_subs = 'bin/transcription/temp/parsed_subs.txt'

    # Output
    updated_subs = 'bin/transcription/updated_subs.ass'

    create_transcription_using_timestamps(timing_subs, time_stamps_file, transcription_data, transcription_text)

    create_updated_subs_ass(time_stamps_file, transcription_text, timing_subs, parsed_subs, updated_subs)


def manage_subtitles():
    pass

def step_3():
    """
    - Se extraen los segmentos de subtítulo desde el archivo Aegis sub.
    - Se crean objeto tipo Subtitulo y se guardan en
    :return:
    """
    spanish_subs = 'bin/translation/src/updated_subs_V2.ass'
    subtitulos_json = 'bin/translation/temp/subtitulos.json'

    # Extraer las secciones de subtítulos.
    sections, sections_clean = util.extract_sections_from_subs(spanish_subs)

    # Crear, guarda y retorna una lista de subtítulos de la clase Subtitulo.
    create_save_return_subtitles(sections, sections_clean, subtitulos_json)


def step_4():
    spanish_subs = 'bin/translation/src/updated_subs_V2.ass'
    subtitulos_json = 'bin/translation/temp/subtitulos.json'
    transcription_text = 'bin/translation/temp/transcription_text.txt'
    subtitulos_definitivos = 'bin/translation/subtitulos_finales.ass'
    time_stamps_file = 'bin/translation/temp/time_stamps.json'
    parsed_subs = 'bin/translation/temp/parsed_subs.txt'
    prompt = "You translate Spanish to English. Your primary duty involves translating phrases and rhymes originating from rap battles. It's essential to consider the context and idiomatic expressions used in the source material. Ensure that the translation maintains the same line count as the original."

    # Traducir subtítulos
    translate_subtitles(subtitulos_json, prompt)

    combine_subtitles_to_text(subtitulos_json, transcription_text)

    create_final_aegis_subs(time_stamps_file, transcription_text, parsed_subs, spanish_subs, subtitulos_definitivos)
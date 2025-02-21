import os.path
from wrapper import *

VIDEO_NAME = 'Ego_Fest_2'


def step_0():
    """
    - Prepara el audio del video para usarla en el video
    :return:
    """
    video = "bin/video"
    audio = "bin/audio"
    extension = "wav"
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
    overwrite = False

    # Folders
    path = os.path.normpath('bin/transcription')
    src_path = os.path.join(path, 'src')
    temp_path = os.path.join(path, 'temp')

    # List all files in the source directory
    src_files = os.listdir('bin/video')
    for index in range(len(src_files)):
        src_files[index] = os.path.splitext(src_files[index])[0]

    for video_name in src_files:
        # Source
        transcription_data = os.path.join(src_path, video_name) + '.json'
        timing_subs = os.path.join(src_path, video_name) + '_timing.ass'

        # Archivos Temporales
        time_stamps_file = os.path.join(temp_path, video_name) + '_time_stamps.json'
        transcription_text = os.path.join(temp_path, video_name) + '_transcription_text.txt'
        parsed_subs = os.path.join(temp_path, video_name) + '_parsed_subs.txt'

        # Output
        updated_subs = os.path.join(path, video_name) + '_updated_subs.ass'

        if os.path.exists(transcription_text):
            if overwrite:
                overwrite_file = input(
                    f"Updated subs for {video_name} already exists. Do you want to overwrite it? (yes/no): ")
                if overwrite_file.lower() == "yes":
                    # Overwrite the file
                    create_transcription_using_timestamps(timing_subs, time_stamps_file, transcription_data,
                                                          transcription_text)
                    create_updated_subs_ass(time_stamps_file, transcription_text, timing_subs, parsed_subs,
                                            updated_subs)
                    print(f"{video_name + '_updated_subs.ass'} overwritten.")
                else:
                    print("File not overwritten.")
        else:
            create_transcription_using_timestamps(timing_subs, time_stamps_file, transcription_data, transcription_text)
            create_updated_subs_ass(time_stamps_file, transcription_text, timing_subs, parsed_subs, updated_subs)
            print(f"{video_name + '_updated_subs.ass'} created.")


def step_3():
    """
    - Se extraen los segmentos de subtítulo desde el archivo Aegis sub.
    - Se crean objeto tipo Subtitulo y se guardan en
    :return:
    """
    # Folders
    path = os.path.normpath('bin/translation')
    src_path = os.path.join(path, 'src')
    temp_path = os.path.join(path, 'temp')

    # List all files in the source directory
    src_files = os.listdir('bin/video')
    for index in range(len(src_files)):
        src_files[index] = os.path.splitext(src_files[index])[0]

    for video_name in src_files:
        # Source
        spanish_subs = os.path.join(src_path, video_name) + '_updated_subs.ass'
        subtitulos_json = os.path.join(temp_path, video_name) + '_subtitulos.json'

        # Extraer las secciones de subtítulos.
        sections, sections_clean = util.extract_sections_from_subs(spanish_subs)

        # Crear, guarda y retorna una lista de subtítulos de la clase Subtitulo.
        create_save_return_subtitles(sections, sections_clean, subtitulos_json)


def step_4():
    # Folders
    path = os.path.normpath('bin/translation')
    src_path = os.path.join(path, 'src')
    temp_path = os.path.join(path, 'temp')

    # List all files in the source directory
    src_files = os.listdir('bin/video')
    for index in range(len(src_files)):
        src_files[index] = os.path.splitext(src_files[index])[0]

    for video_name in src_files:
        # Source
        spanish_subs = os.path.join(src_path, video_name) + '_updated_subs.ass'
        subtitulos_json = os.path.join(temp_path, video_name) + '_subtitulos.json'

        transcription_text = os.path.join(temp_path, video_name) + '_text.txt'
        subtitulos_definitivos = os.path.join(path, video_name) + '_finales.ass'
        time_stamps_file = os.path.join(temp_path, video_name) + '_time_stamps.json'
        parsed_subs = os.path.join(temp_path, video_name) + '_parsed_subs.txt'

        # Traducir subtítulos
        translate_subtitles(subtitulos_json)

        combine_subtitles_to_text(subtitulos_json, transcription_text)

        create_final_aegis_subs(time_stamps_file, transcription_text, parsed_subs, spanish_subs, subtitulos_definitivos)


if __name__ == '__main__':
    # --- Preparación --- #
    # Se preparan los archivos de video y audio a utilizar
    # step_0()

    # --- Transcripción --- #
    # Se usa la API de AssemblyAI para transcribir automáticamente lo dicho en un audio
    # step_1()

    # --- Subtitular --- #
    # Se ajusta la transcripción a los tiempos designados para los subtítulos
    step_2()

    # --- Crear Subtitles --- #
    # Se crean los subtítulos JSON
    #step_3()

    # --- Traducción --- #
    # Se usa la API de OpenAI para traducir los subtítulos
    #step_4()

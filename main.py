from wrapper import *

VIDEO_NAME = "MINUTAZO de BNET - MÉTRICAS ANALIZADAS - BNET VS TIRPA FMS 2020"
USE_CLEAN_AUDIO = True

# TODO: implement a way to save the project states in a JSON
PROJECTS_STATES_PATH = "projects_states.json"


def step_0():
    """
    Extrae el audio del video y lo guarda en un archivo WAV.
    """
    video = "bin/video"
    audio = "bin/audio"
    extension = "wav"
    video2audio(video, audio, extension)


def step_1():
    """
    - Transcripción del audio haciendo uso de la API de AssemblyAI.
    - Guardado de la data de la transcripción.
    """
    audio_path = 'bin/clean_audio' if USE_CLEAN_AUDIO else 'bin/audio'
    data_path = 'bin/transcription/src'

    manage_transcriptions(audio_path, data_path)


def step_2():
    """
    - Se usa la transcripción de AssemblyAI y se ordenan usando los
    **timestamps** del archivo *.ass*
    - Se crea un archivo *.ass* con los subtítulos automáticos añadidos.
    :return:
    """
    overwrite = False

    # Folders
    path = os.path.normpath('bin/transcription')
    src_path = os.path.join(path, 'src')
    temp_path = os.path.join(path, 'temp')
    os.makedirs(src_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)

    # List all files in the source directory
    src_files = os.listdir('bin/video')
    for index in range(len(src_files)):
        src_files[index] = os.path.splitext(src_files[index])[0]

    for video in src_files:
        # Paths
        video_src_path = os.path.join(src_path, video)
        video_temp_path = os.path.join(temp_path, video)
        video_path =os.path.join(path, video)
        
        # Source
        transcription_data = f'{video_src_path}.json'
        timing_subs = f'{video_src_path}_timing.ass'

        # Archivos Temporales
        time_stamps_file = f'{video_temp_path}_time_stamps.json'
        transcription_text = f'{video_temp_path}_transcription_text.txt'
        parsed_subs = f'{video_temp_path}_parsed_subs.txt'

        # Output
        updated_subs =  f'{video_path}_updated_subs.ass'

        if os.path.exists(transcription_text):
            if overwrite:
                overwrite_file = input(
                    f'Updated subs for "{video}" already exists.\n'
                    'Do you want to overwrite it? (yes/no): ')
                if overwrite_file.lower() == "yes":
                    # Overwrite the file
                    create_transcription_using_timestamps(
                        timing_subs, time_stamps_file,
                        transcription_data, transcription_text)
                    create_updated_subs_ass(
                        time_stamps_file, transcription_text,
                        timing_subs, parsed_subs, updated_subs)
                    print(f"{video + '_updated_subs.ass'} overwritten.")
                else:
                    print("File not overwritten.")
        else:
            create_transcription_using_timestamps(
                timing_subs, time_stamps_file, transcription_data,
                transcription_text)
            create_updated_subs_ass(
                time_stamps_file, transcription_text, timing_subs,
                parsed_subs, updated_subs)
            print(f"{video + '_updated_subs.ass'} created.")


def step_3():
    """
    - Se extraen los segmentos de subtítulo desde el archivo Aegis sub.
    - Se crean objeto tipo Subtitulo y se guardan en
    """
    overwrite = True

    # Folders
    path = os.path.normpath('bin/translation')
    src_path = os.path.join(path, 'src')
    temp_path = os.path.join(path, 'temp')
    os.makedirs(src_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)

    # List all files in the source directory
    src_files = os.listdir('bin/video')
    for index in range(len(src_files)):
        src_files[index] = os.path.splitext(src_files[index])[0]

    for video in src_files:
        # Paths
        video_src_path = os.path.join(src_path, video)
        video_temp_path = os.path.join(temp_path, video)

        # Source
        es_subs = f'{video_src_path}_updated_subs.ass'
        subtitulos_json = f'{video_temp_path}_subtitulos.json'

        # If no source subtitles, then skip it
        if not os.path.exists(es_subs):
            continue

        # If JSON subs already done, skip it unless overwrite = True
        if os.path.exists(subtitulos_json):
            if overwrite:
                overwrite_file = input(
                    f'Subtitle JSON for "{video}" already exists.\n'
                    'Do you want to overwrite it? (yes/no): ')
                if overwrite_file.lower() == "yes":
                    # Extraer las secciones de subtítulos.
                    sections, sections_clean = (
                        util.extract_sections_from_subs(es_subs))
                    # Crear, guarda y retorna una lista de Subtitulos.
                    create_save_return_subtitles(
                        sections, sections_clean, subtitulos_json)
        else:
            # Extraer las secciones de subtítulos.
            sections, sections_clean = (
                util.extract_sections_from_subs(es_subs))
            # Crear, guarda y retorna una lista de Subtitulos.
            create_save_return_subtitles(
                sections, sections_clean, subtitulos_json)


def step_4():
    overwrite = False

    # Folders
    path = os.path.normpath('bin/translation')
    src_path = os.path.join(path, 'src')
    temp_path = os.path.join(path, 'temp')
    os.makedirs(src_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)

    # List all files in the source directory
    src_files = os.listdir('bin/video')
    for index in range(len(src_files)):
        src_files[index] = os.path.splitext(src_files[index])[0]

    for video in src_files:
        # Paths
        video_src_path = os.path.join(src_path, video)
        video_temp_path = os.path.join(temp_path, video)
        video_path =os.path.join(path, video)

        # Source
        spanish_subs = f'{video_src_path}_updated_subs.ass'
        subtitulos_json = f'{video_temp_path}_subtitulos.json'
        transcription_text = f'{video_temp_path}_text.txt'
        subtitulos_definitivos = f'{video_path}_finales.ass'
        time_stamps_file = f'{video_temp_path}_time_stamps.json'
        parsed_subs = f'{video_temp_path}_parsed_subs.txt'

        # If no source JSON, then skip it
        if not os.path.exists(subtitulos_json):
            continue

        # If definitive subs are done, skip them unless overwrite = True
        if os.path.exists(subtitulos_definitivos):
            if overwrite:
                overwrite_file = input(
                    f'Translation for "{video}" already exists.\n'
                    'Do you want to overwrite it? (yes/no): ')
                if overwrite_file.lower() == "yes":
                    # Traducir subtítulos
                    translate_subtitles(subtitulos_json)
                    combine_subtitles_to_text(
                        subtitulos_json, transcription_text)
                    create_final_aegis_subs(
                        time_stamps_file, transcription_text,
                        parsed_subs, spanish_subs, subtitulos_definitivos)
        else:
            # Traducir subtítulos
            translate_subtitles(subtitulos_json)
            combine_subtitles_to_text(
                subtitulos_json, transcription_text)
            create_final_aegis_subs(
                time_stamps_file, transcription_text,
                parsed_subs, spanish_subs, subtitulos_definitivos)


if __name__ == '__main__':
    # --- Preparación --- #
    # Se preparan los archivos de video y audio a utilizar
    # step_0()

    # --- Transcripción --- #
    # Se usa la API de AssemblyAI para transcribir automáticamente lo dicho en un audio
    # step_1()

    # --- Subtitular --- #
    # Se ajusta la transcripción a los tiempos designados para los subtítulos
    # step_2()

    # --- Crear Subtitles --- #
    # Se crean los subtítulos JSON
    # step_3()

    # --- Traducción --- #
    # Se usa la API de OpenAI para traducir los subtítulos
    step_4()

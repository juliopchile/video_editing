import os.path

from wrapper import *
import json

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


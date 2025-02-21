import os
import time

import requests
from tqdm import tqdm

import functions.utility_functions as util

# Global Variables
CHUNK_SIZE = 5_242_880  # 5MB


class AssemblyAI:
    """
    A class to interact with AssemblyAI API for audio transcription.

    Attributes
    ----------
    api_key : str
        The API key for AssemblyAI.
    chunk_size : int, optional
        The size of chunks to split the audio file for upload (default is CHUNK_SIZE).
    upload_endpoint : str
        The endpoint for uploading audio files to AssemblyAI.
    transcript_endpoint : str
        The endpoint for requesting and retrieving transcriptions from AssemblyAI.
    configuration : dict
        The configuration settings for the transcription request.
    audio_file : str
        The path to the audio file to be transcribed.
    upload_url : str
        The URL of the uploaded audio file on AssemblyAI.
    transcript_id : str
        The ID of the transcription request.
    data : dict
        The data returned from the transcription request.
    error : str
        The error message, if any, from the transcription request.
    """

    def __init__(self, api_key, chunk_size=CHUNK_SIZE):
        """
        Constructs all the necessary attributes for the AssemblyAI object.

        Parameters
        ----------
            api_key : str
                The API key for AssemblyAI.
            chunk_size : int, optional
                The size of chunks to split the audio file for upload (default is CHUNK_SIZE).
        """
        self.api_key = api_key
        self.chunk_size = chunk_size
        self.upload_endpoint = 'https://api.assemblyai.com/v2/upload'
        self.transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'
        self.configuration = {}
        self.audio_file = ""
        self.upload_url = None
        self.transcript_id = None
        self.data = None
        self.error = None

    def config(self, **kwargs):
        """
        Updates the configuration settings.

        Parameters
        ----------
            **kwargs : Any
                The configuration settings to be updated.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_header(self, auth_only=False):
        """
        Returns the headers for the API request.

        Parameters
        ----------
            auth_only : bool, optional
                If True, only the 'authorization' header is returned (default is False).

        Returns
        -------
            dict
                The headers for the API request.
        """
        if auth_only:
            return {'authorization': self.api_key}
        else:
            return {'authorization': self.api_key, 'content-type': 'application/json'}

    def upload(self):
        """
        Uploads the audio file to AssemblyAI.
        """
        file_size = os.path.getsize(self.audio_file)
        progress = tqdm(total=file_size, unit='B', unit_scale=True, desc=self.audio_file)

        upload_response = requests.post(url=self.upload_endpoint,
                                        headers=self.get_header(True),
                                        data=util.read_file_with_progress(self.audio_file, self.chunk_size, progress))
        self.upload_url = upload_response.json()['upload_url']

    def transcribe(self):
        """
        Sends a transcription request to AssemblyAI.
        """
        transcript_request = {'audio_url': self.upload_url}
        transcript_request.update(self.configuration)
        print(transcript_request)
        transcript_response = requests.post(url=self.transcript_endpoint,
                                            json=transcript_request,
                                            headers=self.get_header(False))
        self.transcript_id = transcript_response.json()['id']

    def poll(self):
        """
        Polls AssemblyAI for the status of the transcription request.

        Returns
        -------
            dict
                The status of the transcription request.
        """
        polling_endpoint = self.transcript_endpoint + '/' + self.transcript_id
        polling_response = requests.get(url=polling_endpoint, headers=self.get_header(False)).json()
        return polling_response

    def polling_transcription_url(self, n=10):
        """
        Continuously polls AssemblyAI for the transcription until it's completed or an error occurs.

        Parameters
        ----------
            n : int, optional
                The number of seconds to wait between each poll (default is 30).

        Returns
        -------
            tuple
                The data and error message (if any) from the transcription request.
        """
        while True:
            data = self.poll()
            if data['status'] == 'completed':
                print('Transcription Complete.')
                self.data = data
                self.error = None
                return data, None
            elif data['status'] == 'error':
                print("Error!!!", data['error'])
                self.data = data
                self.error = data['error']
                return data, data['error']
            print(f"waiting for {n} seconds")
            time.sleep(n)

    def make_and_save_transcription(self, title):
        self.upload()
        print(f'upload_url = {self.upload_url}')
        self.transcribe()
        print(f'transcript_id = {self.transcript_id}')
        transcript_data, error = self.polling_transcription_url()
        if transcript_data:
            util.save_data(transcript_data, title)
        elif error:
            print("Error!!!", error)


if __name__ == "__main__":
    pass

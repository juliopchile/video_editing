import openai
from functions.api_secrets import API_KEY_OPENAI, OPEN_AI_ASSISTANT
import time
import logging
from datetime import datetime


client = openai.OpenAI(api_key=API_KEY_OPENAI)
MODEL = "gpt-4-1106-preview"


def wait_for_run_completion(client, thread_id, run_id, sleep_interval=2.5):
    """

    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                return response
        except openai.OpenAIError:  # Replace with the actual exception
            raise openai.OpenAIError
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


def create_assistant(name, prompt, model=MODEL):
    assistant = client.beta.assistants.create(name=name, instructions=prompt, model=model)
    return assistant.id


def create_thread():
    thread = client.beta.threads.create()
    return thread.id


def append_message(thread_id, message_txt, initial_instruction=None):
    if initial_instruction is not None:
        client.beta.threads.messages.create(thread_id=thread_id, role='user', content=initial_instruction)
    client.beta.threads.messages.create(thread_id=thread_id, role='user', content=message_txt)


def create_run(assistant_id, thread_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run.id


def translate_text(message: str, initial_instruction=None, assistant_id=OPEN_AI_ASSISTANT):
    thread_id = create_thread()
    append_message(thread_id, message, initial_instruction)
    run_id = create_run(assistant_id, thread_id)
    response = wait_for_run_completion(client=client, thread_id=thread_id, run_id=run_id)
    return response


def translate_gpt(_api_key: str, _message: str, _prompt: str, _examples = None, _model: str = "gpt-4-1106-preview"):
    """DEPRECATED Use translate_text instead"""
    openai.api_key = _api_key

    if _examples is not None:
        _messages = [
            {"role": "system", "content": _prompt},
            {"role": "system", "name": "example_user", "content": _examples[0]},
            {"role": "system", "name": "example_assistant", "content": _examples[1]},
            {"role": "user", "content": _message},
        ]
    else:
        _messages = [
            {"role": "system", "content": _prompt},
            {"role": "user", "content": _message},
        ]

    # Make an API request to translate the text using chat completions endpoint
    try:
        response = openai.ChatCompletion.create(
            model=_model,  # Choose the chat model for translation
            messages=_messages,
            max_tokens=1700, # Set the maximum number of tokens in the response
            temperature=0.33,
        )

        # Extract the translated text from the response
        translated_text = response.choices[0].message["content"]

        return translated_text

    except openai.OpenAIError:  # Replace with the actual exception
        raise openai.OpenAIError

import openai
from functions.api_secrets import API_KEY_OPENAI, OPEN_AI_ASSISTANT
import time
import logging
from datetime import datetime


client = openai.OpenAI(api_key=API_KEY_OPENAI)
model = "gpt-3.5-turbo-16k"
assistant_id = "asst_CxeDSd9FdSw0bGsttttP4wK9"

thread = client.beta.threads.create()
thread_id = thread.id

# ==== Create a Message ====
message_txt = "You will receive a transcription of a rap battle in spanish. Translate each line to english."
message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role='user',
    content=message_txt
)

# === Run our Assistant ===
run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
    instructions="Translate the given text"
)
run_id = run.id

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
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                return messages
                #break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


# === Run ===
mensaje = wait_for_run_completion(client=client, thread_id=thread_id, run_id=run_id)
print(mensaje)

# ==== Steps --- Logs ==
run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
print(f"Steps---> {run_steps.data[0]}")
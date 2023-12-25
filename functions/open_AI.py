import openai

def translate_gpt(_api_key: str, _message: str, _prompt: str, _examples = None, _model: str = "gpt-4-1106-preview"):
    # Set your OpenAI API key
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
            max_tokens=1024, # Set the maximum number of tokens in the response
            temperature=0.5,
        )

        # Extract the translated text from the response
        translated_text = response.choices[0].message["content"]

        return translated_text

    except openai.OpenAIError:  # Replace with the actual exception
        print("Rate limit exceeded, waiting for 60 seconds")

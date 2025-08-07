import json
from collections.abc import Iterable
from openai import OpenAI
from openai.types.responses.tool_param import ToolParam
from openai.types.responses.response_input_param import ResponseInputParam
from openai.types.shared_params.reasoning import Reasoning
from openai.types.shared_params.responses_model import ResponsesModel
from openai._types import NotGiven
from functions.super_secrets import API_KEY_OPENAI

API_KEY = API_KEY_OPENAI

JSON_SCHEMA: ToolParam = {
    "type": "function",
    "name": "translate_texts",
    "description": "Translate an array of strings from in the given language",
    "parameters": {
        "type": "object",
        "properties": {
            "translated": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of translated strings in the same order.",
            }
        },
        "required": ["translated"],
        "additionalProperties": False,
    },
    "strict": True,
}

SYSTEM_PROMPT: str = (
    "Role: You are a profesional translator fluent in all languages. " 
    "Your task is to translate the given text from its original language into "
    "the specified target language or laguages.\n\n"
    "Instructions:\n"
    "• Output only the translation; do not include any commentary, questions, "
    "or extra text.\n"
    "• Output in plain text unless a specific format is given.\n"
    "• Translate naturally and fluently, ensuring that the meaning, tone, and "
    "intent from the original text are preserved.\n"
    "• Use a literal translation when appropriate, but adapt or interpret "
    "sections to best preserve meaning when a word-for-word translation would "
    "be unclear.\n"
    "• When cultural references, idioms, or expressions are present, adapt "
    "them to fit the target language audience while maintaining their "
    "original intent.\n"
    "• Accurately translate technical terms, specialized jargon, or "
    "industry-specific vocabulary.\n"
    "• Profanity filter: OFF."
    
)

DEVELOPER_PROMPT: str = (
    "You are a rap battle translator. Your task is to translate Spanish rap "
    "battle verses into English, preserving the original style, slang, "
    "wordplay, and cultural nuances. When given any Spanish rap battle text, "
    "produce an English translation that maintains the punch, attitude, and "
    "creative flair of the original. If needed, adapt idioms and puns to "
    "appropriate English equivalents that capture the same impact, but keep "
    "names untouched and don't add extra lines or phrases."
)


MODEL: ResponsesModel = "o4-mini-2025-04-16"
REASONING: Reasoning = {"effort": "low"}


def from_string(section: str) -> list[str]:
    sections = section.split(sep="\n")
    return sections

def to_string(sections: list[str]) -> str:
    return "\n".join(sections)


def translate_list(spanish_text: str):
    # Convert the string into a 
    parrafos = from_string(spanish_text)
    
    # Use the OpenAI API for the tarnslation
    client = OpenAI(api_key=API_KEY)

    user_message: str = json.dumps({"verses": parrafos}, ensure_ascii=False)

    # 1. Define tus “mensajes”
    messages: str | ResponseInputParam | NotGiven = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "developer", "content": DEVELOPER_PROMPT},
        {"role": "user", "content": user_message}
    ]

    # 2. Define tu “herramienta” / función
    tools: Iterable[ToolParam] = [JSON_SCHEMA]


    # 3. Llama al endpoint “Responses”
    response = client.responses.create(
        model=MODEL,
        reasoning=REASONING,
        input=messages,
        tools=tools,
    )
    
    # Process the response
    translated_list = json.loads(response.output[1].arguments)["translated"]
    #response_dict = response.output[1].model_dump()
    #translated_dict = json.loads(response_dict["arguments"])
    #translated_list = translated_dict["translated"]

    # Convert the list into a string and return it
    translated_text = to_string(translated_list)
    return translated_text

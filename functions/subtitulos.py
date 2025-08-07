from typing import Any
from openai import OpenAIError
from functions.open_AI import translate_list


class Subtitulo:
    def __init__(self,
                 spanish: str,
                 clean_spanish: str,
                 english: str = "",
                 done_translating: bool = False):
        self.spanish = spanish
        self.clean_spanish = clean_spanish
        self.english = english
        self.done_translating = done_translating

    def to_dict(self):
        return {
            "spanish": self.spanish,
            "clean_spanish": self.clean_spanish,
            "english": self.english,
            "done_translating": self.done_translating
        }

    def translate(self):
        if not self.done_translating:
            try:
                self.english = translate_list(self.clean_spanish)
                self.done_translating = True
            except OpenAIError as error:
                print(f"OpenAIError {error}")
                self.done_translating = False
            finally:
                pass
        else:
            print("Skip (already translated)")

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            spanish=data["spanish"],
            clean_spanish=data["clean_spanish"],
            english=data["english"],
            done_translating=data["done_translating"]
        )

"""This module provides a simple interface for interacting with LLMs.
"""

import os
from openai import OpenAI

class OpenAIClient:
    """
    A client for interacting with the OpenAI API.
    """

    def __init__(self, model="gpt-4-turbo-preview", system_prompt="You are a helpful assistant.", temperature=0.5):
        open_ai_key = os.getenv("OPENAI_API_KEY")
        if not open_ai_key:
            raise ValueError("OPENAI_API_KEY is not set in the environment")
        self.client = OpenAI(api_key=open_ai_key)
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature

    def prompt(self, user_prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"{user_prompt}"}
            ],
            temperature=self.temperature
        )
        text_only = response.choices[0].message.content
        return text_only

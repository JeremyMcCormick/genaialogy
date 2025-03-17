"""Test the LLM module."""

from unittest import TestCase
from genaialogy.tools.llm import OpenAIClient


class TestLLM(TestCase):

    def test_openai_client(self):
        llm = OpenAIClient()
        result = llm.prompt("Hello, world!")
        print("Result: ", result)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

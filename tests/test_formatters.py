from formatters import format_reasoning_response, format_error_response
from providers.base import LLMError

def test_format_reasoning_response():
    response = format_reasoning_response("test reasoning")
    assert response == "<ant_thinking>test reasoning</ant_thinking>"

def test_format_error_response():
    error = LLMError("test_provider", "test error")
    response = format_error_response(error)
    assert response == "<error provider='test_provider'>test error</error>" 
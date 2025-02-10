def format_reasoning_response(content: str) -> str:
    """Wrap reasoning output in required XML tags"""
    return f"<ant_thinking>{content}</ant_thinking>"

def format_error_response(error) -> str:
    """Format error responses consistently"""
    return f"<error provider='{error.provider}'>{error.message}</error>" 
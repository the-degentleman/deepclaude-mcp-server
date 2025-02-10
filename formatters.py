def format_reasoning_response(reasoning: str) -> str:
    """
    Enhanced formatting with metadata and structure
    """
    return f"""<ant_thinking>
Source: {reasoning.source if hasattr(reasoning, 'source') else 'Unknown'}
Confidence: {reasoning.confidence if hasattr(reasoning, 'confidence') else 'N/A'}
---
{reasoning}
</ant_thinking>

Now we should provide our final answer based on the above thinking.""" 
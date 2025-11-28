"""Summarizer Module

Responsible for generating official and simplified summaries using Ollama (LLaMA-3).
TODO: Implement full Ollama integration.
"""

import warnings
from typing import Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    warnings.warn("Ollama not installed. Summarization will use placeholder.")


def check_ollama_available() -> bool:
    """Check if Ollama is available and running."""
    if not OLLAMA_AVAILABLE:
        return False
    
    try:
        # Try to list models to check if Ollama is running
        ollama.list()
        return True
    except Exception:
        return False


def generate_official_summary(text: str, max_length: int = 500) -> str:
    """
    Generate an official/formal summary of the text.
    
    Args:
        text: Input text to summarize
        max_length: Maximum length of summary in words
        
    Returns:
        str: Official summary
        
    TODO: Implement Ollama LLaMA-3 integration
    """
    if not text or not text.strip():
        return ""
    
    # TODO: Replace with actual Ollama implementation
    # Example Ollama call:
    # response = ollama.generate(
    #     model='llama3',
    #     prompt=f"Generate a formal, official summary of this government circular:\n\n{text}"
    # )
    # return response['response']
    
    # Placeholder implementation
    words = text.split()
    summary_words = words[:min(len(words), max_length)]
    summary = ' '.join(summary_words)
    
    return f"[OFFICIAL SUMMARY - Placeholder]\n\n{summary}..."


def generate_simplified_summary(text: str, max_length: int = 300) -> str:
    """
    Generate a simplified/citizen-friendly summary of the text.
    
    Args:
        text: Input text to summarize
        max_length: Maximum length of summary in words
        
    Returns:
        str: Simplified summary
        
    TODO: Implement Ollama LLaMA-3 integration
    """
    if not text or not text.strip():
        return ""
    
    # TODO: Replace with actual Ollama implementation
    # Example Ollama call:
    # response = ollama.generate(
    #     model='llama3',
    #     prompt=f"Generate a simple, easy-to-understand summary for citizens:\n\n{text}"
    # )
    # return response['response']
    
    # Placeholder implementation
    words = text.split()
    summary_words = words[:min(len(words), max_length)]
    summary = ' '.join(summary_words)
    
    return f"[SIMPLIFIED SUMMARY - Placeholder]\n\n{summary}..."


def generate_summaries(text: str) -> dict:
    """
    Generate both official and simplified summaries.
    
    Args:
        text: Input text to summarize
        
    Returns:
        dict: Dictionary with 'official' and 'simplified' summaries
    """
    return {
        'official': generate_official_summary(text),
        'simplified': generate_simplified_summary(text)
    }


if __name__ == "__main__":
    # Test the module
    print("Testing Summarizer Module")
    print("=" * 60)
    
    # Check Ollama availability
    print(f"Ollama Available: {check_ollama_available()}")
    print()
    
    # Test text
    test_text = """
    Government of India
    Ministry of Health and Family Welfare
    
    CIRCULAR NO. 2024/123
    
    Subject: Implementation of New Health Guidelines
    
    All state health departments are hereby informed that new health guidelines
    have been approved by the central government. These guidelines cover various
    aspects of public health including vaccination programs, disease surveillance,
    and health infrastructure development. All states must comply with these
    guidelines within 90 days of this circular.
    """
    
    print("Test Text:")
    print(test_text)
    print("\n" + "=" * 60)
    
    # Generate summaries
    summaries = generate_summaries(test_text)
    
    print("\nOfficial Summary:")
    print("-" * 60)
    print(summaries['official'])
    
    print("\n\nSimplified Summary:")
    print("-" * 60)
    print(summaries['simplified'])
    
    print("\n" + "=" * 60)
    print("Note: This is using placeholder implementation.")
    print("To use Ollama: pip install ollama && ollama pull llama3")

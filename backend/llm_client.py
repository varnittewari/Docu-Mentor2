import openai
import config

# Configure the OpenAI client
client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

def generate_docstring_for_function(code_snippet: str) -> str | None:
    """
    Uses an LLM to generate a docstring for a given function's code.

    Args:
        code_snippet: A string containing the full function definition.

    Returns:
        The generated docstring as a string, or None if an error occurs.
    """
    try:
        prompt = f"""
        Generate a concise, professional Python docstring for the following function.
        The docstring should follow the Google Python Style Guide.
        Do not include the function signature or any other text, only the complete docstring itself enclosed in triple quotes.

        Function:
        ```python
        {code_snippet}
        ```
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a senior software engineer specializing in writing excellent documentation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )

        docstring = response.choices[0].message.content.strip()
        return docstring

    except Exception as e:
        print(f"Error generating docstring: {e}")
        return None 
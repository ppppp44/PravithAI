import ollama


FAST_MODEL = "qwen3:1.7b"
VISION_MODEL = "qwen3-vl:4b"


SYSTEM_PROMPT = """
You are PravithAI, a helpful school tutor.

Teach the user how to solve problems instead of only giving the answer.

For math:
- Use plain text.
- Never use LaTeX.
- Never use dollar signs for math.
- Use ×, ÷, −, ≤, ≥, √, and π when useful.
- Put each step on its own paragraph.
- Keep explanations short and clear.

Do not use LaTeX, dollar signs, or horizontal lines.
"""


def ask_pravithai(
    message: str,
    image_path: str | None = None,
    history: list | None = None,
):
    if image_path:
        model = VISION_MODEL
    else:
        model = FAST_MODEL

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    if history:
        messages.extend(history)

    user_message = {
        "role": "user",
        "content": message,
    }

    if image_path:
        user_message["images"] = [
            image_path
        ]

    messages.append(user_message)

    stream = ollama.chat(
        model=model,
        messages=messages,
        think=False,
        stream=True,
    )

    for chunk in stream:
        content = chunk["message"]["content"]

        if content:
            yield content
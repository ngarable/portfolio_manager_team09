import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

def stream_chat(messages, model="gpt-4o-mini"):
    """Stream ChatGPT responses in real time."""
    with client.chat.completions.stream(
        model=model,
        messages=messages,
        temperature=0.7
    ) as stream:
        for event in stream:
            if event.type == "message.delta" and event.delta.get("content"):
                yield event.delta["content"]

def chatbot():
    print("💬 ChatGPT‑4 Chatbot — type 'exit' to quit.")
    conversation = []

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break

        # Append user message to history
        conversation.append({"role": "user", "content": user_input})

        print("Bot:", end=" ", flush=True)
        for chunk in stream_chat(conversation):
            print(chunk, end="", flush=True)

        print()  # New line
        # Append assistant message so it has context
        conversation.append({"role": "assistant", "content": ""})  # Will be updated

if __name__ == "__main__":
    chatbot()

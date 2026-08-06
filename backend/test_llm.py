from dotenv import load_dotenv
load_dotenv()

from groq import Groq

client = Groq()
resp = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello in one sentence."}]
)
print(resp.choices[0].message.content)

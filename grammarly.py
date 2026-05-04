import requests, os, random, json
API_KEY = os.getenv("OPENROUTER_API_KEY")
# MODEL_ID = "anthropic/claude-haiku-4.5"
MODEL_ID = "google/gemini-2.5-flash"
PRESET_ID = "@preset/grammar"
# URL = "https://openrouter.ai/api/v1/chat/completions"
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
def call(text):
  with open("system_prompts/grammarly_systemPrompt.txt", "r") as f:
    system_prompt = f.read()
  response = requests.post(
    url = URL,
    headers = {
      "Authorization": f"Bearer {API_KEY}",
      "Content-Type": "application/json"
    },
    data = json.dumps({
      "model": MODEL_ID,
      "messages": [
        {
          "role": "system",
          "content": system_prompt
        },
        {
          "role": "user",
          "content": [
              {
                "type": "text",
                "text": f"{text}"
              }
          ]
        }
      ]
    })
  )
  responseMSG = response.json()
  if "choices" not in responseMSG:
    print("Error: API response missing 'choices' key")
    print(f"Full response: {responseMSG}")
    raise KeyError(f"API returned an error or unexpected format: {responseMSG}")
  return responseMSG["choices"][0]["message"]["content"]
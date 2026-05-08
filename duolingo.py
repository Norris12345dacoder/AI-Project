import requests, os, json
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_ID = "google/gemini-2.5-flash"
# PRESET_ID = "@preset/duolingo"
# URL = "https://openrouter.ai/api/v1/chat/completions"
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
def call(language):
  with open("system_prompts/duolingo_systemPrompt.txt", "r", encoding = "utf-8") as f:
    system_prompt = f.read()
  response = requests.post(
    url = URL,
    headers = {
      "Authorization": f"Bearer {API_KEY}",
      "Content-Type": "application/json"
    },
    data = json.dumps({
      "model": MODEL_ID,
      "max_tokens": 2000,
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
                "text": f"Generate the questions in {language}."
              }
          ]
        }
      ]
    })
  )
  if response.status_code >= 400:
    raise RuntimeError(f"API HTTP {response.status_code}: {response.text[:300]}")
  try:
    responseMSG = response.json()
  except json.JSONDecodeError:
    raise RuntimeError(f"Non-JSON response: {response.text[:300]}")
  if "choices" not in responseMSG:
    raise RuntimeError(f"Unexpected API format: {responseMSG}")
  return responseMSG["choices"][0]["message"]["content"]
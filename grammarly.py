import requests, os, json
API_KEY = os.getenv("OPENROUTER_API_KEY")
# MODEL_ID = "anthropic/claude-haiku-4.5"
MODEL_ID = "google/gemini-2.5-flash"
# PRESET_ID = "@preset/grammar"
# URL = "https://openrouter.ai/api/v1/chat/completions"
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"


def _request_completion(system_prompt, text, max_tokens):
  response = requests.post(
    url = URL,
    headers = {
      "Authorization": f"Bearer {API_KEY}",
      "Content-Type": "application/json"
    },
    data = json.dumps({
      "model": MODEL_ID,
      "max_tokens": max_tokens,
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
                "text": str(text)
              }
          ]
        }
      ]
    }),
    timeout = (5, 90)
  )
  if response.status_code >= 400:
    raise RuntimeError(f"Hack Club at HTTP {response.status_code}: {response.text[:300]}")
  try:
    responseMSG = response.json()
  except json.JSONDecodeError:
    raise RuntimeError(f"Non-JSON response from API: {response.text[:300]}")
  return responseMSG


def call(text):
  if not API_KEY:
    raise RuntimeError("Missing API_Key")
  with open("system_prompts/grammarly_systemPrompt.txt", "r", encoding = "utf-8") as f:
    system_prompt = f.read()
  last_response = None
  for token_limit in (2000, 4000, 8000):
    responseMSG = _request_completion(system_prompt, text, token_limit)
    last_response = responseMSG
    if "choices" not in responseMSG or not responseMSG["choices"]:
      raise RuntimeError(f"Unexpected API format: {responseMSG}")
    choice = responseMSG["choices"][0]
    finish_reason = choice.get("finish_reason")
    if finish_reason == "length":
      continue
    return choice["message"]["content"]
  raise RuntimeError(f"Model output was truncated by token limits: {last_response}")
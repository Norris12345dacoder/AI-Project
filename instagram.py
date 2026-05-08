import requests, json, os
API_KEY = os.getenv("OPENROUTER_API_KEY")
# API_KEY = os.getenv("HACKCLUBAI_API_KEY")
# MODEL_ID = "openai/gpt-4o"
MODEL_ID = "qwen/qwen3-vl-235b-a22b-instruct"
# PRESET_ID = "@preset/caption-generator"
# URL = "https://openrouter.ai/api/v1/chat/completions"
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
def call(imageURL, language, length, hashtags):
  with open("system_prompts/instagram_systemPrompt.txt", "r") as f:
    system_prompt = f.read()
  captionLength = 50
  if length == "Long":
    captionLength = 100
  elif length == "Short":
    captionLength = 20
  hashtagNo = 5
  if hashtags == "More":
    hashtagNo = 10
  elif hashtags == "Less":
    hashtagNo = 2
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
                "text": f"Here is the image, generate an Instagram caption for the product in the image, I want the caption length to be in around {captionLength} and have {hashtagNo} hashtags, then generate the caption to {language} and delete the original one"
              },
              {
                  "type": "image_url",
                  "image_url": {
                      "url": imageURL
                  }
              }
          ]
        }
      ]
    }),
    timeout = (5, 30)
  )
  if response.status_code >= 400:
    raise RuntimeError(f"Hack Club AI HTTP {response.status_code}: {response.text[:300]}")
  try:
    responseMSG = response.json()
  except json.JSONDecodeError:
    raise RuntimeError(f"Non-JSON response from API: {response.text[:300]}")
  if "choices" not in responseMSG:
    raise RuntimeError(f"Unexpected API format: {responseMSG}")
  return responseMSG["choices"][0]["message"]["content"]
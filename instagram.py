import requests, json, os, random
API_KEY = os.getenv("OPENROUTER_API_KEY")
# API_KEY = os.getenv("HACKCLUBAI_API_KEY")
# MODEL_ID = "openai/gpt-4o"
MODEL_ID = "qwen/qwen3-vl-235b-a22b-instruct"
PRESET_ID = "@preset/caption-generator"
# URL = "https://openrouter.ai/api/v1/chat/completions"
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
imageLinks = ["https://watchwired.com/wp-content/uploads/2023/09/Rolex-watch-10-1024x585.jpg", "https://static1.topspeedimages.com/wordpress/wp-content/uploads/jpg/202208/new-porsche-911-gt3--13.jpg", "https://www.golfposer.com/media/wysiwyg/Travis-Scott-Air-Jordan-Golf-Shoes-eMAG-square.jpg", "https://images.macrumors.com/t/RHw_XUx-pFE6pl5TRv5a-LLIk9Y=/2500x0/filters:no_upscale()/article-new/2024/10/iPhone-17-Pro-Max-Smaller-Notch-Feature.jpg", "https://cdn.vox-cdn.com/uploads/chorus_asset/file/25774827/Tottenham_25_26_Away_Kit_Leaked__1_.jpg", "https://cdn.tatlerasia.com/tatlerasia/i/2021/08/11144803-assorted-traditional-baked-mooncakes3_cover_1000x668.jpg", "https://tse4.mm.bing.net/th/id/OIP.sTa78GZ6FeqR6F0MCCWelwHaDt?cb=12ucfimg=1&rs=1&pid=ImgDetMain&o=7&rm=3"]
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
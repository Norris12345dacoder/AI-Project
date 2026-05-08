import requests, os, json
API_KEY = os.getenv("OPENROUTER_API_KEY")
# MODEL_ID = "google/gemini-2.0-flash-001"
MODEL_ID = "google/gemini-2.5-flash"
# PRESET_ID = "@preset/netflix-analysis"
# URL = "https://openrouter.ai/api/v1/chat/completions"
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
def call(file, type):
  with open("system_prompts/netflix_systemPrompt.txt", "r") as f:
    system_prompt = f.read()
    system_prompt = system_prompt.replace("# System prompt\n\n## This is the system prompt of my preset in Openrouter for the Netflix web scrapping project\n\n", "")
  with open(file, "r") as f:
    data = f.read()
  response = requests.post(
    url = URL,
    headers = {
      "Authorization": f"Bearer {API_KEY}",
      "Content-Type": "application/json"
    },
    data = json.dumps({
      "model": MODEL_ID,
      "max_tokens": 4096,
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
                "text": f"Here is the file content, {data}. Generate the analysis for only {type}."
              }
          ]
        }
      ]
    })
  )
  responseMSG = response.json()
  print("API response: ", responseMSG)
  if "error" in responseMSG:
    return f"API Error: {responseMSG['error']}"
  if "choices" not in responseMSG:
    return f"Unexpected response format: {responseMSG}"
  return responseMSG["choices"][0]["message"]["content"]



# You are a data analyst for Netflix
# You will be given a json file of the Netflix data of different countries
# You will also be given the type of program (movies or tv shows) data you need to extract from the file for your analysis
# In the file for every country, there will be data like top 10 movies, top 10 tv shows etc.

# Your job is to analyze these data and make reports about it.

# Make a list of the top 10 most famous movies/tv shows in the world (include the number of countries this movie/tv show is ranked)

# Plot a pie chart of the most famous movies/tv shows, include all movies/tv shows, plot it by how many countries the movies/tv shows are ranked

# After that for the top 10 most famous movies/tv shows, list each of their rankings in every country and also go on the Internet and find comments about each, both positive and negative (include source).

# Export in html format
# Don't give me other texts (e.g. greetings, suggestions), I just want the html code
# Also don't give me other tags (e.g. <html>, <head>, <body>)
# I want the html code to represent your response that's intended to be put inside a <body> tag, no other thing
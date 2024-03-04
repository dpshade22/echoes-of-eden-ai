import re
import os
import requests
import datetime

# Global configuration
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech/onwK4e9ZLuTAKqWW03F9"
PERPLEXITY_API_KEY = os.getenv('PPLX')
ELEVENLABS_API_KEY = os.getenv('ELVLAB')

def clean_text(text):
  # Remove markdown bold/italic syntax (e.g., **bold**, *italic*)
  text = re.sub(r'\*\*|\*', '', text)

  # Remove bullet points that include Roman numerals followed by a period (e.g., "ii.", "iii.")
  text = re.sub(r'\b(i{1,3}|iv|v{1,3}|ix|x{1,3})\.\s*',
                '',
                text,
                flags=re.IGNORECASE)

  # Remove alphabetic bullet points (e.g., "a.", "A.", "b.", "B.", etc.), case-insensitive
  text = re.sub(r'\b[a-zA-Z]\.\s*', '', text)

  # Remove any remaining non-alphanumeric characters that are not part of spoken language,
  # keeping spaces, apostrophes, and hyphens that may be part of normal speech
  text = re.sub(r'[^\w\s\'\-:\.\?\!]', '', text)

  pattern = r'(\d+)-(\d+)'
  replacement = r'\1 through \2'
  return re.sub(pattern, replacement, text)

def send_text_to_api(text):
  if not PERPLEXITY_API_KEY:
    print("Perplexity API key is not set.")
    return {}

  payload = {
      "model":
      "mixtral-8x7b-instruct",
      "messages": [{
          "role":
          "system",
          "content":
          ("You are an AI designed to generate scripts for a voice LLM. "
           "Generate content suitable for direct vocalization, avoiding non-verbal labels, "
           "instructions, or scene settings.")
      }, {
          "role":
          "user",
          "content":
          f"Use the following to write the spoken content for a Christian podcast episode short, focusing solely on narrative and insights without non-verbal instructions or labels. Convert <tags> to the expected Bible values. Always write the scripture verbatim as found. Use punctuation (such as commas) to increase inflection in sentences. Use the following as your source of the verse to speak as well as the information to commentate on the verse: {text}",
      }],
      "temperature": 1,
      "frequency_penalty": 1.05
  }

  headers = {
      "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
      "Content-Type": "application/json",
      "Accept": "application/json"
  }

  try:
    response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
  except requests.RequestException as e:
    print(f"Error sending text to API: {e}")
    return {}

def write_and_get_pplx_podcast_script(scripture, captured_text):
    current_date = datetime.now().strftime("%B %d")

    podcast_intro = (
        "Welcome back to the Echoes of Eden podcast with your AI host, Jonah. "
        f"Today is {current_date}, we're going to explore the narrative of {scripture}, "
        "book in the <New or Old> Testament.  <Writer of scripture> <Chapter number> <Verse number> wrote... <insert scripture>"
    )

    podcast_outro = "Come back tomorrow for more readings of scripture and insights into the Bible!"
    api_response = send_text_to_api(podcast_intro + captured_text +
                                    podcast_outro)
    api_response = api_response.get('choices',
                                    [{}])[0].get('message',
                                                    {}).get('content', '')
    cleaned_response = clean_text(api_response)

    with open(f'TodaysEcho-{scripture}.txt', 'w') as f:
        f.write(cleaned_response)
        

def digest_to_speech(file_path):
  if not ELEVENLABS_API_KEY:
    print("ElevenLabs API key is not set.")
    return

  with open(f"{file_path}.txt", 'r', encoding='utf-8') as file:
    text_to_speak = file.read()

  payload = {"model_id": "eleven_multilingual_v1", "text": text_to_speak}
  headers = {
      "xi-api-key": ELEVENLABS_API_KEY,
      "Content-Type": "application/json"
  }

  try:
    response = requests.post(ELEVENLABS_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    with open(f'{file_path}.mp3', 'wb') as f:
      for chunk in response.iter_content(chunk_size=1024):
        if chunk:
          f.write(chunk)
  except requests.RequestException as e:
    print(f"Error converting text to speech: {e}")

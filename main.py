from bs4 import BeautifulSoup
from datetime import datetime
from scraper import get_enduring_word_analysis, get_verse_of_the_day, format_bible_reference
from api import write_and_get_pplx_podcast_script, clean_text, digest_to_speech
import requests
import os
import re

override_analysis = ""

if __name__ == "__main__":
  
  scripture, _ = format_bible_reference(get_verse_of_the_day())
  captured_text = get_enduring_word_analysis() if not override_analysis else override_analysis

  if captured_text:
    api_response = write_and_get_pplx_podcast_script(scripture, captured_text)

    if api_response:
      usrDecide = input("Press Enter to convert the text to speech...")
      # digest_to_speech(scripture)
    else:
      print("Failed to process API response.")

  else:
    print("No text captured from URL.")

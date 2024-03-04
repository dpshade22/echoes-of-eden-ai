from bs4 import BeautifulSoup
from datetime import datetime
from scraper import get_enduring_word_analysis, get_verse_of_the_day
from api import send_text_to_api, clean_text, digest_to_speech
import requests
import os
import re


if __name__ == "__main__":
  
  scripture = get_verse_of_the_day()
  captured_text = get_enduring_word_analysis()

  if captured_text:


    if api_response:
      usrDecide = input("Press Enter to convert the text to speech...")
      digest_to_speech(f"TodaysEcho-{scripture}")
    else:
      print("Failed to process API response.")

  else:
    print("No text captured from URL.")

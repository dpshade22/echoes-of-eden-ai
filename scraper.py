import requests
from bs4 import BeautifulSoup
import re


# ----------------- GETTING VERSE OF THE DAY ----------------------------

def format_bible_reference(reference):
    # Use a regular expression to capture the book, chapter, and verse
    match = re.match(r'(\d?\s?[A-Za-z]+)\s(\d+):(\d+)\s\((\w+)\)', reference)
    if not match:
        return None, None  # Return None if the format does not match

    book, chapter, verse, translation = match.groups()

    # Format the book for URL: lowercase, replace spaces with dashes
    # If the book starts with a digit and a space (e.g., "1 Chronicles"), keep the digit
    book_formatted = book.lower().replace(' ', '-')

    # Concatenate the book and chapter for the URL part
    url_part = f"{book_formatted}-{chapter}"

    return url_part, int(verse)


def get_verse_of_the_day():
    url = "https://www.bible.com/verse-of-the-day"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.content, 'html.parser')
    
        css_selector = '.font-aktiv-grotesk.uppercase'
        element = soup.select_one(css_selector)
        if element:
            return element.text.strip()
        else:
            return "Verse not found."
    except requests.RequestException as e:
        print(f"Error fetching Verse of the Day: {e}")
        return None

# ----------------- INTERACTING WITH ENDURING WORD ----------------------------
def get_enduring_word_url(chapter):
    return f"https://enduringword.com/bible-commentary/{chapter}/"

def find_and_capture_text_from_url(url, verseNum):
    html_content = fetch_html_content(url)
    if html_content is None:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    captured_texts = []

    for tag in soup.find_all('h4'):
        # Find ranges in the tag text
        ranges = re.findall(r'(\d+)-(\d+)', tag.text)
        # Convert verseNum to int for comparison (assuming verseNum is a string)
        verseNum_int = int(verseNum)
        for start, end in ranges:
            if verseNum_int >= int(start) and verseNum_int <= int(end):
                capture_text_until_next_h4(tag, captured_texts)
                return ' '.join(captured_texts)  # Return immediately after finding the match

    # If no matching range is found, return an empty string
    return ""

def capture_text_until_next_h4(tag, captured_texts):
  current = tag.find_next_sibling()
  while current and current.name != 'h4':
    if current.name and current.text.strip():
      captured_texts.append(current.text.strip())
    current = current.find_next_sibling()



# ----------------- GENERAL HELPERS ----------------------------
def fetch_html_content(url):
  try:
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.content
  except requests.RequestException as e:
    print(f"Error fetching URL {url}: {e}")
    return None

def get_enduring_word_analysis():
    verse_of_the_day = get_verse_of_the_day()
    print(verse_of_the_day)
    chapter, verseNum = format_bible_reference(verse_of_the_day)

    url = get_enduring_word_url(chapter)
    print(url)
    
    enduring_analysis = find_and_capture_text_from_url(url, verseNum)
    return enduring_analysis

print(get_enduring_word_analysis())
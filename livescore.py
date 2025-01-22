import time
from requests import Session
from bs4 import BeautifulSoup

S_MATCHES = r'.ds-max-w-\[918px\] > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1) > div:nth-child(1)'
cached_match = {}
last_fetched = {}
CACHE_TTL = 60  # Cache Time-to-Live in seconds

# Create a global session to reuse connections and improve performance
session = Session()

def text(soup, selector):
    element = soup.select_one(selector)
    return element.text.strip() if element else ''

def fetch_url(url):
    """ Fetch URL using session and cache response for reuse. """
    current_time = time.time()

    # If cache does not exist or cache is expired, fetch the data again
    if url not in cached_match or current_time - last_fetched[url] > CACHE_TTL:
        print(f"Fetching fresh data for: {url}")
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        cached_match[url] = soup
        last_fetched[url] = current_time
    else:
        print(f"Using cached data for: {url}")

    return cached_match[url]

def get_matches():
    """Retrieve live cricket scores from ESPN Cricinfo."""
    url = "https://www.espncricinfo.com/live-cricket-score"
    soup = fetch_url(url)
    matches = soup.select(S_MATCHES)
    m_data = []

    for match in matches:
        data = {
            'time': text(match, '.ds-text-tight-xs'),
            'teams': [team.text.strip() for team in match.select('.ds-text-tight-m.ds-font-bold.ds-capitalize')],
            'status': text(match, '.ds-text-tight-s.ds-font-medium'),
            'link': f"https://www.espncricinfo.com{match.select_one('a')['href']}"
        }
        m_data.append(data)

    return m_data

def get_match(url):
    """Retrieve detailed match information."""
    soup = fetch_url(url)
    m_details = {}

    m_details['teams'] = {
        't1n': text(soup, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > span'),
        't1o': text(soup, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(2) > span'),
        't1s': text(soup, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(2) > strong'),
        't2n': text(soup, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(2) > span'),
        't2o': text(soup, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(2) > span'),
        't2s': text(soup, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(2) > strong'),
    }
    m_details['bt1'] = {
        'name': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(1) > div > div > a > span'),
        'style': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
        'runs': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(2) > strong'),
        'balls': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(3)'),
        '4s': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(4)'),
        '6s': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(5)'),
        'sr': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(6)'),
    }
    m_details['bt2'] = {
        'name': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div > div > a > span'),
        'style': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
        'runs': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(2) > strong'),
        'balls': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(3)'),
        '4s': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(4)'),
        '6s': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(5)'),
        'sr': text(soup, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(6)'),
    }
    m_details['bw1'] = {
        'name': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(1) > div > div > a > span'),
        'status': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
        'overs': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(2)'),
        'maiden': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(3)'),
        'runs': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(4)'),
        'wkts': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(5)'),
        'econ': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(6)'),
        '0s': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(7)'),
        '4s': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(8)'),
        '6s': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(9)'),
        'spell': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(10)'),
    }
    m_details['bw2'] = {
        'name': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(1) > div > div > a > span'),
        'status': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
        'overs': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(2)'),
        'maiden': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(3)'),
        'runs': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(4)'),
        'wkts': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(5)'),
        'econ': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(6)'),
        '0s': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(7)'),
        '4s': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(8)'),
        '6s': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(9)'),
        'spell': text(soup, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(10)'),
    }
    m_details['info'] = {
        'venue': text(soup, r'.lg\:ds-border-b > tbody > tr:nth-child(1) > td > a > span'),
        'toss': text(soup, r'.lg\:ds-border-b > tbody > tr:nth-child(2) > td:nth-child(2) > span'),
        'series': text(soup, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(2) > div:nth-child(1) > a:nth-child(1) > span:nth-child(1)'),
        'season': text(soup, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(2) > a:nth-child(1) > span:nth-child(1)'),
        'hours': text(soup, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(2) > span:nth-child(1)'),
        'matchdays': text(soup, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(6) > td:nth-child(2) > span:nth-child(1)'),
        'umpires': [text(soup, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(7) > td:nth-child(2) > div:nth-child(1) > a:nth-child(1) > span:nth-child(2) > span:nth-child(1)'),
                    text(soup, r'div.last\:ds-border-0:nth-child(2) > a:nth-child(1) > span:nth-child(2) > span:nth-child(1)'),
                    text(soup, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(8) > td:nth-child(2) > div:nth-child(1) > a:nth-child(1) > span:nth-child(2) > span:nth-child(1)'),
                    text(soup, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(9) > td:nth-child(2) > div:nth-child(1) > a:nth-child(1) > span:nth-child(2) > span:nth-child(1)')],
        'referee': text(soup, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(10) > td:nth-child(2) > div:nth-child(1) > a:nth-child(1) > span:nth-child(2) > span:nth-child(1)')
    }

    return m_details

def get_match_data(url, category, player=None):
    """
    A helper function to extract specific match details.
    Args:
    - url (str): URL of the match.
    - category (str): Category such as 'bt1', 'bt2', 'bw1', 'bw2', or 'info'.
    - player (str): Optional player name to access specific data like runs or overs.
    
    Returns:
    - Data for the requested category.
    """
    match_details = get_match(url)
    
    if category not in match_details:
        return f"Category '{category}' not found"
    
    # If accessing player-specific data (e.g. runs, balls), use player index
    if player:
        return match_details[category].get(player, f"Player '{player}' not found in '{category}'")
    
    return match_details[category]

print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
print(get_match_data('https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/fortune-barishal-vs-khulna-tigers-30th-match-1459566/live-cricket-score', 'bt1', 'runs'))
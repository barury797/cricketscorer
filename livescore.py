import re
import time
import asyncio
from requests import Session
from bs4 import BeautifulSoup

S_MATCHES=r'.ds-max-w-\[918px\] > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1) > a:nth-child(1)'

matches_details, matches_summary, cache_list = {}, {}, {}
MATCHES_CACHE_TTL = 60  # Cache Time-to-Live in seconds
MATCH_CACHE_TTL = 60  # Cache Time-to-Live in seconds
session = Session()

async def matches_data():
    """
    An asynchronous helper function to extract live matches.
    """
    # If cache does not exist or cache is expired, fetch the data again
    if 'matches' not in cache_list or time.time() - cache_list.get('matches', 0) > MATCHES_CACHE_TTL:
        print(f"Fetching fresh data for: {'matches'}")
        # Run the synchronous `get_match` function in a thread
        matches_details['matches'] = await asyncio.to_thread(get_matches)
        cache_list['matches'] = time.time()
    else:
        print(f"Using cached data for matches")
    
    return matches_details['matches']

async def match_data(url, category='summary'):
    """
    An asynchronous helper function to extract specific match details.
    Args:
    - url (str): URL of the match.
    - category (str): Category such as 'bt1', 'bt2', 'bw1', 'bw2', or 'info'.
    """

    if not url:
        return "URL is required."

    # If cache does not exist or cache is expired, fetch the data again
    if url not in cache_list or time.time() - cache_list.get(url, 0) > MATCH_CACHE_TTL:
        print(f"Fetching fresh data for: {url}")
        # Run the synchronous `get_match` function in a thread
        matches_details[url], matches_summary[url] = await asyncio.to_thread(get_match, url)
        cache_list[url] = time.time()
    else:
        print(f"Using cached data for: {url}")
    
    # Retrieve category data
    if category == 'summary':
        return matches_summary[url]
    elif category == 'all':
        return matches_details[url]
    else:
        data = matches_details[url]
        return data[category] if category in data else f"Category '{category}' not found"

def text(sp, selector):
    element = sp.select_one(selector)
    return element.text.strip() if element else ''

def match_status(m_details):
    status = m_details['match']['status'].lower()
    title = m_details['match']['title'].lower()

    if not m_details or not status: return '00'

    if not title: return '10' # Match not started

    if 'chose' in status and m_details['teams']['t1s']: return '30' # 1st Innings

    if 'need' in status and 'balls' in status: return '40' # 2nd Innings (limited overs)
    
    if 'timeout' in title: return '61' # Timeout
    if 'rain' in title: return '62' # Rain Delay
    if 'innings break' in title: return '63'# Innings Break
    if 'lunch' in title: return '64' # Lunch
    if 'tea' in title: return '65' # Tea
    if 'stumps' in title: return '66' # Stumps
    if 'wet outfield' in title: return '67' # Wet Outfield
    if 'match delayed' in title: return '60' # Other breaks

    if 'chose' in status: return '20' # Toss done but match not started

    if 'won' in status: return '70' # Match Concluded

    return '01' # Unknown Status
    

def get_matches():
    matches = BeautifulSoup(session.get("https://www.espncricinfo.com/live-cricket-score").content, 'html.parser').select(S_MATCHES)
    m_data = []

    for match in matches:
        data = {
            'time': text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1)'),
            'score': {
                text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > p:nth-child(2)'): 
                text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > strong:nth-child(2)'),
                                                                                                                                                                              
                text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > p:nth-child(2)'): 
                text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > strong:nth-child(2)'),
            },
            'status': text(match, 'div:nth-child(1) > div:nth-child(1) > p:nth-child(3) > span:nth-child(1)').replace('.', ''),
            'link': f"https://www.espncricinfo.com{match['href']}"
        }
        
        m_data.append(data)

    return m_data

def get_match(url):
    sp = BeautifulSoup(session.get(url).content, 'html.parser')

    timeline_elements = [ e.text for e in sp.select('#main-container > div.ds-relative > div > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-mt-3 > div.ds-mb-2 > div:nth-child(2) > div > div.ds-border-line.ds-border-t > div > div > div.ds-flex.ds-flex-row.ds-w-full.ds-overflow-x-auto.ds-scrollbar-hide.ds-items-center.ds-space-x-2 > div') if e.text != 'See all ❯']
    th_markers = [(i,e) for i,e in enumerate(timeline_elements) if 'th' in e]
    timeline = {f"{int(m.split('th')[0])}th": [m[-1]] + timeline_elements[p+1:p+6] for p,m in th_markers}
    if th_markers and th_markers[0][0] > 0: timeline[f"{max(int(k.split('th')[0]) for k in timeline.keys())+1}th"] = timeline_elements[:th_markers[0][0]] 
    
    m_title = text(sp, '#main-container > div.ds-relative > div > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-w-full.ds-bg-fill-content-prime.ds-overflow-hidden.ds-rounded-xl.ds-border.ds-border-line > div > div:nth-child(1) > div.ds-px-4.ds-py-3.ds-border-b.ds-border-line > div > div.ds-grow > div:nth-last-child(1)').split(', ')

    m_details = {
        'match': {
            'title': text(sp, 'strong.ds-uppercase'),
            'status': text(sp, 'p.ds-text-tight-s:nth-child(3) > span:nth-child(1)').replace('.', ''),
            'matchno': m_title[0],
            'location': m_title[1],
            'date': f'{m_title[2]}, {m_title[3]}',
            'tournament': m_title[4],
        },
        'teams': {
            't1n': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > span'),
            't2n': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(2) > span'),
            't1o': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(2) > span'),
            't1s': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(2) > strong'),
            't2o': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(2) > span'),
            't2s': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(2) > strong'),
            },
        'info': {
            'stadium': text(sp, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > a:nth-child(1) > span:nth-child(1)')
        },
    }
    m_details['match'].update({
        'status_code' : match_status(m_details),
        'crr': text(sp, r'div.md\:ds-mt-0:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)'),
        'rrr': text(sp, r'div.md\:ds-mt-0:nth-child(2) > div:nth-child(1) > div:nth-child(2) > span:nth-child(3)'),
        'timeline': dict(sorted(timeline.items(), key=lambda x: int(x[0].split('th')[0]), reverse=True)),
        'prediction': text(sp, r'.lg\:ds-p-0'),
        'reviews': text(sp, 'div.ds-mt-3:nth-child(3) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')
    })
    for i in range(1, 3):
        m_details[f'bt{i}'] = {
            'name': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({i}) > td:nth-child(1) > div > div > a > span'),
            'style': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({i}) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
            'runs': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({i}) > td:nth-child(2) > strong'),
            'balls': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({i}) > td:nth-child(3)'),
            '4s': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({i}) > td:nth-child(4)'),
            '6s': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({i}) > td:nth-child(5)'),
            'sr': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({i}) > td:nth-child(6)'),
        }
        m_details[f'bw{i}'] = {
            'name': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(1) > div > div > a > span'),
            'style': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
            'overs': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(2)'),
            'maiden': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(3)'),
            'runs': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(4)'),
            'wkts': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(5)'),
            'econ': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(6)'),
            '0s': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(7)'),
            '4s': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(8)'),
            '6s': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(9)'),
            'spell': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({i}) > td:nth-child(10)'),
        }
    for row in sp.select(r'.lg\:ds-border-b > tbody:nth-child(1) tr'):
        cells = row.find_all('td')
        if len(cells) > 1:
            key, value = cells[0].get_text(strip=True), cells[1]
            if key == 'Umpires':
                m_details['info'][key] = [umpire.get_text(strip=True) for umpire in value.find_all('a', title=True)]
                if not m_details['info'][key]:
                    m_details['info'][key] = [span.get_text(strip=True) for span in value.find_all('span', class_='ds-text-tight-s')]
            else:
                m_details['info'][key] = value.get_text(strip=True)  

    m_summary = {
        't1n': m_details['teams']['t1n'],
        't1s': m_details['teams']['t1s'],
        't2n': m_details['teams']['t2n'],
        't2s': m_details['teams']['t2s'],
        'status': m_details['match']['status'],
        'crr': m_details['match']['crr'],
        'rrr': m_details['match']['rrr'],
    }

    return m_details, m_summary


async def main():
    # print(await matches_data())
    url = 'https://www.espncricinfo.com/series/big-bash-league-2024-25-1443056/sydney-sixers-vs-sydney-thunder-challenger-1443099/live-cricket-score'
    print(await match_data(url, 'all'))

if __name__ == "__main__":
    asyncio.run(main())
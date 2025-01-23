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

    timeline_elements = [e.replace('•', '.') for e in sp.select('#main-container > div.ds-relative > div > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-mt-3 > div.ds-mb-2 > div:nth-child(2) > div > div.ds-border-line.ds-border-t > div > div > div.ds-flex.ds-flex-row.ds-w-full.ds-overflow-x-auto.ds-scrollbar-hide.ds-items-center.ds-space-x-2 > div').text if e != 'See all ❯']
    th_markers = [(i,e) for i,e in enumerate(timeline_elements) if 'th' in e]
    timeline = {f"{int(m.split('th')[0])}th": [m[-1]] + timeline_elements[p+1:p+6] for p,m in th_markers}
    if th_markers and th_markers[0][0] > 0:
        timeline[f"{max(int(k.split('th')[0]) for k in timeline.keys())+1}th"] = timeline_elements[:th_markers[0][0]]

    m_details = {
        'match': {
            'status': text(sp, 'p.ds-text-tight-s:nth-child(3) > span:nth-child(1)').replace('.', ''),
            'crr': text(sp, r'div.md\:ds-mt-0:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)'),
            'rrr': text(sp, r'div.md\:ds-mt-0:nth-child(2) > div:nth-child(1) > div:nth-child(2) > span:nth-child(3)'),
            'timeline': dict(sorted(timeline.items(), key=lambda x: int(x[0].split('th')[0]), reverse=True)),
        },
        'teams': {
            't1n': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > span'),
            't1o': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(2) > span'),
            't1s': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(2) > strong'),
            't2n': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(2) > span'),
            't2o': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(2) > span'),
            't2s': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(2) > strong'),
        },
        'bt1': {
            'name': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(1) > div > div > a > span'),
            'style': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
            'runs': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(2) > strong'),
            'balls': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(3)'),
            '4s': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(4)'),
            '6s': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(5)'),
            'sr': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(1) > td:nth-child(6)'),
        },
        'bt2': {
            'name': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div > div > a > span'),
            'style': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
            'runs': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(2) > strong'),
            'balls': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(3)'),
            '4s': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(4)'),
            '6s': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(5)'),
            'sr': text(sp, 'tbody.ds-text-right:nth-child(2) > tr:nth-child(2) > td:nth-child(6)'),
        }, 
        'bw1': {
            'name': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(1) > div > div > a > span'),
            'status': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
            'overs': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(2)'),
            'maiden': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(3)'),
            'runs': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(4)'),
            'wkts': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(5)'),
            'econ': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(6)'),
            '0s': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(7)'),
            '4s': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(8)'),
            '6s': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(9)'),
            'spell': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(1) > td:nth-child(10)'),
        },
        'bw2': {
            'name': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(1) > div > div > a > span'),
            'status': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(1) > div > span:nth-child(2)').replace('(', '').replace(')', ''),
            'overs': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(2)'),
            'maiden': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(3)'),
            'runs': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(4)'),
            'wkts': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(5)'),
            'econ': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(6)'),
            '0s': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(7)'),
            '4s': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(8)'),
            '6s': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(9)'),
            'spell': text(sp, 'tbody.ds-text-right:nth-child(4) > tr:nth-child(2) > td:nth-child(10)'),
        }
    }

    m_summary = {
        't1n': m_details['teams']['t1n'],
        't1s': m_details['teams']['t1s'],
        't2n': m_details['teams']['t2n'],
        't2s': m_details['teams']['t2s'],
        'status': m_details['match']['status'],
        'crr': m_details['match']['crr'],
        'rrr': m_details['match']['rrr'],
    }

    # print(sp.select('div.ds-bg-fill-content-prime:nth-child(4) > div:nth-child(2) > div:nth-child(2) > div'))

    return m_details, m_summary


async def main():
    # print(await matches_data())````
    url = 'https://www.espncricinfo.com/series/sa20-2024-25-1437327/durban-s-super-giants-vs-paarl-royals-18th-match-1449651/live-cricket-score'
    print(await match_data(url, 'all'))

if __name__ == "__main__":
    asyncio.run(main())
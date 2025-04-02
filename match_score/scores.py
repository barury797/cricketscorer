# scores.py

import requests
from bs4 import BeautifulSoup

session = requests.Session()

def text(sp, selector):
    element = sp.select_one(selector)
    return element.text.strip() if element else ''

def get_matches():
    """Fetch all live cricket matches"""
    site = session.get("https://www.espncricinfo.com/live-cricket-score")

    print(site.content)
    
    matches = BeautifulSoup(site.content, 'html.parser'
    ).select(r'#main-container > div.ds-relative > div > div.ds-flex.ds-space-x-5 > div.ds-grow.ds-px-0 > div.ds-max-w-\[918px\] > div:nth-child(3) > div > div:nth-child(1) > div > div.ds-p-0 > div > div')
    
    print(matches)
    
    return [{
        'time': text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1)'),
        'score': {
            text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > p:nth-child(2)'): 
            text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > strong:nth-child(2)'),
            
            text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > p:nth-child(2)'): 
            text(match, 'div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > strong:nth-child(2)'),
        },
        'status': text(match, 'div:nth-child(1) > div:nth-child(1) > p:nth-child(3) > span:nth-child(1)').replace('.', ''),
        'link': f"https://www.espncricinfo.com{match['href']}"
    } for match in matches]

def get_match(url):
    """Fetch detailed information for a specific match"""
    sp = BeautifulSoup(session.get(url).content, 'html.parser')
    
    # Extract timeline
    timeline = sp.select('#main-container > div.ds-relative > div > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-mt-3 > div.ds-mb-2 > div:nth-child(2) > div > div.ds-border-line.ds-border-t > div > div > div > div')
    if not timeline:
        timeline = sp.select('#main-container > div.ds-relative > div > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-mt-3 > div.ds-mb-2 > div:nth-child(2) > div > div.ds-border-line.ds-border-t > div > div > div.ds-flex.ds-flex-row.ds-w-full.ds-overflow-x-auto.ds-scrollbar-hide.ds-items-center.ds-space-x-2 > div')
    
    timeline_elements = [e.text for e in timeline if e.text != 'See all ❯']
    th_markers = [(i, e) for i, e in enumerate(timeline_elements) if 'th' in e]
    
    formatted_timeline = {}
    for p, m in th_markers:
        over = f"{int(m.split('th')[0])}th"
        formatted_timeline[over] = [m[-1]] + timeline_elements[p+1:p+6]
    
    if th_markers and th_markers[0][0] > 0:
        max_over = max(int(k.split('th')[0]) for k in formatted_timeline.keys()) + 1
        formatted_timeline[f"{max_over}th"] = timeline_elements[:th_markers[0][0]]
    
    # Extract match title
    m_title = text(sp, '#main-container > div.ds-relative > div > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-w-full.ds-bg-fill-content-prime.ds-overflow-hidden.ds-rounded-xl.ds-border.ds-border-line > div > div:nth-child(1) > div.ds-px-4.ds-py-3.ds-border-b.ds-border-line > div > div.ds-grow > div:nth-last-child(1)').split(', ')
    
    # Build result data
    result = {
        'match': {
            'status': text(sp, 'p.ds-text-tight-s:nth-child(3) > span:nth-child(1)').replace('.', ''),
            'status2': text(sp, r'div.md\:ds-mt-0:nth-child(2) > div:nth-child(1)').replace('Current RR', 'CRR').replace('Required RR', 'RRR').replace("\xa0", " "),
            'timeline': dict(sorted(formatted_timeline.items(), key=lambda x: int(x[0].split('th')[0]), reverse=True)),
        },
        'teams': {
            't1n': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > span'),
            't2n': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(2) > span'),
            't1s': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(2)'),
            't2s': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(2)'),
        }
    }
    
    # Extract player data
    for plno in range(1, 3):
        # Batters
        result[f'bt{plno}'] = {
            'name': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({plno}) > td:nth-child(1)'),
            'runs': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({plno}) > td:nth-child(2)'),
            'balls': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({plno}) > td:nth-child(3)'),
            'sr': text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({plno}) > td:nth-child(7)')
        }
        
        # Bowlers
        result[f'bw{plno}'] = {
            'name': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({plno}) > td:nth-child(1)'),
            'overs': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({plno}) > td:nth-child(2)'),
            'maiden': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({plno}) > td:nth-child(3)'),
            'runs': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({plno}) > td:nth-child(4)'),
            'wkts': text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({plno}) > td:nth-child(5)')
        }
        
        # Clean up player names
        for t in ['bt', 'bw']:
            if result[f'{t}{plno}']['name']:
                result[f'{t}{plno}']['name'] = result[f'{t}{plno}']['name'].replace('\xa0', ' ').replace('(', '').replace(')', '').replace('*', '').replace('h', '')
    
    return result

if __name__ == "__main__":
    print(get_matches())
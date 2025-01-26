import asyncio
from requests import Session
from bs4 import BeautifulSoup

S_MATCHES=r'.ds-max-w-\[918px\] > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1) > a:nth-child(1)'
session = Session()

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

    timeline = sp.select('#main-container > div.ds-relative > div > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-mt-3 > div.ds-mb-2 > div:nth-child(2) > div > div.ds-border-line.ds-border-t > div > div > div > div')
    if not timeline: timeline = sp.select('#main-container > div.ds-relative > div > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-mt-3 > div.ds-mb-2 > div:nth-child(2) > div > div.ds-border-line.ds-border-t > div > div > div.ds-flex.ds-flex-row.ds-w-full.ds-overflow-x-auto.ds-scrollbar-hide.ds-items-center.ds-space-x-2 > div')
    timeline_elements = [ e.text for e in timeline if e.text != 'See all ❯']
    th_markers = [(i,e) for i,e in enumerate(timeline_elements) if 'th' in e]
    timeline = {f"{int(m.split('th')[0])}th": [m[-1]] + timeline_elements[p+1:p+6] for p,m in th_markers}
    if th_markers and th_markers[0][0] > 0: timeline[f"{max(int(k.split('th')[0]) for k in timeline.keys())+1}th"] = timeline_elements[:th_markers[0][0]] 
    
    m_title = text(sp, '#main-container > div.ds-relative > div > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-w-full.ds-bg-fill-content-prime.ds-overflow-hidden.ds-rounded-xl.ds-border.ds-border-line > div > div:nth-child(1) > div.ds-px-4.ds-py-3.ds-border-b.ds-border-line > div > div.ds-grow > div:nth-last-child(1)').split(', ')

    m_details = {
        'match': {
            'title': text(sp, 'strong.ds-uppercase'),
            'status': text(sp, 'p.ds-text-tight-s:nth-child(3) > span:nth-child(1)').replace('.', ''),
            'status2': text(sp, r'div.md\:ds-mt-0:nth-child(2) > div:nth-child(1)').replace('Current RR','CRR').replace('Required RR','RRR').replace("\xa0"," "),
            'matchno': m_title[0],
            'location': m_title[1],
            'date': f'{m_title[2]}, {m_title[3]}',
            'tournament': m_title[4],
            'timeline': dict(sorted(timeline.items(), key=lambda x: int(x[0].split('th')[0]), reverse=True)),
            'prediction': text(sp, r'.lg\:ds-p-0'),
            'reviews': text(sp, 'div.ds-mt-3:nth-child(3) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')
        },
        'teams': {
            't1n': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > span'),
            't2n': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(2) > span'),
            't1s': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(1) > div:nth-child(2)'),
            't2s': text(sp, 'div.ds-mt-3:nth-child(1) > div:nth-child(2) > div:nth-child(2)'),
            },
        'info': {
            'stadium': text(sp, r'.lg\:ds-border-b > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > a:nth-child(1) > span:nth-child(1)')
        },
        'bt1': {}, 'bt2': {}, 'bw1': {}, 'bw2': {}
    }
    for plno in range(1, 3):
        for i in range(1, 7 + 1):
            for col_idx, data in enumerate(['name', 'runs', 'balls', '4s', '6s', 'sr', 'thisbowler', 'last5balls'], start=1):
                m_details[f'bt{plno}'][data] = text(sp, f'tbody.ds-text-right:nth-child(2) > tr:nth-child({plno}) > td:nth-child({col_idx})')

        for i in range(1, 9 + 1):
            for col_idx, data in enumerate(['name', 'overs', 'maiden', 'runs', 'wkts', 'econ', '0s', '4s', '6s', 'spell'], start=1):
                m_details[f'bw{plno}'][data] = text(sp, f'tbody.ds-text-right:nth-child(4) > tr:nth-child({plno}) > td:nth-child({col_idx})')

        for t in ['bt', 'bw']:
            m_details[f'{t}{plno}']['name'] = m_details[f'{t}{plno}']['name'].replace('\xa0', ' ').replace('(', '').replace(')', '').replace('*', '').replace('h', '')

    for row in sp.select(r'.lg\:ds-border-b > tbody:nth-child(1) tr'):
        cells = row.find_all('td')
        if len(cells) > 1:
            key, value = cells[0].text.strip(), cells[1]
            multiple_elements = value.find_all('a', title=True) or value.find_all('span', class_='ds-text-tight-s')
            m_details['info'][key] = [element.text.strip() for element in multiple_elements] if multiple_elements else value.text.strip()
            if isinstance(m_details['info'][key], list) and len(m_details['info'][key]) == 1:
                m_details['info'][key] = m_details['info'][key][0]

    return m_details


async def main():
    # print(await matches_data())
    url = 'https://www.espncricinfo.com/series/bangladesh-premier-league-2024-25-1459492/durbar-rajshahi-vs-rangpur-riders-34th-match-1459570/live-cricket-score'
    print(get_match(url))

if __name__ == "__main__":
    asyncio.run(main())
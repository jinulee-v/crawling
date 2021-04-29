import datetime
import argparse
from tqdm import tqdm

import requests
from bs4 import BeautifulSoup
from kss import split_sentences

topics = {
  'Minister of Defense': 'BBSMSTR_000000010021',
  'Army': 'BBSMSTR_000000010023',
  'Navy & Marine': 'BBSMSTR_000000010024',
  'Air Force': 'BBSMSTR_000000010025',
  'Joint Chiefs of Staff': 'BBSMSTR_000000010022',
  'Defense Industry': 'BBSMSTR_000000010027',
  'Service & Veterans': 'BBSMSTR_000000010028'
}

def address(date, index, topic_code):
  return 'https://kookbang.dema.mil.kr/newsWeb/{}/{}/{}/view.do'.format(
    date, index, topic_code
  )

def parse(html):

  soup = BeautifulSoup(html, 'html.parser')

  # Title
  title = soup.select(
    '#ntt_title1'
  )[0].text

  # Body text
  body_text = soup.select(
    '#content_body'
  )[0].findAll(text=True, recursive=True)
  body_text = ' '.join([text.strip().replace('\n', '').replace('\t', '') for text in body_text])
  body_text = '\t'.join(split_sentences(body_text))
  
  return [title, body_text]

def crawl(args):
  file = open(args.dst_path, 'a')

  start_date = datetime.date(2010, 7, 3)
  end_date = datetime.date(2020, 4, 20)
  day_count = (end_date - start_date).days + 1

  total_articles = 0

  # Date
  for date in [d for d in (start_date + datetime.timedelta(n) for n in range(day_count)) if d <= end_date]:
    datestr = date.strftime("%Y%m%d")

    # Daily index
    i = 1
    while True:

      req = None
      # Topic format
      for topic, code in topics.items():
        # Request topic
        try:        
          req = requests.get(address(datestr, i, code), allow_redirects=False)
        except KeyboardInterrupt:
          raise KeyboardInterrupt()
        except:
          print(datestr, topic, i)
          pass
        # If found something,
        if req and req.ok:
          if r"var _TRK_CP = \"/메인페이지/\";" in req.text:
            req = None 
            continue
          result = parse(req.text)
          if 'null' in result[0] or 'null' in result[1]:
            req = None
            continue
          
        file.write('\t'.join([datestr, topic] + result) + '\n')
        total_articles += 1
        print('current articles = {}'.format(total_articles), end='\r')
      # If reached the last article, proceed to next date
      if not req:
        break
      
      # Increment i
      i += 1
  
  print("Total articles retrieved: ", total_articles)
  close(file)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--dst-path', type=str, default='data/crawl.tsv', help='Path to store crawl results')
  args = parser.parse_args()

  crawl(args)
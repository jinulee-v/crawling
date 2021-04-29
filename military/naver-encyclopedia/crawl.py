import datetime
import argparse
from tqdm import tqdm

import requests
from bs4 import BeautifulSoup
from kss import split_sentences

topics = {
  'World of arms': '60355',
  'Aircrafts': '63727',
  'Ships': '63767',
  'Automobiles': '63775',
  'KODEF Military Aircrafts': '60348',
  'Guns': '60353',
  'Arms and weapons': '60344'
}
docid_range = {
  'Arms and weapons': (3595436, 6416765),
  'World of arms': (3569789, 3587850),
  'Aircrafts': (5730426, 5730745),
  'Ships': (5732125, 5733089),
  'Guns': (3584340, 4351408),
  'Automobiles': (5174683, 5739171),
  'KODEF Military Aircrafts': (1826490, 1826687)
}

def address(topic, index):
  return 'https://terms.naver.com/entry.naver?docId={}&cid={}&categoryId={}'.format(
    index, topic, topic
  )

def parse(html):

  soup = BeautifulSoup(html, 'html.parser')

  # Title
  title = soup.find(
    'h2', class_='headword'
  ).text

  # Body text
  body_text = soup.select(
    '#size_ct'
  )[0].findAll(text=True, recursive=True)
  body_text = [obj for obj in body_text]
  body_text = ' '.join([text.strip().replace('\n', '').replace('\t', '') for text in body_text])
  body_text = '\t'.join(split_sentences((body_text)))
  
  return [title, body_text]

def crawl(args):

  total_articles = 0
  # Daily index
  for topic, code in topics.items():
    file = open(args.dst_path.replace('.tsv', '_{}.tsv'.format(code)), 'w', encoding='UTF-8')
    print('\n' + topic)
    idx_range = docid_range[topic]
    
    for i in tqdm(range(idx_range[0], idx_range[1]+1)):
      req = None
      # Topic format
      # Request topic
      try:        
        req = requests.get(address(code, i), allow_redirects=False, headers={'User-Agent': 'Mozilla/5.0'})
      except KeyboardInterrupt:
        raise KeyboardInterrupt()
      except:
        print('Failed to recieve data:', i)
      # If found something,
      if req and req.ok:
        try:
          result = parse(req.text)
        except KeyboardInterrupt:
          raise KeyboardInterrupt()
        except Exception as e:
          continue
        file.write('\t'.join([topic] + result) + '\n')
        total_articles += 1
    file.close()
  
  print("Total articles retrieved: ", total_articles)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--dst-path', type=str, default='data/crawl.tsv', help='Path to store crawl results')
  args = parser.parse_args()

  crawl(args)
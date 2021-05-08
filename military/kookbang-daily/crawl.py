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

def address(topic_code, index):
  return 'https://kookbang.dema.mil.kr/newsWeb/{}/list.do?pageIndex={}'.format(
    topic_code, index
  )

def find_total_page(html):

  soup = BeautifulSoup(html, 'html.parser')

  last_page_a_tag = soup.select(
    '#container > div > div.conts_left > div.pagination > a.page_last'
  )[0]
  last_page_link = last_page_a_tag['onclick']
  last_page = ''
  for c in last_page_link:
    if c.isnumeric():
      last_page = last_page + c
  return int(last_page)


def find_article_links(html):

  soup = BeautifulSoup(html, 'html.parser')

  article_lists = soup.select(
    '#container > div > div.conts_left > ul'
  )[0]
  article_links = []
  for a_tag in article_lists.find_all('a'):
    article_links.append('https://kookbang.dema.mil.kr' + a_tag['href'])
  return article_links


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
  body_text = '\t'.join(split_sentences(body_text, safe=True))
  
  return title, body_text

def crawl(args):
  headers = {'User-Agent': 'Mozilla/5.0'}
  if args.resume_cat != 'Minister of Defense' or args.resume_page != 1:
    file = open(args.dst_path, 'a')
  else:
    file = open(args.dst_path, 'w')

  total_articles = 0
  resume = False

  # Category
  for topic, code in topics.items():
    if not resume and topic != args.resume_cat:
      continue
    resume = True
    print(topic)
    try:
      req_first_page = requests.get(address(code, 1), headers=headers)
      total_pages = find_total_page(req_first_page.text)
    except:
      print('First page(list) retrieving', topic, i)
      continue

    print('Total pages', total_pages)

    # Page index
    for i in tqdm(range(args.resume_page, total_pages+1)):
      args.resume_page = 0
      # Request topic
      try:        
        req_page = requests.get(address(code, i), headers=headers)
        article_links = find_article_links(req_page.text)
      except Exception as e:
        print(e)
        continue

      for link in article_links:
        try:
          req = requests.get(link, headers=headers)
          title, body_text = parse(req.text)
        except Exception as e:
          print(e)
          continue
        
        file.write('\t'.join([topic, title, body_text]) + '\n')
        total_articles += 1
        tqdm.write('total articles: {} / cat={}, page={}'.format(total_articles, topic, i))
  
  print("Total articles retrieved: ", total_articles)
  close(file)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--dst-path', type=str, default='data/crawl.tsv', help='Path to store crawl results')
  parser.add_argument('--resume-cat', type=str, default=list(topics.keys())[0])
  parser.add_argument('--resume-page', type=int, default=1)
  args = parser.parse_args()

  crawl(args)
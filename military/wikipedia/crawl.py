import argparse

import wikipediaapi
import requests
from tqdm import tqdm
from kss import split_sentences

topics = [
  '분류:공군',
  '분류:군사 전술',
  '분류:군사 제도',
  '분류:군인'
  '분류:군함',
  '분류:무기',
  '분류:육군',
  '분류:전쟁',
  '분류:해군',
  '분류:해병대',
]

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
  body_text = body_text.replace('. ', '.\t')
  
  return [title, body_text]

def crawl(args):
  if args.load_pages:
    with open(args.load_pages, 'r', encoding='UTF-8') as file:
      wiki_list = file.readl.splitlines()
      wiki_list = [title for title in wiki_list if title]
  else:
    total_articles = 0
    # Init Wikipedia object
    wiki = wikipediaapi.Wikipedia('ko')

    visited_topics = set()
    def get_category_members(category, level=0, max_level=2):
      categorymembers = category.categorymembers
      visited_topics.add(category.title)
      print(category.title)
      wiki_list = []
      for c in categorymembers.values():
        if c.ns == wikipediaapi.Namespace.CATEGORY and c.title not in visited_topics and level < max_level:
          wiki_list.extend(get_category_members(c, level+1, max_level))
        else:
          wiki_list.append(c)
      return wiki_list

    may_exist_dupl_wiki_list = []
    for topic in topics:
      root = wiki.page(topic)
      may_exist_dupl_wiki_list.extend(get_category_members(root))
    wiki_list = set([page.title for page in may_exist_dupl_wiki_list])
    print('Total pages to crawl:')
    print(len(list(wiki_list)))
    if args.save_pages:
      with open(args.save_pages, 'w', encoding='UTF-8') as file:
        file.write('\n'.join(wiki_list))
    
  file = open(args.dst_path, 'w', encoding='UTF-8')
  for title in tqdm(wiki_list):
    response = requests.get(
      'https://ko.wikipedia.org/w/api.php',
      params={
          'action': 'query',
          'format': 'json',
          'titles': title,
          'prop': 'extracts',
          'exintro': True,
          'explaintext': True,
      }).json()
    print()
    result = split_sentences([page['extract'].replace('\n', ' ') for page in response['query']['pages']], safe=True)
    file.write('\t'.join([title] + result) + '\n')
  file.close()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--dst-path', type=str, default='data/crawl.tsv', help='Path to store crawl results')
  parser.add_argument('--save-pages', type=str)
  parser.add_argument('--load-pages', type=str)
  args = parser.parse_args()
  assert not (args.save_pages and args.load_pages)

  crawl(args)
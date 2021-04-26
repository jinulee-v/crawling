import datetime
import argparse
from tqdm import tqdm

import  requests
from bs4 import BeautifulSoup

categories = {
  '국방소식/이슈 바로보기': '467601',
  '국방정책/정책 포커스': '467602',
  '국방정책/생생 현장스케치': '467603',
  '국방이야기': '496968',
  '국방기고/august의 군사세계': '471398',
  '국방기고/울프독의 War History': '471526'
}

def address(index):
  return 'https://mnd9090.tistory.com/{}'.format(
    index
  )

def parse(html):

  soup = BeautifulSoup(html, 'html.parser')

  # Wrong address
  test = soup.select(
    '#absent_post'
  )
  if test:
    print('empty index')
    return None

  # Title
  title = soup.select(
    '#jb_main_content > div.jb_content.jb_content_post > h2'
  )[0].text

  # Category
  category = soup.select(
    '#jb_main_content > div.jb_content.jb_content_post > p.jb_post_info > span.jb_post_info_category > a'
  )[0].text
  if category not in categories:
    return None

  # Body text
  body_text = soup.select(
    '#jb_main_content > div.jb_content.jb_content_post > div.jb_article'
  )[0].findAll(text=True, recursive=True)
  body_text = ' '.join([text.strip().replace('\n', '').replace('\t', '') for text in body_text])
  body_text = body_text.replace('. ', '.\t')
  
  return [category, title, body_text]

def crawl(args):
  file = open(args.data_path, 'w')

  total_articles = 0
  # Daily index
  for i in range(1, 4431):

    req = None
    # Topic format
    # Request topic
    try:        
      req = requests.get(address(i), allow_redirects=False)
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
      except:
        print('Failed parsing:')
        print(address(i))
      
      if not result:
        req = None
        continue
        
      file.write('\t'.join(result) + '\n')
      total_articles += 1
      print('current articles = {}'.format(total_articles), end='\r')
  
  print("Total articles retrieved: ", total_articles)
  file.close()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--dst-path', type=str, default='data/crawl.tsv', help='Path to store crawl results')
  args = parser.parse_args()

  crawl(args)
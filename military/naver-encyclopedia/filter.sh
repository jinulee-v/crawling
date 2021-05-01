for f in data/crawl_*; do
  echo "File -> $f"
  result=${f/crawl_/sentences_}
  result=${result/.tsv/.txt}
  python3 filter.py --src-path $f --dst-path $result
done

rm data/sentences.txt
touch data/sentences.txt
for f in data/sentences_*.txt; do
  echo "File -> $f"
  cat $f >> data/sentences.txt
done
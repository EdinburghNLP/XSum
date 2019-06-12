# Extreme Summarization (XSum) Dataset

**You can always build the dataset using the instructions below. The original dataset is also available upon request.**

This repository contains download and preprocessing instructions for the **XSum** dataset described in our EMNLP 2018 paper "[Don't Give Me the Details, Just the Summary! Topic-Aware Convolutional Neural Networks for Extreme Summarization](https://arxiv.org/abs/1808.08745)". Please contact me at shashi.narayan@ed.ac.uk for any question.

Please cite this paper if you use our code or data.
```
@InProceedings{xsum-emnlp,
  author =      "Shashi Narayan and Shay B. Cohen and Mirella Lapata",
  title =       "Don't Give Me the Details, Just the Summary! {T}opic-Aware Convolutional Neural Networks for Extreme Summarization",
  booktitle =   "Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing ",
  year =        "2018",
  address =     "Brussels, Belgium",
}
```

## What builds the XSum dataset?

**XSum-WebArxiveUrls.txt:** The XSum dataset consists of **226,711** Wayback archived BBC articles ranging over almost a decade (2010 to 2017) and covering a wide variety of domains (e.g., News, Politics, Sports, Weather, Business, Technology, Science, Health, Family, Education, Entertainment and Arts). 

**scripts/download-bbc-articles.py:** Use this script to download BBC articles (html files) from the Wayback Machine.

**scripts/parse-bbc-html-data.py:** Use this script to extract text from BBC html files.

**XSum-WebArxiveUrls-BBCids.txt:** Each article comes with a unique identifier in its URL.

**XSum-TRAINING-DEV-TEST-SPLIT-90-5-5.json:** We used these identifiers to randomly split the dataset into training (90%, 204,045), validation (5%, 11,332), and test (5%, 11,334) set.

## Running the Download and Extraction Scripts

The download script is based on the [methodology](https://github.com/deepmind/rc-data/) proposed in [Hermann et al. (2015)](http://arxiv.org/abs/1506.03340) from Google DeepMind. 

### Prerequisites
Python 2.7, wget, libxml2, libxslt, python-dev and virtualenv. libxml2 must be version 2.9.1. You can install libxslt from here: http://xmlsoft.org/libxslt/downloads.html

### Activating Virtual Environment
```
sudo pip install virtualenv
sudo apt-get install python-dev
virtualenv venv
source venv/bin/activate
wget https://github.com/deepmind/rc-data/raw/master/requirements.txt
pip install -r requirements.txt
sudo apt-get install libxml2-dev libxslt-dev
```

### Download URLs
```
python scripts/download-bbc-articles.py [--timestamp_exactness 14]
```
This will download BBC news articles (html files) from the Wayback Machine. The script could fail to download some URLs (Wayback Machine servers temporarily down). Please **run this script multiple times** to ensure that you have downloaded the whole dataset. Each time you run this script, it stores the missing URLs that should be downloaded in the next turn.

[Sep 19, 2018]: Each URL includes a timestamp (14 letters; year, month, date, hour, minute and second, e.g., 20130206080312) showing when it was stored. By default, it is set to 14 letters. You can lower this to improve your chances to download a BBC article. For example, with timestamp_exactness=4 the time stamp will be chopped to first 4 letters (i.e., 2013) and it will try to download a version of the article stored in 2013 (any month, date, hour, minute or second). Every time you rerun the download script, lower the timestamp_exactness (>= 1) to improve the chances of getting missed URLs from the previous step. However, lower the timestamp_exactness value, more time it will take to retrieve the article.

This will create a directory called "xsum-raw-downloads" with downloaded html files.

### Extract Text from HTML files
```
python scripts/parse-bbc-html-data.py
```
This will extract text (url, body, summary) from html files. It will create a directory called "xsum-extracts-from-downloads" with extracted data (*bbcid.data*) files.

### Deactivate Virtual Environment
```deactivate```

## Postprocessing: Sentence Segmentation, Tokenization, Lemmatization and Final preparation

### Stanford CoreNLP toolkit 

We use the Stanford CoreNLP toolkit to preprocess (segment, tokenize and lemmatize) the extracted files in "xsum-extracts-from-downloads." 

Create a file *stanford-inputlist.txt* which lists extracted data files in "xsum-extracts-from-downloads." For example, it will have entries like:
```
xsum-extracts-from-downloads/2333890.data
xsum-extracts-from-downloads/3245891.data
and so on.
```

Now, run the Stanford CoreNLP toolkit:
```
cd tools/stanford-corenlp-full-2015-12-09
./corenlp.sh -annotators tokenize,ssplit,pos,lemma -ssplit.newlineIsSentenceBreak always -filelist stanford-inputlist.txt -outputFormat xml -outputDirectory StanfordOutput
```

The directory "StanfordOutput" will have CoreNLP output files in the XML format. 

### Extracting data from CoreNLP XML files
```
python3 scripts/process-corenlp-xml-data.py
```
It processes files in "StanfordOutput" and creates a directory "xsum-preprocessed" with three subfolders "document", "document-lemma" and "summary".

* "document-lemma" files are used to train LDA models. 

## LDA Topic Modeling

This part is only used for Topic-ConvS2S models.

We use the gensim's parallelized Latent Dirichlet Allocation [ldamulticore](https://radimrehurek.com/gensim/models/ldamulticore.html) to learn topics over the XSum training ("xsum-preprocessed/document-lemma") data.

### Training LDA Models from Scratch
```
python scripts/lda-gensim-training-document-lemma.py 512 1000 > lda-train.log 2> lda-train.log.2
```
We train 512 topics with 1000 iterations over the training set. "lda-train.log" prints learned topics with their 30 most frequent words.

This script will generate a directory called "lda-train-document-lemma-topic-512-iter-1000".

### Predicting Topics for Each Document in the Corpus
```
python scripts/lda-gensim-decoding-document-lemma.py 512 1000
```
It will use LDA models in "lda-train-document-lemma-topic-512-iter-1000" and create a directory "xsum-preprocessed/document-lemma-topic-512-iter-1000" predicting topics for each document.

### Predicting Topics for Each Word in the Corpus
```
python scripts/lda-gensim-decoding-wordtopicdist.py 512 1000 > ./lda-train-document-lemma-topic-512-iter-1000/word_term_topics.log
```
It will use LDA models in "lda-train-document-lemma-topic-512-iter-1000" and create a file "lda-train-document-lemma-topic-512-iter-1000/word_term_topics.log" predicting topics for each word.

### Pretrained LDA Models
In case you have problems training LDA models, you can download them [here](http://kinloch.inf.ed.ac.uk/public/XSUM-EMNLP18-lda-pretrained.tar.gz) (200MB).


Please contact shashi.narayan@ed.ac.uk if you have any problem downloading and preprocessing this dataset.




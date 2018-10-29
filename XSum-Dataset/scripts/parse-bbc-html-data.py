# Copyright 2014 Google Inc. All Rights Reserved.
# Modifications Copyright 2018 Shashi Narayan

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Script for downloading XSum dataset.
"""

import os
from collections import namedtuple
from lxml import html
import cchardet as chardet
from itertools import chain

RawStory = namedtuple('RawStory', 'url html')
StoryTitle = namedtuple('StoryTitle', 'url title')
StoryRestContent = namedtuple('StoryRestContent', 'url restcontent')

class ParseHtml:
  """Parses the HTML of a news story.

  Args:
    story: The raw Story to be parsed.
    corpus: Either 'cnn' or 'dailymail'.

  Returns:
    A Story containing URL, paragraphs and highlights.
  """

  def __init__(self, story, corpus):
    self.story = story
    self.corpus = corpus
    self.parser = html.HTMLParser(encoding=chardet.detect(self.story.html)['encoding'])
    self.tree = html.document_fromstring(self.story.html, parser=self.parser)
    
    # Elements to delete.
    self.delete_selectors = {
      'bbc': [
        '//blockquote[contains(@class, "twitter-tweet")]',
        '//blockquote[contains(@class, "instagram-media")]'
      ]
    }
    
    # Title Selector
    self.title_selectors = {
      'bbc': [
        '//h1[contains(@class, "story-headline")]',
        '//h1[contains(@class, "story-body__h1")]'
      ]
    }
    
    # Introduction Selector
    self.introduction_selectors = {
      'bbc': [
        '//p[contains(@class, "story-body__introduction")]'
      ]
    }
    
    # Rest Content exclusions: ads, links, bylines, comments, headline and story introduction
    self.bbc_exclude = (
      'not(contains(@class, "story-headline"))'
      ' and not(contains(@class, "story-body__h1"))'
      ' and not(contains(@class, "story-body__introduction"))'
      ' and not(contains(@class, "with-extracted-share-icons"))'
    )

    # Rest Content Selector
    self.restcontent_selectors = {
      'bbc': [
        '//div[contains(@class, "story-body")]//p[%s]' % self.bbc_exclude    # story-body__inner
      ]
    }
    
  def ExtractText(self, selector):
    """Extracts a list of paragraphs given a XPath selector.
    
    Args:
    selector: A XPath selector to find the paragraphs.
    
    Returns:
    A list of raw text paragraphs with leading and trailing whitespace.
    """
    xpaths = map(self.tree.xpath, selector)
    elements = list(chain.from_iterable(xpaths))
    paragraphs = [e.text_content().encode('utf-8') for e in elements]
    paragraphs = map(str.strip, paragraphs)
    paragraphs = [s for s in paragraphs if s and not str.isspace(s)]
    
    return paragraphs

  def getstory_title(self):
    for selector in self.delete_selectors[self.corpus]:
      for bad in self.tree.xpath(selector):
        bad.getparent().remove(bad)
    title = self.ExtractText(self.title_selectors[self.corpus])
    return StoryTitle(self.story.url, title)

  def getstory_introduction(self):
    for selector in self.delete_selectors[self.corpus]:
      for bad in self.tree.xpath(selector):
        bad.getparent().remove(bad)
    introduction = self.ExtractText(self.introduction_selectors[self.corpus])
    return StoryTitle(self.story.url, introduction)
    
  def getstory_restcontent(self):
    for selector in self.delete_selectors[self.corpus]:
      for bad in self.tree.xpath(selector):
        bad.getparent().remove(bad)
    restcontent = self.ExtractText(self.restcontent_selectors[self.corpus])
    return StoryRestContent(self.story.url, restcontent)

##############################################################

def GenerateMapper(t):
  """Parse BBC HTML File

  Args:
    (url, corpus, story)

  Returns:
    A list of title, introduction and rest of the document.
  """
  context_token_limit = 2000

  url, corpus, story_html = t
  
  if not story_html:
    return None
  
  # Extract title
  raw_story = RawStory(url, story_html)
  story_title = ParseHtml(raw_story, corpus).getstory_title()
  # print story_title

  # Extract Introduction
  raw_story = RawStory(url, story_html)
  story_introduction = ParseHtml(raw_story, corpus).getstory_introduction()
  # print story_introduction
  
  # Extract rest of the content
  raw_story = RawStory(url, story_html)
  story_restcontent = ParseHtml(raw_story, corpus).getstory_restcontent()
  # print story_restcontent

  return story_title, story_introduction, story_restcontent

def get_download_file_name(url):
  fileid = url.replace("http://web.archive.org/web/", "")
  fileid = fileid.replace("http://", "")
  htmlfileid = fileid.replace("/", "-") + ".html"
  return htmlfileid

if __name__ == "__main__":
  download_dir = "./xsum-raw-downloads"
  map_webarxiv_bbcid_file = "XSum-WebArxiveUrls-BBCids.txt"
  
  result_dir = "./xsum-extracts-from-downloads"
  os.system("mkdir -p "+result_dir)
  failed_id_file = open("xsum-extracts-from-downloads-failedIds.txt", "w")

  # Get all bbcids
  bbcids_dict = {}
  for line in open(map_webarxiv_bbcid_file).readlines():
    data = line.strip().split()
    bbcids_dict[data[1]] = data[0]
  print len(bbcids_dict)

  count = 0

  # Process all downloads
  for bbcid in bbcids_dict:
    
    if os.path.isfile(result_dir+"/"+bbcid+".data"):
      # Alread processed
      continue

    webarxivid = bbcids_dict[bbcid]
    downloaded_file = download_dir+"/"+get_download_file_name(webarxivid)
    
    if not os.path.isfile(downloaded_file):
      failed_id_file.write(bbcid+"\tHTML FILE IS NOT YET DOWNLOADED.\n")
      continue

    htmldata = open(downloaded_file).read()
    
    # url, corpus, htmldata
    story_title, story_introduction, story_restcontent = GenerateMapper((webarxivid, "bbc", htmldata))

    if not ((len(story_title.title) == 1) and (len(story_introduction.title) == 1) and (len(story_restcontent.restcontent) != 0)):
      failed_id_file.write(bbcid+"\t"+str(len(story_title.title))+"\t"+str(len(story_introduction.title))+
                           "\t"+str(len(story_restcontent.restcontent))+"\n")
      continue

    # Write the parsed output
    foutput = open(result_dir+"/"+bbcid+".data", "w")
    foutput.write("[XSUM]URL[XSUM]\n"+webarxivid+
                  "\n\n[XSUM]INTRODUCTION[XSUM]\n"+story_introduction.title[0]+
                  "\n\n[XSUM]RESTBODY[XSUM]\n"+"\n".join(story_restcontent.restcontent)+"\n")
    foutput.close()

    if count%1000 == 0:
      print count
    count += 1
      
  failed_id_file.close()

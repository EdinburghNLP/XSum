
# Run with python 3

import json
import os
import xml.etree.ElementTree as ET
import itertools

def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

if __name__ == "__main__":

  stanford_directory = "./StanfordOutput"

  # Load split file
  split_dict = json.loads(open("XSum-TRAINING-DEV-TEST-SPLIT-90-5-5.json").read())
  data_types = ["test", "validation", "train"]

  output_directory = "./xsum-preprocessed"
  os.system("mkdir -p "+output_directory)

  count = 1
  for dtype in data_types:
    print(dtype)
    
    # Creating Directories
    os.system("mkdir -p "+output_directory+"/document")
    os.system("mkdir -p "+output_directory+"/document-lemma")
    os.system("mkdir -p "+output_directory+"/summary")
    
    for orgfileid in split_dict[dtype]:

      if (os.path.isfile(output_directory+"/document/"+orgfileid+".document") and
          os.path.isfile(output_directory+"/document-lemma/"+orgfileid+".document-lemma") and
          os.path.isfile(output_directory+"/summary/"+orgfileid+".summary")):
        continue

      # print(orgfileid)
      
      
      stanfordfile = stanford_directory + "/" + orgfileid + ".data.xml"
    
      doc_sentences = []
      doc_sentlemmas = []
      # process xml file
      tree = ET.parse(stanfordfile)
      root = tree.getroot()
      for sentences in root.iter('sentences'):
          for sentence in sentences.iter('sentence'):
              sentence_tokenized = []
              sentence_lemmatized = []
              for token in sentence.iter('token'):
                  word = token.find('word').text
                  sentence_tokenized.append(word)
                  lemma = token.find('lemma').text
                  sentence_lemmatized.append(lemma)
              doc_sentences.append(" ".join(sentence_tokenized))
              doc_sentlemmas.append(" ".join(sentence_lemmatized))
              
      # Extract data
      modeFlag = None

      restbodydata = []
      restbodylemmadata = []
      summarydata = []
      
      allcovered = 0
      for doc_sent, doc_sentlemma in zip(doc_sentences, doc_sentlemmas):
        if "-LSB- XSUM -RSB- URL -LSB- XSUM -RSB-" in doc_sent:
          modeFlag = "URL"
          allcovered += 1
        elif "-LSB- XSUM -RSB- FIRST-SENTENCE -LSB- XSUM -RSB-" in doc_sent:
          modeFlag = "INTRODUCTION"
          allcovered += 1
        elif "-LSB- XSUM -RSB- RESTBODY -LSB- XSUM -RSB-" in doc_sent:
          modeFlag = "RestBody"
          allcovered += 1
        else:
          if modeFlag == "RestBody":
            restbodydata.append(doc_sent)
            restbodylemmadata.append(doc_sentlemma)
          if modeFlag == "INTRODUCTION":
            summarydata.append(doc_sent)

      # print(allcovered)
      if allcovered != 3:
        print("Some information missing", stanfordfile)
        print("\n".join(doc_sentences))
        exit(0)

      # rest body data
      foutput = open(output_directory+"/document/"+orgfileid+".document", "w")
      foutput.write("\n".join(restbodydata)+"\n")
      foutput.close()
      
      # rest body lemma data
      foutput = open(output_directory+"/document-lemma/"+orgfileid+".document-lemma", "w")
      foutput.write("\n".join(restbodylemmadata)+"\n")
      foutput.close()

      # summary data
      foutput = open(output_directory+"/summary/"+orgfileid+".summary", "w")
      foutput.write("\n".join(summarydata)+"\n")
      foutput.close()
      
      if count%1000 == 0:
          print(count)
      count += 1
      
      # exit(0)
    

 

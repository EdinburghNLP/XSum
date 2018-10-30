# Topic-Convolutional Sequence to Sequence Model for Extreme Summarization

This repository contains PyTorch code for our Topic-ConvS2S model from the EMNLP 2018 paper "[Don't Give Me the Details, Just the Summary! Topic-Aware Convolutional Neural Networks for Extreme Summarization](https://arxiv.org/abs/1808.08745)". Please contact me at shashi.narayan@ed.ac.uk for any question.

Our Topic-ConvS2S model builds on an earlier copy of [Facebook AI Research Sequence-to-Sequence Toolkit](https://github.com/pytorch/fairseq). 

Please cite the following paper if you use this code.

```
@InProceedings{xsum-emnlp,
 author = "Shashi Narayan and Shay B. Cohen and Mirella Lapata",
 title = "Don't Give Me the Details, Just the Summary! {T}opic-Aware Convolutional Neural Networks for Extreme Summarization",
 booktitle = "Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing ",
 year = "2018",
 address = "Brussels, Belgium",
}
	
```

## Installation

Our copy of FairSeq code requires PyTorch version >= 0.4.0. Please follow the instructions here: https://github.com/pytorch/pytorch#installation.

After PyTorch is installed, you can install ConvS2S with:
```
pip install -r requirements.txt
python setup.py build
python setup.py develop
```

## Training a New Model

### Data Preprocessing

```
python scripts/xsum-preprocessing-topic-convs2s.py
````
We partition the extracted datset into training, development and test sets. We generate following files in the "data-topic-convs2s" directory:

```
train.document, train.summary, train.document-lemma and train.doc-topics
validation.document, validation.summary, validation.document-lemma and validation.doc-topics
test.document, test.summary, test.document-lemma and test.doc-topics
```

Lines in document, summary, document-lemma and doc-topics files are paired for input documents, output summaries, input lemmatized documents and their document topic vectors. The input documents are truncated to 400 tokens and the length of the summaries limited to 90 tokens. Both document and summary files are lowercased.

```
TEXT=/address/to/the/directory/with/train/validation/test/(document,summary)/files
python preprocess.py --source-lang document --target-lang summary --trainpref $TEXT/train --validpref $TEXT/validation --testpref $TEXT/test --destdir /address/to/the/output/directory/data-bin --joined-dictionary --nwordstgt 50000 --nwordssrc 50000
```

This will create binarized data that will be used for model training. It also generates source and target dictionary files. In this case, both are same ("--joined-dictionary") and with 50000 tokens. 

### Training

```
CUDA_VISIBLE_DEVICES=1 python train.py /address/to/the/output/directory/data-bin --source-lang document --target-lang summary --max-sentences 32 --arch fconv --criterion label_smoothed_cross_entropy --max-epoch 200 --clip-norm 0.1 --lr 0.10 --dropout 0.2 --save-dir /address/to/the/output/directory/where/model/checkpoints/are/saved --no-progress-bar --log-interval 10
```

## Generation with Pre-trained Models

```
CUDA_VISIBLE_DEVICES=1 python generate.py /address/to/the/directory/with/test/(document,summary)/files/to/decode --path /address/to/the/output/directory/with/model/checkpoints/checkpoint-best.pt --batch-size 1 --beam 10 --replace-unk --source-lang document --target-lang summary > test-output-checkpoint-best.pt
```

Make sure that /address/to/the/directory/with/test/(document,summary)/files/to/decode also has source and target dictionary files.

By default, the code will use all available GPUs on your machine. We have used CUDA_VISIBLE_DEVICES environment variable to select specific GPU(s).

### Extract final hypothesis

```
python extract-hypothesis-fairseq.py -o test-output-checkpoint-best.pt -f final-test-output-checkpoint-best.pt
```

## Pre-trained ConvS2S Model (from Narayan et al., EMNLP 2018)

Pretrained ConvS2S model and dictionary files used for decoding:  

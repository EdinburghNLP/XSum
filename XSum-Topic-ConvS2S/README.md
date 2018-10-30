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

Our code requires PyTorch version >= 0.4.0. Please follow the instructions here: https://github.com/pytorch/pytorch#installation.

After PyTorch is installed, you can install Topic-ConvS2S with:
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

Lines in document, summary, document-lemma and doc-topics files are paired for input documents, output summaries, input lemmatized documents and their document topic vectors. The input documents are truncated to 400 tokens and the length of the summaries limited to 90 tokens. Document, document-lemma and summary files are lowercased.

```
TEXT=./data-topic-convs2s
python preprocess.py --source-lang document --target-lang summary --trainpref $TEXT/train --validpref $TEXT/validation --testpref $TEXT/test --destdir ./data-topic-convs2s --joined-dictionary --nwordstgt 50000 --nwordssrc 50000 --output-format raw
```

This will generates source and target dictionary files. In this case, both are same ("--joined-dictionary") and with 50000 tokens. It operates on the raw format data.

### Training

```
CUDA_VISIBLE_DEVICES=1 python train.py ./data-topic-convs2s --source-lang document --target-lang summary --doctopics doc-topics --max-sentences 32 --arch fconv --criterion label_smoothed_cross_entropy --max-epoch 200 --clip-norm 0.1 --lr 0.10 --dropout 0.2 --save-dir ./checkpoints-topic-convs2s --no-progress-bar --log-interval 10
```

## Generation with Pre-trained Models

```
CUDA_VISIBLE_DEVICES=1 python generate.py ./data-topic-convs2s --path ./checkpoints-topic-convs2s/checkpoint_best.pt --batch-size 1 --beam 10 --replace-unk --source-lang document --target-lang summary --doctopics doc-topics --encoder-embed-dim 512 > test-output-topic-convs2s-checkpoint-best.pt 
```

Make sure that ./data-topic-convs2s has test files to decode, source and target dictionary files.

By default, the code will use all available GPUs on your machine. We have used CUDA_VISIBLE_DEVICES environment variable to select specific GPU(s).

### Extract final hypothesis

```
python extract-hypothesis-fairseq.py -o test-output-checkpoint-best.pt -f final-test-output-checkpoint-best.pt
```

## Pre-trained Topic-ConvS2S Model (from Narayan et al., EMNLP 2018)

Pretrained Topic-ConvS2S model and dictionary files used for decoding:  

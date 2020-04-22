# Extreme Summarization

This repository contains data and code for our EMNLP 2018 paper "[Don't Give Me the Details, Just the Summary! Topic-Aware Convolutional Neural Networks for Extreme Summarization](https://arxiv.org/abs/1808.08745)". Please contact me at shashi.narayan@gmail.com for any question.

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

## Extreme Summarization (XSum) dataset

**You can always build the dataset using the instructions below. The original dataset is also available upon request.**

Instructions to download and preprocess the extreme summarization dataset are [here](./XSum-Dataset).

## Looking for a Running Demo of Our System?

A running demo of our abstractive system can be found [here](http://cohort.inf.ed.ac.uk/xsum.html).

## Pretrained models and Test Predictions (Narayan et al., EMNLP 2018)

* [Pretrained ConvS2S model and dictionary files](http://bollin.inf.ed.ac.uk/public/direct/XSUM-EMNLP18-convs2s.tar.gz) (1.1GB)
* [Pretrained Topic-ConvS2S model and dictionary files](http://bollin.inf.ed.ac.uk/public/direct/XSUM-EMNLP18-topic-convs2s.tar.gz) (1.2GB)
* [Pretrained Gensim LDA model](http://bollin.inf.ed.ac.uk/public/direct/XSUM-EMNLP18-lda-pretrained.tar.gz) (200MB)
* Our [model Predictions](xsum-model-predictions.tar.gz)
* [Human Evaluation Data](xsum-human-evaluation-data.tar.gz)

## Topic-Aware Convolutional Model for Extreme Summarization

This repository contains PyTorch code for our Topic-ConvS2S model. Our code builds on an earlier copy of [Facebook AI Research Sequence-to-Sequence Toolkit](https://github.com/pytorch/fairseq). 

We also release the code for the [ConvS2S model](https://arxiv.org/abs/1705.03122). It uses optimized hyperparameters for extreme summarization. Our release facilitates the replication of our experiments, such as training from scratch or predicting with released pretrained models, as reported in the paper.

### Installation
Our code requires PyTorch version 0.4.0 or 0.4.1. Please follow the instructions here: https://github.com/pytorch/pytorch#installation.

After PyTorch is installed, you can install ConvS2S and Topic-ConvS2S:
```
# Install ConvS2S
cd ./XSum-ConvS2S
pip install -r requirements.txt
python setup.py build
python setup.py develop

# Install Topic-ConvS2S
cd ../XSum-Topic-ConvS2S
pip install -r requirements.txt
python setup.py build
python setup.py develop
```

### Training a New Model

#### Data Preprocessing

We partition the extracted datset into training, development and test sets. The input document is truncated to 400 tokens and the length of the summary is limited to 90 tokens. Both *document* and *summary* files are lowercased.

##### ConvS2S
```
python scripts/xsum-preprocessing-convs2s.py
```
It generates the following files in the "data-convs2s" directory: 
``` 
train.document and train.summary
validation.document and validation.summary
test.document and test.summary
```
Lines in *document* and *summary* files are paired as (input document, corresponding output summary).  
```
TEXT=./data-convs2s
python XSum-ConvS2S/preprocess.py --source-lang document --target-lang summary --trainpref $TEXT/train --validpref $TEXT/validation --testpref $TEXT/test --destdir ./data-convs2s-bin --joined-dictionary --nwordstgt 50000 --nwordssrc 50000
```
This will create binarized data that will be used for model training. It also generates source and target dictionary files. In this case, both files are identical (due to "--joined-dictionary") and have 50000 tokens. 

##### Topic-ConvS2S
```
python scripts/xsum-preprocessing-topic-convs2s.py
````
It generates the following files in the "data-topic-convs2s" directory:
```
train.document, train.summary, train.document-lemma and train.doc-topics
validation.document, validation.summary, validation.document-lemma and validation.doc-topics
test.document, test.summary, test.document-lemma and test.doc-topics
```
Lines in document, summary, document-lemma and doc-topics files are paired as (input document, output summary, input lemmatized document, document topic vector).
```
TEXT=./data-topic-convs2s
python XSum-Topic-ConvS2S/preprocess.py --source-lang document --target-lang summary --trainpref $TEXT/train --validpref $TEXT/validation --testpref $TEXT/test --destdir ./data-topic-convs2s --joined-dictionary --nwordstgt 50000 --nwordssrc 50000 --output-format raw
```
This will generate source and target dictionary files. In this case, both files are identical (due to "--joined-dictionary") and have 50000 tokens. It operates on the raw format data.

#### Model Training

By default, the code will use all available GPUs on your machine. We have used CUDA_VISIBLE_DEVICES environment variable to select specific GPU(s).

##### ConvS2S
```
CUDA_VISIBLE_DEVICES=1 python XSum-ConvS2S/train.py ./data-convs2s-bin --source-lang document --target-lang summary --max-sentences 32 --arch fconv --criterion label_smoothed_cross_entropy --max-epoch 200 --clip-norm 0.1 --lr 0.10 --dropout 0.2 --save-dir ./checkpoints-convs2s --no-progress-bar --log-interval 10
```

##### Topic-ConvS2S
```
CUDA_VISIBLE_DEVICES=1 python XSum-Topic-ConvS2S/train.py ./data-topic-convs2s --source-lang document --target-lang summary --doctopics doc-topics --max-sentences 32 --arch fconv --criterion label_smoothed_cross_entropy --max-epoch 200 --clip-norm 0.1 --lr 0.10 --dropout 0.2 --save-dir ./checkpoints-topic-convs2s --no-progress-bar --log-interval 10
```

### Generation with Pre-trained Models

#### ConvS2S
```
CUDA_VISIBLE_DEVICES=1 python XSum-ConvS2S/generate.py ./data-convs2s --path ./checkpoints-convs2s/checkpoint-best.pt --batch-size 1 --beam 10 --replace-unk --source-lang document --target-lang summary > test-output-convs2s-checkpoint-best.pt
```
Make sure that ./data-convs2s also has the source and target dictionary files.

#### Topic-ConvS2S
```
CUDA_VISIBLE_DEVICES=1 python XSum-Topic-ConvS2S/generate.py ./data-topic-convs2s --path ./checkpoints-topic-convs2s/checkpoint_best.pt --batch-size 1 --beam 10 --replace-unk --source-lang document --target-lang summary --doctopics doc-topics --encoder-embed-dim 512 > test-output-topic-convs2s-checkpoint-best.pt 
```
Make sure that ./data-topic-convs2s has the test files to decode, the source and target dictionary files.

### Extract final hypothesis
```
python scripts/extract-hypothesis-fairseq.py -o test-output-convs2s-checkpoint-best.pt -f final-test-output-convs2s-checkpoint-best.pt
python scripts/extract-hypothesis-fairseq.py -o test-output-topic-convs2s-checkpoint-best.pt -f final-test-output-topic-convs2s-checkpoint-best.pt
```




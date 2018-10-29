# Convolutional Sequence to Sequence Model for Extreme Summarization

This repository contains PyTorch code for the ConvS2S model from the EMNLP 2018 paper "[Don't Give Me the Details, Just the Summary! Topic-Aware Convolutional Neural Networks for Extreme Summarization](https://arxiv.org/abs/1808.08745)". Please contact me at shashi.narayan@ed.ac.uk for any question.

Our ConvS2S model is based on [Convolutional Sequence to Sequence Learning](https://arxiv.org/abs/1705.03122). The original code from their paper can be found as a part of [Facebook AI Research Sequence-to-Sequence Toolkit](https://github.com/pytorch/fairseq). Our ConvS2S code is based on an earlier copy of this toolkit. It uses optimized hyperparameters for extreme summarization. Our release facilitates the replication of our experiments, such as training from scratch or predicting with released pretrained models, as reported in the paper.

Please cite the following paper if you use this code.

```
@InProceedings{xsum-emnlp,
  author =      "Shashi Narayan and Shay B. Cohen and Mirella Lapata",
  title =       "Don't Give Me the Details, Just the Summary! {T}opic-Aware Convolutional Neural Networks for Extreme Summarization",
  booktitle =   "Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing ",
  year =        "2018",
  address =     "Brussels, Belgium",
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
python scripts/xsum-preprocessing.py
```

We partition the extracted datset into training, development and test sets. We generate following files: 
``` 
train.document and train.summary
validation.document and validation.summary
test.document and test.summary
```

Lines in *document* and *summary* files are paired for input documents and corresponding output summaries. The input document is truncated to 400 tokens and the length of the summary limited to 90 tokens. Both *document* and *summary* files are lowercased. 

```
TEXT=./data
python preprocess.py --source-lang document --target-lang summary --trainpref $TEXT/train --validpref $TEXT/validation --testpref $TEXT/test --destdir ./data-bin --joined-dictionary --nwordstgt 50000 --nwordssrc 50000
```

This will create binarized data that will be used for model training. It also generates source and target dictionary files. In this case, both are same ("--joined-dictionary") and with 50000 tokens. 

### Training

```
CUDA_VISIBLE_DEVICES=1 python train.py ./data-bin --source-lang document --target-lang summary --max-sentences 32 --arch fconv --criterion label_smoothed_cross_entropy --max-epoch 200 --clip-norm 0.1 --lr 0.10 --dropout 0.2 --save-dir ./checkpoints --no-progress-bar --log-interval 10
```

## Generation with Pre-trained Models

```
CUDA_VISIBLE_DEVICES=1 python generate.py ./data --path ./checkpoints/checkpoint-best.pt --batch-size 1 --beam 10 --replace-unk --source-lang document --target-lang summary > test-output-checkpoint-best.pt
```

Make sure that ./data also has source and target dictionary files.

By default, the code will use all available GPUs on your machine. We have used CUDA_VISIBLE_DEVICES environment variable to select specific GPU(s).

### Extract final hypothesis

```
python extract-hypothesis-fairseq.py -o test-output-checkpoint-best.pt -f final-test-output-checkpoint-best.pt
```

## Pre-trained ConvS2S Model (from Narayan et al., EMNLP 2018)

Pretrained ConvS2S model and dictionary files used for decoding:  

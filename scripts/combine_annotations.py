import json 
import random
import os


def get_x_bbc_ids(x):
    '''
    Extracts bbc_ids and chooses x instances
    '''
    with open("./../xsum_hallucination_annotations/factuality_annotations_xsum_summaries.csv") as f:
        annotations = f.readlines()[1:]
    all_bbc_ids = []
    for annotation in annotations:
        bbc_id = annotation.split(",")[0]
        if bbc_id not in all_bbc_ids:
            all_bbc_ids.append(bbc_id)
    random.seed(42)
    random.shuffle(all_bbc_ids)
    selected = all_bbc_ids[:x] 
    leftover = all_bbc_ids[x:]
    return selected, leftover

def get_url_from_bbc_id(bbc_ids, suffix=""):
    '''
    bbc_ids: output from get_x_bbc_ids(x)
    suffix: to distinguish the selected ids from the leftovers
    Returns the url to use for querying the history machine (although in the next step i just read the file)
    '''
    with open("./XSum-Dataset/XSum-WebArxiveUrls.txt") as f:
        urls = f.readlines()
    filtered_urls = []
    url_bbc_ids = [url.strip()[-8:] for url in urls]
    for i, bbc_id in enumerate(url_bbc_ids):
        if bbc_id in bbc_ids:
            filtered_urls.append(urls[i])
    with open(f"./XSum-Dataset/XSum-WebArxiveUrls{suffix}.txt", "w") as f:
        f.writelines(filtered_urls)
        print(f'Saved {len(filtered_urls)} to ./XSum-Dataset/XSum-WebArxiveUrls{suffix}.txt')
    if len(bbc_ids) > len(filtered_urls):
        print("Warning: there are some annotations that don't have corresponding urls in original dataset")
    elif len(filtered_urls) > len(bbc_ids):
        print("Warning: there are some urls that don't have corresponding annotations")
    return filtered_urls

def get_data_from_urls(suffix):
    '''
    Assumes we already ran the provided script for downloading data
    Returns: dict containing text, summary, and factuality annotations
    '''
    with open(f"./XSum-Dataset/XSum-WebArxiveUrls_{suffix}.txt") as f:
        urls = f.readlines()
        urls = [url.strip() for url in urls]
        bbc_ids = [url.strip()[-8:] for url in urls]

    # collect annotations
    data = {}
    with open("./../xsum_hallucination_annotations/factuality_annotations_xsum_summaries.csv") as f:
        annotations = f.readlines()[1:]
        for annotation in annotations:
            bbc_id = annotation.split(",")[0]
            if bbc_id in bbc_ids:
                if bbc_id not in data:
                    data[bbc_id] = {}
                    data[bbc_id]["annotations"] = []
                annotation = annotation.split(",")[-2].strip()
                data[bbc_id]["annotations"].append(1 if annotation == "yes" else 0)
    #print("annotations", json.dumps(data, indent=4))

    # get all files from dir
    if suffix == 'Filtered':
        output_dir = 'XSum_test.jsonl'
    else:
        output_dir = 'XSum_train.jsonl'
    with open(output_dir, "w") as write_f:
        dirname = f"./XSum-Dataset/xsum-extracts-from-downloads_{suffix}/"
        for i, bbc_id in enumerate(bbc_ids):
            with open(os.path.join(dirname, f'{bbc_id}.data')) as f:
                content = f.read()
                summary_ind = content.index("[XSUM]INTRODUCTION[XSUM]\n")# + len("[XSUM]INTRODUCTION[XSUM]\n") + 1
                content = content.replace("[XSUM]INTRODUCTION[XSUM]\n","")
                text_ind = content.index("[XSUM]RESTBODY[XSUM]\n")# + len("[XSUM]RESTBODY[XSUM]\n") + 1
                content = content.replace("[XSUM]RESTBODY[XSUM]\n","")
                summary = content[summary_ind:text_ind-1]
                text = content[text_ind:]
                data[bbc_id]["summary"] = summary
                data[bbc_id]["text"] = text
                data[bbc_id]["url"] = urls[i]
            write_f.write(json.dumps(data[bbc_id])+'\n')

def main():
    #selected, leftover = get_x_bbc_ids(20)
    #selected_urls = get_url_from_bbc_id(selected, "_Filtered")
    #leftover_urls = get_url_from_bbc_id(leftover, "_Leftover")
    # (from https://github.com/EdinburghNLP/XSum/tree/master/XSum-Dataset)
    # Run XSum-Dataset/scripts/download-bbc-articles.py --timestamp_exactness 14 
    # Make we have xsum-extracts-from-downloads_Filtered/Leftover
    get_data_from_urls('Filtered')
    get_data_from_urls('Leftover')
    #print(filtered_urls)

if __name__ == "__main__":
    main()

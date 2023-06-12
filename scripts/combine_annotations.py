import json 
import random
random.seed(42)


def get_x_bbc_ids(x):
    with open("./../xsum_hallucination_annotations/factuality_annotations_xsum_summaries.csv") as f:
        annotations = f.readlines()[1:]
    all_bbc_ids = set()
    for annotation in annotations:
        all_bbc_ids.add(annotation.split(",")[0])
    return random.sample(list(all_bbc_ids), x)

def get_url_from_bbc_id(bbc_ids):
    with open("./XSum-Dataset/XSum-WebArxiveUrls.txt") as f:
        urls = f.readlines()
    filtered_urls = []
    url_bbc_ids = [url[-9:].strip() for url in urls]
    for i, bbc_id in enumerate(url_bbc_ids):
        if bbc_id in bbc_ids:
            filtered_urls.append(urls[i])
    with open("./XSum-Dataset/XSum-WebArxiveUrls_Filtered.txt", "w") as f:
        f.writelines(filtered_urls)
    assert len(filtered_urls) == len(bbc_ids), "Number of selected urls and bbc_ids do not match"
    return filtered_urls

bbc_ids = get_x_bbc_ids(20)
filtered_urls = get_url_from_bbc_id(bbc_ids)
print(filtered_urls)

def main():
    with open("./XSum-Dataset/chosen_urls.txt", "r") as f:
        chosen_urls = f.readlines()
        bbcids = [url.split("-")[-1].strip() for url in chosen_urls]
        for i in range(len(bbcids)):
            if len(bbcids[i]) > 8:
                bbcids[i] = bbcids[i].split("/")[-1]

    selected = {}
    for category in ["factuality"]:#, "hallucination"]:
        with open(f"./../xsum_hallucination_annotations/{category}_annotations_xsum_summaries.csv", "r") as f:
            annotations = f.readlines()[1:]
            for annotation in annotations:
                bbcid = annotation.split(",")[0]
                print(bbcid, type(bbcid), type(bbcids[0]))
                if bbcid in bbcids:
                    if bbcid not in selected:
                        selected[bbcid] = []
                    selected[bbcid].append(annotation.split(",")[-2].strip())
    print(json.dumps(selected, indent=4))
    '''
    with open(f"./../xsum_hallucination_annotations/{category}_annotations_xsum_summaries.csv", "w") as f:
        f.write("bbc_id,annotation\n")
        for bbcid in bbcids:
            for annotation in annotations:
                if bbcid in annotation:
                    f.write(annotation)
                    break 
    '''

if __name__ == "__main__":
    #main()
    pass

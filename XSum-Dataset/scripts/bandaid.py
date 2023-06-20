import glob

map_webarxiv_bbcid_file = "XSum-WebArxiveUrls-BBCids.txt"
# Get all bbcids
bbcids_dict = {}
for line in open(map_webarxiv_bbcid_file).readlines():
    data = line.strip().split()
    bbcids_dict[data[1]] = data[0]

for suffix in ["Filtered", "Leftover"]:
    source_dir = f"./xsum-extracts-from-downloads_{suffix}/"
    with open(f"XSum-WebArxiveUrls_{suffix}.txt", "w") as write_f:
        #with open(f"../xsum-extracts-from-downloads_{suffix}") as read_f:
        bbcids = glob.glob(f'{source_dir}*') 
        bbcids = [filename.replace(".data", "").replace(source_dir, "") for filename in bbcids]
        urls = [bbcids_dict[id] for id in bbcids]
        write_f.write('\n'.join(urls))
            
'''

os.system("mkdir -p "+result_dir)
failed_id_file = open("xsum-extracts-from-downloads-failedIds.txt", "w")


XSum-WebArxiveUrls_Filtered.txt           XSum-WebArxiveUrls.txt
(venv) risako@cs-u-wolf:~/XSum/XSum-Dataset$ vi XSum-WebArxiveUrls-BBCids.txt
(venv) risako@cs-u-wolf:~/XSum/XSum-Dataset$ vi scripts/parse-bbc-html-data.py
(venv) risako@cs-u-wolf:~/XSum/XSum-Dataset$ vi scripts/bandaid.py
(venv) risako@cs-u-wolf:~/XSum/XSum-Dataset$ ls xsum-extracts-from-downloads_Filtered
'''

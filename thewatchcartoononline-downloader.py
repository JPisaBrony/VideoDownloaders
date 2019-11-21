from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
import js2py
import base64
import os.path

def atob(s):
    return base64.b64decode('{}'.format(s))

ctx = js2py.EvalJs({"atob": atob})

EPISODE_URL_NAME = "star-vs-the-forces-of-evil"
BASE_WEBPAGE_URL = "https://www.thewatchcartoononline.tv"
BASE_DOWNLOAD_DIR = "episodes/"

base_url = requests.get(BASE_WEBPAGE_URL + "/anime/" + EPISODE_URL_NAME, 'html.parser')
soup = BeautifulSoup(base_url.text, "html.parser")
retries = Retry(total=10, backoff_factor=3)
for eps in reversed(soup.findAll("div", {"class": "cat-eps"})):
    ep = eps.find("a")
    ep_url = ep['href']
    print "processing " + ep_url
    
    if os.path.isfile(BASE_DOWNLOAD_DIR + ep.text.replace("/", ".") + ".mp4"):
        print ep.text + " exists. skipping"
        continue
    
    ep_page = requests.get(ep_url, 'html.parser')
    ep_soup = BeautifulSoup(ep_page.text, "html.parser")
    script = ep_soup.findAll("script")[5]
    parsed_script = script.text.replace("document.write", "")
    evaled_script = ctx.eval(parsed_script)
    evaled_soup = BeautifulSoup(evaled_script, "html.parser")
    video_src = evaled_soup.find("iframe")["src"]
    video_url = BASE_WEBPAGE_URL + video_src
    video_req = requests.get(video_url)
    video_soup = BeautifulSoup(video_req.text, "html.parser")
    video_script = video_soup.findAll("script")[8]
    video_split_url = video_script.text.split('$.getJSON("')[1].split('", function(response)')[0]
    video_get_link = BASE_WEBPAGE_URL + video_split_url
    video_json = requests.get(video_get_link, headers={"x-requested-with": "XMLHttpRequest"}).json()
    video_real_link = video_json["server"] + "/getvid?evid=" + video_json["enc"]
    
    with requests.Session() as s:
        s.mount('https://', HTTPAdapter(max_retries=retries))
        r = s.get(video_real_link, stream=True, timeout=30)
        r.raise_for_status()
        print ep.text
        with open(BASE_DOWNLOAD_DIR + ep.text.replace("/", ".") + ".mp4", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

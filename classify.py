# unrar, unzip
# books - pdf, fb2, epub, doc
# Films - mp4, avi

from os import listdir
from os.path import isfile, join, splitext
import shutil
import re
from bs4 import BeautifulSoup
import zipfile, tarfile, rarfile

downloads = '/home/sergey/Downloads'
books = '/home/sergey/Downloads/books'
films = '/home/sergey/Downloads/Films'

def move_files():

    onlyfiles = [f for f in listdir(downloads) if isfile(join(downloads, f))]

    for f in onlyfiles:
        _, file_extension = splitext(f)
        file_ext = file_extension.lower()
        if file_ext in ['.pdf', '.epub', '.doc', '.fb2']:
            shutil.move(join(downloads, f), join(books,f))
        elif file_ext in ['.mp4', '.avi', '.mkv']:
            shutil.move(join(downloads, f), join(films,f))
        elif file_ext in ['.zip', '.rar', '.gz', '.tar']:
            folder = which_folder(join(downloads, f))
            if folder:
                shutil.move(join(downloads, f), join(downloads, join(folder,f)))

            

def archive_format(fn):
    with open(fn, "rb") as f:
        bytes = f.read(262)
        if bytes[257] == 0x75 and bytes[258] == 0x73 and bytes[259] == 0x74 and bytes[260]==0x61 and bytes[261]==0x72:
            return "tar"
        elif bytes[0] == 0x1F and bytes[1] == 0x8B and bytes[2] == 0x08:
            return "gz"
        elif bytes[0] == 0x50 and bytes[1] == 0x4B:
            return "zip"
        elif bytes[0] == 0x52 and bytes[1] == 0x61 and bytes[2] == 0x72 and bytes[3]==0x21:
            return "rar"
    return None


def is_series(fn):
    words = re.findall(r'[a-zA-Z]+', fn)
    searchTerm = ' '.join(words)
    r = requests.get('https://www.google.com/search?q=' + searchTerm + " :site:amazon.com")
    soup = BeautifulSoup(r.text, 'lxml')
    main_div = soup.find("div", {"id": "main"})
    anchors = main_div.find_all("a")
    headers = {
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }
    anchors = anchors[:20]
    for a in anchors:
        href = a["href"]
        if href:
            urls = re.findall(r"(https*:\/\/.*amazon.com.+?)\&", href)
            if urls:
                url=urls[0]
                r = requests.get(url, headers=headers)
                soup = BeautifulSoup(r.text, 'lxml')
                for script in soup(["script", "style"]): # remove all javascript and stylesheet code
                    script.extract()
                # get text
                text = soup.get_text()
                if re.search(r'Season', text):
                    return True
    return False


def list_files(fn, format):
    if format:
        if format == 'zip':
            with zipfile.ZipFile(fn) as myzip:
                return myzip.namelist()
        elif format == 'rar':
            with rarfile.RarFile(fn) as myrar:
                return myrar.namelist()
        elif format in ['tar', 'gz']:
            with tarfile.TarFile(fn) as mytar:
                return [t.name for t in mytar]
    return None



def which_folder(fn):
    print(fn)
    format = archive_format(fn)
    files = list_files(fn, format)
    exts = set()
    for f in files:
        _, ext = splitext(f)
        exts.add(ext)
        if ext in ['.mp4', '.avi', '.mkv']:
            if is_series(f):
                return "Series"
            else:
                return "Films"
    if set([".pdf", ".fb2", ".epub", ".doc"]).intersection(exts):
        return "books"
    return None



if __name__ == '__main__':
    print("Moving files to proper locations")
    move_files()
    print("finished moving files")


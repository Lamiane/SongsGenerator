import requests
import re
from nltk import ngrams
from nltk.tokenize.moses import MosesTokenizer
import datetime 
import json
from utils import ADRES, EMPTY_STRING_LENGTH, ENTER 
    
    
def extract_song_url_from_line(line):
    """ extraxt a song url from an html line
    
    Parameters
    ----------
    line : str
        a line of html with a url to a song
        
    Returns
    -------
     : str
        url to a song
    """
    return re.findall("piosenka.+html", line)[0]


def find_all_subpages(html_source):
    """ On tekstowo.pl a list of all songs of a given artist might be spread across multiple pages.
    This function finds urls of all these pages.
    
    Parameters
    ----------
    html_source : str
        html source of a tekstowo.pl webpage that includes songs of a given artist
    
    Returns
    -------
     : list
        lines that include urls to another pages with songs of this artist
    """
    return [re.findall("/piosenki_artysty.+html",line)[0] 
            for line in html_source 
            if 'alfabetycznie' in line and 'strona' in line]


def get_songs_urls(artists):
    """ Find urls to all songs of given artists.
    
    Parameters
    ----------
    artists : tuple or list
        band names
        
    Returns
    -------
    artist_songs : dict
        keys: band name, values: a list of urls that contain songs
    """
    artist_songs = {}
    for artist in artists:
        artist_url = "https://www.tekstowo.pl/piosenki_artysty,"+artist+".html"
        r = requests.get(artist_url).text.split('\n')
        
        subpages = set(find_all_subpages(r))
        
        songs_urls=set()
        for subpage in subpages:
            r = requests.get(ADRES+subpage)
            not_yet = True
            for line in r.text.split('\n'):
                if not_yet and 'przeboje' not in line:
                    continue
                not_yet=False
                if 'html' in line and artist in line.lower() and 'piosenka' in line:
                        songs_urls.add(ADRES + '/' + extract_song_url_from_line(line.strip()))
        
        artist_songs[artist]=songs_urls
    return artist_songs               


def extract_lyrics(urls):
    """ Extract lyrics from html code given urls.
    
    Parameters
    ----------
    urls : list or tuple
        urls of webpages with song lyrics
        
    Returns
    -------
    songs : lsit
        extracted songs 
    """
    polisher = lambda x: x.encode('iso-8859-1').decode('utf-8')

    songs = []
    for url in urls:
#         print 'parsing', url
        html_source = requests.get(url).text
        not_yet = True
        no_more = False
        lyrics = []
        for line in html_source.split('\n'):
            if 'song-text' in line:
                not_yet = False
            if not not_yet and 'javascript' in line:
                no_more = True
            if not not_yet and not no_more and len(line)>EMPTY_STRING_LENGTH:
                try :
                    lyrics.append(polisher(line.strip()).replace('<br />', ENTER).lower())
                except UnicodeDecodeError:
                    print line, line.__repr__()
        songs.append('\n'.join(lyrics[2:-2]))
    return songs


def download_lyrics(artists):
    """ builds a song book - a dataset with song lyrics of given artists
    
    Parameters
    ----------
    artists : tuple or int
        band names
    
    Returns
    -------
    song_book : dict
        keys: band names, values: list of song lyrics 
    """
    song_book = {}
    for artist in artists:
        print datetime.datetime.now(), artist
        song_book[artist] = extract_lyrics(get_songs_urls([artist,])[artist])
    return song_book


def get_data_from_file(filepaths, identifiers):
    """ Builds dataset based on data from text files
    
    Parameters
    ----------
    filepaths : tuple or list
        paths to files that should be loaded
        
    identifiers : tuple or list
        identifiers of given files
    
    Returns
    -------
    dataset : dict
        keys: identifiers, values: list of poems 
    """
    dataset = {}
    for filepath, identifier in zip(filepaths, identifiers):
        with open(filepath, 'r') as f:
            content = f.read()
#         dataset[identifier] = polisher(content.strip()).replace('\n', ENTER).lower()
        encoder = lambda x: x.decode('utf-8')
        dataset[identifier] = [encoder(content.strip().replace('\n', ENTER).lower()),]
        
    return dataset

if __name__=='__main__':
    # download
    dataset_orig = download_lyrics(['enej', 'lzy', 'happysad', 'kayah', 'czerwone_gitary',
                                'pidzama_porno', 'krzysztof_krawczyk', 'stare_dobre_malze_stwo',
                                'zabili_mi_zolwia', 'elektryczne_gitary', 'monika_brodka',
                                'hey', 'gaba_kulka', 'coma', 'ryszard_rynkowski', 'natalia_kukulska'])
    
    # load from text file
    mick = get_data_from_file(['mickiewicz.txt'], ['mickiewicz'])
    
    # save as json
    with open('dataset.json', 'w') as f:
        json.dump(dataset_orig, f)
import json
from nltk import ngrams
from nltk.tokenize.moses import MosesTokenizer

ADRES = "https://www.tekstowo.pl"
EMPTY_STRING_LENGTH = 6
ENTER = " enterenter "


def preprocess(data_dict, ngram=3):
     """ Build an n-gram representation of given texts.
     returns a list with songs, each song is a list of ngrams, ngrams are represented as tuples
    
    Parameters
    ----------
    data_dict : dict
        dataset generated with `datasets.download_lyrics` or `datasets.get_data_from_file`
        
    ngram : int
        n of n-gram
    
    Returns
    -------
    dataset : str
        generated text 
    """
    dataset = []
    tokeniser = MosesTokenizer()
    for band in data_dict:
        for i in range(len(data_dict[band])):
            song = tokeniser.tokenize(data_dict[band][i], return_str=False)
            n_song = list(ngrams(song, ngram))
            dataset.append(n_song)
    return dataset


def print_a_song(song):
     """ print the generated text
    
    Parameters
    ----------
    song : str
        generated song 
    """
    print(song.replace(ENTER.strip(), '\n').replace('&quot;', '"').replace('&apos;', "'"))


if __name__=='__main__':
    with open('dataset.json', 'r') as f:
        dataset = json.load(f)
        
    preprocessed = preprocess(dataset, ngram=3)

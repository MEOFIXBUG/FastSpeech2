""" from https://github.com/keithito/tacotron """
import re
from text import cleaners
from text.symbols import symbols, _eos, phonemes_symbols, PAD, EOS, _PHONEME_SEP
#import hparams as hp
from text.dict_ import symbols_
import nltk
from g2p_en import G2p
import numpy as np

# Mappings from symbol to numeric ID and vice versa:
_symbol_to_id = {s: i for i, s in enumerate(symbols)}
_id_to_symbol = {i: s for i, s in enumerate(symbols)}

# Regular expression matching text enclosed in curly braces:
_curly_re = re.compile(r'(.*?)\{(.+?)\}(.*)')

symbols_inv = {v: k for k, v in symbols_.items()}

def pad_with_eos_bos(_sequence):
    return _sequence + [_symbol_to_id[_eos]]

valid_symbols = [
    'AA', 'AA0', 'AA1', 'AA2', 'AE', 'AE0', 'AE1', 'AE2', 'AH', 'AH0', 'AH1', 'AH2',
    'AO', 'AO0', 'AO1', 'AO2', 'AW', 'AW0', 'AW1', 'AW2', 'AY', 'AY0', 'AY1', 'AY2',
    'B', 'CH', 'D', 'DH', 'EH', 'EH0', 'EH1', 'EH2', 'ER', 'ER0', 'ER1', 'ER2', 'EY',
    'EY0', 'EY1', 'EY2', 'F', 'G', 'HH', 'IH', 'IH0', 'IH1', 'IH2', 'IY', 'IY0', 'IY1',
    'IY2', 'JH', 'K', 'L', 'M', 'N', 'NG', 'OW', 'OW0', 'OW1', 'OW2', 'OY', 'OY0',
    'OY1', 'OY2', 'P', 'R', 'S', 'SH', 'T', 'TH', 'UH', 'UH0', 'UH1', 'UH2', 'UW',
    'UW0', 'UW1', 'UW2', 'V', 'W', 'Y', 'Z', 'ZH', 'pau', 'sil', 'spn', '~'
]

'''def text_to_sequence(text, cleaner_names):
    Converts a string of text to a sequence of IDs corresponding to the symbols in the text.

      The text can optionally have ARPAbet sequences enclosed in curly braces embedded
      in it. For example, "Turn left on {HH AW1 S S T AH0 N} Street."

      Args:
        text: string to convert to a sequence
        cleaner_names: names of the cleaner functions to run the text through

      Returns:
        List of integers corresponding to the symbols in the text
    
    sequence = []
    if hp.eos:
        text = text + '~'
    try:
        sequence += _symbols_to_sequence(_clean_text(text, cleaner_names))
    except KeyError:
        print("text : ",text)
        exit(0)

    return sequence
'''

def sequence_to_text(sequence):
    '''Converts a sequence of IDs back to a string'''
    result = ''
    for symbol_id in sequence:
        if symbol_id in symbols_inv:
            s = symbols_inv[symbol_id]
            # Enclose ARPAbet back in curly braces:
            if len(s) > 1 and s[0] == '@':
                s = '{%s}' % s[1:]
            result += s
    return result.replace('}{', ' ')


def _clean_text(text, cleaner_names):
    for name in cleaner_names:
        cleaner = getattr(cleaners, name)
        if not cleaner:
            raise Exception('Unknown cleaner: %s' % name)
        text = cleaner(text)
    return text


def _symbols_to_sequence(symbols):
    return [symbols_[s.upper()] for s in symbols]


def _arpabet_to_sequence(text):
    return _symbols_to_sequence(['@' + s for s in text.split()])


def _should_keep_symbol(s):
    return s in _symbol_to_id and s is not '_' and s is not '~'


# For phonemes
_phoneme_to_id = {s: i for i, s in enumerate(valid_symbols)}                         #phonemes_symbols
_id_to_phoneme = {i: s for i, s in enumerate(valid_symbols)}                         #phonemes_symbols


def _should_keep_token(token, token_dict):
    return token in token_dict \
           and token != PAD and token != EOS \
           and token != _phoneme_to_id[PAD] \
           and token != _phoneme_to_id[EOS]

def phonemes_to_sequence(phonemes):
    string = phonemes.split() if isinstance(phonemes, str) else phonemes
    string.append("pau")
    sequence = [_phoneme_to_id[s] for s in string]
                #if _should_keep_token(s, _phoneme_to_id)]
    return np.array(sequence, dtype = 'float32')           ####change to github


def sequence_to_phonemes(sequence, use_eos=False):
    string = [_id_to_phoneme[idx] for idx in sequence]
              #if _should_keep_token(idx, _id_to_phoneme)]
    string = _PHONEME_SEP.join(string)
    if use_eos:
        string = string.replace(EOS, '')
    return string


'''def text_to_phonemes(text, custom_words={}):
    """
    Convert text into ARPAbet.
    For known words use CMUDict; for the rest try 'espeak' (to IPA) followed by 'listener'.
    :param text: str, input text.
    :param custom_words:
        dict {str: list of str}, optional
        Pronounciations (a list of ARPAbet phonemes) you'd like to override.
        Example: {'word': ['W', 'EU1', 'R', 'D']}
    :return: list of str, phonemes
    """
    g2p = G2p()

    def convert_phoneme_CMU(phoneme):
        REMAPPING = {
            'AA0': 'AA1',
            'AA2': 'AA1',
            'AE2': 'AE1',
            'AH2': 'AH1',
            'AO0': 'AO1',
            'AO2': 'AO1',
            'AW2': 'AW1',
            'AY2': 'AY1',
            'EH2': 'EH1',
            'ER0': 'EH1',
            'ER1': 'EH1',
            'ER2': 'EH1',
            'EY2': 'EY1',
            'IH2': 'IH1',
            'IY2': 'IY1',
            'OW2': 'OW1',
            'OY2': 'OY1',
            'UH2': 'UH1',
            'UW2': 'UW1',
        }
        return REMAPPING.get(phoneme, phoneme)

    def convert_phoneme_listener(phoneme):
        VOWELS = ['A', 'E', 'I', 'O', 'U']
        if phoneme[0] in VOWELS:
            phoneme += '1'
        return convert_phoneme_CMU(phoneme)

    try:
        known_words = nltk.corpus.cmudict.dict()
    except LookupError:
        nltk.download('cmudict')
        known_words = nltk.corpus.cmudict.dict()

    for word, phonemes in custom_words.items():
        known_words[word.lower()] = [phonemes]

    words = nltk.tokenize.WordPunctTokenizer().tokenize(text.lower())

    phonemes = []
    PUNCTUATION = '!?.,-:;"\'()'
    for word in words:
        if all(c in PUNCTUATION for c in word):
            pronounciation = ['pau']
        elif word in known_words:
            pronounciation = known_words[word][0]
            pronounciation = list(map(convert_phoneme_CMU, pronounciation))
        else:
            pronounciation = g2p(word)
            pronounciation = list(map(convert_phoneme_CMU, pronounciation))

        phonemes += pronounciation

    return phonemes
'''



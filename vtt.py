import difflib
import re

_THR = 0.9
_HOMOPHONES_FILE = 'cb5c9fae362c896ecd02/english-homophones.txt'
_HOMOPHONES = {}

def load_homophones():
    with open(_HOMOPHONES_FILE, encoding='utf-8') as fin:
        for line in fin:
            group = [word.strip() for word in line.split('/')]
            _HOMOPHONES.update({word:group[0] for word in group})

class Word:
    '''The only real purpose of this class is to force homophones to evaluate as
    equal, for sequence alignment purposes'''
    def __init__(self, word):
        try:
            self.word = _HOMOPHONES[word]
        except KeyError:
            self.word = word
        self.hsh = hash(self.word)

    def __hash__(self):
        return self.hsh

    def __eq__(self, other):
        if not isinstance(other, Word):
            return False
        return self.word == other.word

class VTT:
    '''Class which represents a VTT subtitle file. Each caption is stored as
    triplet of (timestamp text, subtitle line, start_word_count, end_word_count).'''
    def __init__(self, fname: str):
        self.data = []
        self.fname = fname
        self.load(fname)

    def load(self, fname: str):
        '''Load the subtitles'''
        with open(fname, 'r', encoding='utf-8') as fin:
            idx = 0
            timestamp = None
            for line in fin:
                line = line.strip()
                if re.fullmatch(r'^WEBVTT$', line):
                    continue
                if re.fullmatch(r'^\S+\s\-\->\s\S+$', line):
                    timestamp = line
                    continue
                if timestamp:
                    assert timestamp is not None
                    words = len(line.split())
                    self.data.append((timestamp, line, idx, idx + words))
                    idx += words
                    timestamp = None

    def serialize(self):
        '''Generate a new VTT subtitle file'''
        name, _, ext = self.fname.rpartition('.')
        new_fname = f'{name}.new.vtt'
        assert ext == 'vtt'

        with open(new_fname, 'w', encoding='utf-8') as fout:
            fout.write('WEBVTT\n\n')
            for timestamp, line, _, _ in self.data:
                fout.write(timestamp + '\n')
                fout.write(line + '\n\n')

    def to_txt(self):
        '''Produce a plain text representation'''
        return ' '.join([item[1] for item in self.data])

    def repair(self, script):
        captions = self.to_txt().split()
        script = script.split()

        seq1 = [Word(word) for word in captions]
        seq2 = [Word(word) for word in script]
        sm = difflib.SequenceMatcher(None, seq1, seq2)
        opcodes = sm.get_opcodes()
        opcode_idx = 0

        new_data = []
        for timestamp, line, start, end in self.data:

            fixed_line = []
            while opcode_idx < len(opcodes):
                opcode, i1, i2, j1, j2 = opcodes[opcode_idx]
                if i1 >= end:
                    break

                crosses_start = i1 < start
                crosses_end = i2 > end

                if opcode in ['equal', 'replace']:
                    if crosses_start:
                        j1 += start - i1
                        i1 = start
                    if crosses_end:
                        j2 = min(j2, j1 + (end - i1))
                        i2 = end

                if opcode != 'delete':
                    fixed_line.extend(script[j1:j2])
                else:
                    fixed_line.append('*')
                    fixed_line.extend(captions[i1:i2])
                    fixed_line.append('*')

                if crosses_end:
                    # Continue with the same match but the next caption line
                    break

                # Next match, same line
                opcode_idx += 1

            fixed_line = ' '.join(fixed_line)
            # if the match is imperfect, add both the original and the new line
            if difflib.SequenceMatcher(None, line, fixed_line).ratio() < _THR:
                line = f'---{line}\n+++{fixed_line}'
            else:
                line = fixed_line
            new_data.append((timestamp, line, start, end))
        self.data = new_data

load_homophones()

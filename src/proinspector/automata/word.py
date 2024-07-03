from proinspector.automata.letter import Letter, EmptyLetter, ReadState
from proinspector.tools.test_logger import log_test
# a sequence of letters 
class Word:
    def __init__(self, letters = None):
        self.letters = letters

    @property
    def letters(self):
        return self.__letters
    
    @letters.setter
    def letters(self, letters):
        if letters is None:
            letters = []

        if len(letters) > 1 and isinstance(letters[0], EmptyLetter):
            letters = letters[1:]
        
        self.__letters = []        
        for letter in letters:            
            self.__letters.append(letter)

    def contains_readstate(self):
        for letter in self.letters:
            if isinstance(letter,ReadState):
                return True
        return False

    def __hash__(self):
        return hash(repr(self))
    
    def __eq__(self, other):
        if not isinstance(other, Word):
            return False
        return self.letters == other.letters

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return "[{}]".format(", ".join([str(letter) for letter in self.letters]))

    def __repr__(self):
        return "[{}]".format(", ".join([str(letter) for letter in self.letters]))

    def __len__(self):
        return len(self.letters)

    def last_letter(self):
        return self.letters[-1]

    def __add__(self, other):
        """Two words can be appended to produce a new one

        >>> from pylstar.Word import Word
        >>> from pylstar.Letter import Letter
        >>> l1 = Letter("a")
        >>> l2 = Letter("b")
        >>> l3 = Letter("c")
        >>> l4 = Letter("d")
        >>> w1 = Word([l1, l2])
        >>> w2 = Word([l3, l4])
        >>> w3 = w1 + w2
        >>> print(w3)
        [Letter('a'), Letter('b'), Letter('c'), Letter('d')]


        Only two words can be added

        >>> from pylstar.Word import Word
        >>> from pylstar.Letter import Letter
        >>> l1 = Letter("a")
        >>> w1 = Word([l1])
        >>> w2 = "data"
        >>> w3 = w1 + w2
        Traceback (most recent call last):
        ...
        Exception: Only two words can be added
        
        """

        if not isinstance(other, Word):
            raise Exception("Only two words can be added")

        if len(self.letters) >= 1 and isinstance(self.letters[0], EmptyLetter):
            return Word(self.letters[1:] + other.letters)
            
        return Word(self.letters + other.letters)

def test():
    le = EmptyLetter()
    la = Letter('a')
    lb = Letter('b')
    w1 = Word([la,lb])
    log_test(w1)
    w1.letters = [le,la,lb]
    log_test(w1)
    w1.letters = [la,lb,le]
    log_test(w1)

if __name__ == '__main__':
    test()
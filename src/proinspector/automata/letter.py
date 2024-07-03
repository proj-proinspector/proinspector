# wrapper for a set of symbols (e.g. str, int, custom class)
import inspect
from proinspector.term.term import Nonce

class Letter:
    def __init__(self, symbol = None, symbols = None):
        self.symbols = set()
        if symbol is not None:
            self.symbols.add(symbol)
        if symbols is not None:
            self.symbols.update(symbols)

    def __hash__(self):
        return hash(frozenset(self.symbols))

    def __eq__(self, other):
        if not isinstance(other, Letter):
            return False
        
        return self.symbols == other.symbols

    def __ne__(self, other):
        if not isinstance(other, Letter):
            return True
        return self.symbols != other.symbols
    
    @property
    def to_string(self):                
        str_name = "None"
        if self.symbols is not None:
            str_name = ','.join([repr(s) for s in self.symbols])
        return str_name

    def __str__(self):
        return f"Letter({self.to_string})"
        
    def __repr__(self):
        return self.__str__()

    @staticmethod
    def get_class_name():
        return inspect.stack()[1][3]


class EmptyLetter(Letter):

    def __init__(self):
        super(EmptyLetter, self).__init__()

    def __str__(self):
        return "EmptyLetter"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, EmptyLetter):
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, EmptyLetter):
            return True
        return False

class ReadState(Letter):

    def __init__(self):
        super(ReadState, self).__init__()

    def __str__(self):
        return "ReadState"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, ReadState):
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, ReadState):
            return True
        return False

class AttackerM(Letter):#attacker message

    def __init__(self):
        super(AttackerM, self).__init__()

    def __str__(self):
        return "AttackerM"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, AttackerM):
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, AttackerM):
            return True
        return False

    def __hash__(self):
        return hash('AttackerM')

class Alert(Letter):#attacker message

    def __init__(self):
        super(Alert, self).__init__()
    def __str__(self):
        return "Alert"
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Alert):
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, Alert):
            return True
        return False

    def __hash__(self):
        return hash('Alert')

def test():
    l1 = Letter(symbols=['abc'])
    print(l1)
    l2 = Letter(symbols= 'abc')
    print(l2)
    l3 = Letter(symbols= ['abc',1,2])
    print(l3)
    na = Nonce('na')
    lna = Letter(na)
    print(lna)


if __name__ == '__main__':
    print(Letter.get_class_name())
    test()
    print(AttackerM())
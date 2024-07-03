
from proinspector.tools.decorators import pilogger
from copy import deepcopy

@pilogger
class Term:
    # Term is either a Atomic term (e.g. Plain(A)) or Tuple of terms
    def __init__(self, ttype, symbol=None, symbols=None, key=None,abstract=False,attM=False) -> None:
        self.ttype = ttype
        # self.symbols = set()
        self.symbols = []
        self.key = key
        self.abstract = abstract
        self.attM = attM
        if symbol is not None:
            if not isinstance(symbol,str):
                raise TypeError("Term should be a string, not %s" % repr(type(symbol)))
            # self.symbols.add(symbol)
            self.symbols.append(symbol)
        if symbols is not None: 
            if all(map (lambda x: isinstance(x,Term), symbols)):
                # self.symbols.update(symbolL)
                # self.symbols.append(symbols)
                self.symbols = symbols
            else:
                raise SyntaxError("Symbols should be a list of terms")

    def is_abstract(self):
        return self.abstract

    def is_attM(self):
        return self.attM

    def get_ttyp(self):
        return self.ttype 

    def get_key(self):
        return self.key

    def get_terms(self):
        return self.symbols
    # def inst_abs_term(self,symbol):
    #     if not self.abstract:
    #         raise Exception("instantiate non abstract term")
    #     return Term(self.get_ttyp,symbol=)

    @property
    def to_string(self):                
        str_name = "_"
        # if self.symbols is not None:
        if self.symbols:
            str_name = ','.join([repr(s) for s in self.symbols])
        return str_name

    def __str__(self):
        if self.key == None:
            return f"{self.ttype}({self.to_string})"
        else:
            return f"{self.ttype}{{{self.to_string}}}_{self.key}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if (not isinstance(other, Term)) or self.abstract != other.abstract or self.ttype !=other.ttype:
            return False
        
        return self.symbols == other.symbols and self.key == other.key

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        # return hash(frozenset(self.symbols)) + hash(self.ttype)
        return hash(str(self.symbols)) + hash(self.ttype)

#     def __init__(self,symbol=None,abstract=False) -> None:
#         if abstract:
#             super().__init__(ttype="Random")
#         elif symbol is not None:
#             super().__init__(ttype="Random",symbol=symbol)

class Tup(Term):
    def __init__(self,symbols) -> None:
        if all(map (lambda x: not x.abstract,symbols)):
            super().__init__("Tup", symbols=symbols,abstract=False)
        else:
            super().__init__("Tup", symbols=symbols,abstract=True)

    def __str__(self):
        return f"{self.ttype}{{{self.to_string}}}"
    
    def untup(self):
        return self.symbols

class Hash(Term):
    def __init__(self,symbols) -> None:
        if all(map (lambda x: not x.abstract,symbols)):
            super().__init__("Hash", symbols=symbols,abstract=False)
        else:
            super().__init__("Hash", symbols=symbols,abstract=True)

    def __str__(self):
        return f"{self.ttype}{{{self.to_string}}}"
        
class Nonce(Term):
    def __init__(self,symbol=None,abstract=False) -> None:
        if abstract:
            super().__init__(ttype="Nonce",abstract=True)
        elif symbol is not None:
            super().__init__(ttype="Nonce",symbol=symbol)

class Const(Term):
    def __init__(self,symbol=None,abstract=False) -> None:
        if abstract:
            super().__init__(ttype="Const",abstract=True)
        elif symbol is not None:
            super().__init__(ttype="Const",symbol=symbol)
    def __str__(self):
        return f"{self.to_string}"

#Symmetric Key
class Key(Term):
    def __init__(self,symbol=None,abstract=False) -> None:
        if abstract:
            super().__init__(ttype="Key",abstract=abstract)
        elif symbol is not None:
            super().__init__(ttype="Key",symbol=symbol)

#Symmetric encryption 
class SEnc(Term):
    def __init__(self, symbols, key) -> None:
        if isinstance(key,Key):
            if all(map (lambda x: not x.abstract,symbols)) and (not key.abstract):
                super().__init__("SEnc", symbols=symbols,key=key,abstract=False)
            else:
                super().__init__("SEnc", symbols=symbols,key=key,abstract=True)
        else:
            raise TypeError('Use Key to Enc')

    def sdec(self,k):
        if self.key == k:
            return self.symbols
        else:
            return [] 

    # @staticmethod
    # def sdec(msg,k):
    #     if not isinstance(msg,SEnc):
    #         return None
    #     if msg.key == k:
    #         return msg.symbols
    #     else:
    #         return None
#Public Key
class PKey(Term):
    def __init__(self,symbol=None,abstract=False) -> None:
        if abstract:
            super().__init__(ttype="PKey",abstract=abstract)
        elif symbol is not None:
            super().__init__(ttype="PKey",symbol=symbol)

#Private Key
class SKey(Term):
    def __init__(self,symbol=None,abstract=False) -> None:
        if abstract:
            super().__init__(ttype="SKey",abstract=abstract)
        elif symbol is not None:
            super().__init__(ttype="SKey",symbol=symbol)

    def is_skey_of(self,pkey):
        if not isinstance(pkey,PKey):
            return False
        return self.symbols == pkey.symbols

class AEnc(Term):
    #asymmetric encryption, encrypt with public key and decrypte with private key
    def __init__(self, symbols, key) -> None:
        # print(f'symbols is {symbols}')
        if isinstance(key,PKey):
            if all(map (lambda x: not x.abstract,symbols)) and (not key.abstract):
                super().__init__("AEnc", symbols=symbols,key=key, abstract=False)
            else:
                super().__init__("AEnc", symbols=symbols,key=key, abstract=True)
        else:
            raise TypeError('Use PKey to encrypte')

    def adec(self,k):
        if isinstance(k,SKey):
            if k.is_skey_of(self.key):
                return self.symbols
        return [] 

class Expo(Term):
    def __init__(self,symbol=None,abstract=False) -> None:
        if abstract:
            super().__init__(ttype="Expo",abstract=True)
        elif symbol is not None:
            super().__init__(ttype="Expo",symbol=symbol)

class GExp(Term):
    def __init__(self, symbols) -> None:
        if not all(map (lambda x: isinstance(x,Expo),symbols)):
            raise SyntaxError("not Expo")
        if len(symbols) >2:
            raise SyntaxError("Too many exponents")
        if all(map (lambda x: not x.abstract,symbols)):
            super().__init__("GExp", symbols=sorted(symbols), abstract=False)
        else:
            super().__init__("Gexp", symbols=sorted(symbols), abstract=True)

    def exp(self,exponent):
        if len(self.symbols) != 1:
            raise SyntaxError("Too many exponents")
        if not isinstance(exponent,Expo):
            raise SyntaxError("not Expo")
        self.symbols.append

class KDF(Term):
    def __init__(self,symbols) -> None:
        if all(map (lambda x: not x.abstract,symbols)):
            super().__init__("KDF", symbols=symbols,abstract=False)
        else:
            super().__init__("KDF", symbols=symbols,abstract=True)

    def __str__(self):
        return f"{self.ttype}{{{self.to_string}}}"

class AAEnc(Term):
    def __init__(self, symbols, key) -> None:
        if isinstance(key,KDF):
            if all(map (lambda x: not x.abstract,symbols)) and (not key.abstract):
                super().__init__("AAEnc", symbols=symbols,key=key,abstract=False)
            else:
                super().__init__("AAEnc", symbols=symbols,key=key,abstract=True)
        else:
            raise SyntaxError('Use KDF to AAEnc')

    def aadec(self,k):
        if self.key == k:
            return self.symbols
        else:
            return [] 
    
class AttM(Term):#attacker message
    def __init__(self):
        super().__init__("AttM",attM=True)
    # def __str__(self)
    #     return "AttM"

class ErrM(Term):
    def __init__(self):
        super().__init__("ErrM")
    def __str__(self):
        return "ErrM/Alert"



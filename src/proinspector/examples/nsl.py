from proinspector.automata.letter import Letter, EmptyLetter, AttackerM , Alert
from proinspector.automata.word import Word 
from proinspector.automata.transition import Transition
from proinspector.automata.state import State
from proinspector.automata.automata import Automata
from proinspector.tools.test_logger import log_test
from proinspector.testselection.wpmethod import WpMethod
from proinspector.term.term import *
from proinspector.attacker.attacker import *
import logging
import json

class NSLautomata(Automata):
    def __init__(self):
        #states
        s0 = State("s0")
        s1 = State("s1")
        s2 = State("s2")
        se = State("E")#Error state

        x = Const(abstract=True) #Abstract Agent
        rcv1 = Letter(x) 

        na = Nonce('A')
        a = Const('A')
        pkx = PKey(abstract=True)
        enc1 = AEnc([na,a],pkx)
        snd1 = Letter(enc1)

        nx = Nonce(abstract=True)
        pka = PKey('A')
        enc2 = AEnc([na,nx,x],pka)
        rcv2 = Letter(enc2)

        enc3 = AEnc([nx],pkx)
        snd2 = Letter(enc3)
        
        attM = Letter(AttM())
        alert = Letter(ErrM())

        t01 = Transition(s1,rcv1,snd1)
        t0a = Transition(se, attM, alert)
        s0.transitions=[t01,t0a]

        t12 = Transition(s2,rcv2, snd2)
        t1a = Transition(se, attM, alert)
        s1.transitions=[t12,t1a]

        t2a = Transition(se, attM, alert)
        s2.transitions=[t2a]

        tee = Transition(se,attM,alert)
        se.transitions=[tee]
        self.inputs = [rcv1,rcv2,attM]
        super(NSLautomata,self).__init__(s0,'NSL Automata')


    
def nsl_gen_test():
    nsl_automata =NSLautomata()
    # print(nsl_automata.build_dot_code())

    wp = WpMethod(4,nsl_automata.inputs)
    ti = wp.generate_tests(nsl_automata)

    ConstA = Const("A")
    ConstB = Const("B")
    ConstM = Const("M")
    Consts = [ConstA,ConstB,ConstM]

    NonceA = Nonce("A")
    NonceB = Nonce("B")
    NonceM = Nonce("M")
    Nonces = [NonceA,NonceB,NonceM]

    PKeyA = PKey("A")
    PKeyB = PKey("B")
    PKeyM = PKey("M")
    SKeyM = SKey("M")
    PKeys = [PKeyA,PKeyB,PKeyM]

    ground_terms = [
        {"Const": ConstB,
         "Nonce": NonceB,
         "PKey": PKeyB},
        {"Const": ConstM,
         "Nonce": NonceM,
         "PKey": PKeyM},
    ]

    initial_knowledge = {
        "Const": {ConstM,ConstB},
        "Nonce": {NonceM},
        "PKey": {PKeyM},
        "SKey": {SKeyM}
    }
    allow1 = [x for x in Consts]
    allow2 = [AEnc([n1,n2,cs],ks) for n1 in Nonces for n2 in Nonces for cs in Consts for ks in PKeys]
    allow = allow1+allow2
    
    attacker = Attacker(ground_terms,initial_knowledge,allow,ti)
    (ts1,ts2) = attacker.gen_tests()
    print("----phase I concrete traces----")
    Attacker.pprint_test_suit(ts1)
    print("----phase II concrete traces----")
    Attacker.pprint_test_suit(ts2)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    nsl_gen_test()
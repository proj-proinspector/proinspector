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
from itertools import combinations
from proinspector.protocol.TLS.server_mapper import TLSServerMapper 

class TLS13ClientAutomata(Automata):
    def __init__(self):
        #states
        s0 = State("s0")
        s1 = State("s1")
        se = State("E")

        sh = Const('SH')
        ee = Const('EE')
        crt = SEnc([Const('CRT'),PKey(abstract=True)],Key(abstract=True))
        cv = Const('CV')
        fin = Const('FIN')

        rcv1 = Letter(Tup([sh,ee,crt,cv,fin]))
        snd1 = Letter(Tup([Const('FIN'),Const('AD')]))

        attM = Letter(AttM())
        alert = Letter(ErrM())

        t01 = Transition(s1,rcv1,snd1)
        t0a = Transition(se, attM, alert)
        s0.transitions=[t01,t0a]

        t1a = Transition(se, attM, alert)
        s1.transitions=[t1a]

        self.inputs = [rcv1,attM]
        super(TLS13ClientAutomata,self).__init__(s0,'TLS13 Client Automata')

def check_trace_conformance(test_suit,server_mapper:TLSServerMapper):
    counter_example = []
    for (inputs, outputs) in test_suit.items():
        server_mapper.reset()
        if len(inputs) != len(outputs):
            raise Exception("Mismatched input output pair")
        current_io = []
        for i in range(len(inputs)):
            server_mapper.concretize_server_input(inputs[i])
            conform, received = server_mapper.abstract_client_output(outputs[i])
            current_io.append((inputs[i],received))
            if not conform:
                print(received)
                counter_example.append(current_io)
                break
        # server_mapper.close()
    
    return counter_example
    

def tls_gen_test():
    tls13_clientAutomata = TLS13ClientAutomata()
    wp = WpMethod(3,tls13_clientAutomata.inputs)
    ti = wp.generate_tests(tls13_clientAutomata)

    shs = [Const('SH')]
    ees = [Const('EE')]
    crtS = SEnc([Const('CRT'),PKey('Valid')],Key('S'))
    crtM1 = SEnc([Const('CRT'),PKey('Empty')],Key('M'))
    crtM2 = SEnc([Const('CRT'),PKey('Untrusted')],Key('M'))
    crts = [crtS,crtM1,crtM2]
    cvs = [Const('CV'),Const('CVEmpty'),Const('CVUntrusted'),Const('CVUnknown')]
    fins = [Const('FIN')]
    allowed_msgs = [x for x in shs+ees+crts+cvs+fins]
    allowed_msgs += ([Tup([x,y]) for x in shs for y in ees] + 
           [Tup([x,y]) for x in shs for y in crts] + 
           [Tup([x,y]) for x in shs for y in cvs]+ 
           [Tup([x,y]) for x in shs for y in fins]+   
           [Tup([x,y]) for x in ees for y in crts]+   
           [Tup([x,y]) for x in ees for y in cvs]+  
           [Tup([x,y]) for x in ees for y in fins]+   
           [Tup([x,y]) for x in crts for y in cvs]+   
           [Tup([x,y]) for x in crts for y in fins]+   
           [Tup([x,y]) for x in cvs for y in fins]) 
    allowed_msgs += ([Tup([x,y,z]) for x in shs for y in ees for z in crts] + 
            [Tup([x,y,z]) for x in shs for y in ees for z in cvs] + 
            [Tup([x,y,z]) for x in shs for y in ees for z in fins] + 
            [Tup([x,y,z]) for x in shs for y in crts for z in cvs] + 
            [Tup([x,y,z]) for x in shs for y in crts for z in fins] + 
            [Tup([x,y,z]) for x in shs for y in cvs for z in fins] + 
            [Tup([x,y,z]) for x in ees for y in crts for z in cvs] + 
            [Tup([x,y,z]) for x in ees for y in crts for z in fins] + 
            [Tup([x,y,z]) for x in ees for y in cvs for z in fins] + 
            [Tup([x,y,z]) for x in crts for y in cvs for z in fins])
    allowed_msgs += ([Tup([x,y,z,i]) for x in shs for y in ees for z in crts for i in cvs] + 
            [Tup([x,y,z,i]) for x in shs for y in ees for z in crts for i in fins]+
            [Tup([x,y,z,i]) for x in shs for y in ees for z in cvs for i in fins]+
            [Tup([x,y,z,i]) for x in shs for y in crts for z in cvs for i in fins]+ 
            [Tup([x,y,z,i]) for x in ees for y in crts for z in cvs for i in fins])
    allowed_msgs += [Tup([x,y,z,i,j]) for x in shs for y in ees for z in crts for i in cvs for j in fins]

    ground_terms = [
        {
            # "PKey": PKey('S'),
            "PKey": PKey('Valid'),
            "Key": Key('S')
        }
    ]

    initial_knowledge = {
        "Const": {Const('SH'), Const('EE'),Const('CRT'),Const('Fin'), Const('CVEmpty'),Const('CVUntrusted'),Const('CVUnknown')},
        # "PKey": {PKey('M')},
        "PKey": {PKey('Empty'),PKey('Untrusted')},
        "Key": {Key('M')}
    }
    attacker = Attacker(ground_terms,initial_knowledge,allowed_msgs,ti)
    (ts1,ts2) = attacker.gen_tests()
    print("----phase I concrete traces----")
    server_mapper = TLSServerMapper('127.0.0.1',4445,4446,2)
    counter_example = check_trace_conformance(ts1,server_mapper)
    if counter_example != []:
        print(counter_example)
        raise Exception('Phase I Failed, check reference model and IUT')
    print("----phase II concrete traces----")
    counter_example = server_mapper.check_trace_conformance(ts2)
    if counter_example != []:
        # print(len(counter_example))
        print(f'{len(counter_example)} test cases failed, the outputs ProVerif traces are in ./failed-trace')
        TLSServerMapper.write_to_proverif(counter_example)
    else:
        print("All test cases pass.")
        raise Exception('Phase II Failed, check reference model and IUT')

#ncat -c "while read server port; do ./client -v 4 -p 4445 -A /tmp/ca.pem -Y -h 127.0.0.1; done" -l -p 4446 -k
#ncat -c "while read server port; do openssl s_client -quiet  -tls1_3 -no_middlebox -CAfile ca.pem -connect 127.0.0.1:4445; done" -l -p 4446 -k
if __name__ == "__main__":
    tls_gen_test()

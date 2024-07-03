from proinspector.term.term import *
from proinspector.automata.letter import *
from copy import deepcopy

class Attacker:
    def __init__(self, ground_terms, initial_knowledge,allowed_msgs, t_abs) -> None:
        self.ground_terms = ground_terms
        self.initial_knowledge= initial_knowledge
        self.allowed_msgs = allowed_msgs
        self.t_abs = t_abs
        self.t_c = {} 
        self.t_c1 = {}
        self.t_a = {}
        self.t_block = {}

    def pprint_trace(inputs:tuple,outputs:tuple):
        if len(inputs) != len(outputs):
            raise Exception("Mismatched input output pair")
        for i in range(len(inputs)):
            print(f'i[{i}]:{inputs[i]}')
            print(f'o[{i}]:{outputs[i]}')
        
    def pprint_test_suit(test_suit:dict):
        i = 0
        for (k, v) in test_suit.items():
            print(f'Trace#{i}')
            Attacker.pprint_trace(k,v)
            i = i+1
    
    @staticmethod
    def inst_term(term_dict:dict):
        def next(term:Term):
            # print(f'inst term is {term}')
            # print(f'ground terms are {term_dict}')
            if isinstance(term,list):
                abstract = not all(not t.is_abstract() for t in term)
                print(f"terms {term} abstract is{abstract}")
            else: 
                abstract = term.is_abstract()
            if abstract:
                if isinstance(term,AEnc):
                    sl = Attacker.inst_term(term_dict)(term.symbols) 
                    if term.key.is_abstract():
                        k = term_dict["PKey"]
                    else:
                        k = term.key
                    return AEnc(symbols=sl,key=k)
                elif isinstance(term,SEnc):
                    sl = Attacker.inst_term(term_dict)(term.symbols) 
                    if term.key.is_abstract():
                        k = term_dict["Key"]
                    else:
                        k = term.key
                    return SEnc(sl,k)
                elif isinstance(term,Tup):
                    sl=[]
                    for t in term.symbols:
                        sl.append(Attacker.inst_term(term_dict)(t))
                    return Tup(sl)
                elif isinstance(term,GExp):
                    sl = Attacker.inst_term(term_dict)(term.symbols) 
                elif isinstance(term,KDF):
                    sl = Attacker.inst_term(term_dict)(term.symbols) 
                elif isinstance(term,AAEnc):
                    sl = Attacker.inst_term(term_dict)(term.symbols) 
                    if term.key.is_abstract():
                        kl = Attacker.inst_term(term_dict)(term.key.symbols) 
                        k = KDF(kl)
                    else:
                        k = term.key
                    return AAEnc(sl,k)
                else:
                    if isinstance(term,list):
                        # return list(map(lambda x:deepcopy(term_dict[x.get_ttyp()]),term))
                        return [(term_dict[x.get_ttyp()] if x.is_abstract() else x) for x in term]
                    else: 
                        return term_dict[term.get_ttyp()]
            else:
                return term 
        return next

    # def get_t_c1 (self):
    #     return deepcopy(self.t_c1)

    def concrete_terms(self):
        # print(f'T_abs is {self.t_abs}')
        # print(f'groud_terms is {self.ground_terms}')
        temp = []
        for (inputs, outputs) in self.t_abs.items():
            contains_attm = False
            linputs = list(inputs)
            loutputs = list(outputs)
            # print(f'linputs:{linputs}')
            # print(f'loutputs:{loutputs}')
            for i in range(len(linputs)):
                if linputs[i].is_attM():
                    contains_attm = True
                    break
            # print(f'i is {i}')
            if contains_attm:
                print('contain attm')
                # llinputs = [map(self.inst_term(g_t),linputs[0:i]) for g_t in self.ground_terms]
                # lloutputs = [map(self.inst_term(g_t),loutputs[0:i]) for g_t in self.ground_terms]
                # llinputs = [ list(x)+linputs[i:len(linputs)] for x in llinputs]
                # lloutputs = [ list(x)+loutputs[i:len(outputs)] for x in lloutputs]
                llinputs = []
                lloutputs = []
                for g_t in self.ground_terms:
                    temp1 = []
                    temp2 = []
                    for input in linputs[0:i]:
                        inp = self.inst_term(g_t)(input)
                        temp1.append(inp)
                    temp1.append(linputs[i])
                    llinputs.append(temp1)
                    for output in loutputs[0:i]:
                        out = self.inst_term(g_t)(output)
                        temp2.append(out)
                    temp2.append(loutputs[i])
                    lloutputs.append(temp2)
                # print(f'llinputs:{list(llinputs[1])}')
                # lloutputs = [map(self.inst_term(g_t),loutputs) for g_t in self.ground_terms]
                # print(f'lloutputs:{list(lloutputs[1])}')
                #concrete test traces
                for j in range(len(llinputs)):
                    # print(f'llinputs[{j}]:{tuple(llinputs[j])}')
                    # print(f'lloutputs[{j}]:{tuple(lloutputs[j])}')
                    self.t_a.update({tuple(llinputs[j]): tuple(lloutputs[j])})
            else:
                # llinputs = [map(self.inst_term(g_t),linputs) for g_t in self.ground_terms]
                # print('not contain attm')
                llinputs = []
                lloutputs = []
                for g_t in self.ground_terms:
                    temp1 = []
                    temp2 = []
                    for input in linputs:
                        inp = self.inst_term(g_t)(input)
                        temp1.append(inp)
                    llinputs.append(temp1)
                    for output in loutputs:
                        out = self.inst_term(g_t)(output)
                        temp2.append(out)
                    lloutputs.append(temp2)
                        
                # print(f'llinputs:{list(llinputs[1])}')
                # lloutputs = [map(self.inst_term(g_t),loutputs) for g_t in self.ground_terms]
                # print(f'lloutputs:{list(lloutputs[1])}')
                #concrete test traces
                for i in range(len(llinputs)):
                    # print(f'llinputs[{i}]:{tuple(llinputs[i])}')
                    # print(f'lloutputs[{i}]:{tuple(lloutputs[i])}')
                    self.t_c1.update({tuple(llinputs[i]): tuple(lloutputs[i])})
                    self.t_block.update({tuple(llinputs[i][0:len(llinputs[i])-1]): (llinputs[i][-1],lloutputs[i][-1])})


    def expand_knowledge(msg,curr_k):
        if msg.ttype in curr_k:
            curr_k[msg.ttype].add(msg)
        elif not isinstance(msg,Tup):
            curr_k[msg.ttype]= {msg}

        if isinstance(msg,Tup):
            for item in msg.untup():
                Attacker.expand_knowledge(item,curr_k)
        elif isinstance(msg,AEnc):
            keys = curr_k.get("SKey")
            if keys is None:
                return
            lterm = [] 
            for key in keys:
                lterm = msg.adec(key)
                if lterm != []:
                    break
            for term in lterm:
                Attacker.expand_knowledge(term,curr_k)
        elif isinstance(msg,SEnc):
            keys = curr_k.get("Key")
            if keys is None:
                return
            lterm = [] 
            if keys is None:
                return
            for key in keys:
                lterm = msg.sdec(key)
                if lterm != []:
                    break
            for term in lterm:
                Attacker.expand_knowledge(term,curr_k)
        elif isinstance(msg,Key):
            encs = curr_k.get("SEnc")
            if encs is None:
                return 
            for enc in encs:
                lterm = enc.sdec(msg)
                for term in lterm:
                    Attacker.expand_knowledge(term,curr_k)
        elif isinstance(msg,SKey):
            encs = curr_k.get("AEnc")
            if encs is None:
                return 
            for enc in encs:
                lterm = enc.adec(msg)
                for term in lterm:
                    Attacker.expand_knowledge(term,curr_k)

    def knows(msg:Term,knowledge):
        if isinstance(msg,Tup):
            return all(map (lambda x: Attacker.knows(x,knowledge), msg.get_terms()))
        if isinstance(msg,Hash):
            return all(map (lambda x: Attacker.knows(x,knowledge), msg.get_terms()))
        elif isinstance(msg,SEnc):
            knows = knowledge.get(msg.get_ttyp())
            if knows and msg in knows:
                return True
            elif Attacker.knows(msg.get_key(),knowledge):
                return all(map (lambda x: Attacker.knows(x,knowledge), msg.get_terms()))
            else:
                return False
        elif isinstance(msg,AEnc):
            knows = knowledge.get(msg.get_ttyp())
            if knows and msg in knows:
                return True
            elif Attacker.knows(msg.get_key(),knowledge):
                return all(map (lambda x: Attacker.knows(x,knowledge), msg.get_terms()))
            else:
                return False
        else:
            knows = knowledge.get(msg.get_ttyp())
            if knows:
                return msg in knows
            return False
        # knows = knowledge.get(msg.get_ttyp())
        # if knows:
        #     return msg in knows
        # return False

    def can_send(self, knowledge):
        ret = []
        for allowed_msg in self.allowed_msgs:
            if Attacker.knows(allowed_msg,knowledge):
                ret.append(allowed_msg)
        return ret

    def concrete_attM(self):
        att_t = self.t_a
        for (inputs,outputs) in att_t.items():
            current_knowledge = deepcopy(self.initial_knowledge)
            for i in range(len(inputs)):
                if isinstance(inputs[i],AttM):
                    # print('before attm')
                    # print(inputs[0:i])
                    blocked_msgs = self.t_block.get(inputs[0:i])
                    if blocked_msgs != None:
                        for blocked_msg in blocked_msgs:
                            Attacker.expand_knowledge(blocked_msg,current_knowledge)
                    
                    can_send = self.can_send(current_knowledge)
                    att_traces = [inputs[0:i]+(x,) for x in can_send]
                    # By FSM machine construction, AttM() can only followed by AttM().
                    for j in range(i+1,len(inputs)):
                        att_traces = [y[0:j]+(x,) for x in can_send for y in att_traces]
                    # for k in range(len(cases)):
                    for att_trace in att_traces:
                        if self.t_c1.get(att_trace) is None:
                            self.t_c.update({att_trace:outputs})
                    # Attacker.pprint_test_suit(self.t_c)
                    break
                else:
                    # print(inputs[i])
                    Attacker.expand_knowledge(inputs[i],current_knowledge)
                    Attacker.expand_knowledge(outputs[i],current_knowledge)

    def gen_tests(self):
        self.concrete_terms()
        self.concrete_attM()
        return (self.t_c1,self.t_c)

    
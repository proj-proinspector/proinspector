import os
import os.path
import socket

from pathlib import Path
from proinspector.automata.letter import Letter, EmptyLetter, AttackerM , Alert
from proinspector.automata.word import Word 
from proinspector.automata.transition import Transition
from proinspector.automata.state import State
from proinspector.automata.automata import Automata
from proinspector.tools.test_logger import log_test
from proinspector.testselection.wpmethod import WpMethod
from proinspector.term.term import *
from proinspector.attacker.attacker import *
from scapy.all import *
from scapy.layers.tls.handshake import *
from scapy.layers.tls.session import tlsSession
from proinspector.protocol.TLS.server import TLSServer
from proinspector.attacker.attacker import *
from scapy.layers.tls.cert import Cert, PrivKey, PrivKeyRSA
from scapy.layers.tls.record import TLSAlert, _tls_alert_description

dir_path = os.path.dirname(os.path.realpath(__file__))
valid_cert_path = os.path.join(dir_path,'crypto/servers/valid/cert.pem')
valid_key_path= os.path.join(dir_path,'crypto/servers/valid/key.pem')
untrusted_cert_path = os.path.join(dir_path,'crypto/servers/untrusted/cert.pem')
untrusted_key_path= os.path.join(dir_path,'crypto/servers/untrusted/key.pem')

class TLSServerMapper:
    def __init__(self, ip, port, trigger_port, timeout) -> None:
        self.server = TLSServer(
            server= ip,
            sport=port,
            mycert =valid_cert_path,
            mykey = valid_key_path, 
            curve="secp256r1",
            timeout=timeout,
            accept_timeout=10,
        )

        self.ip = ip
        self.trigger_port = trigger_port
        self.server.BIND()

    def trigger_client(self):
        client_trigger = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_trigger.connect((self.ip,self.trigger_port))
        trigger_string = f"blah\n".encode("utf8")
        client_trigger.send(trigger_string)
    
    def reset(self):
        try:
            self.trigger_client()
            self.server.WAITING_CLIENT()
        except socket.timeout:
            raise Exception("Connection time out; check the state of the IUT.")
        self.server.INIT_TLS_SESSION()
        self.server.tls13_handle_ClientHello()

    def close(self):
        self.server.tls_fatal_alert(descr=0)
        self.server.flush_records()

    def parse_receive(self):
        try: 
            self.server.get_next_msg()
        except TimeoutError:
            print("TimeourError")
            return Const("Timeout")
        except ConnectionResetError:
            print("ConnectionError")
            return Const("Connection Error")
        response = self.server.buffer_in
        msg_type = []
        for rsp in response:
            try:
                # If rsp.load exists, it means that scapy was not able to parse the packet correctly
                _ = rsp.load
                # msg_type.append("UnknownPacket not parsed")
                msg_type.append("Alert")
                # print(str(type(rsp.load)))
                # print(rsp.load)
                # print(rsp)
                continue
            except AttributeError:
                pass
            if isinstance(rsp, TLSAlert):
                msg_type.append("Alert")
            else:
                abstract_msg = str(type(rsp)).rsplit(".", maxsplit=1)[-1].replace("'>", "")
                if abstract_msg == "Raw":
                    abstract_msg = "UnknownPacket"+str(type(rsp))
                elif abstract_msg == "TLSApplicationData":
                    try:
                        rsp.data.decode("utf-8")
                    except UnicodeDecodeError:
                        abstract_msg = "UnknownPacket decode"
                msg_type.append(abstract_msg)
        # print(msg_type)  
        self.server.buffer_in = []
        receive = ('+'.join(msg_type))
        print(receive)
        if receive == 'TLSFinished': 
            return Const('FIN')
        elif receive == 'TLSApplicationData':
            return Const('AD')
        elif receive == 'Alert' or msg_type == []:
            return ErrM()
        # return "Nothing" 
        else:
            raise Exception('Unable to parse receive message')

    def concretize_server_input(self,inputs):
        if isinstance(inputs,Tup):
            linputs = inputs.untup()
        else:
            linputs = [inputs]
        for input in linputs:
            if input == Const('SH'):
                self.server.tls13_ServerHello()
            elif input == Const('EE'):
                self.server.tls13_EncryptedExtensions()
            elif isinstance(input,SEnc):
                if input.symbols[0] == Const('CRT'):
                    if input.symbols[1] == PKey('Valid'):
                        self.server.tls13_Certificate(Cert(valid_cert_path),PrivKey(valid_key_path))
                    elif input.symbols[1]==PKey('Empty'):
                        self.server.tls13_Certificate(None,PrivKeyRSA())
                    elif input.symbols[1]==PKey('Untrusted'):
                        self.server.tls13_Certificate(Cert(untrusted_cert_path),PrivKey(untrusted_key_path))
                    else:
                        raise Exception(f'Unknow certificate input: {input}')
            elif  input == Const('CV'):
                self.server.tls13_CertificateVerify2(Cert(valid_cert_path),PrivKey(valid_key_path))
            elif  input == Const('CVEmpty'):
                self.server.tls13_CertificateVerify2(None,PrivKeyRSA())
            elif  input == Const('CVUntrusted'):
                self.server.tls13_CertificateVerify2(Cert(untrusted_cert_path),PrivKey(untrusted_key_path))
            elif  input == Const('CVUnknown'):
                self.server.tls13_InvalidCertificateVerify()
            elif input == Const('FIN'):
                self.server.tls13_Finished()
            else:
                raise Exception(f'Unknow input: {input}')
        self.server.flush_records("TLS13ServerHello")
    
    def abstract_client_output(self, outputs):
        if isinstance(outputs,Tup):
            loutputs= outputs.untup()
        else:
            loutputs= [outputs]
        conform = True
        receives = []
        for output in loutputs:
            receive = self.parse_receive()
            if receive == Const('Timeout') and (output == Const('AD') or output == ErrM()):
                receives.append(output)
                continue
            receives.append(receive)
            if receive != output:
                conform = False
        return (conform,receives)

    
    def check_trace_conformance(self,test_suit):
        counter_example = []
        for (inputs, outputs) in test_suit.items():
            self.reset()
            if len(inputs) != len(outputs):
                raise Exception("Mismatched input output pair")
            current_io = []
            for i in range(len(inputs)):
                self.concretize_server_input(inputs[i])
                conform, received = self.abstract_client_output(outputs[i])
                current_io.append((inputs[i],received))
                if not conform:
                    print(received)
                    counter_example.append(current_io)
                    break
        
        return counter_example
    
    def trace_to_proverif2(indent,inputs,outputs,fh):
        if len(inputs) == 0:
            #print output
            for output in outputs:
                if output == Const('FIN'):
                    fh.write('\t'*indent)
                    fh.write('event endS(cr,sr,chs);\n')
                    fh.write('\t'*indent)
                    fh.write('out(c,enc(Fin,chs));\n')
                    fh.write('\t'*indent)
                    fh.write('out(c,enc(ms,cas))\n')
                else:
                    raise Exception(f'Uable to write output {output} to ProVerif')
            return
        curr_in = inputs[0]
        if curr_in == Const('SH'):
            fh.write('\t'*indent)
            fh.write('in(c, SH(sr:nonce,=GoodParams));\n')
            fh.write('\t'*indent)
            fh.write('in(c,sdh:element);\n')
            fh.write('\t'*indent)
            fh.write('let k = exp(sdh,x) in\n')
            fh.write('\t'*indent)
            fh.write('let chs = kdf_hs(cr,sr,k) in\n')
            fh.write('\t'*indent)
            fh.write('let cas = kdf_hs(cr,sr,k) in\n')
            TLSServerMapper.trace_to_proverif2(indent,inputs[1:],outputs,fh)
        elif curr_in == Const('EE'):
            fh.write('\t'*indent)
            fh.write('in(c,esee:bitstring);\n')
            fh.write('\t'*indent)
            fh.write('let see = dec(esee,chs) in\n')
            fh.write('\t'*indent)
            fh.write('if see = EE then\n')
            TLSServerMapper.trace_to_proverif2(indent+1,inputs[1:],outputs,fh)
            fh.write('\t'*indent+'else\n')
            fh.write('\t'*(indent+1)+'0\n')
        elif isinstance(curr_in,SEnc):
            if curr_in.symbols[0] == Const('CRT'):
                if curr_in.symbols[1] == PKey('Valid'):
                    fh.write('\t'*indent)
                    fh.write('in(c,escrt:bitstring);\n')
                    fh.write('\t'*indent)
                    fh.write('let scrt = dec(escrt,chs) in\n')
                    fh.write('\t'*indent)
                    fh.write('if scrt = CRT(spkS) then\n')
                    TLSServerMapper.trace_to_proverif2(indent+1,inputs[1:],outputs,fh)
                    fh.write('\t'*indent+'else\n')
                    fh.write('\t'*(indent+1)+'0\n')
                elif curr_in.symbols[1] == PKey('Empty'):
                    fh.write('\t'*indent)
                    fh.write('in(c,escrt:bitstring);\n')
                    fh.write('\t'*indent)
                    fh.write('let scrt = dec(escrt,chs) in\n')
                    fh.write('\t'*indent)
                    fh.write('if scrt = CRT(spkM) then\n')
                    TLSServerMapper.trace_to_proverif2(indent+1,inputs[1:],outputs,fh)
                    fh.write('\t'*indent+'else\n')
                    fh.write('\t'*(indent+1)+'0\n')
                else:
                    raise Exception(f'Uable to translate input{curr_in}')
            else:
                raise Exception(f'Uable to translate input{curr_in}')
        elif curr_in == Const('CVEmpty') or curr_in == Const('CVUntrusted') or curr_in ==Const('CV'):#CV is the signature of previously sent CRT
            fh.write('\t'*indent)
            fh.write('in(c,escrtv:bitstring);\n')
            fh.write('\t'*indent)
            fh.write('let scrtv = dec(escrtv,chs) in (**)\n')
            fh.write('\t'*indent)
            fh.write('let (=cr,=sr,=chs) = checksign(scrtv,spkM) in\n')
            TLSServerMapper.trace_to_proverif2(indent,inputs[1:],outputs,fh)
        elif curr_in == Const('CVUnknown'):
            fh.write('\t'*indent)
            fh.write('in(c,escrtv:bitstring);\n')
            fh.write('\t'*indent)
            fh.write('let scrtv = dec(escrtv,chs) in\n')
            TLSServerMapper.trace_to_proverif2(indent,inputs[1:],outputs,fh)
        elif curr_in == Const('FIN'):
            fh.write('\t'*indent)
            fh.write('in(c,efin:bitstring);\n')
            fh.write('\t'*indent)
            fh.write('let fin = dec(efin,chs) in\n')
            fh.write('\t'*indent)
            fh.write('if fin = Fin then\n')
            TLSServerMapper.trace_to_proverif2(indent+1,inputs[1:],outputs,fh)
            fh.write('\t'*indent+'else\n')
            fh.write('\t'*(indent+1)+'0\n')
        else:
            raise Exception('Unable to write input to Proverif')

    def trace_to_proverif(tf,fh):
        fh.write('query x:nonce,y:nonce,k:key; event(endS(x,y,k)) ==> event(beginS(x,y,k)).\n')
        fh.write('query attacker(ms).\n\n')
        fh.write("let ProcTf(spkS:spkey, spkM:spkey) =\n\t(new cr:nonce;\n\tout(c,CH(cr,GoodParams));\n\tnew x: bitstring;\n\tout(c, exp(G,x));\n")
        for (inputs, outputs) in tf:
            if isinstance(inputs,Tup):
                linputs = inputs.untup()
            else:
                linputs = [inputs]
            if isinstance(outputs,Tup):
                loutputs = outputs.untup()
            else:
                loutputs = outputs
            TLSServerMapper.trace_to_proverif2(1,linputs,loutputs,fh)
        fh.write("\t).\n\n")
        fh.write('process\n')
        fh.write('\tnew sskS:sskey;\n')
        fh.write('\tnew sskM:sskey;\n')
        fh.write('\tlet spkS = spk(sskS) in out(c,spkS);\n')
        fh.write('\tlet spkM = spk(sskM) in out(c,sskM);\n')
        fh.write('\t((!Client13(spkS))|(!Server13(spkS,sskS))|(!ProcTf(spkS,spkM)))')
            # for input in linputs:
            #     if input == Const('SH'):
            #         fh.write('\tin(c, SH(sr:nonce,=GoodParams));')
            #         fh.write('\tin(c,sdh:element);')

            # fh.write(str(inputs))
            # fh.write(str(outputs))
        return

    def write_to_proverif(ces:list):
        out_folder = "failed-traces"
        out_path= os.path.join(dir_path,out_folder)
        Path(out_path).mkdir(parents=True, exist_ok=True)
        for i,ce in enumerate(ces):
            f = open(f'{out_path}/clientTf{i}.pv', "w")
            TLSServerMapper.trace_to_proverif(ce,f)











        
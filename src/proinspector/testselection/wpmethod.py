import itertools
from collections import deque

from proinspector.automata.word import Word
from proinspector.automata.letter import Letter, EmptyLetter, AttackerM, Alert
from proinspector.term.term import *
from proinspector.tools.decorators import pilogger

class OutputQuery:
    def __init__(self, word):
        self.input_word = word
        self.output_word = None

    def is_queried(self):
        """This method returns True is the query was queried

        >>> from pylstar.OutputQuery import OutputQuery
        >>> from pylstar.Word import Word
        >>> from pylstar.Letter import Letter
        >>> w1 = Word([Letter("a")])
        >>> output_query = OutputQuery(w1)
        >>> output_query.is_queried()
        False
        >>> print(output_query)
        OutputQuery(I = [Letter('a')], O = None)

        """
        return self.output_word is not None

    def __str__(self):
        return "OutputQuery(I = {}, O = {})".format(self.input_word, self.output_word)

    def multiply(self, queries):
        if queries is None:
            raise Exception("Queries cannot be None")

        return [OutputQuery(self.input_word + query.input_word) for query in queries]
        
    @property
    def input_word(self):
        """Input word that makes the query"""
        return self.__input_word
    
    @input_word.setter
    def input_word(self, input_word):
        if input_word is None:
            raise Exception("Input word cannot be None")
        
        self.__input_word = input_word   

    @property
    def output_word(self):
        return self.__output_word
    
    @output_word.setter
    def output_word(self, output_word):
        self.__output_word = output_word   

@pilogger
class WpMethod:
    def __init__(self, max_states, input_letters) -> None:
        self.max_states = max_states
        self.input_letters = input_letters

    def __computesP(self, hypothesis):
        if hypothesis is None:
            raise Exception("Hypothesis cannot be None")
        self._logger.debug("Computing P")

        P = []
            
        empty_word = Word([EmptyLetter()])
        current_query = OutputQuery(empty_word)
        P.append(current_query)

        open_queries = deque([current_query])
        close_queries = []

        seen_states = set([hypothesis.initial_state])
        while len(open_queries) > 0:
            query = open_queries.popleft()
            tmp_seen_states = set()

            for letter in self.input_letters:
                new_word = query.input_word + Word([letter])
                query_z = OutputQuery(new_word)
                (output_word, visited_states) = hypothesis.play_query(query_z)
                close_queries.append(query_z)
                
                if visited_states[-1] not in seen_states:
                    tmp_seen_states.add(visited_states[-1])
                    open_queries.append(query_z)

            seen_states.update(tmp_seen_states)

        P.extend(close_queries)

        return P

    def __computesZ(self, hypothesis, W):    
        """it follows the formula Z= W U (X^1.W) U .... U (X^(m-1-n).W) U (W^(m-n).W)

        """
        if hypothesis is None:
            raise Exception("Hypothesis cannot be None")
        if W is None:
            raise Exception("W cannot be None")
            
        self._logger.debug("Computing Z")

        Z = []
        Z.extend(W)
        
        states = hypothesis.get_states()
        v = self.max_states - len(states)
        if v < 0:
            v = 0
        self._logger.debug("V= {}".format(v))

        output_queries = []
        for input_letter in self.input_letters:
            output_query = OutputQuery(word = Word([input_letter]))
            output_queries.append(output_query)

        X = dict()
        X[0] = W
        for i in range(1, v+1):
            self._logger.debug("Computing X^{}".format(i))
            X[i] = []
            previous_X = X[i-1]
            for x in previous_X:
                X[i].extend(x.multiply(output_queries))
            for w in W:
                for xi in X[i]:
                    if not xi in Z:
                        Z.append(xi)

        return Z

    def __compute_distinguishable_string(self, hypothesis, couple):
        self._logger.debug("Computes the distinguishable string for state couple '{}'".format(couple))
        if hypothesis is None:
            raise Exception("Hypothesis cannot be None")
        if couple is None:
            raise Exception("couple cannot be None")
            
        # self._logger.debug("Computing distinguishing strings for states {}".format(couple))
        queries_to_test = deque([])
        
        empty_word = Word([EmptyLetter()])
        z_query = OutputQuery(empty_word)
        for letter in self.input_letters:
            new_word = z_query.input_word + Word([letter])
            queries_to_test.append(OutputQuery(new_word))

        distinguishable_query = z_query

        done = False
        i = 0
        while not done:
            query = queries_to_test.popleft()
            if i > self.max_states * self.max_states:
                break

            if not self.__is_distinguishable_states(hypothesis, query, couple):
                done = False
                for letter in self.input_letters:
                    new_query = OutputQuery(query.input_word + Word([letter]))
                    queries_to_test.append(new_query)
            else:
                done = True
                distinguishable_query = query

            i = i + 1

        return distinguishable_query
        
    def __is_distinguishable_states(self, hypothesis, query, couple):
        if hypothesis is None:
            raise Exception("Hypothesis cannot be None")
        if query is None:
            raise Exception("query cannot be None")
        if couple is None:
            raise Exception("couple cannot be None")

        output_word_state0 = hypothesis.play_word(query.input_word, couple[0])[0]
        output_word_state1 = hypothesis.play_word(query.input_word, couple[1])[0]
        
        return output_word_state0 != output_word_state1

    def generate_tests(self, hypothesis):
        if hypothesis is None:
            raise Exception("Hypothesis cannot be None")

        self._logger.info('Generating test suite...')
        W = []

        states = hypothesis.get_states()
        
        # compute all couples of states
        state_couples = itertools.combinations(states, 2)

        # Constructing the characterization set W of the hypothesis
        for couple in state_couples:
            # Computes a distinguishing string for each couple of state
            W.append(self.__compute_distinguishable_string(hypothesis, couple))

        # computes P
        P = self.__computesP(hypothesis)
        # self._logger.debug("P= {}".format(P))

        # computes Z
        Z = self.__computesZ(hypothesis, W)
        # self._logger.debug("Z= {}".format(Z))

        # T = P . Z
        T =  P + Z
        self._logger.debug("----test queries----")
        for i,test_query in enumerate(T[1:]):
            self._logger.debug(f"querey #{i}: {test_query}")
        self._logger.debug("----test queries end----")

        test_sequences = []
        for i_testcase, testcase_query in enumerate(T[1:]):
            # self._logger.debug("Executing testcase {}/{} : {}".format(i_testcase, len(T)-1, testcase_query))
            self._logger.info("test query {}/{} : {}".format(i_testcase, len(T)-1, testcase_query))
            hypothesis_output_word = hypothesis.play_query(testcase_query)[0]
            self._logger.info(f'Hypothesis output{hypothesis_output_word}')
            if not hypothesis_output_word.contains_readstate():
                self._logger.info('Add to test sequences')
                testcase_query.output_word = hypothesis_output_word
                test_sequences.append(testcase_query)
            self._logger.info('Not add to test sequences')
            # print(hypothesis_output_word)
        TI = {}
        for ts in test_sequences:
            inputs = ts.input_word.letters
            outputs= ts.output_word.letters
            input = []
            output = []
            for i in range(len(inputs)):
                if isinstance(inputs[i],AttackerM):
                    input.append(AttM())
                    output.append(ErrM())
                    continue
                if len(inputs[i].symbols) != 1 or len(outputs[i].symbols) != 1 :
                    raise Exception("Should not come here")
                input.append(list(inputs[i].symbols)[0]) 
                output.append(list(outputs[i].symbols)[0]) 
            TI.update({tuple(input):tuple(output)})
        # return test_sequences
        return TI
class Transition:
    """Definition of a transition that belongs to an automata
    """

    def __init__(self, output_state, input_letter, output_letter, name = None):
        self.name = name
        self.output_state = output_state
        self.input_letter = input_letter
        self.output_letter = output_letter

    @property
    def label(self):
        input_symbols = []
        for symbol in self.input_letter.symbols:
            try:
                input_symbols.append(symbol.name)
            except Exception:
                input_symbols.append(str(symbol))

        output_symbols = []
        for symbol in self.output_letter.symbols:
            try:
                output_symbols.append(symbol.name)
            except Exception:
                output_symbols.append(str(symbol))
        
        return "{} / {}".format(",".join(input_symbols), ",".join(output_symbols))
    
    def __str__(self) -> str:
        if self.name:
            return f'Transition {self.name}: [Out State {self.output_letter}, input: {self.input_letter}, output: {self.output_letter}]'
    def __repr__(self) -> str:
        return self.__str__()
    

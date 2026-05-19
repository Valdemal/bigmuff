from kernel.block.function import TFunctionBlock

# todo сделать переменную неглобальной
function_block = TFunctionBlock()

def translate(filename: str) -> TFunctionBlock:
    tok = FCLProgram()

    with open(filename, mode='r') as file:
        FCLTextToTokens(filename, file, tok)
        FCLInit()
        Translate(tok)
        return function_block


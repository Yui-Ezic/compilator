import Lexer
import json


def main():
    # Read the code from example.z and store it in variable
    with open("test.z", 'r') as file:
        content = file.read()

    lex = Lexer.Lexer(content)
    lex.tokenize()

    with open("output.txt", 'w') as file:
        if lex.is_error():
            file.write("ERROR:\n")
            file.write(lex.error)
        else:
            file.write("\nCONST TABLE:\n"
                       "CONST | INDEX\n")
            file.writelines("%s\n" % const for const in lex.consts)
            file.write("\nIDENTIFIERS TABLE:\n"
                       "NAME | INDEX | TYPE\n")
            file.writelines("%s\n" % identifier for identifier in lex.identifiers)
            file.write("\nTOKENS:\n"
                       "LINE | STRING | TOKEN | INDEX\n")
            file.writelines("%s\n" % token for token in lex.tokens)


main()

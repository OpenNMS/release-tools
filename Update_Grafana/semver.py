import re
class Semver:
    def __init__(self) -> None:
        pass

    def Parse(self,inputstring) -> tuple:
        pat=re.match("^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$",inputstring)

        return pat.groups()


#z=Semver()
#z.Parse("1.1.1")
#z.Parse("1.0.0-alpha")
#z.Parse("1.0.0-alpha.1")
#z.Parse("1.0.0-0.3.7")
#z.Parse("1.0.0-x.7.z.92")
#z.Parse("1.0.0-alpha+001")
# <valid semver> ::= <version core>
#                  | <version core> "-" <pre-release>
#                  | <version core> "+" <build>
#                  | <version core> "-" <pre-release> "+" <build>
# 
# <version core> ::= <major> "." <minor> "." <patch>
# 
# <major> ::= <numeric identifier>
# 
# <minor> ::= <numeric identifier>
# 
# <patch> ::= <numeric identifier>
# 
# <pre-release> ::= <dot-separated pre-release identifiers>
# 
# <dot-separated pre-release identifiers> ::= <pre-release identifier>
#                                           | <pre-release identifier> "." <dot-separated pre-release identifiers>
# 
# <build> ::= <dot-separated build identifiers>
# 
# <dot-separated build identifiers> ::= <build identifier>
#                                     | <build identifier> "." <dot-separated build identifiers>
# 
# <pre-release identifier> ::= <alphanumeric identifier>
#                            | <numeric identifier>
# 
# <build identifier> ::= <alphanumeric identifier>
#                      | <digits>
# 
# <alphanumeric identifier> ::= <non-digit>
#                             | <non-digit> <identifier characters>
#                             | <identifier characters> <non-digit>
#                             | <identifier characters> <non-digit> <identifier characters>
# 
# <numeric identifier> ::= "0"
#                        | <positive digit>
#                        | <positive digit> <digits>
# 
# <identifier characters> ::= <identifier character>
#                           | <identifier character> <identifier characters>
# 
# <identifier character> ::= <digit>
#                          | <non-digit>
# 
# <non-digit> ::= <letter>
#               | "-"
# 
# <digits> ::= <digit>
#            | <digit> <digits>
# 
# <digit> ::= "0"
#           | <positive digit>
# 
# <positive digit> ::= "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
# 
# <letter> ::= "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J"
#            | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T"
#            | "U" | "V" | "W" | "X" | "Y" | "Z" | "a" | "b" | "c" | "d"
#            | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n"
#            | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x"
#            | "y" | "z"

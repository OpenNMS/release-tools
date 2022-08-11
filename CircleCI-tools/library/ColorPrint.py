import re


class ColorPrint:
    styles={
        "normal"    : "0",
        "bold"      : "1",
        "light"     : "2",
        "italic"    : "3",
        "underlined": "4",
        "blink"     : "5"
    }
    colors={
        "black" : "30",
        "red"   : "31",
        "green" : "32",
        "yellow": "33",
        "blue"  : "34",
        "purple": "35",
        "cyan"  : "36",
        "white" : "37"
    }

    background_colors={
        "black" : "40",
        "red"   : "41",
        "green" : "42",
        "yellow": "43",
        "blue"  : "44",
        "purple": "45",
        "cyan"  : "46",
        "white" : "47",
    }
    def __init__(self) -> None:
        pass

    def print1(self,msg,token="#"):
        _tokens=re.findall("\{(.*?)\}",msg)


        for _t in _tokens:
            default=self.styles["normal"]
            defaultcolor=self.colors["white"]
            defaultbackground=self.background_colors["black"]
            for _t1 in _t.split(","):
                if "style" in _t1:
                    _t1=_t1.replace("style:","")
                    default=self.styles[_t1]
                elif "background" in _t1:
                    _t1=_t1.replace("background:","")
                    defaultbackground=self.background_colors[_t1]
                if "color" in _t1:
                    _t1=_t1.replace("color:","")
                    if "reset" in _t1:
                        defaultcolor=self.colors["white"]
                    else:
                        defaultcolor=self.colors[_t1]
            msg=msg.replace("{"+_t+"}","\033["+default+";"+defaultcolor+";"+defaultbackground+"m")

        return msg
    @staticmethod
    def print(msg):
        ourColor={
        "#darkred#"   : '\033[31m',
        "#darkgreen#"   : '\033[32m',
        "#darkyellow#"   : '\033[33m',
        "#darkblue#"   : '\033[34m',
        "#darkmagenta#"   : '\033[35m',
        "#darkcyan#"   : '\033[36m',
        "#gray#"   : '\033[37m',
        "#red#"   : '\033[91m',
        "#green#"   : '\033[92m',
        "#yellow#"   : '\033[93m',
        "#blue#"   : '\033[94m',
        "#magenta#"   : '\033[95m',
        "#cyan#"   : '\033[96m',
        "#white#"   : '\033[97m',
        "#end#"    : '\033[0m',
        "#nocolor#": '\x1b[0m',
        '#bold#':'\033[1m'
    } 
        for key in ourColor:
            msg=msg.replace(key,ourColor[key])
        print(msg)
        

if (__name__=="__main__"):
    _coloroutput=ColorPrint()
   # _coloroutput.print("Hi #blue#my#end# name is #red#Morteza#end#")
    #_coloroutput.print1("Hi {color:blue,style:bold}my{color:reset} name is {color:red}Morteza{reset} and")
    print(_coloroutput.print1(u"{style:underlined,color:green,background:black}\N{check mark}{color:reset}\U0001F602"+"I did the work....\N{grinning face}\N{upside-down face}\N{face screaming in fear}"))
#    ColorPrint.print("""
#    #darkred#1 2 3 4 5 6 7 8 9 10
#    #red#1 2 3 4 5 6 7 8 9 10
#    #darkyellow#1 2 3 4 5 6 7 8 9 10
#    #yellow#1 2 3 4 5 6 7 8 9 10
#    #darkblue#1 2 3 4 5 6 7 8 9 10
#    #blue#1 2 3 4 5 6 7 8 9 10
#    #darkmagenta#1 2 3 4 5 6 7 8 9 10
#    #magenta#1 2 3 4 5 6 7 8 9 10
#    #darkcyan#1 2 3 4 5 6 7 8 9 10
#    #cyan#1 2 3 4 5 6 7 8 9 10
#    #darkgreen#1 2 3 4 5 6 7 8 9 10
#    #green#1 2 3 4 5 6 7 8 9 10
#    #gray#1 2 3 4 5 6 7 8 9 10
#    #white#1 2 3 4 5 6 7 8 9 10
#    #nocolor#1 2 3 4 5 6 7 8 9 10
#""")
#
#print('\033[2;31;43m CHEESY \033[0;0m')
#print("\033[48;5;236m\033[38;5;231mStack \033[38;5;208mAbuse\033[0;0m")
#
#def colors_16(color_):
#    return("\033[0;{num}m {num} \033[0;0m".format(num=str(color_)))
#
#
#def colors_256(color_):
#    num1 = str(color_)
#    num2 = str(color_).ljust(3, ' ')
#    if color_ % 16 == 0:
#        return(f"\033[38;5;{num1}m {num2} \033[0;0m\n")
#    else:
#        return(f"\033[38;5;{num1}m {num2} \033[0;0m")
#
#print("The 16 colors scheme is:")
#print(' '.join([colors_16(x) for x in range(90, 98)]))
#print("\nThe 256 colors scheme is:")
#print(' '.join([colors_256(x) for x in range(256)]))
#
#
#import curses
#curses.setupterm()
#print(curses.tigetnum("colors"))


    _emoticon={"grinning face":"\U0001F600",
    "grinning face with big eyes":"\U0001F603",
    "grinning face with smiling eyes":"\U0001F604",
    "beaming face with smiling eyes":"\U0001F601",
    "grinning squinting face":"\U0001F606",
    "grinning face with sweat":"\U0001F605",
    "rolling on the floor laughing":"\U0001F923",
    "face with tears of joy":"\U0001F602",
    "slightly smiling face":"\U0001F642",
    "upside-down face":"\U0001F643",
    "winking face":"\U0001F609",
    "smiling face with smiling eyes":"\U0001F60A",
    "smiling face with halo":"\U0001F607",
    "smiling face with 3 hearts":"\U0001F970",
    "smiling face with heart-eyes":"\U0001F60D",
    "star-struck":"\U0001F929",
    "face blowing a kiss":"\U0001F618",
    "kissing face":"\U0001F617",
    "kissing face with closed eyes":"\U0001F61A",
    "kissing face with smiling eyes":"\U0001F619",
    "face savoring food":"\U0001F60B",
    "face with tongue":"\U0001F61B",
    "winking face with tongue":"\U0001F61C",
    "zany face":"\U0001F92A",
    "squinting face with tongue":"\U0001F61D",
    "money-mouth face":"\U0001F911",
    "hugging face":"\U0001F917",
    "face with hand over mouth":"\U0001F92D",
    "shushing face":"\U0001F92B",
    "thinking face":"\U0001F914",
    "zipper-mouth face":"\U0001F910",
    "face with raised eyebrow":"\U0001F928",
    "neutral face":"\U0001F610",
    "expressionless face":"\U0001F611",
    "face without mouth":"\U0001F636",
    "smirking face":"\U0001F60F",
    "unamused face":"\U0001F612",
    "face with rolling eyes":"\U0001F644",
    "grimacing face":"\U0001F62C",
    "lying face":"\U0001F925",
    "relieved face":"\U0001F60C",
    "pensive face":"\U0001F614",
    "sleepy face":"\U0001F62A",
    "drooling face":"\U0001F924",
    "sleeping face":"\U0001F634",
    "face with medical mask":"\U0001F637",
    "face with thermometer":"\U0001F912",
    "face with head-bandage":"\U0001F915",
    "nauseated face":"\U0001F922"}

    _t=""
    for _e in _emoticon:
        _t+=_emoticon[_e]+"\t"

    print(_t)
    print("🥹 🍌 🥱")

    print("gathering data....✅")
    print("gathering data....✔ ❎")
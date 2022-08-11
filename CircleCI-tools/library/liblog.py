from library import ColorPrint

class liblog:
    def __init__(self,no_colors=False):
        self.colorPrint=ColorPrint.ColorPrint()
    
    def error(self,message,no_colors=False,use_same_color=False,prefix=""):
        if not prefix:
            prefix="Error"
            
        if no_colors:
            if type(message) != str:
                self._print("["+prefix+"] "+str(message))
            else:
                self._print("["+prefix+"] "+message)
        else:
            if use_same_color:
                self._print("#red#["+prefix+"] "+str(message)+"#end#")
            else:
                if type(message) != str:
                    self._print("#red#["+prefix+"]#end# "+str(message))
                else:
                    self._print("#red#["+prefix+"]#end# "+message)
        

    def info(self,message,no_colors=False,use_same_color=False,prefix=""):
        if not prefix:
            prefix="Info"
            
        if no_colors:
            if type(message) != str:
                self._print("["+prefix+"] "+str(message))
            else:
                self._print("["+prefix+"] "+message)
        else:
            if use_same_color:
                self._print("#blue#["+prefix+"] "+str(message)+"#end#")
            else:
                if type(message) != str:
                    self._print("#blue#["+prefix+"]#end# "+str(message))
                else:
                    self._print("#blue#["+prefix+"]#end# "+message)
                

    def warning(self,message,no_colors=False,use_same_color=False,prefix=""):
        if not prefix:
            prefix="Warning"
            
        if no_colors:
            if type(message) != str:
                self._print("["+prefix+"] "+str(message))
            else:
                self._print("["+prefix+"] "+message)
        else:
            if use_same_color:
                self._print("#yellow#["+prefix+"] "+str(message)+"#end#")
            else:
                if type(message) != str:
                    self._print("#yellow#["+prefix+"]#end# "+str(message))
                else:
                    self._print("#yellow#["+prefix+"]#end# "+message)

    def success(self,message,no_colors=False,use_same_color=False,prefix=""):
        if not prefix:
            prefix="Success"
            
        if no_colors:
            if type(message) != str:
                self._print("["+prefix+"] "+str(message))
            else:
                self._print("["+prefix+"] "+message)
        else:
            if use_same_color:
                self._print("#green#["+prefix+"] "+str(message)+"#end#")
            else:
                if type(message) != str:
                    self._print("#green#["+prefix+"]#end# "+str(message))
                else:
                    self._print("#green#["+prefix+"]#end# "+message)


    def print(self,message):
        self._print(message)

    def _print(self,message):
        self.colorPrint.print(message)
        
        

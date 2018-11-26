class AdmRawException(Exception):  # pragma: no cover
    
    def __init__(self, message):
        self.message = message
    
    
    def __str__(self):
        return "WIMS' server responded with an ERROR: " + self.message

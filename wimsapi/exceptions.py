class AdmRawException(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str(self):
        return "ERROR: " + self.message
    
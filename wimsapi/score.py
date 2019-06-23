class ExoScore:
    
    def _init__(self, user, weight, quality, cumul, success, acquis, last):
        self.user = user
        self.weight = weight
        self.quality = quality   # adm/raw 'mean'
        self.cumul = cumul
        self.success = success
        self.acquis = acquis
        self.last = last



class SheetScore:
    
    def _init__(self, user, sheet, quality, cumul, success, acquis, last):
        self.user = user
        self.sheet = sheet
        self.weight = sheet.weight
        self.quality = quality
        self.cumul = cumul
        self.success = success  # adm/raw 'best'
        self.acquis = acquis

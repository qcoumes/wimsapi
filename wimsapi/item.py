from abc import ABC, abstractmethod



class ClassItemABC(ABC):  # pragma: no cover
    """Allow to implement any kind of item of a WIMS class without the need
    of actually modifying wimsapi.class.Class."""
    
    
    @classmethod
    @abstractmethod
    def check(cls, wclass, item):
        """Returns True if item is in wclass, False otherwise.
        
        Item can be either an instance of the corresponding item, or
        string corresponding to the identifier of the item in wclass.
        
        E.G. either SubClass.check(wclass, "identifier") or
        SubClass.check(wclass, SubClass(...))"""
        pass
    
    
    @classmethod
    @abstractmethod
    def remove(cls, wclass, item):
        """Deletes item from wclass.

        Item can be either an instance of the corresponding item, or
        string corresponding to the identifier of the item in wclass.

        E.G. either SubClass.remove(wclass, "identifier") or
        SubClass.remove(wclass, SubClass(...))"""
        pass
    
    
    @classmethod
    @abstractmethod
    def get(cls, wclass, identifier):
        """Returns an instance of cls corresponding to the item identified with
        identifier in wclass."""
        pass
    
    
    @abstractmethod
    def save(self, wclass, check_exists=True):
        """Saves this item in wclass.
        
        If check_exists is True, the api will check if an item with the same ID
        exists on the WIMS' server. If it exists, save will instead modify this
        item instead of trying to create new one."""
        pass
    
    
    @classmethod
    @abstractmethod
    def list(cls, wclass):
        """List every item from wclass."""
        pass

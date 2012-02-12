"""
Modul for å samle kode relatert til importering av data fra
nettbankens kontoutskrifter
"""


class Import(Object):
    """Collection of procedures for importing data from bank records"""
    
    def __init__(self,filename):
        self.filename = filename
        """Name of the file"""
        
    def readDNB(self, filename):
        pass
        
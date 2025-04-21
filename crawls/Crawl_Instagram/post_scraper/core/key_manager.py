class APIKeyManager:
    def __init__(self, keys):
        self.keys = keys
        self.index = 0
    
    def get(self):
        return self.keys[self.index]
    
    def switch(self):
        self.index = (self.index + 1) % len(self.keys)
        return self.get()
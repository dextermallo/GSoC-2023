from abc import ABC, abstractmethod

class Test(ABC):
    id: str
    
    
class Car(Test):
    def __init__(self, id):
        self.id = id
        
    def __str__(self):
        return f"Car {self.id}"
    
class Bike(Test):
    def __init__(self, id):
        self.id = id
        
    def __str__(self):
        return f"Bike {self.id}"


l = [Car(1), Bike(2)]

    
def fn(t: Test):
    print(t.id)
    
for t in l:
    fn(t)
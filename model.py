from dataclasses import dataclass
from typing import Optional
from datetime import date
from typing import List


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self.purchased_quantity = qty
        self._allocations = set()

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference
    
    def __gt__(self, other):          # useful
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta
    
    def __hash__(self):
        return hash(self.reference)
        

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):                   # dont have to worry about duplicates because we are using a set
            self._allocations.add(line) 

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine):
        return self.sku == line.sku and self.available_quantity >= line.qty
    
    @property
    def allocated_quantity(self)  -> int:
        return sum(line.qty for line in self._allocations)
    
    @property
    def available_quantity(self) -> int:
        return self.purchased_quantity - self.allocated_quantity
    

def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))        # sorted() can be used because we defined `__gt__` and it is based on eta of batches
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {line.sku}')            


class OutOfStock(Exception):
    pass

# allocate() is a service that doesnt know the logic in Batch.
#               It only knows how to use the batch method .allocate() and sorts batch
#               It basically asks "Hey Batch, can you take this OrderLine?"
#
#               This is also an example of how not everything needs to be an object
#               since allocate() is a function that accomplishes the same thing someone mightve used an object for

# Batch: holds all of the logic for checking availability and skus.
#       It decides if the line is valid for itself and if there is enough availability

# OrderLine is a simple Value Object that just hodls data at the bottom of the chain.

# [allocate()] --> Batch --> OrderLine means "Services coordinate Entities --> entities manage Value Objects"



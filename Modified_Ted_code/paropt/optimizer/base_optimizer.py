# from collections.abc import Iterable
from abc import abstractmethod

class BaseOptimizer():
  @abstractmethod
  def suggest():
    pass
  
  @abstractmethod
  def update():
    pass
  
  @abstractmethod
  def getResult():
    pass

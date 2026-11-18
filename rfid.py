from abc import ABC,abstractmethod
class RFIDAdapter(ABC):
 @abstractmethod
 def read_tags(self)->list[str]: ...
class SimulatedRFIDAdapter(RFIDAdapter):
 """Desenvolvimento/teste somente; não se conecta a um leitor."""
 def read_tags(self)->list[str]: return []
# Adaptador real futuro: implementar transporte/SDK/API documentados pelo fabricante;
# mapear leituras, validar leitor e tratar eventos sem declarar rastreamento contínuo.

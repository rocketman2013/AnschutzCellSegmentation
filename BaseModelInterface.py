from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def load_images(self, *args, **kwargs):
        pass

    @abstractmethod
    def segment_channels(self, *args, **kwargs):
        pass

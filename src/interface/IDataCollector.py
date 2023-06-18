from abc import ABC, abstractmethod


class IDataCollector(ABC):
    """_summary_
    @TODO: doc
    IDataCollector is an interface for data collector,
    tt is used to read data from a source and store it in a database.
    extend this class to implement your own data collector.
    
    """

    @abstractmethod
    def read_data(self):
        raise NotImplementedError
    
    @abstractmethod
    def store_raw_data(self):
        raise NotImplementedError

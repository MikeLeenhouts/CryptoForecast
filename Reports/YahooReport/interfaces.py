"""Interface definitions for Yahoo Finance data classes."""

from abc import ABC, abstractmethod

class IYahooData(ABC):
    """Abstract base class for Yahoo Finance data retrieval."""
    
    @abstractmethod
    def to_csv(self, path=None, sep=',', data_format=None, csv_dialect='excel'):
        """Export data to CSV format."""
        pass
    
    @abstractmethod
    def to_dfs(self, data_format=None):
        """Export data to pandas DataFrame format."""
        pass

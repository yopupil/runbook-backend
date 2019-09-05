# coding: utf8

__author__ = 'Tharun Mathew Paul (tharun@bigpiventures.com)'


class NotebookService:
    """Service that is responsible for saving notebooks

    Parameters
    ----------
    adapter: NotebookServiceAdapter
        An adapter that is responsible for saving the notebooks. If omitted,
        it defaults to FileAdapter, which saves the notebooks to disk.
    """
    def __init__(self, adapter):
        self.adapter = adapter or FileAdapter()

    def create(self, payload):
        """Create a new notebook using payload arguments"""
        # Validate payload using

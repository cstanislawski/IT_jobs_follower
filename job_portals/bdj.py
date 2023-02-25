"""
Module for handling bulldogjob (https://bulldogjob.pl/) offers tracker.
"""


class BullDogJob:  # pylint: disable=R0903
    """
    Class processing data from bulldogjob sites.
    """

    def __init__(self):
        self.content = ""

    def load_offers(self):
        """
        Loads all the offers present in data_sources, searches pages matching search_regex
        """
        print(self.content)

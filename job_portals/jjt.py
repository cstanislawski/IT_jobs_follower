"""
Module for handling JustJoinIT (https://justjoin.it/?tab=with-salary) offers tracker.
"""


class JustJoinIT:  # pylint: disable=R0903
    """
    Class processing data from JustJoinIT sites.
    """

    def __init__(self):
        self.content = ""

    def load_offers(self):
        """
        Loads all the offers present in data_sources, searches pages matching search_regex
        """
        print(self.content)

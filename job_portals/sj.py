"""
Module for handling JustJoinIT (https://solid.jobs/offers/it) offers tracker.
"""


class SolidJobs:  # pylint: disable=R0903
    """
    Class processing data from solid.jobs sites.
    """

    def __init__(self):
        self.content = ""

    def load_offers(self):
        """
        Loads all the offers present in data_sources, searches pages matching search_regex
        """
        print(self.content)

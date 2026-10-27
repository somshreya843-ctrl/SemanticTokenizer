from .geonames import GeoNamesProvider
from .github import GitHubProvider
from .imdb import IMDbProvider
from .openlibrary import OpenLibraryProvider
from .wikidata import WikidataProvider
from .fao import FAOProvider
from .dictionary import DictionaryProvider
from .local_file import LocalFileProvider


class ProviderRegistry:

    _providers = {
        "geonames": GeoNamesProvider(),
        "github": GitHubProvider(),
        "imdb": IMDbProvider(),
        "openlibrary": OpenLibraryProvider(),
        "wikidata": WikidataProvider(),
        "fao": FAOProvider(),
        "dictionary": DictionaryProvider(),
        "local_file": LocalFileProvider(),
    }

    @classmethod
    def get_provider(cls, name: str):

        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")

        return cls._providers[name]
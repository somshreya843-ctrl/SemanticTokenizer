from entities.builder import EntityBuilder
from entities.sources import SOURCES

for source in SOURCES.values():
    builder = EntityBuilder(source)
    builder.build()
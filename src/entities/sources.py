from .config import EntitySource
from .categories import (
    GEOGRAPHY,
    BIOLOGY,
    ENTERTAINMENT,
    SCIENCE,
    MEDICINE,
    FOOD,
    LANGUAGE,
    SPORTS,
    BUSINESS,
    EDUCATION,
    TECHNOLOGY,
    HISTORY,
    FINANCE,
    AGRICULTURE,
)


SOURCES = {

    "country": EntitySource(
        name="country",
        category=GEOGRAPHY,
        provider="github",
        identifier="iso_countries",
        column="name",
        #output="data/entities/geography/country.txt",
    ),

    "city": EntitySource(
        name="city",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="cities15000",
        column="name",
        #output="data/entities/geography/city.txt",
    ),

    "continent": EntitySource(
        name="continent",
        category=GEOGRAPHY,
        provider="github",
        identifier="continents",
        column="name",
    ),

    "river": EntitySource(
        name="river",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="H",
        feature_code="STM",   # or RIV if that's the code you want
        column="name",
    ),

    "mountain": EntitySource(
        name="mountain",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="T",
        feature_code="MT",
        column="name",
    ),

    "lake": EntitySource(
        name="lake",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="H",
        feature_code="LK",
        column="name",
    ),

    "airport": EntitySource(
        name="airport",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="S",
        feature_code="AIRP",
        column="name",
    ),

    "museum": EntitySource(
        name="museum",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="S",
        feature_code="MUS",
        column="name",
    ),

    "hospital": EntitySource(
        name="hospital",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="S",
        feature_code="HSP",
        column="name",
    ),

    "school": EntitySource(
        name="school",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="S",
        feature_code="SCH",
        column="name",
    ),

    "university": EntitySource(
        name="university",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="S",
        feature_code="UNIV",
        column="name",
    ),

    "bridge": EntitySource(
        name="bridge",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="S",
        feature_code="BDG",
        column="name",
    ),

    "dam": EntitySource(
        name="dam",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="S",
        feature_code="DAM",
        column="name",
    ),

    "park": EntitySource(
        name="park",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="L",
        feature_code="PRK",
        column="name",
    ),

    "forest": EntitySource(
        name="forest",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="V",
        feature_code="FRST",
        column="name",
    ),

    "island": EntitySource(
        name="island",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="T",
        feature_code="ISL",
        column="name",
    ),

    "railway_station": EntitySource(
        name="railway_station",
        category=GEOGRAPHY,
        provider="geonames",
        identifier="allCountries",
        country_code="IN",
        feature_class="S",
        feature_code="RSTN",
        column="name",
    ),

    "movie": EntitySource(
        name="movie",
        category=ENTERTAINMENT,
        provider="imdb",
        identifier="movies",
        column="name",
    ),

    "actor": EntitySource(
        name="actor",
        category=ENTERTAINMENT,
        provider="imdb",
        identifier="actors",
        column="name",
    ),

    "director": EntitySource(
        name="director",
        category=ENTERTAINMENT,
        provider="imdb",
        identifier="directors",
        column="name",
    ),

    "writer": EntitySource(
        name="writer",
        category=ENTERTAINMENT,
        provider="imdb",
        identifier="writers",
        column="name",
    ),

    "producer": EntitySource(
        name="producer",
        category=ENTERTAINMENT,
        provider="imdb",
        identifier="producers",
        column="name",
    ),

    "composer": EntitySource(
        name="composer",
        category=ENTERTAINMENT,
        provider="imdb",
        identifier="composers",
        column="name",
    ),

    "cinematographer": EntitySource(
        name="cinematographer",
        category=ENTERTAINMENT,
        provider="imdb",
        identifier="cinematographers",
        column="name",
    ),

    "editor": EntitySource(
        name="editor",
        category=ENTERTAINMENT,
        provider="imdb",
        identifier="editors",
        column="name",
    ),

    # "language": EntitySource(
    #     name="language",
    #     category=LANGUAGE,
    #     provider="github",
    #     identifier="languages",
    #     column="name",
    # ),

    # "currency": EntitySource(
    #     name="currency",
    #     category="finance",
    #     provider="github",
    #     identifier="currencies",
    #     column="name",
    # ),

    # "chemical_element": EntitySource(
    #     name="chemical_element",
    #     category="science",
    #     provider="github",
    #     identifier="chemical_elements",
    #     column="name",
    # ),

    # "programming_language": EntitySource(
    #     name="programming_language",
    #     category="technology",
    #     provider="github",
    #     identifier="programming_languages",
    #     column="name",
    # ),

    # "book": EntitySource(
    #     name="book",
    #     category=ENTERTAINMENT,
    #     provider="openlibrary",
    #     identifier="books",
    #     column="name",
    # ),

    # "author": EntitySource(
    #     name="author",
    #     category=ENTERTAINMENT,
    #     provider="openlibrary",
    #     identifier="authors",
    #     column="name",
    # ),

    # "publisher": EntitySource(
    #     name="publisher",
    #     category=ENTERTAINMENT,
    #     provider="openlibrary",
    #     identifier="publishers",
    #     column="name",
    # ),

    "language": EntitySource(
        name="language",
        category=LANGUAGE,
        provider="wikidata",
        identifier="languages",
        column="name",
    ),

    "currency": EntitySource(
        name="currency",
        category=FINANCE,
        provider="wikidata",
        identifier="currencies",
        column="name",
    ),

    "chemical_element": EntitySource(
        name="chemical_element",
        category=SCIENCE,
        provider="wikidata",
        identifier="chemical_elements",
        column="name",
    ),

    "programming_language": EntitySource(
        name="programming_language",
        category=TECHNOLOGY,
        provider="wikidata",
        identifier="programming_languages",
        column="name",
    ),

    "software": EntitySource(
        name="software",
        category=TECHNOLOGY,
        provider="wikidata",
        identifier="software",
        column="name",
    ),

    "smartphone": EntitySource(
        name="smartphone",
        category=TECHNOLOGY,
        provider="wikidata",
        identifier="smartphone",
        column="name",
    ),

    "disease": EntitySource(
        name="disease",
        category=MEDICINE,
        provider="wikidata",
        identifier="diseases",
        column="name",
    ),

    "medicine": EntitySource(
        name="medicine",
        category=MEDICINE,
        provider="wikidata",
        identifier="medicines",
        column="name",
    ),

    "company": EntitySource(
        name="company",
        category=BUSINESS,
        provider="wikidata",
        identifier="companies",
        column="name",
    ),

    "compound": EntitySource(
        name="compound",
        category=SCIENCE,
        provider="wikidata",
        identifier="compounds",
        column="name",
    ),

    "metal": EntitySource(
        name="metal",
        category=SCIENCE,
        provider="wikidata",
        identifier="metals",
        column="name",
    ),

    "non_metal": EntitySource(
        name="non_metal",
        category=SCIENCE,
        provider="wikidata",
        identifier="non_metals",
        column="name",
    ),

    "gas": EntitySource(
        name="gas",
        category=SCIENCE,
        provider="wikidata",
        identifier="gases",
        column="name",
    ),

    "mineral": EntitySource(
        name="mineral",
        category=SCIENCE,
        provider="wikidata",
        identifier="minerals",
        column="name",
    ),

    "acid": EntitySource(
        name="acid",
        category=SCIENCE,
        provider="wikidata",
        identifier="acids",
        column="name",
    ),

    "base": EntitySource(
        name="base",
        category=SCIENCE,
        provider="wikidata",
        identifier="bases",
        column="name",
    ),

    "salt": EntitySource(
        name="salt",
        category=SCIENCE,
        provider="wikidata",
        identifier="salts",
        column="name",
    ),

    "polymer": EntitySource(
        name="polymer",
        category=SCIENCE,
        provider="wikidata",
        identifier="polymers",
        column="name",
    ),

    "symptom": EntitySource(
        name="symptom",
        category=MEDICINE,
        provider="wikidata",
        identifier="symptoms",
        column="name",
    ),

    "medical_procedure": EntitySource(
        name="medical_procedure",
        category=MEDICINE,
        provider="wikidata",
        identifier="medical_procedures",
        column="name",
    ),

    "diagnostic_test": EntitySource(
        name="diagnostic_test",
        category=MEDICINE,
        provider="wikidata",
        identifier="diagnostic_tests",
        column="name",
    ),

    "vaccine": EntitySource(
        name="vaccine",
        category=MEDICINE,
        provider="wikidata",
        identifier="vaccines",
        column="name",
    ),

    "crop": EntitySource(
        name="crop",
        category="agriculture",
        provider="fao",
        identifier="crops",
        column="name",
    ),

    "fertilizer": EntitySource(
        name="fertilizer",
        category="agriculture",
        provider="wikidata",
        identifier="fertilizers",
        column="name",
    ),

    "pesticide": EntitySource(
        name="pesticide",
        category="agriculture",
        provider="wikidata",
        identifier="pesticides",
        column="name",
    ),

    "herbicide": EntitySource(
        name="herbicide",
        category="agriculture",
        provider="wikidata",
        identifier="herbicides",
        column="name",
    ),

    "nutrient": EntitySource(
        name="nutrient",
        category="agriculture",
        provider="wikidata",
        identifier="nutrients",
        column="name",
    ),

    "farm_equipment": EntitySource(
        name="farm_equipment",
        category="agriculture",
        provider="wikidata",
        identifier="farm_equipment",
        column="name",
    ),

    "english_word": EntitySource(
        name="english_word",
        category="language",
        provider="dictionary",
        identifier="data/dictionary/english.txt",
        column="name",
    ),

    "person": EntitySource(
        name="person",
        category="people",
        provider="local_file",
        identifier="data/dictionary_candidates/person_final.txt",
        column="name",
    ),

    "animal": EntitySource(
        name="animal",
        category="biology",
        provider="local_file",
        identifier="data/dictionary_candidates/animal_final.txt",
        column="name",
    ),

    "plant": EntitySource(
        name="plant",
        category="biology",
        provider="local_file",
        identifier="data/dictionary_candidates/plant_final.txt",
        column="name",
    ),

    "food": EntitySource(
        name="food",
        category="food",
        provider="local_file",
        identifier="data/dictionary_candidates/food_final.txt",
        column="name",
    ),

    "body_part": EntitySource(
        name="body_part",
        category="biology",
        provider="local_file",
        identifier="data/dictionary_candidates/body_part_final.txt",
        column="name",
    ),

    "group": EntitySource(
        name="group",
        category="group",
        provider="local_file",
        identifier="data/dictionary_candidates/group_final.txt",
        column="name",
    ),

    "attribute": EntitySource(
        name="attribute",
        category="attribute",
        provider="local_file",
        identifier="data/dictionary_candidates/attribute_final.txt",
        column="name",
    ),

    "concept": EntitySource(
        name="concept",
        category="concept",
        provider="local_file",
        identifier="data/dictionary_candidates/concept_final.txt",
        column="name",
    ),

    "object": EntitySource(
        name="object",
        category="object",
        provider="local_file",
        identifier="data/dictionary_candidates/object_final.txt",
        column="name",
    ),

    "quantity": EntitySource(
        name="quantity",
        category="quantity",
        provider="local_file",
        identifier="data/dictionary_candidates/quantity_final.txt",
        column="name",
    ),

    "event": EntitySource(
        name="event",
        category="event",
        provider="local_file",
        identifier="data/dictionary_candidates/event_final.txt",
        column="name",
    ),

    "possession": EntitySource(
        name="possession",
        category="possession",
        provider="local_file",
        identifier="data/dictionary_candidates/possession_final.txt",
        column="name",
    ),

    "time": EntitySource(
        name="time",
        category="time",
        provider="local_file",
        identifier="data/dictionary_candidates/time_final.txt",
        column="name",
    ),

    "phenomenon": EntitySource(
        name="phenomenon",
        category="phenomenon",
        provider="local_file",
        identifier="data/dictionary_candidates/phenomenon_final.txt",
        column="name",
    ),

    "relation": EntitySource(
        name="relation",
        category="relation",
        provider="local_file",
        identifier="data/dictionary_candidates/relation_final.txt",
        column="name",
    ),

    "feeling": EntitySource(
        name="feeling",
        category="feeling",
        provider="local_file",
        identifier="data/dictionary_candidates/feeling_final.txt",
        column="name",
    ),

    "shape": EntitySource(
        name="shape",
        category="shape",
        provider="local_file",
        identifier="data/dictionary_candidates/shape_final.txt",
        column="name",
    ),

    "motive": EntitySource(
        name="motive",
        category="motive",
        provider="local_file",
        identifier="data/dictionary_candidates/motive_final.txt",
        column="name",
    ),

    

}
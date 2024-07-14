from util import (
    create_database_tables,
    create_django_project
)
import sys
import json

if __name__ == "__main__":
    input_data = json.loads(sys.argv[1])
    entities_with_attr = input_data.get("entities_with_attr")
    entities_with_pks = input_data.get("entities_with_pks")
    relationships = input_data.get("relationships")

    # Ensure relationships are tuples
    relationships = [tuple(relationship) for relationship in relationships]

    create_database_tables(entities_with_attr, entities_with_pks, relationships)
    create_django_project()

    print("Data processed successfully.")

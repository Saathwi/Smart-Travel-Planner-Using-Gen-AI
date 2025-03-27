import csv
import json
from pprint import pprint


def create_airport_mapping(csv_file):
    """Create airport mapping dictionary from CSV file with extensive error handling"""
    airport_mapping = {}
    skipped_entries = 0
    created_entries = 0

    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            # Try to detect dialect if standard csv.reader fails
            try:
                dialect = csv.Sniffer().sniff(file.read(1024))
                file.seek(0)
                reader = csv.DictReader(file, dialect=dialect)
            except:
                file.seek(0)
                reader = csv.DictReader(file)

            # Verify required columns exist
            required_columns = {'iata_code', 'name'}
            if not required_columns.issubset(set(reader.fieldnames)):
                missing = required_columns - set(reader.fieldnames)
                raise ValueError(f"CSV missing required columns: {missing}")

            for row_num, row in enumerate(reader, 1):
                try:
                    # Skip airports without IATA codes
                    if not row.get('iata_code'):
                        skipped_entries += 1
                        continue

                    # Clean and standardize data
                    city_name = row['municipality'].lower().strip() if row['municipality'] else ''
                    airport_name = row['name'].lower().strip() if row['name'] else ''
                    iata_code = row['iata_code'].strip().upper()

                    if not city_name and not airport_name:
                        skipped_entries += 1
                        continue

                    entry = {
                        'iata': iata_code,
                        'name': row['name']
                    }

                    # Add multiple access point
                    added = False
                    for key in [city_name, airport_name]:
                        if key and key not in airport_mapping:
                            airport_mapping[key] = entry
                            added = True

                    if added:
                        created_entries += 1
                    else:
                        skipped_entries += 1

                except Exception as e:
                    print(f"Error processing row {row_num}: {str(e)}")
                    print(f"Problematic row: {row}")
                    skipped_entries += 1
                    continue

            # Add common city aliases
            common_aliases = {
                'new delhi': ['delhi', 'ncr', 'national capital region'],
                'bangalore': ['bengaluru', 'bengalooru'],
                'chennai': ['madras'],
                'kolkata': ['calcutta', 'calcuta'],
                'mumbai': ['bombay', 'bambai'],
                'goa': ['vasco da gama', 'dabolim', 'panaji', 'panjim'],
                'hyderabad': ['secunderabad'],
                'pune': ['poonaw']
            }

            for primary_name, aliases in common_aliases.items():
                if primary_name in airport_mapping:
                    for alias in aliases:
                        if alias not in airport_mapping:
                            airport_mapping[alias] = airport_mapping[primary_name]
                            created_entries += 1

    except Exception as e:
        print(f"Fatal error processing CSV: {str(e)}")
        return None

    print(f"\nMapping creation summary:")
    print(f"- Successfully processed entries: {created_entries}")
    print(f"- Skipped entries: {skipped_entries}")
    print(f"- Total mappings created: {len(airport_mapping)}")

    return airport_mapping


if __name__ == "__main__":
    input_file = 'flights data.csv'
    output_file = 'airport_mapping.json'

    print(f"Creating airport mapping from {input_file}...")
    mapping = create_airport_mapping(input_file)

    if mapping:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
            print(f"\nSuccessfully saved mapping to {output_file}")

            # Print sample of the mapping
            print("\nSample entries:")
            sample_keys = list(mapping.keys())[:5]
            for key in sample_keys:
                print(f"{key}: {mapping[key]}")

        except Exception as e:
            print(f"Error saving JSON file: {str(e)}")
    else:
        print("Failed to create airport mapping.")
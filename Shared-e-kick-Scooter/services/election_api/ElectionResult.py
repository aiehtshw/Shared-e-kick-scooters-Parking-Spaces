import pandas as pd
import json

def process_population_data(input_file, json_file):
    """
    Processes population data from an Excel file and updates an existing JSON file.
    """
    try:
        # Load Excel File
        data = pd.ExcelFile(input_file)
        df = data.parse(data.sheet_names[0], skiprows=9)
        df = df.iloc[:, :6]
        df.columns = ['Sıra No', 'İl Adı', 'İlçe Adı', 'Mahalle/Köy', 'Sandık No', 'Kayıtlı Seçmen Sayısı']

        df['Kayıtlı Seçmen Sayısı'] = pd.to_numeric(df['Kayıtlı Seçmen Sayısı'], errors='coerce')
        population_by_neighborhood = df.groupby('Mahalle/Köy')['Kayıtlı Seçmen Sayısı'].sum().reset_index()
        population_by_neighborhood.columns = ['Mahalle', 'Toplam Nüfus']
        population_by_neighborhood = population_by_neighborhood[population_by_neighborhood['Toplam Nüfus'] > 0]

        # Load the existing JSON file
        with open(json_file, "r", encoding="utf-8") as f:
            neighborhood_data = json.load(f)

        # Update the JSON data with real population data
        updated_data = []
        for _, row in population_by_neighborhood.iterrows():
            updated_data.append({
                "neighbourhood": row['Mahalle'],
                "latitude": None,
                "longitude": None,
                "population": row['Toplam Nüfus'],
                "poi_number": 0,
                "pois": [],
                "bus_station_number": 0,
                "bus_stations": [],
                "metro_station_number": 0,
                "metro_stations": []
            })

        # Save the updated JSON
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)

        print(f"Updated JSON saved: {json_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


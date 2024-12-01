import pandas as pd
import json

from services.localize_char.LocalizeChar import tr_upper


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
                "latitude": get_long_lat_by_neighbourhood(row['Mahalle'])[1],
                "longitude": get_long_lat_by_neighbourhood(row['Mahalle'])[0],
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


def get_long_lat_by_neighbourhood(neighbourhood):
    """
    Returns the longitude and latitude for a given neighbourhood (neighborhood).

    Parameters:
        neighbourhood (str): The name of the neighborhood.

    Returns:
        tuple: A tuple of (longitude, latitude) or None if no match is found.
    """
    match tr_upper(neighbourhood):
        case "19 MAYIS MAH.":
            return 29.088955, 40.973511
        case "ACIBADEM MAH.":
            return 29.038741, 41.001781
        case "BOSTANCI MAH.":
            return 29.095764, 40.957852
        case "CADDEBOSTAN MAH.":
            return 29.061369, 40.962856
        case "CAFERAĞA MAH.":
            return 29.0248102, 40.9850403
        case "DUMLUPINAR MAH.":
            return 29.05974, 40.99297,
        case "ERENKÖY MAH.":
            return 32.608181, 35.179008
        case "EĞİTİM MAH.":
            return 29.049488, 40.989437
        case "FENERBAHÇE MAH.":
            return 29.043537, 40.974454
        case "FENERYOLU MAH.":
            return 29.049548, 40.982013
        case "FİKİRTEPE MAH.":
            return 29.050432, 40.993729
        case "GÖZTEPE MAH.":
            return 29.062640, 40.977171
        case "HASANPAŞA MAH.":
            return 29.044654, 40.996225
        case "KOZYATAĞI MAH.":
            return 29.095792, 40.968948
        case "KOŞUYOLU MAH.":
            return 29.034666, 41.006589
        case "MERDİVENKÖY MAH.":
            return 29.069109, 40.987681
        case "OSMANAĞA MAH.":
            return 29.029933, 40.988172
        case "RASİMPAŞA MAH.":
            return 29.025539, 40.996897
        case "SAHRAYICEDİT MAH.":
            return 29.086509, 40.982849
        case "SUADİYE MAH.":
            return 29.081574, 40.961046
        case "ZÜHTÜPAŞA MAH.":
            return 29.038801, 40.986532
        case _:
            return None  # Return None if the neighbourhood does not match any case

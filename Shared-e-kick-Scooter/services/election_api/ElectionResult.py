import pandas as pd

def process_population_data(input_file, output_file):
    """
    Processes population data from an Excel file and exports it to a JSON file.

    Parameters:
        input_file (str): Path to the input Excel file.
        output_file (str): Path to save the output JSON file.
    """
    print("Excel file is reading...")
    try:
        # Load Excel File
        data = pd.ExcelFile(input_file)

        # Skip unnecessary lines
        df = data.parse(data.sheet_names[0], skiprows=9)

        # Filter to only the required 6 columns if there are extras
        df = df.iloc[:, :6]  # Select the first 6 columns
        df.columns = ['Sıra No', 'İl Adı', 'İlçe Adı', 'Mahalle/Köy', 'Sandık No', 'Kayıtlı Seçmen Sayısı']

        # Convert the "Number of Registered Voters" column to a numeric value
        df['Kayıtlı Seçmen Sayısı'] = pd.to_numeric(df['Kayıtlı Seçmen Sayısı'], errors='coerce')

        # Group by neighborhood and calculate total population
        population_by_neighborhood = df.groupby('Mahalle/Köy')['Kayıtlı Seçmen Sayısı'].sum().reset_index()

        # Rename the columns
        population_by_neighborhood.columns = ['neighbourhood', 'total_population']

        # Filter out rows where "Toplam Nüfus" is 0
        population_by_neighborhood = population_by_neighborhood[population_by_neighborhood['total_population'] > 0]

        # Convert to JSON
        population_by_neighborhood.to_json(output_file, orient='records', force_ascii=False, indent=4)

        # Print the Results
        print(f"JSON was saved to : {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

import pandas as pd

# Load Excel File
file_path = "../../database/input/kadikoy.xlsx"
data = pd.ExcelFile(file_path)

# Inspect the sheet and headers to ensure proper parsing
print(data.sheet_names)

# Skip unnecessary lines
df = data.parse(data.sheet_names[0], skiprows=9)

# Check the columns
print(df.columns)

# Filter to only the required 6 columns if there are extras
df = df.iloc[:, :6]  # Select the first 6 columns
df.columns = ['Sıra No', 'İl Adı', 'İlçe Adı', 'Mahalle/Köy', 'Sandık No', 'Kayıtlı Seçmen Sayısı']

# Convert the "Number of Registered Voters" column to a numeric value
df['Kayıtlı Seçmen Sayısı'] = pd.to_numeric(df['Kayıtlı Seçmen Sayısı'], errors='coerce')

# Group by neighborhood and calculate total population
population_by_neighborhood = df.groupby('Mahalle/Köy')['Kayıtlı Seçmen Sayısı'].sum().reset_index()

# Rename the columns
population_by_neighborhood.columns = ['Mahalle', 'Toplam Nüfus']

# Filter out rows where "Toplam Nüfus" is 0
population_by_neighborhood = population_by_neighborhood[population_by_neighborhood['Toplam Nüfus'] > 0]

# Convert to JSON
output_path = '../../database/output/database.json'
population_by_neighborhood.to_json(output_path, orient='records', force_ascii=False, indent=4)

# Print the Results
print(population_by_neighborhood)
print(f"JSON dosyası kaydedildi: {output_path}")

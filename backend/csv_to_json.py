import pandas as pd
import json

print("Loading data...")

df = pd.read_csv('example.csv')
filtered_df = df[df['MMSI'] == 367067950]
data_dict = filtered_df.to_dict(orient='records')
data_json = json.dumps(data_dict, indent=4)

# print(data_json)

with open('filtered_data.json', 'w') as json_file:
    json.dump(data_dict, json_file, indent=4)

print("Data processing complete")

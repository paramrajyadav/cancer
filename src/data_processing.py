import pandas as pd
from sklearn.model_selection import train_test_split
import yaml
import os

def data_processing(data_path):
    # Read the data
    data = pd.read_csv(data_path)

    print(data)
    
    # Check if 'id' column exists before dropping it
    # if 'id' in data.columns:
    data = data.drop(columns=['id'])
    
    # Drop NaN values
    # data = data.dropna()
    
    print("hello")
    # Drop duplicates
    data = data.drop_duplicates()


    
    # Convert 'diagnosis' column to binary (1 for 'M', 0 for others)
    data['diagnosis'] = data['diagnosis'].apply(lambda x: 1 if x == 'M' else 0)
    
    # Add your additional data processing logic here (if any)
    print(data)
    return data

if __name__ =="__main__":
    # args = argparse.ArgumentParser()
    # args.add_argument("--param_yaml",default="params.yaml")
    # parsed_args = args.parse_args()
    # data = data_split(param_yaml_path = parsed_args.jjparam_yaml)
    param_yaml_path = "params.yaml"
    with open(param_yaml_path) as yaml_file:
        param_yaml = yaml.safe_load(yaml_file)
    
    train_data_path = os.path.join(param_yaml["split"]["dir"], param_yaml["split"]["train_file"])
    final_train_data = data_processing(data_path = train_data_path)

    os.makedirs(param_yaml["process"]["dir"], exist_ok=True)
    final_train_data_path = os.path.join(param_yaml["process"]["dir"], param_yaml["process"]["train_file"])
    final_train_data.to_csv(final_train_data_path, index=False)

    test_data_path = os.path.join(param_yaml["split"]["dir"], param_yaml["split"]["test_file"])
    final_test_data = data_processing(data_path = test_data_path)
    final_test_data_path = os.path.join(param_yaml["process"]["dir"], param_yaml["process"]["test_file"])
    final_test_data.to_csv(final_test_data_path, index=False)
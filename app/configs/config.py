import yaml
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory


with open('../app/configs/chat_model_config.yaml', 'r') as f:
    configs = yaml.safe_load(f)
    # print(configs)

# Get the safety_settings dictionary
safety_settings_str = configs['safety_settings']

# Map string keys to HarmCategory values
safety_settings = {
    getattr(HarmCategory, key): getattr(HarmBlockThreshold, value)
    for key, value in safety_settings_str.items()
}

generation_settings = configs['generation_settings']
# print(generation_settings['temperature'])
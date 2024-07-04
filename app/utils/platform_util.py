import yaml
from yaml import SafeLoader


class PlatformUtils:

    def load_yaml_and_get_model(self, model_name):
        with open('../app/configs/llm_platform.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)
        model_code, platform = self.get_model_code_and_platform(model_name, data)

        return model_code, platform

    def get_model_code_and_platform(self, model_name, data):
        for platform, models in data.items():
            for model in models:
                if model_name in model:
                    return model[model_name], platform
        return None, None
    
    def get_llm_platforms(self):
        with open('../app/configs/llm_platform.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)
        
        formatted_data = {}
        for key, value in data.items():
            model_names = [list(item.keys())[0] for item in value]
            formatted_data[key.split('(')[0]] = model_names

        return formatted_data
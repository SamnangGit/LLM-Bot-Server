import yaml
from yaml import SafeLoader


class PlatformUtils:

    def load_yaml_and_get_model(self, model_name):
        with open('../app/configs/llm_platform.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)
        model_code, parent = self.get_model_code_and_parent(model_name, data)

        return model_code, parent

    def get_model_code_and_parent(self, model_name, data):
        for parent, models in data.items():
            for model in models:
                if model_name in model:
                    return model[model_name], parent
        return None, None
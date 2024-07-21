import json


class settings_manager:
    def __init__(self, file_path = "./utils/settings.json") -> None:
        self.__file_path = file_path
        
        with open(self.__file_path) as fp:
            self.__json_settings = json.load(fp)
    
    def save_settings(self) -> None:
        with open(self.__file_path, "w") as fp:
            json.dump(self.__json_settings, fp)
    
    def set_settings_attribute(self, key, value: str) -> None:
        self.__json_settings["settings"][key] = value
    
    def set_settings_IG_attribute(self, key, value: str) -> None:
        self.__json_settings["settings"]["IG"][key] = value
    
    def set_settings_CG1_attribute(self, key, value: str) -> None:
        self.__json_settings["settings"]["CG1"][key] = value
    
    def set_settings_CG2_attribute(self, key, value: str) -> None:
        self.__json_settings["settings"]["CG2"][key] = value
    
    def set_live_plot_attribute(self, key, value: str) -> None:
        self.__json_settings["live plot"][key] = value

    def set_live_plot_IG_attribute(self, key, value: str) -> None:
        self.__json_settings["live plot"]["IG"][key] = value
    
    def set_live_plot_CG1_attribute(self, key, value: str) -> None:
        self.__json_settings["live plot"]["CG1"][key] = value
    
    def set_live_plot_CG2_attribute(self, key, value: str) -> None:
        self.__json_settings["live plot"]["CG2"][key] = value
    
    def get_settings_attribute(self, key) -> None:
        return self.__json_settings["settings"][key]
    
    def get_settings_IG_attribute(self, key) -> None:
        return self.__json_settings["settings"]["IG"][key]
    
    def get_settings_CG1_attribute(self, key) -> None:
        return self.__json_settings["settings"]["CG1"][key]
    
    def get_settings_CG2_attribute(self, key) -> None:
        return self.__json_settings["settings"]["CG2"][key]
    
    def get_live_plot_attribute(self, key) -> None:
        return self.__json_settings["live plot"][key]

    def get_live_plot_IG_attribute(self, key) -> None:
        return self.__json_settings["live plot"]["IG"][key]
    
    def get_live_plot_CG1_attribute(self, key) -> None:
        return self.__json_settings["live plot"]["CG1"][key]
    
    def get_live_plot_CG2_attribute(self, key) -> None:
        return self.__json_settings["live plot"]["CG2"][key]
    
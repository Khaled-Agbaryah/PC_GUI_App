import json


class units_manager:
    def __init__(self, file_path = "./utils/units.json") -> None:
        self.__file_path = file_path
        
        with open(self.__file_path) as fp:
            self.__json_data = json.load(fp)
        
        if len(self.__json_data["time units"]) != len(self.__json_data["time units functions"]) \
        or len(self.__json_data["pressure units"]) != len(self.__json_data["pressure units functions"]):
            raise Exception("units.json file corrupt!")
        
        for i in self.__json_data["time units functions"]:
            y = lambda x: eval(i)
            try:
                y(1)
            except:
                raise Exception("units.json file corrupt!")
        
        for i in self.__json_data["pressure units functions"]:
            y = lambda x: eval(i)
            try:
                y(1)
            except:
                raise Exception("units.json file corrupt!")
    
    def get_time_units(self) -> list[str]:
        return self.__json_data["time units"]
    
    def get_pressure_units(self) -> list[str]:
        return self.__json_data["pressure units"]
    
    def get_time_function(self, unit: str):
        i = self.__json_data["time units"].index(unit)
        return lambda x: eval(self.__json_data["time units functions"][i])
    
    def get_pressure_function(self, unit: str):
        i = self.__json_data["pressure units"].index(unit)
        return lambda x: eval(self.__json_data["pressure units functions"][i])

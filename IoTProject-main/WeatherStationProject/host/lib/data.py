from dataclasses import dataclass
#import sensors
import json
@dataclass
class Data:
    cur_temp: float
    cur_humid: float
    max_temp: float
    min_temp: float
    min_humid: float
    max_humid: float
    min_humid: float
    max_humid: float
    
    def to_dict(self) -> dict:
        return {
            "cur_temp": self.cur_temp,
            "cur_humid": self.cur_humid,
            "max_temp": self.max_temp,
            "min_temp": self.min_temp,
            "min_humid": self.min_humid,
            "max_humid": self.max_humid,
        }
    def to_json(self) -> str:
        return json.dumps({
            "cur_temp": self.cur_temp,
            "cur_humid": self.cur_humid,
        })
    def set_settings(self, min_temp: float, max_temp: float, min_humid: float, max_humid: float) -> None:
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.min_humid = min_humid
        self.max_humid = max_humid
    def set_values(self, cur_temp: float, cur_humid: float) -> None:
        self.cur_temp = cur_temp
        self.cur_humid = cur_humid
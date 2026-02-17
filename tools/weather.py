"""
天气查询工具
调用真实天气API获取天气信息
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WeatherTool:
    """天气查询工具"""
    
    enabled = True
    name = "get_weather"
    description = "获取指定城市在特定日期的天气信息，包括温度、降水概率、风速等。当用户询问天气、是否需要带伞、适合穿什么衣服时使用。"
    
    # 城市代码映射（实际项目应从数据库或API获取）
    CITY_CODES = {
        "北京": "101010100",
        "上海": "101020100",
        "广州": "101280100",
        "深圳": "101280600",
        "杭州": "101210101",
        "成都": "101270101",
        "武汉": "101200101",
        "西安": "101110101",
        "南京": "101190101",
        "重庆": "101040100",
    }
    
    def to_openai_format(self) -> Dict[str, Any]:
        """转换为 OpenAI 工具格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市名称，如'北京'、'上海'、'广州'"
                        },
                        "date": {
                            "type": "string",
                            "description": "日期，格式YYYY-MM-DD。不传则查询今天"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "温度单位，默认celsius"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    
    def execute(self, location: str, date: Optional[str] = None, unit: str = "celsius") -> Dict[str, Any]:
        """执行天气查询"""
        try:
            # 获取城市代码
            city_code = self.CITY_CODES.get(location)
            if not city_code:
                # 尝试模糊匹配
                for city, code in self.CITY_CODES.items():
                    if location in city or city in location:
                        city_code = code
                        location = city
                        break
            
            if not city_code:
                return {
                    "success": False,
                    "error": f"未找到城市'{location}'的代码，支持的城市：{', '.join(self.CITY_CODES.keys())}"
                }
            
            # 模拟API调用（实际项目替换为真实API）
            # 这里使用模拟数据演示
            weather_data = self._mock_weather_api(city_code, date)
            
            # 温度单位转换
            if unit == "fahrenheit" and "temperature" in weather_data:
                weather_data["temperature"] = round(weather_data["temperature"] * 9/5 + 32, 1)
                weather_data["unit"] = "°F"
            else:
                weather_data["unit"] = "°C"
            
            logger.info(f"天气查询成功：{location}, {weather_data.get('temperature')}")
            return {
                "success": True,
                "data": weather_data
            }
            
        except Exception as e:
            logger.error(f"天气查询失败：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _mock_weather_api(self, city_code: str, date: Optional[str] = None) -> Dict[str, Any]:
        """模拟天气API（实际项目替换为真实调用）"""
        import random
        
        # 模拟数据
        conditions = ["晴", "多云", "阴", "小雨", "中雨", "大雨", "雪"]
        return {
            "location": city_code,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "temperature": random.randint(15, 35),
            "condition": random.choice(conditions),
            "humidity": random.randint(40, 90),
            "wind_speed": random.randint(1, 20),
            "wind_direction": random.choice(["东风", "南风", "西风", "北风"]),
            "aqi": random.randint(30, 200),
        }


# 测试
if __name__ == "__main__":
    tool = WeatherTool()
    result = tool.execute("北京")
    print(result)

"""
全局状态管理模块
实现跨 Tab 的数据共享，无需后端数据库
"""
import gradio as gr

class GlobalContext:
    """商家数字档案 - 全局上下文管理器"""
    
    def __init__(self):
        self.shop_name = ""  # 店铺名称
        self.location = ""  # 地理位置
        self.opening_date = ""  # 开业时间
        self.features = []  # 核心特色标签
        self.knowledge_docs = []  # 上传的知识文档
        self.weather = "晴朗"  # 今日天气
        self.holiday = ""  # 节假日标记
        self.inventory_status = ""  # 库存/房态简况
        self.target_audience = ""  # 目标客群
        self.user_preferences = {}  # 用户偏好设置
        
        # 各引擎生成的成果缓存
        self.content_stories = []
        self.planning_activities = []
        self.operation_analysis = []
        self.marketing_materials = []
        
    def update_profile(self, shop_name, location, opening_date, features, 
                      weather, holiday, inventory_status, target_audience):
        """更新商家数字档案"""
        self.shop_name = shop_name
        self.location = location
        self.opening_date = opening_date
        self.features = features if features else []
        self.weather = weather
        self.holiday = holiday
        self.inventory_status = inventory_status
        self.target_audience = target_audience
        
        return self.get_context_summary()
    
    def upload_document(self, doc_content, doc_name):
        """上传知识文档"""
        self.knowledge_docs.append({
            "name": doc_name,
            "content": doc_content
        })
        return f"成功上传文档：{doc_name}"
    
    def get_context_summary(self):
        """获取上下文摘要，用于注入 Prompt"""
        features_str = "、".join(self.features) if self.features else "未设置"
        return f"""【商家档案】
店铺名称：{self.shop_name}
地理位置：{self.location}
开业时间：{self.opening_date}
核心特色：{features_str}
今日天气：{self.weather}
节假日：{self.holiday}
营业状态：{self.inventory_status}
目标客群：{self.target_audience}
已上传文档：{len(self.knowledge_docs)} 份"""
    
    def to_prompt_context(self):
        """转换为 Prompt 注入格式"""
        return {
            "shop_name": self.shop_name,
            "location": self.location,
            "features": ",".join(self.features),
            "weather": self.weather,
            "holiday": self.holiday,
            "inventory_status": self.inventory_status,
            "target_audience": self.target_audience,
            "knowledge_count": len(self.knowledge_docs)
        }
    
    def save_engine_result(self, engine_name, result):
        """保存引擎生成的成果"""
        if engine_name == "content":
            self.content_stories.append(result)
        elif engine_name == "planning":
            self.planning_activities.append(result)
        elif engine_name == "operation":
            self.operation_analysis.append(result)
        elif engine_name == "marketing":
            self.marketing_materials.append(result)


# 创建全局实例
global_context = GlobalContext()


def create_demo_case(case_name="西湖绸伞店"):
    """创建演示案例数据"""
    cases = {
        "西湖绸伞店": {
            "shop_name": "西湖绸伞工艺坊",
            "location": "杭州市西湖区河坊街 128 号",
            "opening_date": "2018 年 5 月",
            "features": ["非遗传承", "宋韵文化", "手工技艺", "文创产品"],
            "weather": "小雨",
            "holiday": "端午节",
            "inventory_status": "库存充足，周末客流高峰",
            "target_audience": "文化体验爱好者、亲子家庭"
        },
        "满觉陇民宿": {
            "shop_name": "满觉陇山居",
            "location": "杭州市西湖区满觉陇村 25 号",
            "opening_date": "2020 年 8 月",
            "features": ["精品民宿", "茶文化", "山景房", "禅修体验"],
            "weather": "多云转晴",
            "holiday": "中秋节",
            "inventory_status": "周末房源紧张，平日有空房",
            "target_audience": "都市白领、情侣度假"
        },
        "龙井茶庄": {
            "shop_name": "龙井问茶庄",
            "location": "杭州市西湖区龙井村狮峰山路 88 号",
            "opening_date": "2015 年 3 月",
            "features": ["茶文化", "品茶体验", "茶叶销售", "传统工艺"],
            "weather": "晴朗",
            "holiday": "清明节",
            "inventory_status": "新茶上市，库存充足",
            "target_audience": "茶叶爱好者、商务人士"
        }
    }
    
    return cases.get(case_name, cases["西湖绸伞店"])

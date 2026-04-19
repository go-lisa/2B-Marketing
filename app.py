"""
基于英特尔 OpenVINO 的本地文旅商家智能助手
主应用入口 - Gradio Web App
"""
import gradio as gr
from state_manager import global_context, create_demo_case
# 使用本地 OpenVINO 模型（替代远程 API）
from api_service_local import llm_service, wanx_service
from prompt_templates import PromptTemplates
import json


# ==================== 数字档案模块 ====================
def update_shop_profile(shop_name, location, opening_date, features, weather, 
                        holiday, inventory_status, target_audience):
    """更新商家数字档案"""
    features_list = [f.strip() for f in features.split(",") if f.strip()]
    summary = global_context.update_profile(
        shop_name=shop_name,
        location=location,
        opening_date=opening_date,
        features=features_list,
        weather=weather,
        holiday=holiday,
        inventory_status=inventory_status,
        target_audience=target_audience
    )
    return summary, "✅ 数字档案已更新，可以开始使用各智能引擎！"


def load_demo_case(case_name):
    """加载演示案例"""
    if not case_name:
        return "", ""
    
    case_data = create_demo_case(case_name)
    
    # 填充到表单
    features_str = "、".join(case_data["features"])
    summary = global_context.update_profile(
        shop_name=case_data["shop_name"],
        location=case_data["location"],
        opening_date=case_data["opening_date"],
        features=case_data["features"],
        weather=case_data["weather"],
        holiday=case_data["holiday"],
        inventory_status=case_data["inventory_status"],
        target_audience=case_data["target_audience"]
    )
    
    # 返回填充值
    return (
        case_data["shop_name"],
        case_data["location"],
        case_data["opening_date"],
        features_str,
        case_data["weather"],
        case_data["holiday"],
        case_data["inventory_status"],
        case_data["target_audience"],
        summary,
        "✅ 已加载演示案例，可以开始体验！"
    )


# ==================== 文化内容官引擎 ====================
def generate_cultural_story(product_name, story_type="游客版"):
    """生成文化故事"""
    if not global_context.shop_name:
        return "⚠️ 请先在【商家数字档案】中填写店铺信息"
    
    context = global_context.to_prompt_context()
    system_prompt = PromptTemplates.get_content_engine_prompt(context)
    
    user_prompt = f"""请为商品/景点"{product_name}"生成{story_type}文化故事。

要求：
1. 深入挖掘产品背后的历史文化、工艺细节、情感寓意
2. 结合我店的特色和地理位置，突出独特性
3. {story_type}版本要{ "通俗易懂、引发情感共鸣" if story_type == "游客版" else "专业深度、详细工艺细节"}
4. 字数：500-800 字"""

    result = llm_service.generate(system_prompt, user_prompt)
    global_context.save_engine_result("content", {"type": "故事", "content": result})
    return result


def generate_multilingual_intro(content, target_language="英文"):
    """多语言文化桥接"""
    if not global_context.shop_name:
        return "⚠️ 请先在【商家数字档案】中填写店铺信息"
    
    context = global_context.to_prompt_context()
    system_prompt = PromptTemplates.get_content_engine_prompt(context)
    
    user_prompt = f"""请将以下内容翻译成{target_language}，并进行文化背景解释：

原文：
{content}

要求：
1. 不仅要翻译字面意思，更要解释文化内涵
2. 对于特有文化概念（如非遗技艺、历史典故），提供简短的背景说明，让外国游客能够理解并产生兴趣
3. 给出商家使用外文内容的真实场景指引，具备实践指导意义，以提升店家在服务外国游客的服务质量，而非仅作翻译工具目的
4. 格式：先翻译，再解释关键文化概念，最后给出店员的实践指导，让外国游客能够了解商家的服务内容，并产生兴趣
"""

    result = llm_service.generate(system_prompt, user_prompt)
    return result


def generate_video_script(product_name):
    """生成短视频脚本"""
    if not global_context.shop_name:
        return "⚠️ 请先在【商家数字档案】中填写店铺信息"
    
    context = global_context.to_prompt_context()
    system_prompt = PromptTemplates.get_content_engine_prompt(context)
    
    user_prompt = f"""请为商品/景点"{product_name}"创作一个 60 秒短视频脚本。

要求包含：
1. 分镜描述（画面内容、拍摄角度）
2. 旁白文案（每句台词和对应时间）
3. 背景音乐建议（风格、情绪）
4. 字幕文案（重点金句）
5. 开头 3 秒必须有吸引力，结尾有行动号召

格式示例：
【0-3 秒】画面：特写镜头... 旁白：... BGM：...
【4-15 秒】画面：..."""

    result = llm_service.generate(system_prompt, user_prompt)
    global_context.save_engine_result("content", {"type": "视频脚本", "content": result})
    return result


# ==================== 文化内容官引擎 - 多模态 ====================
def generate_cultural_story_with_image(product_name, story_type, image_input):
    """生成文化故事（支持图片输入）"""
    if not global_context.shop_name:
        return "⚠️ 请先在【商家数字档案】中填写店铺信息"
    
    context = global_context.to_prompt_context()
    system_prompt = PromptTemplates.get_content_engine_prompt(context)
    
    # 构建用户提示词
    user_prompt = f"""请为商品/景点"{product_name}"生成{story_type}文化故事。

要求：
1. 深入挖掘产品背后的历史文化、工艺细节、情感寓意
2. 结合我店的特色和地理位置，突出独特性
3. {story_type}版本要{"通俗易懂、引发情感共鸣" if "游客版" in story_type else "专业深度、详细工艺细节"}
4. 字数：500-800 字

{'''5. 请仔细分析上传的图片，从视觉角度描述产品的特征、工艺细节、材质质感等，并融入文化故事中。''' if image_input else ''}
"""

    # 如果有图片，使用多模态 API
    if image_input:
        import tempfile
        import os
        
        # 保存上传的图片到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            # Gradio 上传图片的格式是 numpy array，需要转换为 PIL Image 再保存
            from PIL import Image as PILImage
            if isinstance(image_input, PILImage.Image):
                image_input.save(tmp_file.name, 'JPEG')
            else:
                # 如果是其他格式，尝试直接保存
                try:
                    img = PILImage.fromarray(image_input)
                    img.save(tmp_file.name, 'JPEG')
                except:
                    return "图片格式不支持"
            
            tmp_file_path = tmp_file.name
        
        try:
            result = llm_service.generate_with_image(system_prompt, user_prompt, tmp_file_path)
        finally:
            # 清理临时文件
            os.unlink(tmp_file_path)
    else:
        result = llm_service.generate(system_prompt, user_prompt)
    
    global_context.save_engine_result("content", {"type": "故事（多模态）" if image_input else "故事", "content": result})
    return result


# ==================== 体验策划师引擎 ====================
def generate_activity_plan(activity_theme=""):
    """生成体验活动方案"""
    if not global_context.shop_name:
        return "⚠️ 请先在【商家数字档案】中填写店铺信息"
    
    context = global_context.to_prompt_context()
    system_prompt = PromptTemplates.get_planning_engine_prompt(context)
    
    user_prompt = f"""请设计一个店内微活动方案。
{"活动主题：" + activity_theme if activity_theme else "请根据当前天气和节假日自主创意"}

要求：
1. 充分利用在地资源和现有场地
2. 强调文化体验和互动参与
3. 方案要切实可行，成本低
4. 输出完整的活动策划包"""

    result = llm_service.generate(system_prompt, user_prompt)
    global_context.save_engine_result("planning", {"type": "活动方案", "content": result})
    return result


# ==================== 口碑诊疗所引擎 ====================
def analyze_review(review_text):
    """分析游客评价"""
    if not global_context.shop_name:
        return "⚠️ 请先在【商家数字档案】中填写店铺信息"
    
    context = global_context.to_prompt_context()
    system_prompt = PromptTemplates.get_operation_engine_prompt(context)
    
    user_prompt = f"""请分析以下游客评价，并提供回复和整改建议：

评价内容：
{review_text}

要求：
1. 提取情感和关键问题
2. 生成 2-3 个不同风格的高情商回复
3. 提供具体可执行的整改建议（低成本）
4. 体现真诚和专业"""

    result = llm_service.generate(system_prompt, user_prompt)
    global_context.save_engine_result("operation", {"type": "评价分析", "content": result})
    return result


# ==================== 营销推广员引擎 ====================
def generate_marketing_materials(campaign_theme=""):
    """生成营销物料"""
    if not global_context.shop_name:
        return "⚠️ 请先在【商家数字档案】中填写店铺信息", None
    
    context = global_context.to_prompt_context()
    system_prompt = PromptTemplates.get_marketing_engine_prompt(context)
    
    user_prompt = f"""请为我店生成全渠道营销物料。
{"营销主题：" + campaign_theme if campaign_theme else "结合当前节假日和活动"}

要求：
1. 海报设计提示词（用于 AI 绘图）
2. 朋友圈文案 3 个版本
3. 小红书种草文案
4. 公众号推文大纲
5. 私域引流话术

请结构化输出所有内容。"""

    result = llm_service.generate(system_prompt, user_prompt)
    global_context.save_engine_result("marketing", {"type": "营销物料", "content": result})
    
    # 生成海报设计提示词
    poster_prompt = f"""新中式风格海报，{global_context.shop_name}，
融合{context.get('features', '传统文化')}元素，
{context.get('holiday', '')}节日氛围，
高品质商业摄影风格，暖色调，细节精致"""
    
    return result, poster_prompt


def generate_poster_image(poster_prompt):
    """调用 Wanx 生成海报图片"""
    if not poster_prompt:
        return None
    
    image_url = wanx_service.generate_poster(poster_prompt)
    return image_url


# ==================== 营销推广引擎 - 包装设计 ====================
def generate_packaging_design(product_image, product_name, design_style, cultural_elements, extra_requirements):
    """生成产品包装设计（基于产品图片）"""
    if not global_context.shop_name:
        return None, None, None, "⚠️ 请先在【商家数字档案】中填写店铺信息"
    
    # 构建文化元素描述
    cultural_desc = f"{cultural_elements}（{global_context.shop_name}特色）"
    
    # 如果有产品图片，先分析产品特征
    design_prompt_extra = ""
    if product_image is not None:
        import tempfile
        import os
        from PIL import Image as PILImage
        
        # 保存上传的图片到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            if isinstance(product_image, PILImage.Image):
                product_image.save(tmp_file.name, 'JPEG')
            else:
                try:
                    img = PILImage.fromarray(product_image)
                    img.save(tmp_file.name, 'JPEG')
                except:
                    return None, None, None, "图片格式不支持"
            
            tmp_file_path = tmp_file.name
        
        try:
            # 分析产品图片特征
            analysis_system_prompt = """你是一位专业的产品包装设计师。请仔细分析这张产品图片，提取以下信息：
1. 产品类型和形态（如：茶叶罐、酒瓶、礼盒等）
2. 当前包装的材质和质感
3. 现有的色彩搭配
4. 产品的档次定位（高端/中端/大众）
5. 适合的设计风格建议

请用简洁的语言描述，100-200 字。"""
            
            product_analysis = llm_service.generate_with_image(
                analysis_system_prompt,
                "请详细分析这个产品的外观特征，为包装设计提供参考。",
                tmp_file_path,
                max_tokens=500
            )
            
            design_prompt_extra = f"原产品特征分析：{product_analysis}\n\n设计要求：{extra_requirements}"
            
        finally:
            os.unlink(tmp_file_path)
    else:
        design_prompt_extra = extra_requirements
    
    # 调用包装设计服务（传入优化后的提示词）
    designs = wanx_service.generate_packaging_design(
        product_name=product_name,
        style=design_style,
        cultural_elements=cultural_desc,
        prompt_extra=design_prompt_extra
    )
    
    if designs:
        # 生成设计理念说明
        context = global_context.to_prompt_context()
        
        design_explanation_prompt = f"""请为以下产品设计撰写设计理念说明：

产品名称：{product_name}
设计风格：{design_style}
文化元素：{cultural_desc}
{f'原产品特征：{design_prompt_extra}' if design_prompt_extra else ''}

请从以下角度阐述设计理念：
1. **配色方案**：为什么选择这些颜色？有什么文化寓意？
2. **纹样图案**：图案来源是什么？与当地文化有何关联？
3. **材质工艺**：推荐什么材质和工艺？如何体现品质感？
4. **文化故事**：如何通过设计讲述品牌故事？
5. **价值提升**：这个设计如何帮助产品卖出更高价格？

要求：专业、有深度、能打动消费者，300-500 字。"""

        explanation = llm_service.generate(
            "你是一位资深产品包装设计师，擅长将地域文化融入现代包装设计。",
            design_explanation_prompt
        )
        
        return (
            designs.get('main'),
            designs.get('gift_bag'),
            designs.get('card'),
            explanation
        )
    else:
        return None, None, None, "包装设计生成失败"


# ==================== 执行中心 ====================
def generate_daily_report():
    """生成今日运营日报"""
    if not global_context.shop_name:
        return "⚠️ 请先填写商家数字档案"
    
    report = f"""# {global_context.shop_name} - 今日运营日报
生成时间：2026-03-09

## 📊 基本信息
{global_context.get_context_summary()}

## 📝 今日成果汇总
"""
    
    # 汇总各引擎成果
    if global_context.content_stories:
        report += "\n### 文化内容\n"
        for item in global_context.content_stories[-2:]:
            report += f"- {item.get('type', '')}\n"
    
    if global_context.planning_activities:
        report += "\n### 活动策划\n"
        for item in global_context.planning_activities[-2:]:
            report += f"- {item.get('type', '')}\n"
    
    if global_context.operation_analysis:
        report += "\n### 口碑管理\n"
        for item in global_context.operation_analysis[-2:]:
            report += f"- {item.get('type', '')}\n"
    
    if global_context.marketing_materials:
        report += "\n### 营销物料\n"
        for item in global_context.marketing_materials[-2:]:
            report += f"- {item.get('type', '')}\n"
    
    report += "\n\n## 🎯 明日待办\n"
    report += "1. 检查活动物料准备情况\n"
    report += "2. 跟进差评整改措施\n"
    report += "3. 发布营销内容到各平台\n"
    
    return report


# ==================== 商家小助手 ====================
def chat_with_assistant(user_message, chat_history):
    """与商家小助手对话"""
    if not global_context.shop_name:
        return "请先在【商家数字档案】中填写您的店铺信息，这样我才能更好地了解您的需求并提供帮助。", chat_history
    
    context = global_context.to_prompt_context()
    
    system_prompt = f"""你是一位专业的文旅行业智能助手，服务于{context.get('shop_name', '未知店铺')}。

【店铺信息】
- 位置：{context.get('location', '未知')}
- 特色：{context.get('features', '无')}
- 今日天气：{context.get('weather', '未知')}
- 节假日：{context.get('holiday', '未知')}
- 目标客群：{context.get('target_audience', '普通游客')}

【你的职责】
1. 解答商家关于文旅运营的任何问题
2. 提供基于在地文化的专业建议
3. 引导商家使用各个功能模块
4. 语气亲切、专业、实用

【回答要求】
- 结合店铺实际情况给出建议
- 突出文化特色和在地资源
- 提供可执行的具体方案
- 避免空泛的理论
"""

    user_prompt = f"""{user_message}

请根据我的店铺情况，给出专业、实用的建议。"""

    response = llm_service.generate(system_prompt, user_prompt)
    
    # 更新聊天记录
    chat_history.append((user_message, response))
    
    return "", chat_history


# ==================== UI 构建 ====================
with gr.Blocks(
    title="基于英特尔 OpenVINO 的本地文旅商家智能助手",
    theme=gr.themes.Base(
        primary_hue="slate",
        secondary_hue="gray",
        neutral_hue="neutral",
    ),
    css="""
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto;
    }
    .main-header {
        text-align: left;
        padding: 0px 20px;
    }
    .main-title {
        font-size: 28px;
        font-weight: 600;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.05em !important;
    }
    .section-header {
        padding: 5px 0;
        border-bottom: 1px solid #f3f4f6;
        margin-bottom: 24px;
    }
    .feature-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .info-box {
        background: #f9fafb;
        border-left: 3px solid #374151;
        padding: 12px 16px;
        margin: 16px 0;
        font-size: 13px;
        color: #374151;
    }
    .assistant-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }
    /* Landing Page 高端样式 - OpenAI 风格 */
    .landing-hero {
        background: #ffffff; /* 基础背景色（图片加载失败时兜底） */
        background-image: url("https://www.wallpaperhub.app/_next/image?url=https%3A%2F%2Fcdn.wallpaperhub.app%2Fcloudcache%2Fa%2F6%2Ff%2F1%2F0%2F2%2Fa6f102bda1cf50c3a43f5af2c03234764f0dd9bc.jpg&w=4500&q=100"); /* 正确的背景图写法 */
        background-repeat: no-repeat; /* 可选：防止图片重复 */
        background-size: cover; /* 可选：让图片覆盖整个容器 */
        background-position: center; /* 可选：让图片居中显示 */
        border-bottom: 1px solid #e5e7eb;
        padding: 80px 40px;
        margin-bottom: 20px;
        text-align: center;
    }
    .landing-hero h1 {
        font-size: 56px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-bottom: 16px !important;
        letter-spacing: 0.05em !important;
        line-height: 1.1 !important;
    }
    .landing-hero p {
        font-size: 20px !important;
        color: #ffffff !important;
        font-weight: 400 !important;
        margin-top: 0 !important;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    .feature-card-premium {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0;
        padding: 32px;
        margin-bottom: 24px;
    }
    .stat-number {
        font-size: 48px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    .stat-label {
        font-size: 14px;
        color: #000000;
        margin-top: 8px;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .engine-badge {
        display: inline-block;
        color: #000000;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 16px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .step-number {
        font-size: 14px;
        font-weight: 600;
        color: #000000;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .scenario-tag {
        display: inline-block;
        background: #f9fafb;
        color: #374151;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 400;
        margin: 4px 8px 4px 0;
        border: 1px solid #e5e7eb;
    }
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    .comparison-table th {
        background: #ffffff;
        padding: 16px;
        text-align: left;
        font-weight: 600;
        color: #000000;
        border-bottom: 2px solid #000000;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .comparison-table td {
        padding: 20px 16px;
        border-bottom: 1px solid #f3f4f6;
        font-size: 15px;
        color: #374151;
    }
    .comparison-table tr:last-child td {
        border-bottom: none;
    }
    .gradio-container .prose h1 {
        font-size: 28px;
        font-weight: 600;
        color: #000000;
        margin-bottom: 20px;
        letter-spacing: -0.02em;
    }
    .gradio-container .prose h3 {
        font-size: 20px;
        font-weight: 600;
        color: #000000;
        margin-top: 40px;
        margin-bottom: 20px;
        letter-spacing: -0.02em;
    }
    .gradio-container .prose h4 {
        font-size: 16px;
        font-weight: 600;
        color: #000000;
        margin-top: 24px;
        margin-bottom: 12px;
    }
    .gradio-container .prose p {
        line-height: 1.8;
        color: #374151;
        margin-bottom: 16px;
        font-size: 15px;
    }
    .gradio-container .prose ul {
        margin-bottom: 16px;
        padding-left: 24px;
    }
    .gradio-container .prose li {
        margin-bottom: 10px;
        line-height: 1.7;
    }
    """
) as demo:
    
    # 顶部标题
    gr.HTML('''
    <div class="main-header">
        <h1 class="main-title">基于英特尔 OpenVINO 的本地文旅商家智能助手</h1>
    </div>
    ''')
    
    with gr.Tabs() as tabs:
        
        # Tab 0: Landing Page - 产品介绍
        with gr.TabItem("首页"):
            # Hero Section - 极简白底
            gr.HTML('''
            <div class="landing-hero">
                <h1>本地文旅商家智能助手</h1>
                <p>一站式 AI 智能营销平台，专为小微文旅企业打造<br>基于英特尔 OpenVINO 技术，完全本地运行，零成本、高隐私</p>
            </div>
            ''')
            
            # 核心数据统计
            gr.Markdown("### 核心价值")
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML('''
                    <div style="text-align: center; padding: 32px 24px;">
                        <div class="stat-number">5-10 万</div>
                        <div class="stat-label">每年节省营销费用</div>
                    </div>
                    ''')
                with gr.Column(scale=1):
                    gr.HTML('''
                    <div style="text-align: center; padding: 32px 24px;">
                        <div class="stat-number">10 倍+</div>
                        <div class="stat-label">内容生产效率提升</div>
                    </div>
                    ''')
                with gr.Column(scale=1):
                    gr.HTML('''
                    <div style="text-align: center; padding: 32px 24px;">
                        <div class="stat-number">30 秒</div>
                        <div class="stat-label">AI 生成专业方案</div>
                    </div>
                    ''')

            gr.Markdown("---")
            
            # 产品定位与优势对比
            gr.Markdown("### 为什么选择我们")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML('''
                    <div class="feature-card-premium">
                        <span class="engine-badge">产品定位</span>
                        <h4 style="margin: 8px 0 16px 0; font-size: 18px; color: #000000;">为小微文旅商家量身定制</h4>
                        <p style="color: #374151; line-height: 1.8; margin-bottom: 24px;">服务民宿、非遗店、小景区、文创店等，提供全流程 AI 智能营销服务。</p>
                        
                        <h5 style="font-size: 13px; font-weight: 600; color: #000000; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">核心理念</h5>
                        <ul style="margin: 0; padding-left: 20px; color: #374151; line-height: 2;">
                            <li>深度挖掘文化价值，拒绝通用电商话术</li>
                            <li>基于在地资源策划，强调真实体验感</li>
                            <li>视觉风格符合国风，文案侧重生活方式</li>
                            <li>关注体验修复，提供可落地整改建议</li>
                        </ul>
                    </div>
                    ''')
                
                with gr.Column(scale=1):
                    gr.HTML('''
                    <div class="feature-card-premium">
                        <h4 style="margin-top: 0; margin-bottom: 20px; font-size: 18px; color: #000000;">传统方式 vs 文旅智脑</h4>
                        <table class="comparison-table">
                            <thead>
                                <tr>
                                    <th>传统方式</th>
                                    <th>文旅智脑</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>请设计师：¥5,000-30,000</td>
                                    <td><strong>AI 生成：免费</strong></td>
                                </tr>
                                <tr>
                                    <td>写文案：几小时</td>
                                    <td><strong>AI 生成：30 秒</strong></td>
                                </tr>
                                <tr>
                                    <td>做海报：找广告公司</td>
                                    <td><strong>一键出图</strong></td>
                                </tr>
                                <tr>
                                    <td>学运营：高学习成本</td>
                                    <td><strong>零门槛上手</strong></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    ''')
            
            # 功能架构
            gr.Markdown("### 四大智能引擎")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML('''
                    <div class="feature-card-premium">
                        <span class="engine-badge">引擎 1</span>
                        <h4 style="margin: 8px 0 12px 0; color: #000000; font-size: 18px;">文化内容官</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #374151; line-height: 1.8;">
                            <li>深度故事生成（多模态图片分析）</li>
                            <li>多语言翻译桥接</li>
                            <li>短视频脚本创作</li>
                        </ul>
                    </div>
                    ''')
                    
                    gr.HTML('''
                    <div class="feature-card-premium">
                        <span class="engine-badge">引擎 2</span>
                        <h4 style="margin: 8px 0 12px 0; color: #000000; font-size: 18px;">体验策划师</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #374151; line-height: 1.8;">
                            <li>动态活动策划</li>
                            <li>完整物料包生成</li>
                            <li>成本预估清单</li>
                        </ul>
                    </div>
                    ''')
                
                with gr.Column(scale=1):
                    gr.HTML('''
                    <div class="feature-card-premium">
                        <span class="engine-badge">引擎 3</span>
                        <h4 style="margin: 8px 0 12px 0; color: #000000; font-size: 18px;">口碑诊疗所</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #374151; line-height: 1.8;">
                            <li>情感分析诊断</li>
                            <li>高情商回复模板</li>
                            <li>行动整改清单</li>
                        </ul>
                    </div>
                    ''')
                    
                    gr.HTML('''
                    <div class="feature-card-premium">
                        <span class="engine-badge">引擎 4</span>
                        <h4 style="margin: 8px 0 12px 0; color: #000000; font-size: 18px;">营销推广员</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #374151; line-height: 1.8;">
                            <li>智能包装设计（多图生成）</li>
                            <li>全渠道文案矩阵</li>
                            <li>私域引流话术</li>
                        </ul>
                    </div>
                    ''')
            
            # 使用流程
            gr.Markdown("### 四步开启智能营销")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML('''
                    <div style="margin-bottom: 32px;">
                        <div class="step-number">STEP 01</div>
                        <h5 style="font-size: 16px; font-weight: 600; color: #000000; margin-bottom: 8px;">建立数字档案</h5>
                        <p style="margin: 0; color: #374151; line-height: 1.7;">填写店铺基础信息（位置、特色、客群等），AI 将基于此提供个性化服务</p>
                    </div>
                    
                    <div style="margin-bottom: 32px;">
                        <div class="step-number">STEP 02</div>
                        <h5 style="font-size: 16px; font-weight: 600; color: #000000; margin-bottom: 8px;">选择功能模块</h5>
                        <p style="margin: 0; color: #374151; line-height: 1.7;">根据需求选择对应的智能引擎：文化内容 / 活动策划 / 口碑管理 / 营销推广</p>
                    </div>
                    ''')
                
                with gr.Column(scale=1):
                    gr.HTML('''
                    <div style="margin-bottom: 32px;">
                        <div class="step-number">STEP 03</div>
                        <h5 style="font-size: 16px; font-weight: 600; color: #000000; margin-bottom: 8px;">获取 AI 成果</h5>
                        <p style="margin: 0; color: #374151; line-height: 1.7;">30-60 秒即可生成专业方案，可直接使用的文案、设计图、策划案</p>
                    </div>
                    
                    <div style="margin-bottom: 32px;">
                        <div class="step-number">STEP 04</div>
                        <h5 style="font-size: 16px; font-weight: 600; color: #000000; margin-bottom: 8px;">持续优化</h5>
                        <p style="margin: 0; color: #374151; line-height: 1.7;">与商家小助手互动，获得持续建议，基于您的实际情况提供针对性指导</p>
                    </div>
                    ''')
            
            # 适用场景
            gr.Markdown("### 适用场景")
            
            gr.HTML('''
            <div class="feature-card-premium" style="text-align: center;">
                <span class="scenario-tag">特色民宿</span>
                <span class="scenario-tag">非遗工坊</span>
                <span class="scenario-tag">茶庄茶馆</span>
                <span class="scenario-tag">文创小店</span>
                <span class="scenario-tag">小型景区</span>
                <span class="scenario-tag">老字号餐饮</span>
                <span class="scenario-tag">精品酒店</span>
                <span class="scenario-tag">民俗体验馆</span>
            </div>
            ''')
            
            # 底部行动号召
            gr.HTML('''
            <div style="text-align: center; padding: 80px 20px 60px 20px; background: #f9fafb; border-top: 1px solid #e5e7eb; margin-top: 40px;">
                <p style="font-size: 20px; color: #000000; margin-bottom: 12px; font-weight: 600;">
                    准备好开启智能营销之旅了吗？
                </p>
                <p style="font-size: 15px; color: #6b7280; margin-bottom: 32px;">
                    请点击上方<strong>「商家数字档案」</strong>，建立您的<strong>店铺数字档案</strong>
                </p>
                <div style="display: inline-block; background: #000000; color: #ffffff; padding: 16px 40px; font-size: 15px; font-weight: 600; letter-spacing: 0.02em;">
                    立即开始
                </div>
            </div>
            ''')
        
        # Tab 1: 商家数字档案
        with gr.TabItem("商家数字档案"):
            with gr.Row():
                gr.Markdown(
                    """**说明**：填写您的店铺基础信息。这些数据将作为全局上下文，
                    为后续所有智能服务提供个性化支持。**建议完整填写以获得最佳效果**。""",
                    elem_classes=["info-box"]
                )
            
            with gr.Row():
                with gr.Column(scale=2):
                    shop_name_input = gr.Textbox(
                        label="店铺名称",
                        placeholder="例如：西湖绸伞工艺坊",
                        info="给您的店铺起一个有文化感的名字"
                    )
                    location_input = gr.Textbox(
                        label="地理位置",
                        placeholder="例如：杭州市西湖区河坊街 128 号",
                        info="精确到街道或景区，有助于推荐在地资源"
                    )
                    opening_date_input = gr.Textbox(
                        label="开业时间",
                        placeholder="例：2018 年 5 月",
                        info="帮助讲述品牌历史故事"
                    )
                    features_input = gr.Textbox(
                        label="核心特色（用逗号分隔）",
                        placeholder="例：非遗传承，宋韵文化，手工技艺，文创产品",
                        info="标签化展示您的文化特色"
                    )
                
                with gr.Column(scale=2):
                    weather_input = gr.Dropdown(
                        label="今日天气",
                        choices=["晴朗", "多云", "小雨", "大雨", "阴天"],
                        value="晴朗",
                        info="影响活动策划的重要因子"
                    )
                    holiday_input = gr.Textbox(
                        label="节假日",
                        placeholder="例：端午节 / 周末 / 平日",
                        info="用于生成应景的营销内容"
                    )
                    inventory_input = gr.Textbox(
                        label="营业状态",
                        placeholder="例：库存充足，周末客流高峰",
                        info="当前的经营情况简述"
                    )
                    audience_input = gr.Textbox(
                        label="目标客群",
                        placeholder="例：文化体验爱好者、亲子家庭",
                        info="帮助精准定位营销策略"
                    )
                    
                    update_btn = gr.Button("保存数字档案", variant="primary")
            
            with gr.Row():
                demo_case_dropdown = gr.Dropdown(
                    label="演示案例",
                    choices=["西湖绸伞店", "满觉陇民宿", "龙井茶庄"],
                    value="西湖绸伞店",
                    info="点击快速填充数据，方便演示体验"
                )
            
            profile_summary = gr.Textbox(
                label="档案摘要",
                lines=8,
                interactive=False
            )
            profile_status = gr.Textbox(label="状态", interactive=False)
            
            update_btn.click(
                fn=update_shop_profile,
                inputs=[shop_name_input, location_input, opening_date_input, features_input,
                       weather_input, holiday_input, inventory_input, audience_input],
                outputs=[profile_summary, profile_status]
            )
            
            demo_case_dropdown.change(
                fn=load_demo_case,
                inputs=demo_case_dropdown,
                outputs=[shop_name_input, location_input, opening_date_input, features_input,
                        weather_input, holiday_input, inventory_input, audience_input,
                        profile_summary, profile_status]
            )
        
        # Tab 1: 文化内容官
        with gr.TabItem("文化内容引擎"):
            with gr.Row():
                gr.Markdown(
                    """**定位**：将商品/景点转化为具有文化深度的 IP 内容。\n\n"
                    **核心理念**：深度挖掘历史文化价值，拒绝通用电商话术。""",
                    elem_classes=["info-box"]
                )
            
            with gr.Row():
                with gr.Column(scale=1):
                    product_name = gr.Textbox(
                        label="商品/景点名称",
                        placeholder="例：西湖绸伞·经典款",
                        info="输入您想包装的商品或景点"
                    )
                    story_type_radio = gr.Radio(
                        choices=["游客版（通俗易懂）", "专家版（专业深度）"],
                        value="游客版（通俗易懂）",
                        label="故事版本"
                    )
                    
                    # 新增：图片上传功能
                    image_input = gr.Image(
                        label="产品图片（可选）",
                        type="pil",
                        sources=["upload", "clipboard"]
                    )
                    
                    generate_story_btn = gr.Button("生成文化故事", variant="primary")
                    
                    gr.Markdown("---")
                    
                    content_to_translate = gr.Textbox(
                        label="需要翻译的内容",
                        lines=5,
                        placeholder="粘贴需要多语言介绍的文字...",
                        info="AI 会翻译并解释文化背景"
                    )
                    target_lang = gr.Dropdown(
                        choices=["英文", "日文", "韩文", "法文"],
                        value="英文",
                        label="目标语言"
                    )
                    translate_btn = gr.Button("多语言介绍")
                    
                    gr.Markdown("---")
                    
                    video_product = gr.Textbox(
                        label="短视频商品",
                        placeholder="例：龙井明前茶",
                        info="自动生成 60 秒带货脚本"
                    )
                    generate_video_btn = gr.Button("生成短视频脚本")
                
                with gr.Column(scale=2):
                    story_output = gr.Markdown(label="文化故事", show_copy_button=True)
                    translation_output = gr.Markdown(label="多语言介绍", show_copy_button=True)
                    video_output = gr.Markdown(label="短视频脚本", show_copy_button=True)
            
            # 修改：使用新的多模态函数
            generate_story_btn.click(
                fn=generate_cultural_story_with_image,
                inputs=[product_name, story_type_radio, image_input],
                outputs=story_output
            )
            
            translate_btn.click(
                fn=generate_multilingual_intro,
                inputs=[content_to_translate, target_lang],
                outputs=translation_output
            )
            
            generate_video_btn.click(
                fn=generate_video_script,
                inputs=[video_product],
                outputs=video_output
            )
        
        # Tab 2: 体验策划师
        with gr.TabItem("体验策划引擎"):
            with gr.Row():
                gr.Markdown(
                    """**定位**：基于在地资源的微活动设计师。\n\n"
                    **核心理念**：强调线下体验与互动，充分利用现有场地和资源。""",
                    elem_classes=["info-box"]
                )
            
            with gr.Row():
                with gr.Column(scale=1):
                    activity_theme_input = gr.Textbox(
                        label="活动主题（可选）",
                        placeholder="例：雨天室内亲子手作",
                        info="留空则 AI 根据天气和节假日自动创意"
                    )
                    generate_activity_btn = gr.Button("生成活动方案", variant="primary")
                
                with gr.Column(scale=2):
                    activity_output = gr.Markdown(label="完整活动策划包", show_copy_button=True)
            
            generate_activity_btn.click(
                fn=generate_activity_plan,
                inputs=[activity_theme_input],
                outputs=activity_output
            )
        
        # Tab 3: 口碑诊疗所
        with gr.TabItem("口碑管理引擎"):
            with gr.Row():
                gr.Markdown(
                    """**定位**：舆情分析与服务质量提升顾问。\n\n"
                    **核心理念**：关注体验感修复，提供可落地的物理整改建议。""",
                    elem_classes=["info-box"]
                )
            
            with gr.Row():
                with gr.Column(scale=1):
                    review_input = gr.Textbox(
                        label="游客评价内容",
                        placeholder="粘贴游客的差评或建议...",
                        lines=6
                    )
                    analyze_review_btn = gr.Button("分析评价", variant="primary")
                
                with gr.Column(scale=2):
                    review_output = gr.Markdown(label="诊断报告与回复建议", show_copy_button=True)
            
            analyze_review_btn.click(
                fn=analyze_review,
                inputs=[review_input],
                outputs=review_output
            )
        
        # Tab 4: 营销推广员
        with gr.TabItem("营销推广引擎"):
            gr.Markdown(
                """**定位**：全渠道营销物料自动生成器。\n\n"
                **核心理念**：视觉风格符合国风，文案侧重生活方式而非价格战。""",
                elem_classes=["info-box"]
            )
            
            # 上部区域：营销方案生成
            gr.Markdown("### 📦 全渠道营销文案")
            with gr.Row():
                    with gr.Column(scale=1):
                        campaign_theme_input = gr.Textbox(
                            label="营销主题（可选）",
                            placeholder="例：端午文化节 / 新品上市",
                            info="留空则结合节假日自动生成"
                        )
                        generate_marketing_btn = gr.Button("生成营销物料包", variant="primary")
                    
                    with gr.Column(scale=2):
                        marketing_output = gr.Markdown(label="全渠道营销文案", show_copy_button=True)
            
            gr.Markdown("---")
            
            # 中部区域：海报生成
            gr.Markdown("### 🖼️ AI 海报生成")
            with gr.Row():
                    with gr.Column(scale=1):
                        poster_prompt_output = gr.Textbox(
                            label="海报设计提示词",
                            lines=3,
                            info="复制此提示词到 AI 绘图工具生成海报"
                        )
                        generate_poster_btn = gr.Button("生成海报", variant="primary")
                    
                    with gr.Column(scale=2):
                        poster_image_output = gr.Image(label="海报图片", height=400)
            
            gr.Markdown("---")
            
            # 下部区域：包装设计升级
            gr.Markdown("### 🎨 产品包装设计升级")
            gr.Markdown(
                """**说明**：请上传您家产品的实拍照片，AI 将基于产品特征进行包装设计升级。
                
**为什么需要产品图片？**
- ✅ AI 分析产品形态、材质、现有配色
- ✅ 识别产品档次和定位
- ✅ 生成与产品匹配的包装设计方案
- ✅ 避免设计与实物不符的情况

**拍照建议**：
- 📸 清晰展示产品全貌和细节
- 💡 光线充足，背景简洁
- 🎯 多角度拍摄（正面、侧面、顶部）"""
            )
            
            with gr.Row():
                with gr.Column(scale=1):
                    product_image_input = gr.Image(
                        label="📷 上传产品图片",
                        type="pil",
                        sources=["upload", "clipboard"],
                        info="请上传您家产品的实拍照片（必填）"
                    )
                    
                    packaging_product = gr.Textbox(
                        label="产品名称",
                        placeholder="例：西湖龙井·明前特级",
                        info="需要重新设计包装的产品"
                    )
                    design_style = gr.Dropdown(
                        label="设计风格",
                        choices=["宋韵极简", "国潮插画", "西湖十景", "非遗传统", "现代中式", "禅意美学"],
                        value="宋韵极简",
                        info="选择您喜欢的包装风格"
                    )
                    cultural_elements = gr.Textbox(
                        label="文化元素",
                        placeholder="例：龙井茶园、西湖山水、宋代点茶",
                        info="希望融入的当地文化元素"
                    )
                    extra_requirements = gr.Textbox(
                        label="额外要求（可选）",
                        placeholder="例：希望用绿色为主色调，体现生态环保理念",
                        lines=2
                    )
                    generate_packaging_btn = gr.Button("生成包装设计", variant="primary", size="lg")
                
                with gr.Column(scale=2):
                    gr.Markdown("**产品包装设计效果**")
                    
                    with gr.Row():
                        main_design_image = gr.Image(label="主包装设计")
                        gift_bag_image = gr.Image(label="礼品袋设计")
                    
                    card_image = gr.Image(label="明信片/卡片设计")
                    design_explanation = gr.Markdown(label="设计理念说明", show_copy_button=True)
            
            generate_marketing_btn.click(
                fn=generate_marketing_materials,
                inputs=[campaign_theme_input],
                outputs=[marketing_output, poster_prompt_output]
            )
            
            generate_poster_btn.click(
                fn=generate_poster_image,
                inputs=[poster_prompt_output],
                outputs=poster_image_output
            )
            
            # 绑定包装设计事件
            generate_packaging_btn.click(
                fn=generate_packaging_design,
                inputs=[product_image_input, packaging_product, design_style, cultural_elements, extra_requirements],
                outputs=[main_design_image, gift_bag_image, card_image, design_explanation]
            )

        # Tab 5: 商家小助手
        with gr.TabItem("商家小助手"):
            gr.Markdown(
                """**智能助手**：基于您的店铺信息，随时解答运营问题，提供专业建议。

**可以问我**：
- 如何提升店铺的文化氛围？
- 最近有什么适合的活动策划？
- 如何处理游客的投诉？
- 怎样写更有吸引力的营销文案？
- 其他任何关于店铺运营的问题...
""",
                elem_classes=["info-box"]
            )
            
            chatbot = gr.Chatbot(
                label="与助手对话",
                height=400,
                show_copy_button=True,
                avatar_images=(
                    None,
                    "https://img.alicdn.com/imgextra/i2/O1CN01KZz8xY1VlUJmVEtjP_!!6000000002693-0-tps-200-200.jpg"
                )
            )
            
            with gr.Row():
                with gr.Column(scale=4):
                    assistant_input = gr.Textbox(
                        label="输入问题",
                        placeholder="请输入您的问题，例如：如何提升店铺的文化氛围？",
                        lines=2
                    )
                with gr.Column(scale=1):
                    send_btn = gr.Button("发送", variant="primary")
            
            clear_btn = gr.Button("清空对话", size="sm")
            
            # 绑定事件
            send_btn.click(
                fn=chat_with_assistant,
                inputs=[assistant_input, chatbot],
                outputs=[assistant_input, chatbot]
            )
            
            assistant_input.submit(
                fn=chat_with_assistant,
                inputs=[assistant_input, chatbot],
                outputs=[assistant_input, chatbot]
            )
            
            clear_btn.click(
                fn=lambda: ("", []),
                inputs=None,
                outputs=[assistant_input, chatbot]
            )
    
    # 底部说明
    gr.HTML('''
    <div style="text-align: center; padding: 30px 20px; border-top: 1px solid #e5e7eb; margin-top: 40px; color: #6b7280; font-size: 13px;">
        <p style="margin: 0;">© 2026 基于英特尔 OpenVINO 的本地文旅商家智能助手</p>
        <p style="margin: 4px 0 0 0;">Powered by OpenVINO, ModelScope</p>
    </div>
    ''')


if __name__ == "__main__":
    # 启动应用
    demo.launch(
        server_name="localhost",
        server_port=7860,
        share=False,  # 如需公开分享设为 True
        inbrowser=True,
    )

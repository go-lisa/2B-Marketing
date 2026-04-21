---
name: tourism-assistant-demo
description: Execute the local tourism SMB assistant powered by Intel OpenVINO. This skill demonstrates 8 core AI features including cultural story generation, multilingual translation, video script creation, activity planning, reputation management, marketing materials generation, and poster image generation. All processing is done locally with no API costs.
---

# 基于英特尔 OpenVINO 的本地文旅商家智能助手

## 技能描述

本技能自动化执行"基于英特尔 OpenVINO 的本地文旅商家智能助手"项目，提供 8 大核心 AI 功能。所有处理均在本地完成，无需网络连接，零成本使用。

**核心功能：**
- 📋 构建商家数字档案（必须首先执行）
- 📖 生成文化故事（支持多模态）
- 🌍 国际化营销引擎（多语言翻译）
- 🎬 短视频脚本创作
- 🎯 体验策划引擎（活动方案生成）
- 💬 口碑管理引擎（评价分析与回复）
- 📢 全渠道营销物料构建
- 🖼️ AI 海报生成（输出图片文件）

**技术特色：**
- ✅ 完全本地运行，数据隐私保护
- ✅ 基于英特尔 OpenVINO 加速推理
- ✅ 零成本，无需 API Key
- ✅ 离线可用，无网络依赖

## 前置要求

### 系统要求
- **操作系统**: Windows 10/11, Linux, 或 macOS
- **Python**: 3.8 - 3.11
- **处理器**: Intel CPU 系列
- **内存**: 最低 16 GB，推荐 32 GB
- **存储**: 至少 20 GB 可用空间（模型文件约 12 GB）

### 依赖工具
- Git（用于克隆代码仓库）
- pip（Python 包管理器）

## 执行步骤

### 步骤 1: 克隆项目代码

```bash
git clone https://github.com/go-lisa/2B-Marketing.git
cd 2B-Marketing
```

**注意**: 如果 `cd 2B-Marketing` 执行出错，请手动找到刚才拉取的项目目录并进入。

### 步骤 2: 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 步骤 3: 下载模型文件

```bash
# 创建模型目录
mkdir -p lab1-multimodal-vlm
mkdir -p lab4-image-generation

# 使用 Python 脚本下载模型（严格按照 demo-notebook.ipynb 顺序）
python3 << 'EOF'
from pathlib import Path

# 下载 Qwen3-VL 多模态模型
model_dir = Path("lab1-multimodal-vlm/Qwen3-VL-4B-Instruct-int4-ov")
if not model_dir.exists():
    print("正在下载 Qwen3-VL 模型...")
    from modelscope import snapshot_download
    snapshot_download("snake7gun/Qwen3-VL-4B-Instruct-int4-ov", local_dir=str(model_dir))
    print(f"✅ Qwen3-VL 模型已下载到: {model_dir}")
else:
    print(f"✅ Qwen3-VL 模型已存在，跳过下载")

# 下载 Z-Image-Turbo 图像生成模型
model_dir = Path("lab4-image-generation/Z-Image-Turbo-int4-ov")
if not model_dir.exists():
    print("正在下载 Z-Image-Turbo 模型...")
    from modelscope import snapshot_download
    snapshot_download("snake7gun/Z-Image-Turbo-int4-ov", local_dir=str(model_dir))
    print(f"✅ Z-Image-Turbo 模型已下载到: {model_dir}")
else:
    print(f"✅ Z-Image-Turbo 模型已存在，跳过下载")

print("\n🎉 所有模型下载完成！")
EOF
```

**说明：**
- 首次下载约需 10-15 GB 存储空间
- 下载时间取决于网络速度（通常 10-30 分钟）
- 如果模型已存在，会自动跳过下载

### 步骤 4: 环境导入和初始化

创建 `init_env.py` 文件：

```python
"""环境初始化模块 - 必须在所有功能之前执行"""
import sys
from pathlib import Path

# 确保在 2B-Marketing 目录下运行
project_root = Path(".").resolve()
if not (project_root / "state_manager.py").exists():
    print("⚠️  请在 2B-Marketing/ 目录下运行")
    sys.exit(1)

# 导入项目模块
from state_manager import global_context, create_demo_case
from api_service_local import llm_service, wanx_service
from prompt_templates import PromptTemplates

print("✅ 模块导入成功")
print(f"📍 项目路径: {project_root}")
```

---

## 🎯 核心功能（可独立调用）

**重要说明：**
- ⚠️ **每次调用任何功能前，必须先执行「构建数字档案」**
- ✅ 每个功能都可以独立调用，不需要按顺序执行
- 📝 文本结果直接输出到控制台
- 🖼️ 图片结果保存到文件，可直接读取展示

### 功能 0: 构建数字档案（必须首先执行）

**这是所有功能的前置条件，每次会话开始时必须先执行！**

创建 `setup_profile.py`：

```python
"""构建商家数字档案 - 必须在其他功能之前执行"""
from init_env import *

# 加载预设的演示案例
demo_case_name = "西湖绸伞店"  # 可选：西湖绸伞店、满觉陇民宿、龙井茶庄

case_data = create_demo_case(demo_case_name)

# 更新全局上下文
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

print("=" * 60)
print("📋 商家数字档案已加载")
print("=" * 60)
print(summary)
print("\n✅ 可以开始使用各智能引擎！")
```

**执行方式：**
```bash
python setup_profile.py
```

---

### 功能 1: 生成文化故事

创建 `generate_story.py`：

```python
"""生成文化故事"""
from init_env import *

# 测试商品名称
product_name = "西湖绸伞·经典款"
story_type = "游客版"  # 可选：游客版、专家版

print(f"🎨 正在为 '{product_name}' 生成{story_type}文化故事...")
print("-" * 60)

# 调用文化内容引擎
context = global_context.to_prompt_context()
system_prompt = PromptTemplates.get_content_engine_prompt(context)

user_prompt = f"""请为商品/景点"{product_name}"生成{story_type}文化故事。

要求：
1. 深入挖掘产品背后的历史文化、工艺细节、情感寓意
2. 结合我店的特色和地理位置，突出独特性
3. {story_type}版本要{"通俗易懂、引发情感共鸣" if story_type == "游客版" else "专业深度、详细工艺细节"}
4. 字数：500-800 字"""

result = llm_service.generate(system_prompt, user_prompt)

# 保存结果
global_context.save_engine_result("content", {"type": "故事", "content": result})

print(result)
print("\n✅ 文化故事生成完成")
```

**执行方式：**
```bash
python generate_story.py
```

---

### 功能 2: 国际化营销引擎（多语言翻译）

创建 `multilingual_translation.py`：

```python
"""国际化营销引擎 - 多语言翻译"""
from init_env import *

# 使用上一步生成的故事内容进行翻译
target_language = "英文"

print(f"🌍 正在将文化故事翻译成{target_language}...")
print("-" * 60)

# 提取上一步的故事内容（简化示例，实际使用时可以传入具体内容）
sample_content = """西湖绸伞，又称"西湖纸伞"，是杭州传统手工艺品的代表之一。
始于南宋时期，已有800多年历史。伞面采用特制桑皮纸，
伞骨选用江南特产淡竹，经过72道工序精心制作而成。
每一把绸伞都承载着江南水乡的诗意与浪漫。"""

context = global_context.to_prompt_context()
system_prompt = PromptTemplates.get_content_engine_prompt(context)

user_prompt = f"""请将以下内容翻译成{target_language}，并进行文化背景解释：

原文：
{sample_content}

要求：
1. 不仅要翻译字面意思，更要解释文化内涵
2. 对于特有文化概念（如非遗技艺、历史典故），提供简短的背景说明
3. 给出商家使用外文内容的真实场景指引
4. 格式：先翻译，再解释关键文化概念，最后给出店员的实践指导
"""

translation_result = llm_service.generate(system_prompt, user_prompt)

print(translation_result)
print("\n✅ 多语言翻译完成")
```

**执行方式：**
```bash
python multilingual_translation.py
```

---

### 功能 3: 短视频脚本

创建 `video_script.py`：

```python
"""短视频脚本创作"""
from init_env import *

product_name = "西湖绸伞·经典款"

print(f"🎬 正在为 '{product_name}' 创作短视频脚本...")
print("-" * 60)

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

script_result = llm_service.generate(system_prompt, user_prompt)
global_context.save_engine_result("content", {"type": "视频脚本", "content": script_result})

print(script_result)
print("\n✅ 短视频脚本生成完成")
```

**执行方式：**
```bash
python video_script.py
```

---

### 功能 4: 体验策划引擎

创建 `activity_planning.py`：

```python
"""体验策划引擎 - 生成活动方案"""
from init_env import *

activity_theme = ""  # 留空让 AI 自主创意，或指定主题如"端午文化节"

print("🎯 正在生成店内微活动方案...")
print("-" * 60)

context = global_context.to_prompt_context()
system_prompt = PromptTemplates.get_planning_engine_prompt(context)

user_prompt = f"""请设计一个店内微活动方案。
{"活动主题：" + activity_theme if activity_theme else "请根据当前天气和节假日自主创意"}

要求：
1. 充分利用在地资源和现有场地
2. 强调文化体验和互动参与
3. 方案要切实可行，成本低
4. 输出完整的活动策划包"""

activity_result = llm_service.generate(system_prompt, user_prompt)
global_context.save_engine_result("planning", {"type": "活动方案", "content": activity_result})

print(activity_result)
print("\n✅ 活动方案生成完成")
```

**执行方式：**
```bash
python activity_planning.py
```

---

### 功能 5: 口碑管理引擎

创建 `reputation_management.py`：

```python
"""口碑管理引擎 - 评价分析"""
from init_env import *

# 模拟一条游客评价
review_text = """昨天去了这家店，环境还不错，但是服务员态度有点冷淡。
我问了几个关于产品的问题，回答得很敷衍。
不过产品本身质量还可以，就是感觉缺乏文化讲解。
希望店家能加强员工培训吧。"""

print("💬 正在分析游客评价...")
print("-" * 60)
print(f"评价内容：\n{review_text}\n")
print("-" * 60)

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

review_result = llm_service.generate(system_prompt, user_prompt)
global_context.save_engine_result("operation", {"type": "评价分析", "content": review_result})

print(review_result)
print("\n✅ 评价分析完成")
```

**执行方式：**
```bash
python reputation_management.py
```

---

### 功能 6: 全渠道营销物料构建

创建 `marketing_materials.py`：

```python
"""全渠道营销物料构建"""
from init_env import *

campaign_theme = ""  # 当日主题

print("📢 正在生成全渠道营销物料...")
print("-" * 60)

context = global_context.to_prompt_context()
system_prompt = PromptTemplates.get_marketing_engine_prompt(context)

user_prompt = f"""请为我店生成全渠道营销物料。
{"营销主题：" + campaign_theme if campaign_theme else "默认：端午节"}

要求：
1. 海报设计提示词（用于 AI 绘图）
2. 朋友圈文案 3 个版本
3. 小红书种草文案
4. 公众号推文大纲
5. 私域引流话术

请结构化输出所有内容。"""

marketing_result = llm_service.generate(system_prompt, user_prompt)
global_context.save_engine_result("marketing", {"type": "营销物料", "content": marketing_result})

print(marketing_result)
print("\n✅ 营销物料生成完成")
```

**执行方式：**
```bash
python marketing_materials.py
```

---

### 功能 7: 海报生成

创建 `generate_poster.py`：

```python
"""海报生成 - 输出图片文件"""
from init_env import *
from PIL import Image

# 从营销物料中提取海报提示词（这里使用示例提示词）
poster_prompt = f"""新中式风格海报，{global_context.shop_name}，
融合{global_context.features}元素，
{global_context.holiday}节日氛围，
高品质商业摄影风格，暖色调，细节精致"""

print("🖼️  正在生成海报图片...")
print(f"提示词：{poster_prompt[:100]}...")
print("-" * 60)

# 调用图像生成服务
poster_image = wanx_service.generate_poster(poster_prompt, size="512*512")

if poster_image:
    # 保存图片到文件
    output_path = "generated_poster.png"
    poster_image.save(output_path, format='PNG')
    print(f"\n✅ 海报图片生成完成！")
    print(f"📁 图片已保存到: {output_path}")
    print(f"💡 可直接读取此图片文件展示给用户")
else:
    print("❌ 海报图片生成失败")
```

**执行方式：**
```bash
python generate_poster.py
```

**输出：**
- 生成文件：`generated_poster.png`
- 可直接读取并展示此图片

---

## 📊 调用示例

### 完整流程（按顺序执行）

```bash
# 1. 环境准备
git clone https://github.com/go-lisa/2B-Marketing.git
cd 2B-Marketing
pip install -r requirements.txt

# 下载模型（首次需要）
mkdir -p lab1-multimodal-vlm lab4-image-generation
python3 -c "
from pathlib import Path
from modelscope import snapshot_download
for model_name, model_dir in [
    ('snake7gun/Qwen3-VL-4B-Instruct-int4-ov', 'lab1-multimodal-vlm/Qwen3-VL-4B-Instruct-int4-ov'),
    ('snake7gun/Z-Image-Turbo-int4-ov', 'lab4-image-generation/Z-Image-Turbo-int4-ov')
]:
    if not Path(model_dir).exists():
        snapshot_download(model_name, local_dir=model_dir)
"

# 2. 构建数字档案（必须首先执行）
python setup_profile.py

# 3. 按需调用各个功能
python generate_story.py              # 生成文化故事
python multilingual_translation.py    # 多语言翻译
python video_script.py                # 短视频脚本
python activity_planning.py           # 体验策划
python reputation_management.py       # 口碑管理
python marketing_materials.py         # 营销物料
python generate_poster.py             # 海报生成（输出图片文件）
```

### 独立调用示例

**场景 1: 只生成文化故事**
```bash
python setup_profile.py        # 必须先执行
python generate_story.py       # 然后调用所需功能
```

**场景 2: 生成营销物料和海报**
```bash
python setup_profile.py            # 必须先执行
python marketing_materials.py      # 生成文案
python generate_poster.py          # 生成海报图片
# 读取 generated_poster.png 展示给用户
```

**场景 3: 口碑分析**
```bash
python setup_profile.py            # 必须先执行
python reputation_management.py    # 分析评价
```

---

## 📁 输出文件说明

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `generated_poster.png` | 图片 | AI 生成的海报，可直接读取展示 |
| 控制台输出 | 文本 | 所有功能的文本结果直接输出到控制台 |

**可以直接：**
- ✅ 读取控制台输出的文本结果
- ✅ 读取 `generated_poster.png` 并展示图片
- ✅ 根据用户需求灵活调用不同功能

---

## 🔧 故障排除

### 问题 1: 模型文件未找到

**错误信息**: `FileNotFoundError: 模型路径不存在`

**解决方案**:
```bash
# 确认模型文件位置
ls -la lab1-multimodal-vlm/Qwen3-VL-4B-Instruct-int4-ov/
ls -la lab4-image-generation/Z-Image-Turbo-int4-ov/

# 如果不存在，重新下载
python3 -c "
from modelscope import snapshot_download
snapshot_download('snake7gun/Qwen3-VL-4B-Instruct-int4-ov', local_dir='lab1-multimodal-vlm/Qwen3-VL-4B-Instruct-int4-ov')
snapshot_download('snake7gun/Z-Image-Turbo-int4-ov', local_dir='lab4-image-generation/Z-Image-Turbo-int4-ov')
"
```

### 问题 2: 内存不足

**错误信息**: `RuntimeError: Not enough memory`

**解决方案**:
- 关闭其他占用内存的程序
- 增加虚拟内存（页面文件）
- 考虑升级到 32 GB 内存

### 问题 3: 依赖安装失败

**解决方案**:
```bash
# 升级 pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

---

## 📈 性能参考

### CPU 模式（Intel i7-12700）
- **文本生成**: 5-10 tokens/秒
- **图片生成**: 2-5 分钟/张（512x512）
- **内存占用**: 12-16 GB

### GPU 模式（Intel Arc A770）
- **文本生成**: 15-30 tokens/秒
- **图片生成**: 30-60 秒/张（512x512）
- **内存占用**: 8-12 GB

---

## 📝 许可证

MIT License

## 🙏 致谢

- **英特尔 OpenVINO 团队** - 提供强大的推理引擎
- **ModelScope** - 提供高质量的开源模型
- **Qwen 团队** - Qwen3-VL 多模态大模型
- **Z-Image 团队** - Z-Image-Turbo 图像生成模型

---

**© 2026 基于英特尔 OpenVINO 的本地文旅商家智能助手** | 让文化赋能每一家小微文旅企业

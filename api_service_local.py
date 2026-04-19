"""
本地 OpenVINO 模型服务模块
使用 Qwen3-VL（文本+多模态）和 Z-Image-Turbo（图像生成）替代远程 API
"""
from pathlib import Path
import torch
from PIL import Image
import tempfile
import os


class LLMService:
    """本地 LLM 服务 - 基于 Qwen3-VL OpenVINO 模型"""
    
    def __init__(self, model_path=None, device="CPU"):
        """
        初始化本地 LLM 服务
        
        Args:
            model_path: Qwen3-VL 模型路径，默认为 lab1-multimodal-vlm/Qwen3-VL-4B-Instruct-int4-ov
            device: 推理设备（CPU/GPU）
        """
        if model_path is None:
            # 默认模型路径（相对于 code 目录的上一级）
            model_path = Path(__file__).parent.parent / "lab1-multimodal-vlm" / "Qwen3-VL-4B-Instruct-int4-ov"
        
        self.model_path = Path(model_path)
        self.device = device
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"模型路径不存在: {self.model_path}")
        
        # 延迟加载模型（首次调用时加载）
        self._model = None
        self._processor = None
        self._load_model()
    
    def _load_model(self):
        """加载 OpenVINO 模型"""
        try:
            from optimum.intel.openvino import OVModelForVisualCausalLM
            from transformers import AutoProcessor
            
            print(f"正在加载 Qwen3-VL 模型...")
            print(f"模型路径: {self.model_path}")
            print(f"推理设备: {self.device}")
            
            # 加载处理器
            min_pixels = 256 * 28 * 28
            max_pixels = 1280 * 28 * 28
            self._processor = AutoProcessor.from_pretrained(
                self.model_path, 
                min_pixels=min_pixels, 
                max_pixels=max_pixels
            )
            
            # 加载 OpenVINO 模型
            self._model = OVModelForVisualCausalLM.from_pretrained(
                self.model_path, 
                device=self.device
            )
            
            print("✅ Qwen3-VL 模型加载完成")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {str(e)}")
            raise
    
    def generate(self, system_prompt, user_prompt, max_tokens=2000, temperature=0.7):
        """
        调用本地 LLM 生成文本
        
        Args:
            system_prompt: 系统提示词（角色设定）
            user_prompt: 用户输入
            max_tokens: 最大生成长度
            temperature: 温度参数（当前 OpenVINO 模型暂不支持）
            
        Returns:
            生成的文本内容
        """
        try:
            # 构建对话消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [{"type": "text", "text": user_prompt}]}
            ]
            
            # 应用聊天模板
            text = self._processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # 处理输入
            inputs = self._processor(
                text=[text], 
                images=None, 
                videos=None, 
                padding=True, 
                return_tensors="pt"
            )
            
            # 生成文本
            generated_ids = self._model.generate(
                **inputs, 
                max_new_tokens=max_tokens,
                do_sample=(temperature > 0),
                temperature=temperature if temperature > 0 else 1.0
            )
            
            # 解码输出（保留特殊标记以便后续处理）
            response = self._processor.batch_decode(
                generated_ids, 
                skip_special_tokens=False
            )[0]
            
            # 提取助手回复（去除 prompt 部分）
            # Qwen 格式：<|im_start|>system...<|im_end|><|im_start|>user...<|im_end|><|im_start|>assistant...
            if "<|im_start|>assistant" in response:
                # 提取 assistant 之后的内容
                response = response.split("<|im_start|>assistant")[-1]
                # 移除结束标记
                response = response.replace("<|im_end|>", "").strip()
            elif "<|assistant|>" in response:
                # 备用格式
                response = response.split("<|assistant|>")[-1].strip()
            
            return response
                
        except Exception as e:
            return f"生成出错：{str(e)}"
    
    def generate_with_image(self, system_prompt, user_prompt, image_path=None, max_tokens=2000, temperature=0.7):
        """
        调用本地 LLM 生成文本（支持图片输入）
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户输入文本
            image_path: 可选的图片路径
            max_tokens: 最大生成长度
            temperature: 温度参数
            
        Returns:
            生成的文本内容
        """
        try:
            # 构建对话消息
            content_items = []
            
            if image_path and Path(image_path).exists():
                # 添加图片
                content_items.append({"type": "image", "image": str(image_path)})
            
            # 添加文本
            content_items.append({"type": "text", "text": user_prompt})
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content_items}
            ]
            
            # 应用聊天模板并处理视觉信息
            from qwen_vl_utils import process_vision_info
            
            text = self._processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            image_inputs, video_inputs = process_vision_info(messages)
            
            # 处理输入
            inputs = self._processor(
                text=[text], 
                images=image_inputs, 
                videos=video_inputs, 
                padding=True, 
                return_tensors="pt"
            )
            
            # 生成文本
            generated_ids = self._model.generate(
                **inputs, 
                max_new_tokens=max_tokens,
                do_sample=(temperature > 0),
                temperature=temperature if temperature > 0 else 1.0
            )
            
            # 解码输出（保留特殊标记以便后续处理）
            response = self._processor.batch_decode(
                generated_ids, 
                skip_special_tokens=False
            )[0]
            
            # 提取助手回复
            # Qwen 格式：<|im_start|>system...<|im_end|><|im_start|>user...<|im_end|><|im_start|>assistant...
            if "<|im_start|>assistant" in response:
                # 提取 assistant 之后的内容
                response = response.split("<|im_start|>assistant")[-1]
                # 移除结束标记
                response = response.replace("<|im_end|>", "").strip()
            elif "<|assistant|>" in response:
                # 备用格式
                response = response.split("<|assistant|>")[-1].strip()
            
            return response
                
        except Exception as e:
            return f"生成出错：{str(e)}"


class WanxService:
    """本地图像生成服务 - 基于 Z-Image-Turbo OpenVINO 模型"""
    
    def __init__(self, model_path=None, device="CPU"):
        """
        初始化本地图像生成服务
        
        Args:
            model_path: Z-Image-Turbo 模型路径，默认为 lab4-image-generation/Z-Image-Turbo-int4-ov
            device: 推理设备（CPU/GPU）
        """
        if model_path is None:
            # 默认模型路径（相对于 code 目录的上一级）
            model_path = Path(__file__).parent.parent / "lab4-image-generation" / "Z-Image-Turbo-int4-ov"
        
        self.model_path = Path(model_path)
        self.device = device
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"模型路径不存在: {self.model_path}")
        
        # 延迟加载模型（首次调用时加载）
        self._pipe = None
        self._load_model()
    
    def _load_model(self):
        """加载 OpenVINO 图像生成模型"""
        try:
            from optimum.intel import OVZImagePipeline
            
            print(f"正在加载 Z-Image-Turbo 模型...")
            print(f"模型路径: {self.model_path}")
            print(f"推理设备: {self.device}")
            
            # 加载 OpenVINO Pipeline
            self._pipe = OVZImagePipeline.from_pretrained(
                self.model_path, 
                device=self.device
            )
            
            print("✅ Z-Image-Turbo 模型加载完成")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {str(e)}")
            raise
    
    def generate_poster(self, prompt, size="1024*1024"):
        """
        生成海报图片
        
        Args:
            prompt: 生成提示词
            size: 图片尺寸（格式："1024*1024" 或 "1024x1024"）
            
        Returns:
            PIL Image 对象（而非 URL）
        """
        try:
            # 解析尺寸
            if "*" in size:
                width, height = map(int, size.split("*"))
            elif "x" in size.lower():
                width, height = map(int, size.lower().split("x"))
            else:
                width, height = 1024, 1024
            
            print(f"正在生成图片: {width}x{height}")
            print(f"提示词: {prompt[:100]}...")
            
            # 生成图片
            result = self._pipe(
                prompt=prompt,
                height=height,
                width=width,
                num_inference_steps=6,
                guidance_scale=0.0,
                generator=torch.Generator("cpu").manual_seed(42),
            )
            
            image = result.images[0]
            print("✅ 图片生成完成")
            
            return image
                
        except Exception as e:
            print(f"图片生成失败：{str(e)}")
            return None
    
    def generate_packaging_design(self, product_name, style, cultural_elements, prompt_extra=""):
        """
        生成产品包装设计（系列图）
        
        Args:
            product_name: 产品名称
            style: 设计风格
            cultural_elements: 文化元素
            prompt_extra: 额外提示词
            
        Returns:
            dict: 包含主设计图和延展设计的 PIL Image 对象
        """
        try:
            designs = {}
            
            # 1. 主包装设计
            main_prompt = f"""高品质产品包装设计，{product_name}，
风格：{style}，
文化元素：{cultural_elements}，
专业商业摄影，影棚灯光，细节精致，高端质感，8K 超高清"""
            
            if prompt_extra:
                main_prompt += f"，{prompt_extra}"
            
            designs['main'] = self.generate_poster(main_prompt, "512*512")
            
            # 2. 礼品袋设计
            gift_bag_prompt = f"""配套礼品袋设计，{product_name}，
风格：{style}，
图案：{cultural_elements}，
展开平面图，白色背景，专业设计稿"""
            
            designs['gift_bag'] = self.generate_poster(gift_bag_prompt, "512*512")
            
            # 3. 明信片/卡片设计
            card_prompt = f"""配套明信片设计，{product_name}，
风格：{style}，
主题：{cultural_elements}，
精美插画，留白区域用于书写，文艺风格"""
            
            designs['card'] = self.generate_poster(card_prompt, "512*512")
            
            return designs
            
        except Exception as e:
            print(f"包装设计生成失败：{str(e)}")
            return None


# 创建服务实例（使用 CPU 设备，如需 GPU 可改为 "GPU"）
llm_service = LLMService(device="CPU")
wanx_service = WanxService(device="CPU")

"""
EchoMate AI agent v1.1 - 核心引擎
基于成就动机理论的三层式 Prompt 链分析引擎

支持的模型提供商：
- Anthropic (Claude)
- OpenAI (GPT-4)
- 通义千问 (Qwen)
- Kimi (月之暗面)
- 豆包 (Doubao)
- 智谱 AI (GLM)
- 百度文心一言
- Ollama (本地模型)
- 自定义 OpenAI 兼容 API
"""

import json
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from prompts.system_prompts import PERCEPTION_LAYER_PROMPT, REASONING_LAYER_PROMPT, GENERATION_LAYER_PROMPT


# ==================== 模型配置 ====================

MODEL_CONFIGS = {
    # 国际模型
    "anthropic": {
        "display_name": "Anthropic Claude",
        "default_model": "claude-sonnet-4-20250514",
        "base_url": "https://api.anthropic.com",
        "auth_header": "x-api-key",
    },
    "openai": {
        "display_name": "OpenAI GPT",
        "default_model": "gpt-4o",
        "base_url": "https://api.openai.com/v1",
    },

    # 国产大模型 (OpenAI 兼容格式)
    "qwen": {
        "display_name": "通义千问 (阿里云)",
        "default_model": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "env_var": "DASHSCOPE_API_KEY",
    },
    "kimi": {
        "display_name": "Kimi (月之暗面)",
        "default_model": "moonshot-v1-8k",
        "base_url": "https://api.moonshot.cn/v1",
    },
    "doubao": {
        "display_name": "豆包 (字节)",
        "default_model": "doubao-pro-4k",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    },
    "zhipu": {
        "display_name": "智谱 AI (GLM)",
        "default_model": "glm-4",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
    },
    "baichuan": {
        "display_name": "百川智能",
        "default_model": "Baichuan4",
        "base_url": "https://api.baichuan-ai.com/v1",
    },
    "deepseek": {
        "display_name": "深度求索",
        "default_model": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1",
    },
    "minimax": {
        "display_name": "MiniMax",
        "default_model": "abab6.5-chat",
        "base_url": "https://api.minimax.chat/v1",
    },

    # 本地模型
    "ollama": {
        "display_name": "Ollama (本地)",
        "default_model": "qwen2.5:7b",
        "base_url": "http://localhost:11434",
    },

    # 自定义
    "custom": {
        "display_name": "自定义 OpenAI 兼容 API",
        "default_model": "custom-model",
        "base_url": "",
    },
}


class DialogueStage(str, Enum):
    """对话阶段枚举"""
    ICE_BREAKING = "破冰期"
    INFORMATION_EXCHANGE = "信息交换期"
    EMOTIONAL_RESONANCE = "情感共振期"


class MomentumState(str, Enum):
    """动量状态枚举"""
    POSITIVE = "正向"
    NEUTRAL = "中性"
    NEGATIVE = "负向"


class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"


@dataclass
class PerceptionResult:
    """感知层分析结果"""
    anxiety_level: int
    psychological_tags: List[str]
    avoidance_indicators: List[str]
    self_handicapping_detected: bool
    confidence_score: float


@dataclass
class ReasoningResult:
    """推理层分析结果"""
    dialogue_stage: str
    dialogue_momentum: str
    resistance_factors: List[str]
    stagnation_cause: str
    attribution_pattern: str
    recommended_strategy: str
    confidence_score: float


@dataclass
class Suggestion:
    """对话建议"""
    id: int
    script: str
    rationale: str
    expected_response: str
    difficulty_level: str
    alignment_with_stage: str


@dataclass
class MetaGuidance:
    """元指导（心理引导）"""
    attribution_reframe: str
    confidence_builder: str


@dataclass
class GenerationResult:
    """生成层分析结果"""
    suggestions: List[Suggestion]
    meta_guidance: MetaGuidance


@dataclass
class AnalysisResult:
    """完整分析结果"""
    perception: PerceptionResult
    reasoning: ReasoningResult
    generation: GenerationResult
    timestamp: str
    user_input: str
    conversation_history: List[Dict[str, str]]
    user_mbti: Optional[str] = None
    other_mbti: Optional[str] = None


class DatingAgentEngine:
    """
    EchoMate AI agent v1.1 核心引擎

    基于成就动机理论、自我妨碍理论和归因训练原理，
    通过三层式 Prompt 链分析用户对话，生成具体可执行的建议。
    """

    # Prompt 模板从 prompts.system_prompts 模块导入
    # - PERCEPTION_LAYER_PROMPT
    # - REASONING_LAYER_PROMPT
    # - GENERATION_LAYER_PROMPT

    def __init__(
        self,
        model_provider: str = "qwen",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None
    ):
        """
        初始化 Agent 引擎

        Args:
            model_provider: 模型提供商
                - "anthropic": Anthropic Claude
                - "openai": OpenAI GPT-4
                - "qwen": 通义千问 (阿里云)
                - "kimi": Kimi (月之暗面)
                - "doubao": 豆包 (字节)
                - "zhipu": 智谱 AI (GLM)
                - "baichuan": 百川智能
                - "deepseek": 深度求索
                - "minimax": MiniMax
                - "ollama": Ollama (本地)
                - "custom": 自定义 OpenAI 兼容 API
            api_key: API Key
            base_url: 自定义 API 基础 URL（仅 custom 模式需要）
            model_name: 自定义模型名称
            custom_headers: 自定义请求头
        """
        self.model_provider = model_provider.lower()
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.custom_headers = custom_headers or {}

        if self.model_provider not in MODEL_CONFIGS:
            raise ValueError(f"不支持的模型提供商：{self.model_provider}")

        self.config = MODEL_CONFIGS[self.model_provider]

    def _get_model_name(self) -> str:
        """获取模型名称"""
        return self.model_name or self.config.get("default_model", "unknown")

    def _get_base_url(self) -> str:
        """获取 API 基础 URL"""
        if self.model_provider == "custom" and self.base_url:
            return self.base_url
        return self.config.get("base_url", "")

    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """
        调用大模型 API

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词

        Returns:
            模型响应文本
        """
        if self.model_provider == "anthropic":
            return self._call_anthropic(prompt, system_prompt)
        elif self.model_provider == "ollama":
            return self._call_ollama(prompt, system_prompt)
        else:
            # 其他所有提供商都使用 OpenAI 兼容格式
            return self._call_openai_compatible(prompt, system_prompt)

    def _call_openai_compatible(self, prompt: str, system_prompt: str) -> str:
        """
        调用 OpenAI 兼容格式的 API
        支持：OpenAI, Qwen, Kimi, Doubao, Zhipu, Baichuan, DeepSeek, MiniMax, Custom
        """
        url = f"{self._get_base_url()}/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            **self.custom_headers
        }

        # 特殊处理：阿里云 DashScope 需要使用 X-DashScope-SSE 头
        if self.model_provider == "qwen":
            headers["X-DashScope-SSE"] = "disable"

        payload = {
            "model": self._get_model_name(),
            "messages": [
                {"role": "system", "content": system_prompt or "你是一位专业的心理学分析师。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500,
            "stream": False
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()

            # 提取响应内容
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            elif "data" in data and "choices" in data["data"]:
                return data["data"]["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"API 响应格式异常：{data}")

        except requests.exceptions.Timeout:
            raise TimeoutError("API 请求超时 (120 秒)，可能原因：\n1. 网络连接不稳定\n2. API 服务响应慢\n3. 请检查 API Key 是否正确")
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "401" in error_msg:
                raise RuntimeError("API Key 无效，请检查配置")
            elif "403" in error_msg:
                raise RuntimeError("API Key 无权限或 IP 被限制")
            elif "429" in error_msg:
                raise RuntimeError("API 请求频率超限，请稍后再试")
            elif "500" in error_msg:
                raise RuntimeError("API 服务内部错误，请稍后再试")
            else:
                raise RuntimeError(f"API 请求失败：{str(e)}")

    def _call_anthropic(self, prompt: str, system_prompt: str) -> str:
        """调用 Anthropic API"""
        url = "https://api.anthropic.com/v1/messages"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": self._get_model_name(),
            "max_tokens": 1500,
            "system": system_prompt or "你是一位专业的心理学分析师。",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
        except requests.exceptions.Timeout:
            raise TimeoutError("API 请求超时 (120 秒)，可能原因：\n1. 网络连接不稳定\n2. API 服务响应慢\n3. 请检查 API Key 是否正确")
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "401" in error_msg:
                raise RuntimeError("API Key 无效，请检查配置")
            elif "403" in error_msg:
                raise RuntimeError("API Key 无权限或 IP 被限制")
            elif "429" in error_msg:
                raise RuntimeError("API 请求频率超限，请稍后再试")
            elif "500" in error_msg:
                raise RuntimeError("API 服务内部错误，请稍后再试")
            else:
                raise RuntimeError(f"API 请求失败：{str(e)}")

    def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        """调用 Ollama API（本地模型）"""
        url = f"{self._get_base_url()}/api/chat"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "model": self._get_model_name(),
            "messages": [
                {"role": "system", "content": system_prompt or "你是一位专业的心理学分析师。"},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1500
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
        except requests.exceptions.Timeout:
            raise TimeoutError("API 请求超时，请确保 Ollama 服务正在运行")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API 请求失败：{str(e)}")

    def _extract_json(self, text: str) -> Dict:
        """从模型响应中提取 JSON"""
        import re
        json_pattern = r'\{[\s\S]*\}'
        match = re.search(json_pattern, text)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # 尝试修复常见的 JSON 错误
                json_str = json_str.replace("'", '"')
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                # 尝试使用更宽松的解析
                try:
                    import ast
                    return ast.literal_eval(json_str)
                except:
                    pass
                raise ValueError(f"JSON 解析失败")
        raise ValueError(f"无法从响应中提取 JSON")

    def analyze(
        self,
        user_input: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_mbti: Optional[str] = None,
        other_mbti: Optional[str] = None
    ) -> AnalysisResult:
        """
        执行三层式对话分析

        Args:
            user_input: 用户当前输入/想分析的对话内容
            conversation_history: 对话历史列表，每项包含 {"role": "user/other", "content": "..."}
            user_mbti: 用户的 MBTI 类型（可选）
            other_mbti: 对方的 MBTI 类型（可选）

        Returns:
            AnalysisResult: 完整分析结果
        """
        conversation_history = conversation_history or []

        # 构建 MBTI 相关信息
        mbti_info = ""
        if user_mbti and user_mbti != "未填写" and other_mbti and other_mbti != "未填写":
            mbti_info = f"\n\n## MBTI 性格信息\n- 用户 MBTI: {user_mbti}\n- 对方 MBTI: {other_mbti}\n\n请在分析中考虑双方性格差异对沟通方式的影响。"
        elif user_mbti and user_mbti != "未填写":
            mbti_info = f"\n\n## MBTI 性格信息\n- 用户 MBTI: {user_mbti}\n\n请在分析中考虑用户的性格特点。"
        elif other_mbti and other_mbti != "未填写":
            mbti_info = f"\n\n## MBTI 性格信息\n- 对方 MBTI: {other_mbti}\n\n请在分析中考虑对方的性格特点。"

        # Step 1: 感知层分析
        perception_prompt = self.PERCEPTION_LAYER_PROMPT.replace(
            "{{user_input}}", user_input
        ).replace(
            "{{conversation_history}}",
            str(conversation_history[-5:]) if conversation_history else "无"
        ).replace(
            "{{mbti_info}}", mbti_info if mbti_info else "无"
        )

        perception_text = self._call_llm(
            perception_prompt,
            "你是一位专业的心理学分析师，请严格按照 JSON 格式输出分析结果。"
        )
        perception_data = self._extract_json(perception_text)

        perception = PerceptionResult(
            anxiety_level=perception_data.get("anxiety_level", 5),
            psychological_tags=perception_data.get("psychological_tags", []),
            avoidance_indicators=perception_data.get("avoidance_indicators", []),
            self_handicapping_detected=perception_data.get("self_handicapping_detected", False),
            confidence_score=perception_data.get("confidence_score", 0.8)
        )

        # Step 2: 推理层分析
        reasoning_prompt = self.REASONING_LAYER_PROMPT.replace(
            "{{anxiety_level}}", str(perception.anxiety_level)
        ).replace(
            "{{psychological_tags}}", ", ".join(perception.psychological_tags)
        ).replace(
            "{{avoidance_indicators}}", ", ".join(perception.avoidance_indicators)
        ).replace(
            "{{conversation_history}}", str(conversation_history[-5:]) if conversation_history else "无"
        ).replace(
            "{{current_turn}}", user_input
        ).replace(
            "{{mbti_info}}", mbti_info if mbti_info else "无"
        )

        reasoning_text = self._call_llm(
            reasoning_prompt,
            "你是一位专业的心理学推理师，请严格按照 JSON 格式输出分析结果。"
        )
        reasoning_data = self._extract_json(reasoning_text)

        reasoning = ReasoningResult(
            dialogue_stage=reasoning_data.get("dialogue_stage", "破冰期"),
            dialogue_momentum=reasoning_data.get("dialogue_momentum", "中性"),
            resistance_factors=reasoning_data.get("resistance_factors", []),
            stagnation_cause=reasoning_data.get("stagnation_cause", ""),
            attribution_pattern=reasoning_data.get("attribution_pattern", ""),
            recommended_strategy=reasoning_data.get("recommended_strategy", ""),
            confidence_score=reasoning_data.get("confidence_score", 0.8)
        )

        # Step 3: 生成层分析
        generation_prompt = self.GENERATION_LAYER_PROMPT.replace(
            "{{dialogue_stage}}", reasoning.dialogue_stage
        ).replace(
            "{{dialogue_momentum}}", reasoning.dialogue_momentum
        ).replace(
            "{{resistance_factors}}", ", ".join(reasoning.resistance_factors)
        ).replace(
            "{{stagnation_cause}}", reasoning.stagnation_cause
        ).replace(
            "{{recommended_strategy}}", reasoning.recommended_strategy
        ).replace(
            "{{anxiety_level}}", str(perception.anxiety_level)
        ).replace(
            "{{mbti_info}}", mbti_info if mbti_info else "无"
        )

        generation_text = self._call_llm(
            generation_prompt,
            "你是一位专业的对话策略师，请严格按照 JSON 格式输出建议。"
        )
        generation_data = self._extract_json(generation_text)

        suggestions_data = generation_data.get("suggestions", [])
        suggestions = [
            Suggestion(
                id=s.get("id", i),
                script=s.get("script", ""),
                rationale=s.get("rationale", ""),
                expected_response=s.get("expected_response", ""),
                difficulty_level=s.get("difficulty_level", "中"),
                alignment_with_stage=s.get("alignment_with_stage", "")
            )
            for i, s in enumerate(suggestions_data, 1)
        ]

        meta_guidance_data = generation_data.get("meta_guidance", {})
        meta_guidance = MetaGuidance(
            attribution_reframe=meta_guidance_data.get("attribution_reframe", ""),
            confidence_builder=meta_guidance_data.get("confidence_builder", "")
        )

        generation = GenerationResult(
            suggestions=suggestions,
            meta_guidance=meta_guidance
        )

        return AnalysisResult(
            perception=perception,
            reasoning=reasoning,
            generation=generation,
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            conversation_history=conversation_history,
            user_mbti=user_mbti if user_mbti != "未填写" else None,
            other_mbti=other_mbti if other_mbti != "未填写" else None
        )

    def analyze_quick(self, user_input: str) -> Dict:
        """
        快速分析模式 - 返回简化结果

        Args:
            user_input: 用户输入

        Returns:
            简化版分析结果字典
        """
        result = self.analyze(user_input)

        return {
            "anxiety_level": result.perception.anxiety_level,
            "stage": result.reasoning.dialogue_stage,
            "suggestions": [
                {
                    "script": s.script,
                    "rationale": s.rationale
                }
                for s in result.generation.suggestions
            ],
            "meta_guidance": {
                "attribution_reframe": result.generation.meta_guidance.attribution_reframe,
                "confidence_builder": result.generation.meta_guidance.confidence_builder
            }
        }

    @staticmethod
    def get_available_providers() -> List[Dict]:
        """获取所有可用的模型提供商列表"""
        return [
            {
                "key": key,
                "name": config["display_name"],
                "default_model": config.get("default_model", ""),
                "base_url": config.get("base_url", "")
            }
            for key, config in MODEL_CONFIGS.items()
        ]

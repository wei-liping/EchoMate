"""
婚恋 AI Agent - 核心引擎
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


class DatingAgentEngine:
    """
    婚恋 AI Agent 核心引擎

    基于成就动机理论、自我妨碍理论和归因训练原理，
    通过三层式 Prompt 链分析用户对话，生成具体可执行的建议。
    """

    # ==================== Prompt 模板 ====================

    PERCEPTION_LAYER_PROMPT = """
# Role: 心理学 AI 分析师 - 感知层

## 任务描述
你是一位精通成就动机理论和自我妨碍（Self-Handicapping）理论的心理学分析师。
你的任务是分析用户的对话输入，识别其中的心理指标。

## 分析维度

### 1. 回避型措辞识别 (Avoidance Language)
检测以下模式：
- 模糊化表达："可能"、"也许"、"不太确定"
- 自我贬低前置："我不太会聊天，但是..."
- 话题转移尝试：主动改变话题以回避深度交流
- 延迟回复倾向：表达"不知道该怎么说"

### 2. 过度补偿行为 (Overcompensation)
检测以下模式：
- 过度解释：对简单问题给出冗长回答
- 讨好性表达：频繁使用"您觉得呢？""您说呢？"
- 完美主义倾向：反复修改自己的表述

### 3. 社交防御机制 (Social Defense)
检测以下模式：
- 预设失败："反正我这样的人..."
- 归因外化："可能是因为...才这样"
- 情感隔离：用理性分析回避情感表达

## 输出格式
请严格按照以下 JSON 格式输出（仅输出 JSON，不要其他内容）：

{
    "anxiety_level": <1-10 的整数>,
    "psychological_tags": ["标签 1", "标签 2"],
    "avoidance_indicators": ["具体引用或描述"],
    "self_handicapping_detected": <true/false>,
    "confidence_score": <0.0-1.0 的浮点数>
}

## 可用标签列表
- "回避型依恋"
- "自我妨碍倾向"
- "社交焦虑"
- "完美主义"
- "讨好型沟通"
- "情感隔离"
- "归因外化"
- "低自我效能感"

## 用户输入
{{user_input}}

## 对话历史
{{conversation_history}}

## 分析要求
1. 先进行内部推理，分析用户表达中的关键语言模式
2. 基于成就动机理论，判断用户是将社交视为"挑战"还是"威胁"
3. 输出结构化 JSON 结果
"""

    REASONING_LAYER_PROMPT = """
# Role: 心理学 AI 推理师 - 推理层

## 任务描述
你是一位结合物理建模思维与心理学的推理专家。
你将接收感知层的分析结果，并判断当前对话所处的阶段及僵局成因。

## 物理建模思维框架
将对话状态视为一个受外力影响的动态系统：
- **动量（Momentum）**: 对话的自然推进力
- **阻力（Resistance）**: 心理防御、焦虑等阻碍因素
- **外力（External Force）**: AI 干预、环境变化等

## 对话阶段判断

### 阶段 1: 破冰期 (Ice-breaking Phase)
特征：
- 双方首次或前 3 轮对话
- 话题以基本信息交换为主
- 社交规范主导互动

### 阶段 2: 信息交换期 (Information Exchange Phase)
特征：
- 已有基础了解
- 话题深入至兴趣、价值观
- 开始试探性自我暴露

### 阶段 3: 情感共振期 (Emotional Resonance Phase)
特征：
- 话题涉及情感体验
- 双方有共情回应
- 互动具有自发性

## 僵局成因分析（基于自我妨碍理论）

| 成因类型 | 表现 | 归因模式 |
|---------|------|---------|
| 策略性自我妨碍 | 故意不努力，为失败留借口 | "我没认真而已" |
| 行为性自我妨碍 | 制造实际障碍（如拖延回复） | "刚好有事" |
| 归因偏差 | 将成功归因于运气，失败归因于能力 | "只是运气好" |
| 低成就动机 | 回避挑战，选择确定性高的互动 | "不想太复杂" |

## 输入数据
- 焦虑值：{{anxiety_level}}
- 心理标签：{{psychological_tags}}
- 回避指标：{{avoidance_indicators}}
- 对话历史：{{conversation_history}}
- 当前对话：{{current_turn}}

## 输出格式
请严格按照以下 JSON 格式输出（仅输出 JSON，不要其他内容）：

{
    "dialogue_stage": "<破冰期/信息交换期/情感共振期>",
    "dialogue_momentum": "<正向/中性/负向>",
    "resistance_factors": ["阻力因素 1", "阻力因素 2"],
    "stagnation_cause": "<具体成因描述>",
    "attribution_pattern": "<用户的归因模式>",
    "recommended_strategy": "<干预策略：降低难度/重构认知/提供话术>",
    "confidence_score": <0.0-1.0>
}

## 分析要求
1. 结合物理建模思维，分析对话的"动量"与"阻力"平衡
2. 基于成就动机理论，判断用户当前的动机状态
3. 输出结构化 JSON 结果
"""

    GENERATION_LAYER_PROMPT = """
# Role: 对话策略生成师 - 生成层

## 任务描述
你是一位精通认知负荷理论和成就动机训练的对话策略专家。
你的任务是生成具体、可立即发送的对话建议，帮助用户突破冷场困境。

## 核心原则

### 1. 降低认知负荷 (Cognitive Load Reduction)
- 话术必须具体到可直接复制发送
- 避免抽象建议如"多关心对方"
- 提供完整的句式结构

### 2. 成就动机引导 (Achievement Motivation Framing)
- 将对话框定为"可练习的技能"
- 强调努力与进步，而非天赋
- 使用成长型思维语言

### 3. 归因训练 (Attribution Training)
- 引导用户将冷场归因为"策略问题"而非"能力问题"
- 提供替代性策略选项
- 避免人格层面的自我否定

## 输入数据
- 对话阶段：{{dialogue_stage}}
- 动量状态：{{dialogue_momentum}}
- 阻力因素：{{resistance_factors}}
- 僵局成因：{{stagnation_cause}}
- 推荐策略：{{recommended_strategy}}
- 焦虑水平：{{anxiety_level}}

## 输出要求

### 建议数量
提供 2-3 条建议，按推荐度排序。

### 建议结构
每条建议应包含：
1. **话术文本**：可直接发送的完整句子
2. **策略说明**：为什么这样说有效（1 句话）
3. **预期反应**：对方可能的回应方向

### 语言风格
- 自然、口语化
- 避免过度正式或刻意
- 符合中文社交习惯

## 输出格式
请严格按照以下 JSON 格式输出（仅输出 JSON，不要其他内容）：

{
    "suggestions": [
        {
            "id": 1,
            "script": "<可直接发送的话术>",
            "rationale": "<策略说明>",
            "expected_response": "<预期反应>",
            "difficulty_level": "<低/中/高>",
            "alignment_with_stage": "<为何符合当前对话阶段>"
        }
    ],
    "meta_guidance": {
        "attribution_reframe": "<帮助用户重构对冷场的归因>",
        "confidence_builder": "<一句建立信心的话>"
    }
}
"""

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
            response = requests.post(url, headers=headers, json=payload, timeout=60)
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
            raise TimeoutError("API 请求超时，请检查网络连接或重试")
        except requests.exceptions.RequestException as e:
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
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
        except requests.exceptions.Timeout:
            raise TimeoutError("API 请求超时，请检查网络连接或重试")
        except requests.exceptions.RequestException as e:
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

    def analyze(self, user_input: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> AnalysisResult:
        """
        执行三层式对话分析

        Args:
            user_input: 用户当前输入/想分析的对话内容
            conversation_history: 对话历史列表，每项包含 {"role": "user/other", "content": "..."}

        Returns:
            AnalysisResult: 完整分析结果
        """
        conversation_history = conversation_history or []

        # Step 1: 感知层分析
        perception_prompt = self.PERCEPTION_LAYER_PROMPT.replace(
            "{{user_input}}", user_input
        ).replace(
            "{{conversation_history}}",
            str(conversation_history[-5:]) if conversation_history else "无"
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
            conversation_history=conversation_history
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

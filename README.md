# 婚恋 AI Agent - 基于成就动机理论的对话分析助手

<div align="center">

**成就动机理论 × 归因训练 × 物理建模思维**

一个生产级的 AI Agent 工具，帮助婚恋平台用户突破对话冷场困境

[快速开始](#快速开始) • [支持的模型](#支持的模型) • [使用方法](#使用方法) • [API 文档](#api-文档)

</div>

---

## 项目背景

### 痛点分析

传统婚恋平台用户常因以下心理困境导致对话冷场：

| 心理现象 | 表现形式 | 影响 |
|---------|---------|------|
| **社交焦虑** | 担心说错话、过度自我监控 | 回复延迟、对话中断 |
| **自我妨碍 (Self-Handicapping)** | "我不太会聊天"等前置防御 | 降低投入、回避挑战 |
| **归因偏差** | 将冷场归因为"能力不足" | 自我否定、退出互动 |

### 核心理论

1. **成就动机理论 (Achievement Motivation Theory)** - 将社交视为可练习的技能
2. **归因训练 (Attribution Training)** - 引导成长型思维
3. **物理建模思维** - 用"动量/阻力"分析对话状态

---

## 项目结构

```
ai_date_with_ta/
├── engine.py           # 核心分析引擎（三层 Prompt 链）
├── main.py             # Streamlit Web 应用
├── cli.py              # 命令行工具
├── requirements.txt    # 依赖清单
├── README.md           # 项目文档
├── prompts/
│   ├── __init__.py
│   └── system_prompts.py  # Prompt 模板（演示版）
└── data/
    └── simulated_cases.py # 模拟测试数据
```

---

## 快速开始

### 1. 安装依赖

```bash
cd ai_date_with_ta
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 方式 1: 使用 CLI 配置
python cli.py config --provider qwen --api-key YOUR_DASHSCOPE_KEY

# 方式 2: 直接使用参数
python cli.py analyze --text "不知道该怎么聊天..." --provider kimi --api-key YOUR_KIMI_KEY
```

### 3. 启动应用

**Web 界面:**
```bash
streamlit run main.py
```
然后访问 `http://localhost:8501`

**命令行:**
```bash
# 完整分析
python cli.py analyze --text "刚匹配到一个女生，不知道该怎么开启话题..." --provider qwen

# 快速分析
python cli.py quick --text "TA 回复好冷淡，我该怎么办"

# 从文件读取
python cli.py analyze -i conversation.txt --json
```

---

## 支持的模型

### 国产大模型 (推荐)

| 提供商 | 默认模型 | API Key 获取 |
|--------|---------|-------------|
| **通义千问 (Qwen)** | `qwen-plus` | [阿里云 DashScope](https://dashscope.console.aliyun.com/apiKey) |
| **Kimi (月之暗面)** | `moonshot-v1-8k` | [Moonshot Platform](https://platform.moonshot.cn/console/api-keys) |
| **豆包 (Doubao)** | `doubao-pro-4k` | [VolcEngine Ark](https://console.volcengine.com/ark) |
| **智谱 AI (GLM)** | `glm-4` | [BigModel Open Platform](https://open.bigmodel.cn/usercenter/apikeys) |
| **百川智能** | `Baichuan4` | [Baichuan Platform](https://platform.baichuan-ai.com/console/apiKey) |
| **深度求索** | `deepseek-chat` | [DeepSeek Platform](https://platform.deepseek.com/api_keys) |
| **MiniMax** | `abab6.5-chat` | [MiniMax Platform](https://platform.minimaxi.com/user-center/api-key) |

### 国际模型

| 提供商 | 默认模型 |
|--------|---------|
| **Anthropic** | `claude-sonnet-4-20250514` |
| **OpenAI** | `gpt-4o` |

### 本地部署

| 提供商 | 默认模型 | 说明 |
|--------|---------|------|
| **Ollama** | `qwen2.5:7b` | 本地运行，无需 API Key |
| **自定义** | `custom-model` | 任意 OpenAI 兼容 API |

### 查看所有支持的提供商

```bash
python cli.py config --list-providers
```


---

## 使用方法

### Web 界面

1. 访问 `http://localhost:8501`
2. 在侧边栏选择模型提供商并输入 API Key
3. 在输入框粘贴对话内容或描述情境
4. 点击"开始分析"获取建议

### CLI 命令

```bash
# 查看帮助
python cli.py --help

# 配置默认提供商
python cli.py config --provider anthropic

# 分析对话
python cli.py analyze -t "TA 说'在忙'，然后就没下文了..."

# 输出 JSON 格式（便于集成）
python cli.py analyze -t "不知道该怎么回复..." --json
```

### 代码集成

```python
from engine import DatingAgentEngine

# 初始化引擎 - 使用通义千问
engine = DatingAgentEngine(model_provider="qwen", api_key="YOUR_DASHSCOPE_KEY")

# 初始化引擎 - 使用 Kimi
engine = DatingAgentEngine(model_provider="kimi", api_key="YOUR_KIMI_KEY")

# 初始化引擎 - 使用本地 Ollama
engine = DatingAgentEngine(model_provider="ollama", model_name="qwen2.5:7b")

# 执行分析
result = engine.analyze(
    user_input="TA 说'在忙'，然后就没下文了...",
    conversation_history=[
        {"role": "user", "content": "在干嘛呢？"},
        {"role": "other", "content": "在忙"}
    ]
)

# 获取建议
print("焦虑水平:", result.perception.anxiety_level)
print("对话阶段:", result.reasoning.dialogue_stage)
for s in result.generation.suggestions:
    print(f"建议：{s.script}")
```

---

## 核心功能

### 三层式分析

| 层级 | 功能 | 输出 |
|------|------|------|
| **感知层** | 识别回避型措辞、自我妨碍倾向 | 焦虑值 (1-10)、心理标签 |
| **推理层** | 判断对话阶段、分析僵局成因 | 阶段、动量、归因模式 |
| **生成层** | 生成具体话术建议 | 2-3 条可发送建议 |

### 模型选择建议

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| **最佳效果** | Kimi / Qwen | 中文理解能力强，心理学概念准确 |
| **性价比** | DeepSeek / Qwen | 价格低廉，效果良好 |
| **本地部署** | Ollama + Qwen2.5 | 免费，数据隐私好 |
| **国际模型** | Claude Sonnet 4 | 心理学理解最深，支持中文 |
| **Ollama** | 本地模型 | 免费，需自行部署 |

---

## API 文档

### DatingAgentEngine

```python
class DatingAgentEngine:
    """婚恋 AI Agent 核心引擎"""

    def __init__(self, model_provider: str, api_key: Optional[str]):
        """
        Args:
            model_provider: "openai", "anthropic", 或 "ollama"
            api_key: API Key（Ollama 不需要）
        """

    def analyze(self, user_input: str, conversation_history: List[Dict]) -> AnalysisResult:
        """执行完整的三层分析"""

    def analyze_quick(self, user_input: str) -> Dict:
        """快速分析模式，返回简化结果"""
```

### AnalysisResult

```python
@dataclass
class AnalysisResult:
    perception: PerceptionResult      # 感知层结果
    reasoning: ReasoningResult        # 推理层结果
    generation: GenerationResult      # 生成层结果
    timestamp: str                    # 分析时间
    user_input: str                   # 用户输入
    conversation_history: List[Dict]  # 对话历史
```

---

## 模拟数据

运行模拟数据查看效果对比：

```bash
python data/simulated_cases.py
```

**汇总结果:**
- 平均对话轮次增加：+4.4 轮
- 平均焦虑值降低：-3.2 分
- 回复延迟降低率：76%

---

## License

MIT License

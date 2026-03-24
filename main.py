"""
EchoMate AI agent v1.1 - Streamlit 应用
生产级对话分析助手

环境变量支持（用于 GitHub Secrets / Streamlit Cloud 部署）：
- DEFAULT_PROVIDER: 默认模型提供商 (默认：qwen)
- API_KEY: API Key
- MODEL_NAME: 自定义模型名称
- BASE_URL: 自定义 API 基础 URL
"""

import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from engine import DatingAgentEngine, AnalysisResult, MODEL_CONFIGS


# =============================================================================
# MBTI 性格类型定义
# =============================================================================

MBTI_TYPES = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

MBTI_DESCRIPTIONS = {
    "ISTJ": "物流师型 - 务实、有条理、可靠",
    "ISFJ": "守卫者型 - 温暖、体贴、有责任感",
    "INFJ": "提倡者型 - 理想主义、富有洞察力",
    "INTJ": "建筑师型 - 战略思维、独立自主",
    "ISTP": "鉴赏家型 - 灵活、动手能力强",
    "ISFP": "探险家型 - 温和、敏感、审美佳",
    "INFP": "调停者型 - 理想主义、富有同情心",
    "INTP": "逻辑学家型 - 好奇、创新、重逻辑",
    "ESTP": "企业家型 - 活力充沛、敢冒风险",
    "ESFP": "表演者型 - 热情、爱社交、活泼",
    "ENFP": "竞选者型 - 热情、有创造力、善于社交",
    "ENTP": "辩论家型 - 聪明、好奇、喜欢挑战",
    "ESTJ": "总经理型 - 高效、注重秩序、领导力强",
    "ESFJ": "执政官型 - 关心他人、受欢迎、合作",
    "ENFJ": "主人公型 - 有魅力、善于领导、助人",
    "ENTJ": "指挥官型 - 果断、战略眼光、高效",
}

# MBTI 兼容性简要说明
MBTI_COMPATIBILITY_HINT = """
💡 **MBTI 性格匹配提示**

不同性格类型在沟通方式上有差异：
- **内向 (I) vs 外向 (E)**: 能量来源不同，I 需要独处，E 需要社交
- **感知 (S) vs 直觉 (N)**: 信息处理不同，S 重事实，N 重可能性
- **思考 (T) vs 情感 (F)**: 决策方式不同，T 重逻辑，F 重感受
- **判断 (J) vs 知觉 (P)**: 生活方式不同，J 重计划，P 重灵活

选择双方的 MBTI 类型，AI 将给出更有针对性的沟通建议。
"""


# =============================================================================
# 导出功能
# =============================================================================

def generate_export_markdown(result: AnalysisResult) -> str:
    """
    生成可导出的 Markdown 格式分析报告

    Args:
        result: 分析结果对象

    Returns:
        Markdown 格式的字符串
    """
    md = f"""# EchoMate 分析报告

**生成时间:** {result.timestamp}

"""

    # MBTI 信息（如有）
    if result.user_mbti or result.other_mbti:
        md += "## MBTI 性格分析\n\n"
        if result.user_mbti:
            md += f"- **你的 MBTI**: {result.user_mbti}\n"
        if result.other_mbti:
            md += f"- **对方的 MBTI**: {result.other_mbti}\n"
        md += "\n"

    md += f"""---

## 提问内容

{result.user_input}

---

## 分析结果

### 感知层 (Perception Layer)

| 指标 | 值 |
|------|-----|
| 焦虑水平 | {result.perception.anxiety_level}/10 |
| 置信度 | {result.perception.confidence_score:.0%} |

**心理标签:**
"""
    for tag in result.perception.psychological_tags:
        md += f"- {tag}\n"

    if result.perception.self_handicapping_detected:
        md += "\n⚠️ **自我妨碍倾向:** 检测到\n"

    md += "\n**回避指标:**\n"
    if result.perception.avoidance_indicators:
        for indicator in result.perception.avoidance_indicators:
            md += f"- {indicator}\n"
    else:
        md += "- 未检测到明显回避行为\n"

    md += f"""
### 推理层 (Reasoning Layer)

| 指标 | 值 |
|------|-----|
| 对话阶段 | {result.reasoning.dialogue_stage} |
| 动量状态 | {result.reasoning.dialogue_momentum} |
| 置信度 | {result.reasoning.confidence_score:.0%} |

**僵局成因:** {result.reasoning.stagnation_cause}

**归因模式:** {result.reasoning.attribution_pattern}

**推荐策略:** {result.reasoning.recommended_strategy}

**阻力因素:**
"""
    if result.reasoning.resistance_factors:
        for factor in result.reasoning.resistance_factors:
            md += f"- {factor}\n"
    else:
        md += "- 无明显阻力\n"

    md += """
### 对话建议

"""
    for i, suggestion in enumerate(result.generation.suggestions, 1):
        md += f"""#### 建议 {i}

**话术:**
```
{suggestion.script}
```

**策略说明:** {suggestion.rationale}

**预期反应:** {suggestion.expected_response}

**难度:** {suggestion.difficulty_level} | **阶段匹配:** {suggestion.alignment_with_stage}

---
"""

    md += f"""## 心理引导

**归因重构:** {result.generation.meta_guidance.attribution_reframe}

**信心建立:** {result.generation.meta_guidance.confidence_builder}

---

*报告由 EchoMate AI agent v1.1 生成*
"""
    return md


def generate_export_text(result: AnalysisResult) -> str:
    """
    生成纯文本格式的分析报告（用于 PDF 生成或简单导出）

    Args:
        result: 分析结果对象

    Returns:
        纯文本格式的字符串
    """
    lines = [
        "=" * 60,
        "EchoMate 分析报告",
        "=" * 60,
        f"生成时间：{result.timestamp}",
        "",
        "=" * 60,
        "提问内容",
        "=" * 60,
        result.user_input,
        "",
        "=" * 60,
        "分析结果",
        "=" * 60,
        "",
        "--- 感知层 (Perception Layer) ---",
        f"焦虑水平：{result.perception.anxiety_level}/10",
        f"置信度：{result.perception.confidence_score:.0%}",
        f"心理标签：{', '.join(result.perception.psychological_tags)}",
    ]

    if result.perception.self_handicapping_detected:
        lines.append("⚠️ 自我妨碍倾向：检测到")

    lines.extend([
        "",
        "--- 推理层 (Reasoning Layer) ---",
        f"对话阶段：{result.reasoning.dialogue_stage}",
        f"动量状态：{result.reasoning.dialogue_momentum}",
        f"僵局成因：{result.reasoning.stagnation_cause}",
        f"归因模式：{result.reasoning.attribution_pattern}",
        f"推荐策略：{result.reasoning.recommended_strategy}",
        "",
        "--- 对话建议 ---",
    ])

    for i, suggestion in enumerate(result.generation.suggestions, 1):
        lines.extend([
            "",
            f"[建议 {i}]",
            f"话术：{suggestion.script}",
            f"策略说明：{suggestion.rationale}",
            f"预期反应：{suggestion.expected_response}",
        ])

    lines.extend([
        "",
        "=" * 60,
        "心理引导",
        "=" * 60,
        f"归因重构：{result.generation.meta_guidance.attribution_reframe}",
        f"信心建立：{result.generation.meta_guidance.confidence_builder}",
        "",
        "=" * 60,
    ])

    return "\n".join(lines)


# =============================================================================
# 页面配置
# =============================================================================

st.set_page_config(
    page_title="EchoMate AI agent v1.1",
    page_icon="🔓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CSS 样式优化
# =============================================================================

st.markdown("""
<style>
    .stAlert {
        border-radius: 10px;
    }
    .suggestion-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
    }
    .provider-option {
        padding: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 侧边栏配置
# =============================================================================

with st.sidebar:
    st.title("⚙️ 配置")

    st.markdown("### 模型设置")

    # 检查环境变量（用于 GitHub Secrets / Streamlit Cloud 部署）
    env_api_key = os.getenv("API_KEY")
    env_provider = os.getenv("DEFAULT_PROVIDER", "qwen")
    env_model_name = os.getenv("MODEL_NAME")
    env_base_url = os.getenv("BASE_URL")

    if env_api_key:
        st.success("✅ 已从环境变量加载 API 配置")
        st.caption("配置来源：GitHub Secrets / Streamlit Cloud Secrets")

    # 获取所有可用的模型提供商
    providers = DatingAgentEngine.get_available_providers()
    provider_options = {p["name"]: p["key"] for p in providers}

    # 按类别分组显示
    st.markdown("**国际模型**")
    st.caption("Anthropic, OpenAI")

    st.markdown("**国产大模型**")
    st.caption("通义千问，Kimi, 豆包，智谱等")

    st.markdown("**本地部署**")
    st.caption("Ollama, 自定义 API")

    # 如果有环境变量的 provider，尝试找到对应的索引
    default_index = 2  # 默认 qwen
    if env_provider and env_provider in [p["key"] for p in providers]:
        provider_keys = [p["key"] for p in providers]
        default_index = provider_keys.index(env_provider)

    selected_provider_name = st.selectbox(
        "选择模型提供商",
        options=list(provider_options.keys()),
        index=default_index,
        help="选择一个模型提供商"
    )

    model_provider = provider_options[selected_provider_name]

    # 显示对应模型的说明和默认模型名称
    provider_config = MODEL_CONFIGS.get(model_provider, {})
    default_model = provider_config.get("default_model", "")

    st.info(f"**默认模型**: `{default_model}`")

    # 自定义模型名称
    custom_model_name = st.text_input(
        "自定义模型名称 (可选)",
        value=env_model_name if env_model_name else "",
        placeholder=default_model,
        help="留空则使用默认模型"
    )

    # 自定义 API 端点 (仅 custom 模式)
    custom_base_url = ""
    if model_provider == "custom":
        custom_base_url = st.text_input(
            "自定义 API 基础 URL",
            value=env_base_url if env_base_url else "",
            placeholder="https://your-api.com/v1",
            help="输入自定义的 OpenAI 兼容 API 端点"
        )

    # API Key 输入 - 优先使用环境变量
    api_key = None
    if model_provider != "ollama":
        if env_api_key:
            api_key = env_api_key
            st.text_input(
                "API Key",
                type="password",
                value=env_api_key,
                help="API Key 来自环境变量，可在 GitHub Secrets 中配置"
            )
            st.caption("如需覆盖，请在下方输入新的 API Key")
            override_key = st.text_input(
                "覆盖 API Key (可选)",
                type="password",
                help="输入新的 API Key 将覆盖环境变量配置"
            )
            if override_key:
                api_key = override_key
        else:
            api_key = st.text_input(
                "API Key",
                type="password",
                help="API Key 仅存储在本地会话中"
            )

        # 根据不同提供商显示不同的获取链接提示
        if model_provider == "qwen":
            st.markdown("[📖 获取阿里云 DashScope API Key](https://dashscope.console.aliyun.com/apiKey)")
        elif model_provider == "kimi":
            st.markdown("[📖 获取 Kimi API Key](https://platform.moonshot.cn/console/api-keys)")
        elif model_provider == "zhipu":
            st.markdown("[📖 获取智谱 AI API Key](https://open.bigmodel.cn/usercenter/apikeys)")
        elif model_provider == "deepseek":
            st.markdown("[📖 获取 DeepSeek API Key](https://platform.deepseek.com/api_keys)")
        elif model_provider == "doubao":
            st.markdown("[📖 获取豆包 API Key](https://console.volcengine.com/ark)")
        elif model_provider == "baichuan":
            st.markdown("[📖 获取百川 API Key](https://platform.baichuan-ai.com/console/apiKey)")
        elif model_provider == "minimax":
            st.markdown("[📖 获取 MiniMax API Key](https://platform.minimaxi.com/user-center/api-key)")

    if model_provider == "ollama":
        st.info(
            "💡 Ollama 使用本地模型，无需 API Key\n\n"
            "确保 Ollama 服务正在运行：\n"
            "```bash\nollama serve\n```"
        )
        ollama_model = st.text_input("Ollama 模型名", value="qwen2.5:7b")

    st.markdown("---")

    # 会话管理
    st.markdown("### 会话管理")

    if st.button("🗑️ 清空对话历史", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.analysis_history = []
        st.rerun()

    if st.button("💾 导出会话记录", use_container_width=True):
        history = st.session_state.get("analysis_history", [])
        if history:
            json_str = json.dumps(history, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 下载 JSON",
                data=json_str,
                file_name=f"dating_agent_history_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )

    # 导出当前分析结果（MD/TXT）
    if st.session_state.get("last_analysis") is not None:
        result = st.session_state.last_analysis

        # 生成 MD 内容
        md_content = generate_export_markdown(result)
        # 生成 TXT 内容
        txt_content = generate_export_text(result)

        col_md1, col_md2 = st.columns(2)
        with col_md1:
            st.download_button(
                label="📥 导出为 MD",
                data=md_content,
                file_name=f"chat_debug_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_md2:
            st.download_button(
                label="📥 导出为 TXT",
                data=txt_content,
                file_name=f"chat_debug_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    st.markdown("---")
    st.markdown("### 关于")
    st.markdown("""
    **EchoMate AI agent v1.1**

    基于成就动机理论与归因训练原理，
    帮助突破聊天冷场困境。

    **核心理论:**
    - 成就动机理论
    - 自我妨碍理论
    - 归因训练
    - 物理建模思维
    """)

# =============================================================================
# 会话状态初始化
# =============================================================================

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "engine" not in st.session_state:
    st.session_state.engine = None

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

# =============================================================================
# 引擎初始化
# =============================================================================

def init_engine():
    """初始化 Agent 引擎"""
    if model_provider == "ollama":
        model_name = ollama_model if 'ollama_model' in locals() else "qwen2.5:7b"
        return DatingAgentEngine(
            model_provider="ollama",
            model_name=model_name
        )
    elif model_provider == "custom":
        return DatingAgentEngine(
            model_provider="custom",
            api_key=api_key,
            base_url=custom_base_url,
            model_name=custom_model_name if custom_model_name else "custom-model"
        )
    elif api_key:
        return DatingAgentEngine(
            model_provider=model_provider,
            api_key=api_key,
            model_name=custom_model_name if custom_model_name else None
        )
    return None

# 当配置变化时重新初始化引擎
current_config = {
    "provider": model_provider,
    "api_key": api_key,
    "model_name": custom_model_name if 'custom_model_name' in locals() else "",
    "base_url": custom_base_url if 'custom_base_url' in locals() else ""
}

if "prev_config" not in st.session_state:
    st.session_state.prev_config = None

if st.session_state.prev_config != current_config:
    st.session_state.engine = init_engine()
    st.session_state.prev_config = current_config

# =============================================================================
# 主界面
# =============================================================================

st.title("🔓 EchoMate AI agent v1.1")
st.markdown("""
基于**成就动机理论**与**归因训练**原理，帮助您突破聊天冷场困境。

输入您的对话内容或描述当前情境，获取专业心理学分析的对话建议。
""")

# =============================================================================
# 对话输入区
# =============================================================================

st.markdown("### 📝 输入对话内容")

col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area(
        "当前对话/想分析的内容",
        height=150,
        placeholder="""例如：
刚匹配到一个女生，她资料里说喜欢看电影，但我不知道该怎么开启话题...

或者直接粘贴对话：
你：你好，看到你也喜欢旅行，去过哪里印象最深呀？
对方：嗯，去了挺多的，一时说不上来""",
        help="尽可能详细地描述当前对话情境或粘贴对话原文"
    )

with col2:
    st.markdown("#### 对话情境（可选）")

    dialogue_stage_select = st.selectbox(
        "当前对话阶段",
        options=["自动检测", "破冰期", "信息交换期", "情感共振期"],
        help="如不确定可选择'自动检测'"
    )

    anxiety_self_rating = st.slider(
        "您当前的焦虑程度",
        min_value=1,
        max_value=10,
        value=5,
        help="1=非常放松，10=极度紧张"
    )

    st.markdown("---")
    st.markdown("#### MBTI 性格分析（可选）")

    # MBTI 提示折叠框
    with st.expander("📘 MBTI 性格类型说明"):
        st.markdown(MBTI_COMPATIBILITY_HINT)

    # 用户自己的 MBTI
    user_mbti = st.selectbox(
        "你的 MBTI 类型",
        options=["未填写"] + MBTI_TYPES,
        index=0,
        help="选择你的 MBTI 性格类型"
    )

    # 显示用户 MBTI 描述
    if user_mbti != "未填写":
        st.caption(f"📌 {MBTI_DESCRIPTIONS.get(user_mbti, '')}")

    # 对方的 MBTI
    other_mbti = st.selectbox(
        "对方的 MBTI 类型",
        options=["未填写"] + MBTI_TYPES,
        index=0,
        help="选择对方的 MBTI 性格类型"
    )

    # 显示对方 MBTI 描述
    if other_mbti != "未填写":
        st.caption(f"📌 {MBTI_DESCRIPTIONS.get(other_mbti, '')}")

    # 如果两者都填写，显示兼容性提示
    if user_mbti != "未填写" and other_mbti != "未填写":
        st.info(f"💞 分析将考虑 **{user_mbti}** 与 **{other_mbti}** 的性格差异")

    # 添加对话历史
    st.markdown("#### 添加历史对话")
    if st.button("➕ 添加一轮对话"):
        st.session_state.show_add_dialog = True

    if st.session_state.get("show_add_dialog", False):
        with st.form("add_dialog_form"):
            role = st.selectbox("角色", ["对方", "我"])
            content = st.text_area("内容")
            submitted = st.form_submit_button("添加")
            if submitted and content:
                st.session_state.conversation_history.append({
                    "role": "other" if role == "对方" else "user",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
                st.session_state.show_add_dialog = False
                st.rerun()

# =============================================================================
# 分析按钮
# =============================================================================

col_btn1, col_btn2, col_btn3 = st.columns([1, 4, 1])
with col_btn2:
    analyze_btn = st.button("🔍 开始分析", type="primary", use_container_width=True)

# =============================================================================
# 执行分析
# =============================================================================

if analyze_btn and user_input and st.session_state.engine:
    if not api_key and model_provider != "ollama":
        st.error("⚠️ 请先在侧边栏输入 API Key")
    else:
        with st.status("🔄 正在执行三层分析...", expanded=True) as status:
            try:
                # 进度条和状态标签
                progress_bar = st.progress(0)
                status_text = st.empty()

                # 第 1 步：感知层分析
                status_text.markdown("**🧠 感知层** - 正在分析心理指标...")
                progress_bar.progress(10)

                result = st.session_state.engine.analyze(
                    user_input=user_input,
                    conversation_history=st.session_state.conversation_history,
                    user_mbti=user_mbti if 'user_mbti' in locals() else None,
                    other_mbti=other_mbti if 'other_mbti' in locals() else None
                )

                # 感知层完成
                progress_bar.progress(33)
                status_text.markdown("**✅ 🧠 感知层** - 完成")

                # 第 2 步：推理层分析
                status_text.markdown("**🤖 推理层** - 正在分析对话状态...")
                progress_bar.progress(50)

                # 推理层完成（结果已在 analyze 中返回）
                progress_bar.progress(66)
                status_text.markdown("**✅ 🤖 推理层** - 完成")

                # 第 3 步：生成层分析
                status_text.markdown("**💡 生成层** - 正在生成对话建议...")
                progress_bar.progress(80)

                # 生成层完成（结果已在 analyze 中返回）
                progress_bar.progress(100)
                status_text.markdown("**✅ 💡 生成层** - 完成")

                # 分析完成
                st.session_state.last_analysis = result
                st.session_state.analysis_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user_input": user_input,
                    "perception": {
                        "anxiety_level": result.perception.anxiety_level,
                        "tags": result.perception.psychological_tags
                    },
                    "reasoning": {
                        "stage": result.reasoning.dialogue_stage,
                        "momentum": result.reasoning.dialogue_momentum
                    },
                    "suggestions_count": len(result.generation.suggestions)
                })

                status.update(label="✅ 分析完成！", state="complete")
                status_text.empty()
                progress_bar.empty()

            except Exception as e:
                status.update(label="❌ 分析失败", state="error")
                st.error(f"分析失败：{str(e)}")
                st.info("请检查 API Key 是否正确，或尝试更换模型提供商")

elif analyze_btn and not st.session_state.engine:
    st.warning("⚠️ 请先配置 API Key 或选择 Ollama 本地模型")

# =============================================================================
# 分析结果展示
# =============================================================================

if st.session_state.last_analysis:
    result = st.session_state.last_analysis

    st.markdown("---")
    st.markdown("## 📊 分析结果")

    # 顶层指标
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        anxiety = result.perception.anxiety_level
        if anxiety <= 3:
            st.metric("焦虑水平", f"{anxiety}/10", "低")
        elif anxiety <= 6:
            st.metric("焦虑水平", f"{anxiety}/10", "中")
        else:
            st.metric("焦虑水平", f"{anxiety}/10", "高")

    with col_m2:
        st.metric("对话阶段", result.reasoning.dialogue_stage)

    with col_m3:
        st.metric("动量状态", result.reasoning.dialogue_momentum)

    with col_m4:
        st.metric("建议数量", len(result.generation.suggestions))

    # 标签页展示三层分析
    tab1, tab2, tab3 = st.tabs([
        "🧠 感知层",
        "🤖 推理层",
        "💡 建议"
    ])

    with tab1:
        st.markdown("### 感知层 (Perception Layer)")
        st.markdown("识别用户输入中的潜在心理指标")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### 焦虑值")
            st.progress(anxiety / 10)

        with col_b:
            st.markdown("#### 心理标签")
            for tag in result.perception.psychological_tags:
                st.badge(tag, color="orange")

        if result.perception.self_handicapping_detected:
            st.warning("⚠️ 检测到自我妨碍倾向")

        st.markdown("#### 回避指标")
        if result.perception.avoidance_indicators:
            for indicator in result.perception.avoidance_indicators:
                st.markdown(f"- {indicator}")
        else:
            st.markdown("- 未检测到明显回避行为")

        st.info(f"💡 分析置信度：{result.perception.confidence_score:.0%}")

    with tab2:
        st.markdown("### 推理层 (Reasoning Layer)")
        st.markdown("模拟物理状态机，判断对话阶段与僵局成因")

        col_c, col_d = st.columns(2)

        with col_c:
            st.markdown("#### 对话状态")
            st.info(f"**阶段**: {result.reasoning.dialogue_stage}")
            st.info(f"**动量**: {result.reasoning.dialogue_momentum}")

        with col_d:
            st.markdown("#### 阻力因素")
            if result.reasoning.resistance_factors:
                for factor in result.reasoning.resistance_factors:
                    st.markdown(f"- {factor}")
            else:
                st.markdown("- 无明显阻力")

        st.markdown("#### 僵局成因")
        st.markdown(f"> {result.reasoning.stagnation_cause}")

        st.markdown("#### 归因模式")
        st.markdown(f"{result.reasoning.attribution_pattern}")

        st.success(f"**推荐策略**: {result.reasoning.recommended_strategy}")
        st.info(f"推理置信度：{result.reasoning.confidence_score:.0%}")

    with tab3:
        st.markdown("### 生成层 (Generation Layer)")
        st.markdown("输出具体、可立即发送的对话建议")

        for i, suggestion in enumerate(result.generation.suggestions, 1):
            with st.expander(f"💬 建议{i}: {suggestion.script[:50]}...", expanded=(i==1)):
                st.markdown(f"**话术:**")
                st.code(suggestion.script, language="")
                st.markdown(f"**策略说明:** {suggestion.rationale}")
                st.markdown(f"**预期反应:** {suggestion.expected_response}")

                col_x, col_y = st.columns(2)
                with col_x:
                    st.markdown(f"**难度:** {suggestion.difficulty_level}")
                with col_y:
                    st.markdown(f"**阶段匹配:** {suggestion.alignment_with_stage}")

                # 一键复制
                if st.button("📋 复制此话术", key=f"copy_{i}"):
                    st.code(suggestion.script)

        st.markdown("---")
        st.markdown("### 🌟 心理引导")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.info(f"**归因重构:** {result.generation.meta_guidance.attribution_reframe}")
        with col_m2:
            st.success(f"**信心建立:** {result.generation.meta_guidance.confidence_builder}")

# =============================================================================
# 对话历史展示
# =============================================================================

if st.session_state.conversation_history:
    st.markdown("---")
    st.markdown("## 📜 对话历史")

    for i, conv in enumerate(st.session_state.conversation_history):
        role_icon = "👤" if conv["role"] == "user" else "👥"
        role_name = "我" if conv["role"] == "user" else "对方"

        with st.chat_message(conv["role"], avatar=role_icon):
            st.markdown(f"**{role_name}:** {conv['content']}")
            if "timestamp" in conv:
                st.caption(f"{conv['timestamp'][:16]}")

# =============================================================================
# 页脚
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>

EchoMate AI agent v1.1 | 基于成就动机理论 × 归因训练 × 物理建模思维

</div>
""", unsafe_allow_html=True)

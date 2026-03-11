"""
婚恋 AI Agent - Streamlit 应用
生产级对话分析助手
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Optional

from engine import DatingAgentEngine, AnalysisResult, MODEL_CONFIGS

# =============================================================================
# 页面配置
# =============================================================================

st.set_page_config(
    page_title="婚恋 AI Agent - 对话分析助手",
    page_icon="💬",
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

    selected_provider_name = st.selectbox(
        "选择模型提供商",
        options=list(provider_options.keys()),
        index=2,  # 默认选择 qwen
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
        value="",
        placeholder=default_model,
        help="留空则使用默认模型"
    )

    # 自定义 API 端点 (仅 custom 模式)
    custom_base_url = ""
    if model_provider == "custom":
        custom_base_url = st.text_input(
            "自定义 API 基础 URL",
            value="",
            placeholder="https://your-api.com/v1",
            help="输入自定义的 OpenAI 兼容 API 端点"
        )

    # API Key 输入
    api_key = None
    if model_provider != "ollama":
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

    st.markdown("---")
    st.markdown("### 关于")
    st.markdown("""
    **婚恋 AI Agent** v1.0

    基于成就动机理论与归因训练原理，
    帮助婚恋平台用户突破对话冷场困境。

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

st.title("💬 婚恋 AI Agent - 对话分析助手")
st.markdown("""
基于**成就动机理论**与**归因训练**原理，帮助您突破对话冷场困境。

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
        with st.spinner("🔍 正在进行三层分析...\n\n感知层 → 推理层 → 生成层"):
            try:
                # 执行分析
                result = st.session_state.engine.analyze(
                    user_input=user_input,
                    conversation_history=st.session_state.conversation_history
                )

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

                st.success("✅ 分析完成！")

            except Exception as e:
                st.error(f"❌ 分析失败：{str(e)}")
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

婚恋 AI Agent v1.0 | 基于成就动机理论 × 归因训练 × 物理建模思维

</div>
""", unsafe_allow_html=True)

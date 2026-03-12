<template>
  <div class="app">
    <header class="header">
      <h1>🔓 聊天 Debug AI Agent</h1>
      <p class="subtitle">基于成就动机理论 × 归因训练 × 物理建模思维</p>
    </header>

    <main class="main">
      <!-- 配置区域 -->
      <section class="config-section">
        <details>
          <summary>⚙️ API 配置（首次使用需要设置）</summary>
          <div class="config-form">
            <div class="form-group">
              <label>模型提供商</label>
              <select v-model="config.provider">
                <option value="qwen">通义千问 (Qwen)</option>
                <option value="kimi">Kimi (月之暗面)</option>
                <option value="deepseek">DeepSeek</option>
                <option value="zhipu">智谱 AI (GLM)</option>
                <option value="doubao">豆包 (字节)</option>
              </select>
            </div>
            <div class="form-group">
              <label>API Key</label>
              <input
                type="password"
                v-model="config.apiKey"
                placeholder="输入你的 API Key"
              />
              <small>API Key 仅存储在本地，不会上传到服务器</small>
            </div>
            <div class="form-group">
              <label>模型名称（可选）</label>
              <input
                type="text"
                v-model="config.modelName"
                :placeholder="getDefaultModel(config.provider)"
              />
            </div>
            <button @click="saveConfig" class="btn btn-primary">保存配置</button>
          </div>
        </details>
      </section>

      <!-- MBTI 选择区域 -->
      <section class="mbti-section">
        <h3>📊 MBTI 性格分析（可选）</h3>
        <div class="mbti-grid">
          <div class="form-group">
            <label>你的 MBTI 类型</label>
            <select v-model="mbti.userMbti">
              <option value="">未填写</option>
              <option v-for="type in mbtiTypes" :key="type" :value="type">{{ type }}</option>
            </select>
            <small v-if="mbti.userMbti">{{ getMbtiDescription(mbti.userMbti) }}</small>
          </div>
          <div class="form-group">
            <label>对方的 MBTI 类型</label>
            <select v-model="mbti.otherMbti">
              <option value="">未填写</option>
              <option v-for="type in mbtiTypes" :key="type" :value="type">{{ type }}</option>
            </select>
            <small v-if="mbti.otherMbti">{{ getMbtiDescription(mbti.otherMbti) }}</small>
          </div>
        </div>
        <div v-if="mbti.userMbti && mbti.otherMbti" class="mbti-hint">
          💡 分析将考虑 <strong>{{ mbti.userMbti }}</strong> 与 <strong>{{ mbti.otherMbti }}</strong> 的性格差异
        </div>
      </section>

      <!-- 输入区域 -->
      <section class="input-section">
        <div class="input-header">
          <h3>📝 输入对话内容</h3>
          <button @click="newConversation" :disabled="loading" class="btn btn-secondary btn-small">
            ➕ 新建对话
          </button>
        </div>
        <textarea
          v-model="userInput"
          placeholder="例如：&#10;刚匹配到一个女生，她资料里说喜欢看电影，但我不知道该怎么开启话题...&#10;&#10;或者直接粘贴对话：&#10;你：你好，看到你也喜欢旅行，去过哪里印象最深呀？&#10;对方：嗯，去了挺多的，一时说不上来"
          rows="6"
        ></textarea>
        <button @click="analyze" :disabled="loading" class="btn btn-primary btn-large">
          {{ loading ? '🔄 分析中...' : '🔍 开始分析' }}
        </button>
      </section>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <div class="progress-bar">
          <div class="progress" :style="{ width: progress + '%' }"></div>
        </div>
        <p>{{ loadingText }}</p>
      </div>

      <!-- 结果展示 -->
      <section v-if="result" class="result-section">
        <div class="result-header">
          <h2>📊 分析结果</h2>
          <button @click="exportToMarkdown" class="btn btn-secondary btn-small">
            📥 导出对话
          </button>
        </div>

        <!-- 顶层指标 -->
        <div class="metrics-grid">
          <div class="metric-card">
            <span class="metric-label">焦虑水平</span>
            <span class="metric-value">{{ result.perception.anxiety_level }}/10</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">对话阶段</span>
            <span class="metric-value">{{ result.reasoning.dialogue_stage }}</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">动量状态</span>
            <span class="metric-value">{{ result.reasoning.dialogue_momentum }}</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">建议数量</span>
            <span class="metric-value">{{ result.generation.suggestions?.length || 0 }}</span>
          </div>
        </div>

        <!-- 感知层 -->
        <div class="result-card">
          <h4>🧠 感知层分析</h4>
          <div class="tags">
            <span v-for="tag in result.perception.psychological_tags" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
          <p v-if="result.perception.self_handicapping_detected" class="warning">
            ⚠️ 检测到自我妨碍倾向
          </p>
        </div>

        <!-- 推理层 -->
        <div class="result-card">
          <h4>🤖 推理层分析</h4>
          <p><strong>僵局成因:</strong> {{ result.reasoning.stagnation_cause }}</p>
          <p><strong>推荐策略:</strong> {{ result.reasoning.recommended_strategy }}</p>
        </div>

        <!-- 对话建议 -->
        <div class="result-card">
          <h4>💡 对话建议</h4>
          <div v-for="suggestion in result.generation.suggestions" :key="suggestion.id" class="suggestion-card">
            <div class="suggestion-script">{{ suggestion.script }}</div>
            <div class="suggestion-rationale">
              <strong>策略说明:</strong> {{ suggestion.rationale }}
            </div>
            <div class="suggestion-expected">
              <strong>预期反应:</strong> {{ suggestion.expected_response }}
            </div>
            <button @click="copyText(suggestion.script)" class="btn btn-small">📋 复制话术</button>
          </div>
        </div>

        <!-- 心理引导 -->
        <div class="result-card">
          <h4>🌟 心理引导</h4>
          <p><strong>归因重构:</strong> {{ result.generation.meta_guidance.attribution_reframe }}</p>
          <p><strong>信心建立:</strong> {{ result.generation.meta_guidance.confidence_builder }}</p>
        </div>
      </section>

      <!-- 错误提示 -->
      <div v-if="error" class="error">
        <strong>❌ 错误:</strong> {{ error }}
      </div>
    </main>

    <footer class="footer">
      <div class="footer-content">
        <p>聊天 Debug (Chat-lock Debugger) AI Agent v2.0 | 基于成就动机理论 × 归因训练 × 物理建模思维</p>
        <a href="https://github.com/wei-liping/chat-lock-debugger" target="_blank" rel="noopener noreferrer" class="github-link" title="GitHub 项目">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
        </a>
      </div>
    </footer>
  </div>
</template>

<script>
import { marked } from 'marked';

// MBTI 类型定义
const MBTI_TYPES = [
  "ISTJ", "ISFJ", "INFJ", "INTJ",
  "ISTP", "ISFP", "INFP", "INTP",
  "ESTP", "ESFP", "ENFP", "ENTP",
  "ESTJ", "ESFJ", "ENFJ", "ENTJ"
];

const MBTI_DESCRIPTIONS = {
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
};

// 模型配置
const MODEL_CONFIGS = {
  qwen: { defaultModel: 'qwen-plus', baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1' },
  kimi: { defaultModel: 'moonshot-v1-8k', baseUrl: 'https://api.moonshot.cn/v1' },
  deepseek: { defaultModel: 'deepseek-chat', baseUrl: 'https://api.deepseek.com/v1' },
  zhipu: { defaultModel: 'glm-4', baseUrl: 'https://open.bigmodel.cn/api/paas/v4' },
  doubao: { defaultModel: 'doubao-pro-4k', baseUrl: 'https://ark.cn-beijing.volces.com/api/v3' },
};

export default {
  name: 'App',
  data() {
    return {
      config: {
        provider: 'qwen',
        apiKey: '',
        modelName: ''
      },
      mbti: {
        userMbti: '',
        otherMbti: ''
      },
      userInput: '',
      loading: false,
      progress: 0,
      loadingText: '',
      result: null,
      error: '',
      mbtiTypes: MBTI_TYPES,
      mbtiDescriptions: MBTI_DESCRIPTIONS,
      modelConfigs: MODEL_CONFIGS
    }
  },
  mounted() {
    this.loadConfig();
    this.loadEnvDefaults();
  },
  methods: {
    loadEnvDefaults() {
      // 从环境变量加载默认值（GitHub Actions 构建时注入）
      if (import.meta.env.VITE_PROVIDER && !this.config.provider) {
        this.config.provider = import.meta.env.VITE_PROVIDER;
      }
      if (import.meta.env.VITE_API_KEY && !this.config.apiKey) {
        this.config.apiKey = import.meta.env.VITE_API_KEY;
      }
      if (import.meta.env.VITE_MODEL_NAME && !this.config.modelName) {
        this.config.modelName = import.meta.env.VITE_MODEL_NAME;
      }
    },
    getDefaultModel(provider) {
      return MODEL_CONFIGS[provider]?.defaultModel || 'default-model';
    },
    getMbtiDescription(type) {
      return MBTI_DESCRIPTIONS[type] || '';
    },
    loadConfig() {
      const saved = localStorage.getItem('chat-debug-config');
      if (saved) {
        this.config = JSON.parse(saved);
      }
    },
    saveConfig() {
      localStorage.setItem('chat-debug-config', JSON.stringify(this.config));
      alert('配置已保存到本地！');
    },
    async analyze() {
      if (!this.userInput.trim()) {
        this.error = '请输入对话内容';
        return;
      }
      if (!this.config.apiKey) {
        this.error = '请先配置 API Key';
        return;
      }

      this.loading = true;
      this.error = '';
      this.result = null;
      this.progress = 0;

      try {
        // Step 1: 感知层分析
        this.loadingText = '🧠 感知层 - 正在分析心理指标...';
        this.progress = 10;

        const perceptionResult = await this.callPerceptionLayer();
        this.progress = 33;
        this.loadingText = '✅ 🧠 感知层 - 完成';

        // Step 2: 推理层分析
        this.loadingText = '🤖 推理层 - 正在分析对话状态...';
        this.progress = 50;

        const reasoningResult = await this.callReasoningLayer(perceptionResult);
        this.progress = 66;
        this.loadingText = '✅ 🤖 推理层 - 完成';

        // Step 3: 生成层分析
        this.loadingText = '💡 生成层 - 正在生成对话建议...';
        this.progress = 80;

        const generationResult = await this.callGenerationLayer(reasoningResult, perceptionResult);
        this.progress = 100;
        this.loadingText = '✅ 💡 生成层 - 完成';

        this.result = {
          perception: perceptionResult,
          reasoning: reasoningResult,
          generation: generationResult
        };

      } catch (err) {
        this.error = err.message;
      } finally {
        setTimeout(() => {
          this.loading = false;
        }, 500);
      }
    },
    async callPerceptionLayer() {
      const prompt = this.buildPerceptionPrompt();
      const response = await this.callLLM(prompt);
      return this.extractJson(response);
    },
    async callReasoningLayer(perception) {
      const prompt = this.buildReasoningPrompt(perception);
      const response = await this.callLLM(prompt);
      return this.extractJson(response);
    },
    async callGenerationLayer(reasoning, perception) {
      const prompt = this.buildGenerationPrompt(reasoning, perception);
      const response = await this.callLLM(prompt);
      return this.extractJson(response);
    },
    async callLLM(prompt) {
      const config = MODEL_CONFIGS[this.config.provider];
      const url = `${config.baseUrl}/chat/completions`;

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({
          model: this.config.modelName || config.defaultModel,
          messages: [
            { role: 'system', content: '你是一位专业的心理学分析师，请严格按照 JSON 格式输出分析结果。' },
            { role: 'user', content: prompt }
          ],
          temperature: 0.7,
          max_tokens: 1500,
          stream: false
        })
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: '请求失败' }));
        throw new Error(`API 调用失败：${error.error?.message || response.statusText}`);
      }

      const data = await response.json();
      return data.choices[0].message.content;
    },
    extractJson(text) {
      const match = text.match(/\{[\s\S]*\}/);
      if (match) {
        try {
          return JSON.parse(match[0]);
        } catch {
          // 尝试修复 JSON
          const fixed = match[0].replace(/'/g, '"');
          return JSON.parse(fixed);
        }
      }
      throw new Error('无法解析 AI 响应');
    },
    buildPerceptionPrompt() {
      const mbtiInfo = this.buildMbtiInfo();
      return `
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
请严格按照以下 JSON 格式输出：

{
    "anxiety_level": <1-10 的整数，10 表示最高焦虑>,
    "psychological_tags": ["标签 1", "标签 2", ...],
    "avoidance_indicators": ["具体引用或描述"],
    "self_handicapping_detected": <true/false>,
    "confidence_score": <0.0-1.0 的浮点数，表示分析置信度>
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
${this.userInput}

## MBTI 性格信息
${mbtiInfo}

## 分析要求
1. 先进行内部推理，分析用户表达中的关键语言模式
2. 基于成就动机理论，判断用户是将社交视为"挑战"还是"威胁"
3. 输出结构化 JSON 结果
`;
    },
    buildReasoningPrompt(perception) {
      const mbtiInfo = this.buildMbtiInfo();
      return `
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

## MBTI 性格兼容性分析（如提供）
如果提供了双方 MBTI 信息，请考虑：
- **内向 (I) vs 外向 (E)**: 能量来源和社交偏好差异
- **感知 (S) vs 直觉 (N)**: 信息处理和关注点差异
- **思考 (T) vs 情感 (F)**: 决策方式和价值观差异
- **判断 (J) vs 知觉 (P)**: 计划性和灵活性差异

## 输入数据
- 焦虑值：${perception.anxiety_level}
- 心理标签：${perception.psychological_tags?.join(', ') || '无'}
- 当前对话：${this.userInput}
- MBTI 信息：${mbtiInfo}

## 输出格式
请严格按照以下 JSON 格式输出：

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
3. 如有 MBTI 信息，考虑性格差异对沟通的影响
4. 输出结构化 JSON 结果
`;
    },
    buildGenerationPrompt(reasoning, perception) {
      const mbtiInfo = this.buildMbtiInfo();
      return `
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

### 4. MBTI 性格匹配建议（如提供）
- 根据用户 MBTI 特点调整建议难度
- 根据对方 MBTI 特点调整沟通方式
- 考虑双方性格差异提供兼容性建议

## 输入数据
- 对话阶段：${reasoning.dialogue_stage}
- 动量状态：${reasoning.dialogue_momentum}
- 推荐策略：${reasoning.recommended_strategy}
- 焦虑水平：${perception.anxiety_level}
- MBTI 信息：${mbtiInfo}

## 输出要求

### 建议数量
提供 2-3 条建议，按推荐度排序。

### 建议结构
每条建议应包含：
1. **话术文本**：可直接发送的完整句子
2. **策略说明**：为什么这样说有效（1 句话）
3. **预期反应**：对方可能的回应方向

## 输出格式
请严格按照以下 JSON 格式输出：

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
`;
    },
    buildMbtiInfo() {
      if (this.mbti.userMbti && this.mbti.otherMbti) {
        return `用户 MBTI: ${this.mbti.userMbti}, 对方 MBTI: ${this.mbti.otherMbti}`;
      } else if (this.mbti.userMbti) {
        return `用户 MBTI: ${this.mbti.userMbti}`;
      } else if (this.mbti.otherMbti) {
        return `对方 MBTI: ${this.mbti.otherMbti}`;
      }
      return '无';
    },
    copyText(text) {
      navigator.clipboard.writeText(text);
      alert('已复制到剪贴板！');
    },
    newConversation() {
      this.userInput = ''
      this.result = null
      this.error = ''
      this.progress = 0
      this.loading = false
    },
    exportToMarkdown() {
      if (!this.result) return

      const now = new Date()
      const timestamp = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).replace(/[\/:]/g, '')

      const filename = `chat-debug-report-${timestamp}.md`

      let md = `# 聊天 Debug AI Agent - 对话分析报告\n\n`
      md += `**生成时间**: ${new Date().toLocaleString('zh-CN')}\n\n`

      // MBTI 信息
      if (this.mbti.userMbti || this.mbti.otherMbti) {
        md += `## MBTI 信息\n`
        if (this.mbti.userMbti) {
          md += `- **你的类型**: ${this.mbti.userMbti} - ${this.getMbtiDescription(this.mbti.userMbti)}\n`
        }
        if (this.mbti.otherMbti) {
          md += `- **对方类型**: ${this.mbti.otherMbti} - ${this.getMbtiDescription(this.mbti.otherMbti)}\n`
        }
        md += `\n`
      }

      // 输入对话
      md += `## 输入对话\n\n`
      md += `> ${this.userInput.replace(/\n/g, '\n> ')}\n\n`

      // 分析结果
      md += `## 分析结果\n\n`

      // 顶层指标
      md += `### 核心指标\n\n`
      md += `- **焦虑水平**: ${this.result.perception.anxiety_level}/10\n`
      md += `- **对话阶段**: ${this.result.reasoning.dialogue_stage}\n`
      md += `- **动量状态**: ${this.result.reasoning.dialogue_momentum}\n`
      md += `- **建议数量**: ${this.result.generation.suggestions?.length || 0}\n\n`

      // 感知层
      md += `### 感知层分析\n\n`
      md += `**心理标签**: ${this.result.perception.psychological_tags?.join(', ') || '无'}\n\n`
      if (this.result.perception.self_handicapping_detected) {
        md += `⚠️ **检测到自我妨碍倾向**\n\n`
      }

      // 推理层
      md += `### 推理层分析\n\n`
      md += `- **僵局成因**: ${this.result.reasoning.stagnation_cause}\n`
      md += `- **推荐策略**: ${this.result.reasoning.recommended_strategy}\n`
      md += `- **阻力因素**: ${this.result.reasoning.resistance_factors?.join(', ') || '无'}\n\n`

      // 对话建议
      md += `### 对话建议\n\n`
      this.result.generation.suggestions?.forEach((s, index) => {
        md += `#### 建议 ${index + 1}\n\n`
        md += `**话术**:\n`
        md += `> ${s.script}\n\n`
        md += `- **策略说明**: ${s.rationale}\n`
        md += `- **预期反应**: ${s.expected_response}\n`
        md += `- **难度等级**: ${s.difficulty_level || '未指定'}\n\n`
      })

      // 心理引导
      md += `### 心理引导\n\n`
      md += `- **归因重构**: ${this.result.generation.meta_guidance?.attribution_reframe || '无'}\n`
      md += `- **信心建立**: ${this.result.generation.meta_guidance?.confidence_builder || '无'}\n`

      // 创建下载
      const blob = new Blob([md], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    }
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.app {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  color: white;
  padding: 30px 0;
}

.header h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
}

.subtitle {
  opacity: 0.9;
  font-size: 1.1em;
}

.main {
  background: white;
  border-radius: 15px;
  padding: 30px;
  margin-top: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.config-section {
  margin-bottom: 25px;
}

.config-section details {
  background: #f5f7fa;
  border-radius: 10px;
  padding: 15px;
}

.config-section summary {
  cursor: pointer;
  font-weight: 600;
  color: #667eea;
}

.config-form {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.mbti-section {
  background: #f0f4ff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 25px;
}

.mbti-section h3 {
  color: #667eea;
  margin-bottom: 15px;
}

.mbti-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.mbti-hint {
  margin-top: 15px;
  padding: 10px;
  background: #e8eeff;
  border-radius: 8px;
  text-align: center;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.form-group select:focus,
.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.form-group small {
  display: block;
  margin-top: 5px;
  color: #888;
  font-size: 12px;
}

.input-section {
  margin-bottom: 25px;
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.input-header h3 {
  margin: 0;
  color: #333;
}

.input-section textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 15px;
  resize: vertical;
  font-family: inherit;
}

.input-section textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #f0f4ff;
  color: #667eea;
  border: 1px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-large {
  width: 100%;
  margin-top: 15px;
  padding: 15px;
  font-size: 17px;
}

.btn-small {
  padding: 8px 16px;
  font-size: 13px;
}

.loading {
  background: #f0f4ff;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  margin: 20px 0;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
}

.result-section {
  margin-top: 30px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.result-header h2 {
  margin: 0;
  color: #333;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 25px;
}

.metric-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}

.metric-label {
  font-size: 12px;
  opacity: 0.9;
  display: block;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
}

.result-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}

.result-card h4 {
  color: #667eea;
  margin-bottom: 15px;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.tag {
  background: #667eea;
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.warning {
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  padding: 10px 15px;
  border-radius: 5px;
  margin-top: 10px;
}

.suggestion-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 15px;
}

.suggestion-script {
  background: #f0f4ff;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  margin-bottom: 10px;
  font-size: 15px;
  line-height: 1.6;
}

.suggestion-rationale,
.suggestion-expected {
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
}

.error {
  background: #ffe6e6;
  border-left: 4px solid #ff4444;
  padding: 15px;
  border-radius: 5px;
  margin: 20px 0;
}

.footer {
  text-align: center;
  color: rgba(255,255,255,0.8);
  padding: 30px 0;
  font-size: 14px;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.github-link {
  display: flex;
  align-items: center;
  color: rgba(255,255,255,0.8);
  transition: all 0.3s;
}

.github-link:hover {
  color: white;
  transform: scale(1.1);
}

.github-link svg {
  width: 24px;
  height: 24px;
}

@media (max-width: 600px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .mbti-grid {
    grid-template-columns: 1fr;
  }
}
</style>

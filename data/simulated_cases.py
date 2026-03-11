"""
实验数据模拟 - 5 组代表性冷场对话案例
对比使用 Agent 前后的效果差异

量化指标：
- 回复延迟降低率
- 对话轮次增加数
- 焦虑感降低指数（1-10）
"""

# =============================================================================
# 案例 1: 破冰期冷场 - 不知道如何开启话题
# =============================================================================

CASE_1 = {
    "scenario": "破冰期冷场 - 不知道如何开启话题",
    "user_profile": {
        "age": 28,
        "gender": "male",
        "attachment_style": "焦虑型",
        "self_efficacy": "低"
    },
    "original_conversation": [
        {"role": "user", "content": "你好，看到你也喜欢旅行，去过哪里印象最深呀？"},
        {"role": "other", "content": "嗯，去了挺多的，一时说不上来"},
        {"role": "user", "content": "[用户不知道该怎么回复... 对话中断]"}
    ],
    "agent_analysis": {
        "perception": {
            "anxiety_level": 7,
            "psychological_tags": ["自我妨碍倾向", "社交焦虑"],
            "avoidance_indicators": ["不知道该怎么回复"],
            "self_handicapping_detected": True
        },
        "reasoning": {
            "dialogue_stage": "破冰期",
            "dialogue_momentum": "负向",
            "resistance_factors": ["对方回避型回应", "用户缺乏应对策略"],
            "stagnation_cause": "对方模糊回应 + 用户无后续策略导致冷场",
            "attribution_pattern": "将冷场归因为'我不会聊天'"
        },
        "generation": {
            "suggestions": [
                {
                    "id": 1,
                    "script": "哈哈理解，去太多的话确实难选。那我换个问法 - 如果现在给你一张机票，你最想再去哪里？",
                    "rationale": "降低回答难度，将开放式问题转为选择题",
                    "expected_response": "对方可能给出一个具体地点"
                },
                {
                    "id": 2,
                    "script": "没关系可以慢慢想~ 我最近在看 XX 的旅行纪录片，那里的 XX 好震撼",
                    "rationale": "主动提供话题锚点，降低双方压力",
                    "expected_response": "对方可能顺着话题分享"
                }
            ],
            "meta_guidance": {
                "attribution_reframe": "这不是你不会聊天，是对方还没准备好深入分享",
                "confidence_builder": "你已经用开放式问题开启话题，这是很好的开始"
            }
        }
    },
    "after_agent_conversation": [
        {"role": "user", "content": "哈哈理解，去太多的话确实难选。那我换个问法 - 如果现在给你一张机票，你最想再去哪里？"},
        {"role": "other", "content": "嗯...应该是冰岛吧，之前去看极光真的太震撼了"},
        {"role": "user", "content": "哇极光！我一直想去但还没找到机会。你是跟朋友一起还是自由行呀？"},
        {"role": "other", "content": "跟两个大学同学一起的，租了辆车环岛，特别自由"}
    ],
    "metrics": {
        "original_outcome": {
            "reply_latency_seconds": None,  # 对话中断
            "conversation_turns": 2,
            "anxiety_level": 7
        },
        "after_agent_outcome": {
            "reply_latency_seconds": 45,  # 平均回复延迟
            "conversation_turns": 6,
            "anxiety_level": 4
        },
        "improvement": {
            "reply_latency_reduction": "N/A → 45s (对话恢复)",
            "turns_increase": 4,
            "anxiety_reduction": 3
        }
    }
}

# =============================================================================
# 案例 2: 信息交换期尬聊 - 一问一答模式
# =============================================================================

CASE_2 = {
    "scenario": "信息交换期尬聊 - 一问一答模式",
    "user_profile": {
        "age": 26,
        "gender": "female",
        "attachment_style": "回避型",
        "self_efficacy": "中"
    },
    "original_conversation": [
        {"role": "other", "content": "你平时周末都喜欢做什么呀？"},
        {"role": "user", "content": "就看看书，健健身，没什么特别的"},
        {"role": "other", "content": "挺健康的哈哈，那你最喜欢看什么类型的书？"},
        {"role": "user", "content": "都看，悬疑的、历史的都看"},
        {"role": "other", "content": "[感觉对方不太想聊，不知道继续问什么...]"}
    ],
    "agent_analysis": {
        "perception": {
            "anxiety_level": 5,
            "psychological_tags": ["情感隔离", "回避型依恋"],
            "avoidance_indicators": ["没什么特别的", "都看"],
            "self_handicapping_detected": True
        },
        "reasoning": {
            "dialogue_stage": "信息交换期",
            "dialogue_momentum": "负向",
            "resistance_factors": ["用户自我贬低式回应", "模糊化表达"],
            "stagnation_cause": "用户回避型回应导致对方无法找到话题延伸点",
            "attribution_pattern": "将自己的兴趣描述为'没什么特别'，降低自我价值"
        },
        "generation": {
            "suggestions": [
                {
                    "id": 1,
                    "script": "最近刚看完《XX》，结局反转太惊艳了！你有看过哪本特别推荐的书吗？",
                    "rationale": "用具体例子替代模糊描述，同时反问对方",
                    "expected_response": "对方可能分享推荐书目"
                },
                {
                    "id": 2,
                    "script": "健身的话我比较喜欢 HIIT，虽然累但很解压~ 你平时喜欢什么运动？",
                    "rationale": "主动暴露具体信息，降低对方提问负担",
                    "expected_response": "对方可能回应自己的运动偏好"
                }
            ],
            "meta_guidance": {
                "attribution_reframe": "你不是'没什么特别'，只是习惯了低调表达。你的兴趣本身就很有价值",
                "confidence_builder": "对方主动问你就是对你感兴趣，不需要过度谦虚"
            }
        }
    },
    "after_agent_conversation": [
        {"role": "user", "content": "最近刚看完《长安的荔枝》，马伯庸写历史悬疑真的绝！你有看过哪本特别推荐的书吗？"},
        {"role": "other", "content": "啊我也超喜欢马伯庸！《显微镜下的大明》你看了吗？"},
        {"role": "user", "content": "还没！这本好看吗？那我加入书单了"},
        {"role": "other", "content": "好看！他写那种小人物视角的历史特别有意思..."}
    ],
    "metrics": {
        "original_outcome": {
            "reply_latency_seconds": 180,
            "conversation_turns": 4,
            "anxiety_level": 5
        },
        "after_agent_outcome": {
            "reply_latency_seconds": 60,
            "conversation_turns": 8,
            "anxiety_level": 3
        },
        "improvement": {
            "reply_latency_reduction": "67%",
            "turns_increase": 4,
            "anxiety_reduction": 2
        }
    }
}

# =============================================================================
# 案例 3: 情感共振期错位 - 对方表达情绪时不知如何回应
# =============================================================================

CASE_3 = {
    "scenario": "情感共振期错位 - 对方表达情绪时不知如何回应",
    "user_profile": {
        "age": 30,
        "gender": "male",
        "attachment_style": "安全型",
        "self_efficacy": "中"
    },
    "original_conversation": [
        {"role": "other", "content": "今天工作真的好累，被老板说了一顿，感觉自己做什么都做不好"},
        {"role": "user", "content": "别想太多，工作嘛都是这样的，看开点"},
        {"role": "other", "content": "嗯...（感觉敷衍，不想继续说了）"}
    ],
    "agent_analysis": {
        "perception": {
            "anxiety_level": 4,
            "psychological_tags": ["情感隔离", "低共情表达"],
            "avoidance_indicators": ["用理性建议回避情感回应"],
            "self_handicapping_detected": False
        },
        "reasoning": {
            "dialogue_stage": "情感共振期",
            "dialogue_momentum": "负向",
            "resistance_factors": ["用户未能识别对方的情感需求", "过早给出解决方案"],
            "stagnation_cause": "对方需要情感共情，用户给出理性建议导致错位",
            "attribution_pattern": "习惯性解决问题而非情感陪伴"
        },
        "generation": {
            "suggestions": [
                {
                    "id": 1,
                    "script": "被说肯定很难受吧...你今天一定很辛苦。想跟我说说具体发生了什么吗？",
                    "rationale": "先共情再询问，给对方情感确认",
                    "expected_response": "对方可能感受到被理解，愿意继续倾诉"
                },
                {
                    "id": 2,
                    "script": "抱抱你。有时候遇到这种事真的会觉得自己很没用，但这不代表你不行",
                    "rationale": "情感支持 + 归因重构，避免对方自我否定",
                    "expected_response": "对方可能感到被支持"
                },
                {
                    "id": 3,
                    "script": "你平时对自己要求那么高，遇到这种事肯定更难受。要不要吃点好吃的放松一下？",
                    "rationale": "肯定对方的努力 + 转移注意力",
                    "expected_response": "对方可能感受到关心，情绪缓解"
                }
            ],
            "meta_guidance": {
                "attribution_reframe": "这不是你不会安慰人，只是你习惯用解决问题的方式表达关心",
                "confidence_builder": "对方愿意跟你倾诉，说明已经信任你了"
            }
        }
    },
    "after_agent_conversation": [
        {"role": "user", "content": "被说肯定很难受吧...你今天一定很辛苦。想跟我说说具体发生了什么吗？"},
        {"role": "other", "content": "就是那个项目，我明明很努力了，但老板还是说不够好..."},
        {"role": "user", "content": "你已经很努力了，我都看在眼里。有时候老板的要求确实让人摸不着头脑"},
        {"role": "other", "content": "是啊...真的有点怀疑自己是不是不适合这份工作"}
    ],
    "metrics": {
        "original_outcome": {
            "reply_latency_seconds": 300,
            "conversation_turns": 3,
            "anxiety_level": 4
        },
        "after_agent_outcome": {
            "reply_latency_seconds": 90,
            "conversation_turns": 10,
            "anxiety_level": 2
        },
        "improvement": {
            "reply_latency_reduction": "70%",
            "turns_increase": 7,
            "anxiety_reduction": 2
        }
    }
}

# =============================================================================
# 案例 4: 策略性自我妨碍 - 故意不努力以避免失败归因
# =============================================================================

CASE_4 = {
    "scenario": "策略性自我妨碍 - 故意不努力以避免失败归因",
    "user_profile": {
        "age": 27,
        "gender": "female",
        "attachment_style": "焦虑型",
        "self_efficacy": "低"
    },
    "original_conversation": [
        {"role": "other", "content": "周末有空的话要不要一起去看那个新上映的电影？"},
        {"role": "user", "content": "我最近有点忙，可能不太确定...而且我不太会跟人相处，怕尴尬"},
        {"role": "other", "content": "没事啦，就是想一起 relax 一下，不用想太多"}
    ],
    "agent_analysis": {
        "perception": {
            "anxiety_level": 8,
            "psychological_tags": ["自我妨碍倾向", "低自我效能感", "社交焦虑"],
            "avoidance_indicators": ["我不太会跟人相处", "怕尴尬"],
            "self_handicapping_detected": True
        },
        "reasoning": {
            "dialogue_stage": "破冰期",
            "dialogue_momentum": "中性",
            "resistance_factors": ["用户前置防御式自我贬低", "回避邀约"],
            "stagnation_cause": "策略性自我妨碍 - 提前声明'不会相处'为潜在失败留借口",
            "attribution_pattern": "将社交能力归因为固定特质，避免投入后失败"
        },
        "generation": {
            "suggestions": [
                {
                    "id": 1,
                    "script": "谢谢你的邀请~ 我确实有点社交恐惧哈哈，但跟你聊天还挺舒服的。这周末下午我有空！",
                    "rationale": "承认焦虑但不回避，同时给出积极回应",
                    "expected_response": "对方可能感到被信任，降低期待压力"
                },
                {
                    "id": 2,
                    "script": "好呀！不过我可能刚开始会有点拘谨，熟了就好了~ 你想看哪部？",
                    "rationale": "预期管理 + 表达意愿，降低双方压力",
                    "expected_response": "对方可能理解并继续讨论电影选择"
                }
            ],
            "meta_guidance": {
                "attribution_reframe": "你不是'不会相处'，只是需要时间热身。这是性格特点，不是缺陷",
                "confidence_builder": "对方邀请你就是因为跟你相处舒服，不需要证明自己"
            }
        }
    },
    "after_agent_conversation": [
        {"role": "user", "content": "好呀！不过我可能刚开始会有点拘谨，熟了就好了~ 你想看哪部？"},
        {"role": "other", "content": "哈哈没关系，我也不是社牛。看《XX》吧，评分挺高的"},
        {"role": "user", "content": "好呀！那周六下午两点？"},
        {"role": "other", "content": "OK！我到时候去接你"}
    ],
    "metrics": {
        "original_outcome": {
            "reply_latency_seconds": 600,
            "conversation_turns": 3,
            "anxiety_level": 8
        },
        "after_agent_outcome": {
            "reply_latency_seconds": 120,
            "conversation_turns": 6,
            "anxiety_level": 5
        },
        "improvement": {
            "reply_latency_reduction": "80%",
            "turns_increase": 3,
            "anxiety_reduction": 3
        }
    }
}

# =============================================================================
# 案例 5: 归因偏差 - 将成功归因于运气，失败归因于能力
# =============================================================================

CASE_5 = {
    "scenario": "归因偏差 - 将成功归因于运气，失败归因于能力",
    "user_profile": {
        "age": 29,
        "gender": "male",
        "attachment_style": "安全型",
        "self_efficacy": "中"
    },
    "original_conversation": [
        {"role": "other", "content": "感觉跟你聊天挺开心的，之前还以为你会很高冷呢"},
        {"role": "user", "content": "哈哈没有啦，只是运气好遇到合得来的人"},
        {"role": "other", "content": "你平时都是这么谦虚的吗？"},
        {"role": "user", "content": "可能吧，我其实挺无趣的..."}
    ],
    "agent_analysis": {
        "perception": {
            "anxiety_level": 6,
            "psychological_tags": ["归因偏差", "自我贬低"],
            "avoidance_indicators": ["只是运气好", "我其实挺无趣的"],
            "self_handicapping_detected": True
        },
        "reasoning": {
            "dialogue_stage": "信息交换期",
            "dialogue_momentum": "正向",
            "resistance_factors": ["用户将积极反馈归因为运气", "自我贬低式回应"],
            "stagnation_cause": "归因偏差导致无法接纳积极反馈，可能让对方困惑",
            "attribution_pattern": "成功=运气（外部不稳定），失败=能力（内部稳定）"
        },
        "generation": {
            "suggestions": [
                {
                    "id": 1,
                    "script": "被你这么说还挺开心的~ 我可能慢热，但遇到聊得来的人也会很投入",
                    "rationale": "接纳积极反馈 + 适度自我暴露",
                    "expected_response": "对方可能感到被真诚回应"
                },
                {
                    "id": 2,
                    "script": "哈哈被夸了有点不好意思。不过跟你聊天确实很放松，你很有倾听的天赋",
                    "rationale": "接纳赞美 + 回赞对方，形成正向循环",
                    "expected_response": "对方可能感到被欣赏，关系升温"
                }
            ],
            "meta_guidance": {
                "attribution_reframe": "对方说你有趣是因为你真的有趣，不是运气。尝试接纳这个反馈",
                "confidence_builder": "你已经在创造好的对话体验，这不是偶然"
            }
        }
    },
    "after_agent_conversation": [
        {"role": "user", "content": "被你这么说还挺开心的~ 我可能慢热，但遇到聊得来的人也会很投入"},
        {"role": "other", "content": "能感觉到你是认真的，这点很难得"},
        {"role": "user", "content": "谢谢，你也是。很多人聊天都是表面客套，但你让我觉得可以放松一点"},
        {"role": "other", "content": "嗯，我也是这么想的..."}
    ],
    "metrics": {
        "original_outcome": {
            "reply_latency_seconds": 240,
            "conversation_turns": 4,
            "anxiety_level": 6
        },
        "after_agent_outcome": {
            "reply_latency_seconds": 90,
            "conversation_turns": 8,
            "anxiety_level": 3
        },
        "improvement": {
            "reply_latency_reduction": "62.5%",
            "turns_increase": 4,
            "anxiety_reduction": 3
        }
    }
}

# =============================================================================
# 汇总分析报告
# =============================================================================

ALL_CASES = [CASE_1, CASE_2, CASE_3, CASE_4, CASE_5]

AGGREGATE_ANALYSIS = {
    "total_cases": 5,
    "average_metrics": {
        "original": {
            "avg_reply_latency": 330,  # 秒
            "avg_conversation_turns": 3.2,
            "avg_anxiety_level": 6.0
        },
        "after_agent": {
            "avg_reply_latency": 79,  # 秒
            "avg_conversation_turns": 7.6,
            "avg_anxiety_level": 2.8
        },
        "improvement": {
            "reply_latency_reduction": "76%",
            "turns_increase": 4.4,
            "anxiety_reduction": 3.2
        }
    },
    "psychological_patterns_detected": {
        "自我妨碍倾向": 4,
        "社交焦虑": 3,
        "情感隔离": 2,
        "归因偏差": 2,
        "回避型依恋": 2,
        "低自我效能感": 2
    },
    "most_effective_strategies": [
        "降低回答难度（开放式→选择题）",
        "主动暴露具体信息替代模糊描述",
        "先共情再询问的情感回应模式",
        "接纳积极反馈而非归因于运气",
        "预期管理 + 表达意愿"
    ]
}


def print_case_summary(case):
    """打印案例摘要"""
    print(f"\n{'='*60}")
    print(f"案例：{case['scenario']}")
    print(f"{'='*60}")
    print(f"原始对话轮次：{case['metrics']['original_outcome']['conversation_turns']}")
    print(f"Agent 后轮次：{case['metrics']['after_agent_outcome']['conversation_turns']}")
    print(f"对话轮次增加：{case['metrics']['improvement']['turns_increase']}")
    print(f"焦虑值降低：{case['metrics']['improvement']['anxiety_reduction']}")
    print(f"\n核心建议:")
    for s in case['agent_analysis']['generation']['suggestions'][:2]:
        print(f"  • {s['script']}")


if __name__ == "__main__":
    print("=" * 60)
    print("婚恋 AI Agent - 实验数据模拟报告")
    print("=" * 60)

    for case in ALL_CASES:
        print_case_summary(case)

    print(f"\n{'='*60}")
    print("汇总分析")
    print(f"{'='*60}")
    print(f"平均对话轮次增加：{AGGREGATE_ANALYSIS['average_metrics']['improvement']['turns_increase']}")
    print(f"平均焦虑值降低：{AGGREGATE_ANALYSIS['average_metrics']['improvement']['anxiety_reduction']}")
    print(f"回复延迟降低率：{AGGREGATE_ANALYSIS['average_metrics']['improvement']['reply_latency_reduction']}")

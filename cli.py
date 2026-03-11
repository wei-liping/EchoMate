#!/usr/bin/env python3
"""
聊天 Debug (Chat-lock Debugger) AI agent v1.1 - CLI 命令行工具
快速分析对话，获取建议
"""

import argparse
import json
import sys
from pathlib import Path

from engine import DatingAgentEngine, MODEL_CONFIGS


def list_providers():
    """列出所有可用的模型提供商"""
    print("\n可用的模型提供商:")
    print("-" * 50)
    providers = DatingAgentEngine.get_available_providers()
    for p in providers:
        print(f"  {p['key']:12} - {p['name']} ({p['default_model']})")
    print()


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    config_file = Path(config_path)
    if config_file.exists():
        return json.loads(config_file.read_text())
    return {}


def save_config(config: dict, config_path: str):
    """保存配置文件"""
    config_file = Path(config_path)
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))


def cmd_analyze(args):
    """分析对话命令"""
    config = load_config(args.config)

    provider = args.provider or config.get("provider", "qwen")
    api_key = args.api_key or config.get("api_key")
    model_name = args.model_name or config.get("model_name")
    base_url = args.base_url or config.get("base_url")

    if not api_key and provider != "ollama":
        print("❌ 错误：请提供 API Key 或设置环境变量")
        print("   使用 --api-key 参数或在配置文件中设置")
        print(f"   支持的提供商：{', '.join(MODEL_CONFIGS.keys())}")
        sys.exit(1)

    engine = DatingAgentEngine(
        model_provider=provider,
        api_key=api_key,
        model_name=model_name,
        base_url=base_url
    )

    # 读取输入
    if args.input:
        user_input = Path(args.input).read_text()
    elif args.text:
        user_input = args.text
    else:
        print("请输入对话内容 (Ctrl+D 结束):")
        user_input = sys.stdin.read()

    if not user_input.strip():
        print("❌ 错误：输入为空")
        sys.exit(1)

    # 执行分析
    print(f"\n🔍 正在分析... (模型：{provider})")
    print("-" * 50)

    try:
        result = engine.analyze(user_input)

        # 输出结果
        print(f"\n📊 分析结果\n")

        # 感知层
        print(f"🧠 感知层:")
        print(f"   焦虑水平：{result.perception.anxiety_level}/10")
        print(f"   心理标签：{', '.join(result.perception.psychological_tags)}")
        if result.perception.self_handicapping_detected:
            print(f"   ⚠️  自我妨碍倾向：检测到")

        # 推理层
        print(f"\n🤖 推理层:")
        print(f"   对话阶段：{result.reasoning.dialogue_stage}")
        print(f"   动量状态：{result.reasoning.dialogue_momentum}")
        print(f"   僵局成因：{result.reasoning.stagnation_cause}")

        # 生成层
        print(f"\n💡 对话建议:\n")
        for i, s in enumerate(result.generation.suggestions, 1):
            print(f"  [{i}] {s.script}")
            print(f"      策略：{s.rationale}")
            print(f"      预期：{s.expected_response}")
            print()

        # 心理引导
        print(f"🌟 心理引导:")
        print(f"   归因重构：{result.generation.meta_guidance.attribution_reframe}")
        print(f"   信心建立：{result.generation.meta_guidance.confidence_builder}")

        # JSON 输出
        if args.json:
            print("\n" + "=" * 50)
            print("JSON 输出:")
            output = {
                "perception": {
                    "anxiety_level": result.perception.anxiety_level,
                    "psychological_tags": result.perception.psychological_tags,
                    "self_handicapping_detected": result.perception.self_handicapping_detected
                },
                "reasoning": {
                    "dialogue_stage": result.reasoning.dialogue_stage,
                    "dialogue_momentum": result.reasoning.dialogue_momentum,
                    "stagnation_cause": result.reasoning.stagnation_cause
                },
                "suggestions": [
                    {
                        "script": s.script,
                        "rationale": s.rationale,
                        "expected_response": s.expected_response
                    }
                    for s in result.generation.suggestions
                ],
                "meta_guidance": {
                    "attribution_reframe": result.generation.meta_guidance.attribution_reframe,
                    "confidence_builder": result.generation.meta_guidance.confidence_builder
                }
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 分析失败：{str(e)}")
        sys.exit(1)


def cmd_config(args):
    """配置管理命令"""
    config = {}

    if args.provider:
        config["provider"] = args.provider
    if args.api_key:
        config["api_key"] = args.api_key
    if args.model_name:
        config["model_name"] = args.model_name
    if args.base_url:
        config["base_url"] = args.base_url

    if config:
        save_config(config, args.config)
        print(f"✅ 配置已保存到：{args.config}")
    else:
        # 显示当前配置
        if Path(args.config).exists():
            print(f"当前配置 ({args.config}):")
            print(json.dumps(load_config(args.config), indent=2))
        else:
            print("暂无配置，使用 --provider 和 --api-key 设置")

    # 显示可用的提供商列表
    if args.list_providers:
        list_providers()


def cmd_quick(args):
    """快速分析模式"""
    config = load_config(args.config)
    provider = config.get("provider", "qwen")
    api_key = config.get("api_key")
    model_name = config.get("model_name")
    base_url = config.get("base_url")

    if not api_key and provider != "ollama":
        print("❌ 请先配置 API Key: dating-agent config --api-key YOUR_KEY")
        sys.exit(1)

    engine = DatingAgentEngine(
        model_provider=provider,
        api_key=api_key,
        model_name=model_name,
        base_url=base_url
    )

    user_input = args.text
    if not user_input:
        print("请输入对话内容:")
        user_input = input("> ")

    result = engine.analyze_quick(user_input)

    print(f"\n焦虑水平：{result['anxiety_level']}/10")
    print(f"对话阶段：{result['stage']}")
    print(f"\n建议:")
    for i, s in enumerate(result['suggestions'], 1):
        print(f"  {i}. {s['script']}")
    print(f"\n{result['meta_guidance']['confidence_builder']}")


def main():
    # 获取可用的提供商列表用于帮助信息
    providers_list = ', '.join(MODEL_CONFIGS.keys())

    parser = argparse.ArgumentParser(
        description="聊天 Debug (Chat-lock Debugger) AI agent v1.1 - 对话分析助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
支持的模型提供商:
  {providers_list}

示例:
  %(prog)s analyze --text "不知道该怎么和 TA 聊天..." --provider qwen
  %(prog)s analyze -i conversation.txt --provider kimi --api-key YOUR_KEY
  %(prog)s config --provider qwen --api-key YOUR_KEY
  %(prog)s config --list-providers  # 列出所有支持的提供商
  %(prog)s quick --text "刚匹配不知道说什么"
        """
    )

    parser.add_argument(
        "--config", "-c",
        default=str(Path.home() / ".dating_agent" / "config.json"),
        help="配置文件路径 (默认：~/.dating_agent/config.json)"
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析对话")
    analyze_parser.add_argument("--text", "-t", help="对话文本")
    analyze_parser.add_argument("--input", "-i", help="输入文件路径")
    analyze_parser.add_argument("--provider", "-p", help=f"模型提供商 (默认：qwen). 支持的：{providers_list}")
    analyze_parser.add_argument("--api-key", "-k", help="API Key")
    analyze_parser.add_argument("--model-name", "-m", help="自定义模型名称")
    analyze_parser.add_argument("--base-url", "-u", help="自定义 API 基础 URL")
    analyze_parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    analyze_parser.set_defaults(func=cmd_analyze)

    # config 命令
    config_parser = subparsers.add_parser("config", help="配置管理")
    config_parser.add_argument("--provider", "-p", help=f"模型提供商。支持的：{providers_list}")
    config_parser.add_argument("--api-key", "-k", help="API Key")
    config_parser.add_argument("--model-name", "-m", help="自定义模型名称")
    config_parser.add_argument("--base-url", "-u", help="自定义 API 基础 URL")
    config_parser.add_argument("--list-providers", "-l", action="store_true", help="列出所有支持的提供商")
    config_parser.set_defaults(func=cmd_config)

    # quick 命令
    quick_parser = subparsers.add_parser("quick", help="快速分析")
    quick_parser.add_argument("--text", "-t", help="对话文本")
    quick_parser.set_defaults(func=cmd_quick)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # 创建配置目录
    config_dir = Path(args.config).parent
    config_dir.mkdir(parents=True, exist_ok=True)

    args.func(args)


if __name__ == "__main__":
    main()

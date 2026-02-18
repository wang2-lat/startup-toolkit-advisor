#!/usr/bin/env python3
import typer
import json
from typing import List, Dict
from pathlib import Path
from datetime import datetime

app = typer.Typer(help="创业者工具推荐+需求验证助手")

# 工具数据库
TOOLS_DB = {
    "项目管理": [
        {"name": "Notion", "price": 0, "max_price": 10, "features": ["文档", "数据库", "协作"], "team_size": "1-50"},
        {"name": "Trello", "price": 0, "max_price": 12.5, "features": ["看板", "任务管理"], "team_size": "1-20"},
        {"name": "Asana", "price": 0, "max_price": 24.99, "features": ["项目跟踪", "时间线"], "team_size": "5-100"},
    ],
    "客户管理": [
        {"name": "HubSpot CRM", "price": 0, "max_price": 50, "features": ["联系人管理", "邮件追踪"], "team_size": "1-50"},
        {"name": "Pipedrive", "price": 14, "max_price": 99, "features": ["销售管道", "自动化"], "team_size": "1-100"},
    ],
    "营销推广": [
        {"name": "Mailchimp", "price": 0, "max_price": 350, "features": ["邮件营销", "自动化"], "team_size": "1-无限"},
        {"name": "Canva", "price": 0, "max_price": 12.99, "features": ["设计", "社交媒体"], "team_size": "1-50"},
    ],
    "数据分析": [
        {"name": "Google Analytics", "price": 0, "max_price": 0, "features": ["网站分析", "用户行为"], "team_size": "1-无限"},
        {"name": "Mixpanel", "price": 0, "max_price": 89, "features": ["产品分析", "漏斗"], "team_size": "1-100"},
    ],
    "沟通协作": [
        {"name": "Slack", "price": 0, "max_price": 12.5, "features": ["即时通讯", "集成"], "team_size": "1-无限"},
        {"name": "飞书", "price": 0, "max_price": 20, "features": ["文档", "会议", "OKR"], "team_size": "1-无限"},
    ]
}

# 需求验证问卷模板
SURVEY_TEMPLATES = {
    "B2B SaaS": [
        "您目前使用什么工具解决[核心问题]？",
        "每月在这个问题上花费多少时间/金钱？",
        "如果有工具能节省50%时间，您愿意付多少钱？",
        "您的决策流程是怎样的？谁是最终决策者？",
        "您最近一次购买类似工具是什么时候？为什么选择它？"
    ],
    "电商": [
        "您最近一次购买[产品类别]是什么时候？",
        "您通常在哪些平台购买这类产品？",
        "影响您购买决策的前3个因素是什么？",
        "您愿意为[核心价值]多付多少钱？",
        "您会推荐给朋友吗？为什么？"
    ],
    "本地服务": [
        "您多久需要一次[服务类型]？",
        "您目前如何找到服务提供商？",
        "您最看重的是价格、质量还是便利性？",
        "您上次使用类似服务遇到了什么问题？",
        "您愿意为上门服务多付多少钱？"
    ],
    "内容/教育": [
        "您在[领域]学习上每月花费多少时间？",
        "您目前使用哪些学习资源？",
        "您最大的学习障碍是什么？",
        "您愿意为系统化课程付多少钱？",
        "您更喜欢视频、文字还是互动式学习？"
    ]
}

@app.command()
def recommend(
    budget: int = typer.Option(..., prompt="每月工具预算（元）"),
    team_size: int = typer.Option(..., prompt="团队人数"),
    business_type: str = typer.Option(..., prompt="业务类型（B2B SaaS/电商/本地服务/内容教育）")
):
    """根据预算和场景推荐工具组合"""
    
    typer.echo("\n🔍 分析中...\n")
    
    # 筛选工具
    recommendations = {}
    total_cost = 0
    
    for category, tools in TOOLS_DB.items():
        best_tool = None
        for tool in tools:
            # 检查预算和团队规模
            max_cost = tool["max_price"] * team_size if tool["max_price"] > 0 else 0
            if max_cost <= budget - total_cost:
                if best_tool is None or tool["max_price"] > best_tool["max_price"]:
                    best_tool = tool
        
        if best_tool:
            recommendations[category] = best_tool
            cost = best_tool["max_price"] * team_size if best_tool["max_price"] > 0 else 0
            total_cost += cost
    
    # 输出推荐
    typer.echo("=" * 60)
    typer.echo(f"📦 推荐工具组合（预算: ¥{budget}/月，团队: {team_size}人）")
    typer.echo("=" * 60)
    
    for category, tool in recommendations.items():
        cost = tool["max_price"] * team_size if tool["max_price"] > 0 else 0
        typer.echo(f"\n【{category}】{tool['name']}")
        typer.echo(f"  💰 月成本: ¥{cost:.2f} ({tool['price']}-{tool['max_price']}/人)")
        typer.echo(f"  ✨ 功能: {', '.join(tool['features'])}")
    
    typer.echo(f"\n{'=' * 60}")
    typer.echo(f"💵 总成本: ¥{total_cost:.2f}/月 (剩余预算: ¥{budget - total_cost:.2f})")
    typer.echo(f"{'=' * 60}\n")
    
    # 保存推荐
    save = typer.confirm("是否保存推荐方案？")
    if save:
        filename = f"recommendation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "budget": budget,
                "team_size": team_size,
                "business_type": business_type,
                "recommendations": recommendations,
                "total_cost": total_cost
            }, f, ensure_ascii=False, indent=2)
        typer.echo(f"✅ 已保存到 {filename}")

@app.command()
def survey(
    business_type: str = typer.Option(..., prompt="业务类型（B2B SaaS/电商/本地服务/内容教育）"),
    product_name: str = typer.Option(..., prompt="产品/服务名称")
):
    """生成需求验证问卷"""
    
    # 匹配模板
    template_key = None
    for key in SURVEY_TEMPLATES.keys():
        if key.lower() in business_type.lower() or business_type.lower() in key.lower():
            template_key = key
            break
    
    if not template_key:
        template_key = "B2B SaaS"  # 默认模板
    
    questions = SURVEY_TEMPLATES[template_key]
    
    typer.echo("\n" + "=" * 60)
    typer.echo(f"📋 需求验证问卷 - {product_name}")
    typer.echo("=" * 60)
    typer.echo(f"\n业务类型: {template_key}\n")
    
    for i, q in enumerate(questions, 1):
        typer.echo(f"{i}. {q}")
    
    typer.echo("\n" + "=" * 60)
    typer.echo("💡 使用建议:")
    typer.echo("  • 至少访谈20-30个目标用户")
    typer.echo("  • 重点关注用户的实际行为，而非假设")
    typer.echo("  • 询问具体金额和时间，避免模糊回答")
    typer.echo("  • 如果70%以上用户愿意付费，需求验证通过")
    typer.echo("=" * 60 + "\n")
    
    # 保存问卷
    save = typer.confirm("是否保存问卷？")
    if save:
        filename = f"survey_{product_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"需求验证问卷 - {product_name}\n")
            f.write(f"业务类型: {template_key}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for i, q in enumerate(questions, 1):
                f.write(f"{i}. {q}\n")
        typer.echo(f"✅ 已保存到 {filename}")

@app.command()
def compare(
    budget: int = typer.Option(..., prompt="每月预算（元）"),
    team_size: int = typer.Option(..., prompt="团队人数")
):
    """对比不同工具方案的成本"""
    
    typer.echo("\n💰 成本对比分析\n")
    
    scenarios = [
        {"name": "免费方案", "multiplier": 0},
        {"name": "基础方案", "multiplier": 0.3},
        {"name": "专业方案", "multiplier": 0.7},
        {"name": "企业方案", "multiplier": 1.0}
    ]
    
    typer.echo("=" * 80)
    typer.echo(f"{'方案':<15} {'月成本':<15} {'年成本':<15} {'包含工具':<30}")
    typer.echo("=" * 80)
    
    for scenario in scenarios:
        total_monthly = 0
        tools_included = []
        
        for category, tools in TOOLS_DB.items():
            for tool in tools:
                cost_per_person = tool["price"] + (tool["max_price"] - tool["price"]) * scenario["multiplier"]
                if cost_per_person * team_size <= budget * scenario["multiplier"]:
                    total_monthly += cost_per_person * team_size
                    tools_included.append(tool["name"])
                    break
        
        total_yearly = total_monthly * 12
        tools_str = ", ".join(tools_included[:3]) + ("..." if len(tools_included) > 3 else "")
        
        typer.echo(f"{scenario['name']:<15} ¥{total_monthly:<14.2f} ¥{total_yearly:<14.2f} {tools_str:<30}")
    
    typer.echo("=" * 80)
    typer.echo(f"\n💡 建议: 预算 ¥{budget}/月 适合选择「基础方案」或「专业方案」\n")

@app.command()
def guide():
    """获客渠道指南"""
    
    typer.echo("\n" + "=" * 60)
    typer.echo("🎯 创业者获客渠道指南")
    typer.echo("=" * 60)
    
    channels = {
        "B2B SaaS": [
            "LinkedIn 内容营销（发布行业洞察）",
            "产品评测网站（Product Hunt, G2）",
            "行业社群/论坛（知识星球、Reddit）",
            "SEO 优化（针对长尾关键词）",
            "冷邮件外展（个性化模板）"
        ],
        "电商": [
            "小红书种草（KOC合作）",
            "抖音/快手短视频",
            "拼多多/淘宝站内推广",
            "私域流量（微信社群）",
            "直播带货"
        ],
        "本地服务": [
            "美团/大众点评",
            "本地微信群/朋友圈",
            "地推传单（商圈/社区）",
            "老客户转介绍（优惠激励）",
            "抖音同城推广"
        ],
        "内容/教育": [
            "知乎专栏（长文干货）",
            "B站/YouTube 视频教程",
            "公众号/小报童",
            "免费试听课（引流）",
            "知识付费平台（小鹅通、千聊）"
        ]
    }
    
    for biz_type, channel_list in channels.items():
        typer.echo(f"\n【{biz_type}】")
        for i, channel in enumerate(channel_list, 1):
            typer.echo(f"  {i}. {channel}")
    
    typer.echo("\n" + "=" * 60)
    typer.echo("⚠️  避坑指南:")
    typer.echo("  • 不要一开始就投广告，先验证需求")
    typer.echo("  • 选1-2个渠道深耕，不要广撒网")
    typer.echo("  • 追踪每个渠道的转化率（用UTM参数）")
    typer.echo("  • 前100个客户靠手动获取，不靠广告")
    typer.echo("=" * 60 + "\n")

if __name__ == "__main__":
    app()
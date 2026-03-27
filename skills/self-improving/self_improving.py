#!/usr/bin/env python3
"""
Self-Improving Skill

基于复盘数据生成改进建议，推动组织自我进化。
"""

import sys
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta

sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/skills/pmo-manager"))
from src.api import PMOManagerAPI


class SelfImprovingSkill:
    """自我改进技能"""
    
    def __init__(self):
        self.pmo = PMOManagerAPI()
    
    def analyze_retro(self, retro_id: str) -> Dict[str, Any]:
        """
        分析单个复盘并生成改进建议
        
        Args:
            retro_id: 复盘 ID
            
        Returns:
            分析结果和建议
        """
        retro = self.pmo.get_retro(retro_id)
        if not retro:
            return {"success": False, "error": "复盘不存在"}
        
        items = self.pmo.retro_service.storage.list_retro_items(retro_id)
        actions = self.pmo.retro_service.storage.list_action_items(retro_id)
        
        # 分类统计
        categories = {}
        for item in items:
            cat = item.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        # 生成洞察
        insights = []
        
        # 分析高频问题
        if 'mad' in categories and len(categories['mad']) > 1:
            insights.append({
                "type": "pattern",
                "severity": "high",
                "description": f"发现 {len(categories['mad'])} 个愤怒/不满的反馈，需要重点关注",
                "recommendation": "组织专项讨论，分析根本原因并制定改进计划"
            })
        
        if 'sad' in categories and len(categories['sad']) > 1:
            insights.append({
                "type": "pattern", 
                "severity": "medium",
                "description": f"发现 {len(categories['sad'])} 个沮丧/失望的反馈",
                "recommendation": "识别改进机会，将沮丧点转化为行动计划"
            })
        
        # 分析成功经验
        if 'glad' in categories:
            best_practices = [item.content for item in categories['glad']]
            insights.append({
                "type": "strength",
                "severity": "low",
                "description": f"识别 {len(best_practices)} 个成功经验",
                "recommendation": "将这些实践固化为团队规范，在其他项目中推广"
            })
        
        # 生成改进建议
        suggestions = self._generate_suggestions(categories, insights)
        
        return {
            "success": True,
            "retro_id": retro_id,
            "summary": {
                "total_items": len(items),
                "categories": {cat: len(items) for cat, items in categories.items()},
                "action_items": len(actions)
            },
            "insights": insights,
            "suggestions": suggestions
        }
    
    def _generate_suggestions(self, categories: Dict, insights: List) -> List[Dict]:
        """生成改进建议"""
        suggestions = []
        
        # 基于 mad 反馈生成建议
        if 'mad' in categories:
            for item in categories['mad']:
                suggestion = {
                    "source": f"mad: {item.content[:50]}",
                    "title": f"改进: {item.content[:30]}...",
                    "description": item.content,
                    "priority": "P0" if item.votes >= 3 else "P1",
                    "category": "process_improvement",
                    "action_type": "fix"
                }
                suggestions.append(suggestion)
        
        # 基于 sad 反馈生成建议
        if 'sad' in categories:
            for item in categories['sad']:
                suggestion = {
                    "source": f"sad: {item.content[:50]}",
                    "title": f"优化: {item.content[:30]}...",
                    "description": item.content,
                    "priority": "P1",
                    "category": "opportunity",
                    "action_type": "enhance"
                }
                suggestions.append(suggestion)
        
        # 基于 glad 反馈生成建议（保持和推广）
        if 'glad' in categories:
            for item in categories['glad']:
                suggestion = {
                    "source": f"glad: {item.content[:50]}",
                    "title": f"固化: {item.content[:30]}...",
                    "description": f"将成功经验 '{item.content}' 固化为团队最佳实践",
                    "priority": "P2",
                    "category": "best_practice",
                    "action_type": "document"
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def create_action_items(self, retro_id: str, suggestions: List[Dict]) -> Dict[str, Any]:
        """
        根据建议创建改进行动项
        
        Args:
            retro_id: 复盘 ID
            suggestions: 建议列表
            
        Returns:
            创建结果
        """
        created = []
        failed = []
        
        for suggestion in suggestions:
            try:
                # 分配给合适的角色
                assignee = self._determine_assignee(suggestion)
                
                result = self.pmo.create_action_item(
                    retro_id=retro_id,
                    title=suggestion['title'],
                    assignee_id=assignee,
                    due_date=datetime.now() + timedelta(days=14),
                    priority=suggestion.get('priority', 'P1'),
                    description=suggestion['description']
                )
                
                if result['success']:
                    created.append({
                        "action_id": result['action_item'].action_id,
                        "title": suggestion['title'],
                        "assignee": assignee
                    })
                else:
                    failed.append({
                        "title": suggestion['title'],
                        "error": result.get('message', '未知错误')
                    })
            except Exception as e:
                failed.append({
                    "title": suggestion['title'],
                    "error": str(e)
                })
        
        return {
            "success": True,
            "created": created,
            "failed": failed,
            "total": len(suggestions)
        }
    
    def _determine_assignee(self, suggestion: Dict) -> str:
        """根据建议类型确定负责人"""
        category = suggestion.get('category', '')
        action_type = suggestion.get('action_type', '')
        
        # 流程改进 → PMO
        if category == 'process_improvement':
            return 'caocan'
        
        # 技术问题 → 架构师
        if '技术' in suggestion.get('description', '') or '代码' in suggestion.get('description', ''):
            return 'xiaohe'
        
        # 产品问题 → 产品经理
        if '需求' in suggestion.get('description', '') or '产品' in suggestion.get('description', ''):
            return 'zhangliang'
        
        # 环境问题 → DevOps
        if '环境' in suggestion.get('description', '') or '部署' in suggestion.get('description', ''):
            return 'zhoubo'
        
        # 文档/知识 → 知识库管理员
        if action_type == 'document':
            return 'lujia'
        
        # 默认分配给 PMO
        return 'caocan'
    
    def analyze_trends(self, retro_ids: List[str]) -> Dict[str, Any]:
        """
        分析多个复盘的趋势
        
        Args:
            retro_ids: 复盘 ID 列表
            
        Returns:
            趋势分析结果
        """
        all_items = []
        
        for retro_id in retro_ids:
            items = self.pmo.retro_service.storage.list_retro_items(retro_id)
            all_items.extend(items)
        
        # 统计高频主题
        word_freq = {}
        for item in all_items:
            words = item.content.split()
            for word in words:
                if len(word) > 2:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # 找出重复出现的问题
        recurring_issues = [word for word, count in word_freq.items() if count >= 3]
        
        return {
            "success": True,
            "total_retros": len(retro_ids),
            "total_items": len(all_items),
            "recurring_themes": recurring_issues[:10],
            "suggestion": "如果发现重复出现的问题，考虑制定系统性解决方案"
        }


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(prog='self-improving', description='自我改进技能')
    subparsers = parser.add_subparsers(dest='command')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析复盘')
    analyze_parser.add_argument('retro_id', help='复盘 ID')
    analyze_parser.add_argument('--create-actions', '-a', action='store_true', help='自动创建行动项')
    
    # trends 命令
    trends_parser = subparsers.add_parser('trends', help='分析趋势')
    trends_parser.add_argument('retro_ids', nargs='+', help='复盘 ID 列表')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    skill = SelfImprovingSkill()
    
    if args.command == 'analyze':
        result = skill.analyze_retro(args.retro_id)
        if result['success']:
            print(f"=== 复盘分析结果 ({args.retro_id}) ===\n")
            print(f"统计: {result['summary']}\n")
            
            print("洞察:")
            for insight in result['insights']:
                emoji = "🔴" if insight['severity'] == 'high' else "🟡" if insight['severity'] == 'medium' else "🟢"
                print(f"  {emoji} {insight['description']}")
                print(f"     建议: {insight['recommendation']}\n")
            
            print(f"改进建议 ({len(result['suggestions'])} 条):")
            for i, suggestion in enumerate(result['suggestions'], 1):
                print(f"  {i}. [{suggestion['priority']}] {suggestion['title']}")
            
            if args.create_actions:
                print("\n创建改进行动项...")
                create_result = skill.create_action_items(args.retro_id, result['suggestions'])
                print(f"  ✅ 成功创建 {len(create_result['created'])} 个")
                if create_result['failed']:
                    print(f"  ❌ 失败 {len(create_result['failed'])} 个")
        else:
            print(f"❌ 分析失败: {result.get('error')}")
    
    elif args.command == 'trends':
        result = skill.analyze_trends(args.retro_ids)
        if result['success']:
            print(f"=== 趋势分析 ({result['total_retros']} 个复盘) ===\n")
            print(f"总条目数: {result['total_items']}")
            print(f"\n重复主题: {', '.join(result['recurring_themes'])}")
            print(f"\n建议: {result['suggestion']}")


if __name__ == '__main__':
    main()

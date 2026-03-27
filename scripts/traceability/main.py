#!/usr/bin/env python3
"""
InfinityCompany Traceability Checker

Usage:
    python main.py --check all --report daily
    python main.py --check git --since "7 days ago"
    python main.py --check notion --report weekly

Environment Variables:
    NOTION_API_KEY - Notion API Key
    NOTION_STORY_DB_ID - Story database ID
    NOTION_TASK_DB_ID - Task database ID
    NOTION_BUG_DB_ID - Bug database ID
    NOTION_ITERATION_DB_ID - Iteration database ID
    NOTION_RETROSPECTIVE_DB_ID - Retrospective database ID
    NOTION_EXTERNAL_REQ_DB_ID - External requirements database ID
"""

import os
import sys
import argparse
import json
from datetime import datetime, date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.git_checker import GitCommitChecker
from core.document_checker import DocumentChecker
from core.notion_checker import NotionChecker
from core.retro_checker import RetroChecker
from utils.logger import get_logger, log_check_result


logger = get_logger()


class TraceabilityReport:
    """留痕校验报告生成器"""
    
    def __init__(self, report_type: str = "daily"):
        self.report_type = report_type
        self.generated_at = datetime.now()
        self.sections = []
        self.summary = {
            "total_checks": 0,
            "passed": 0,
            "warnings": 0,
            "errors": 0
        }
    
    def add_section(self, name: str, status: str, errors: list, warnings: list, 
                    info: list = None, stats: dict = None):
        """添加报告章节"""
        section = {
            "name": name,
            "status": status,
            "errors": errors or [],
            "warnings": warnings or [],
            "info": info or [],
            "stats": stats or {}
        }
        self.sections.append(section)
        
        # Update summary
        self.summary["total_checks"] += 1
        if not errors and not warnings:
            self.summary["passed"] += 1
        self.summary["warnings"] += len(warnings or [])
        self.summary["errors"] += len(errors or [])
    
    def to_markdown(self) -> str:
        """生成 Markdown 格式报告"""
        lines = [
            "# 留痕校验报告",
            "",
            f"> **报告类型**: {self.report_type}  ",
            f"> **生成时间**: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"> **校验版本**: v1.0.0",
            "",
            "---",
            "",
            "## 📊 总体概览",
            "",
            "| 指标 | 数值 |",
            "|-----|------|",
            f"| 总检查项 | {self.summary['total_checks']} |",
            f"| 通过 | {self.summary['passed']} ✅ |",
            f"| 警告 | {self.summary['warnings']} ⚠️ |",
            f"| 错误 | {self.summary['errors']} ❌ |",
            "",
            "---",
            "",
            "## 🔍 详细检查结果",
            ""
        ]
        
        for section in self.sections:
            status_emoji = "✅" if section["status"] == "passed" else "⚠️" if section["status"] == "warning" else "❌"
            
            lines.extend([
                f"### {section['name']}",
                "",
                f"**状态**: {status_emoji} {section['status']}",
                ""
            ])
            
            if section["errors"]:
                lines.append("**错误**:")
                for error in section["errors"][:10]:  # Limit to 10
                    lines.append(f"- ❌ {error}")
                if len(section["errors"]) > 10:
                    lines.append(f"- ... 还有 {len(section['errors']) - 10} 个错误")
                lines.append("")
            
            if section["warnings"]:
                lines.append("**警告**:")
                for warning in section["warnings"][:10]:
                    lines.append(f"- ⚠️ {warning}")
                if len(section["warnings"]) > 10:
                    lines.append(f"- ... 还有 {len(section['warnings']) - 10} 个警告")
                lines.append("")
            
            if section["stats"]:
                lines.append("**统计**:")
                for key, value in section["stats"].items():
                    lines.append(f"- {key}: {value}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Action items
        if self.summary["errors"] > 0 or self.summary["warnings"] > 0:
            lines.extend([
                "## 📋 待办事项",
                "",
                "| 优先级 | 事项 | 状态 |",
                "|-------|------|------|"
            ])
            
            for section in self.sections:
                for error in section["errors"][:5]:
                    lines.append(f"| 🔴 高 | [{section['name']}] {error[:50]}... | 待处理 |")
                for warning in section["warnings"][:3]:
                    lines.append(f"| 🟡 中 | [{section['name']}] {warning[:50]}... | 待处理 |")
            
            lines.append("")
        
        lines.append("*报告由 InfinityCompany 留痕校验系统自动生成*")
        
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """生成 JSON 格式报告"""
        return json.dumps({
            "metadata": {
                "report_type": self.report_type,
                "generated_at": self.generated_at.isoformat(),
                "version": "1.0.0"
            },
            "summary": self.summary,
            "sections": self.sections
        }, ensure_ascii=False, indent=2)
    
    def save(self, output_dir: str = "./reports"):
        """保存报告到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = self.generated_at.strftime('%Y%m%d_%H%M%S')
        
        # Save Markdown
        md_file = output_path / f"traceability_{self.report_type}_{timestamp}.md"
        md_file.write_text(self.to_markdown(), encoding='utf-8')
        logger.info(f"Report saved to {md_file}")
        
        # Save JSON
        json_file = output_path / f"traceability_{self.report_type}_{timestamp}.json"
        json_file.write_text(self.to_json(), encoding='utf-8')
        
        return md_file, json_file


def run_git_check(since: str = "7 days ago") -> tuple:
    """运行 Git 检查"""
    logger.info("Running Git checks...")
    
    checker = GitCommitChecker()
    result = checker.run_all_checks(since=since)
    
    status = "error" if result.errors else "warning" if result.warnings else "passed"
    
    log_check_result(logger, "Git 提交校验", result.errors, result.warnings, result.info)
    
    return status, result.errors, result.warnings, result.info, result.stats


def run_document_check() -> tuple:
    """运行文档检查"""
    logger.info("Running document checks...")
    
    checker = DocumentChecker()
    result = checker.run_all_checks()
    
    status = "error" if result.errors else "warning" if result.warnings else "passed"
    
    log_check_result(logger, "文档更新校验", result.errors, result.warnings, result.info)
    
    return status, result.errors, result.warnings, result.info, {}


def run_notion_check() -> tuple:
    """运行 Notion 检查"""
    logger.info("Running Notion checks...")
    
    api_key = os.getenv('NOTION_API_KEY')
    if not api_key:
        logger.warning("NOTION_API_KEY not set, skipping Notion checks")
        return "passed", [], ["NOTION_API_KEY not set, skipped"], [], {}
    
    try:
        checker = NotionChecker(api_key)
        result = checker.run_all_checks()
        
        errors = [e.get('message', str(e)) for e in result.errors]
        warnings = [w.get('message', str(w)) for w in result.warnings]
        info = [i.get('message', str(i)) for i in result.info]
        
        status = "error" if errors else "warning" if warnings else "passed"
        
        log_check_result(logger, "Notion 看板校验", errors, warnings, info)
        
        return status, errors, warnings, info, result.stats
    except Exception as e:
        logger.error(f"Notion check failed: {e}")
        return "error", [f"Notion check failed: {e}"], [], [], {}


def run_retro_check() -> tuple:
    """运行复盘检查"""
    logger.info("Running retrospective checks...")
    
    api_key = os.getenv('NOTION_API_KEY')
    if not api_key:
        logger.warning("NOTION_API_KEY not set, skipping retrospective checks")
        return "passed", [], ["NOTION_API_KEY not set, skipped"], [], {}
    
    try:
        from core.notion_checker import NotionChecker
        notion_checker = NotionChecker(api_key)
        checker = RetroChecker(notion_checker)
        result = checker.run_all_checks()
        
        errors = [e.get('message', str(e)) for e in result.errors]
        warnings = [w.get('message', str(w)) for w in result.warnings]
        info = [i.get('message', str(i)) for i in result.info]
        
        status = "error" if errors else "warning" if warnings else "passed"
        
        log_check_result(logger, "复盘同步校验", errors, warnings, info)
        
        return status, errors, warnings, info, result.summary
    except Exception as e:
        logger.error(f"Retrospective check failed: {e}")
        return "error", [f"Retrospective check failed: {e}"], [], [], {}


def main():
    parser = argparse.ArgumentParser(
        description='InfinityCompany Traceability Checker'
    )
    parser.add_argument(
        '--check',
        choices=['all', 'git', 'document', 'notion', 'retro'],
        default='all',
        help='Check type to run'
    )
    parser.add_argument(
        '--report',
        choices=['daily', 'weekly', 'monthly', 'iteration'],
        default='daily',
        help='Report type'
    )
    parser.add_argument(
        '--since',
        default='7 days ago',
        help='Git log since time (e.g., "7 days ago", "2024-01-01")'
    )
    parser.add_argument(
        '--output',
        default='./reports',
        help='Output directory for reports'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json', 'both'],
        default='both',
        help='Report format'
    )
    parser.add_argument(
        '--fail-on-error',
        action='store_true',
        help='Exit with error code if any check fails'
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting traceability check: {args.check}")
    logger.info(f"Report type: {args.report}")
    
    report = TraceabilityReport(report_type=args.report)
    has_error = False
    
    # Run checks
    if args.check in ['all', 'git']:
        try:
            status, errors, warnings, info, stats = run_git_check(args.since)
            report.add_section("Git 提交校验", status, errors, warnings, info, stats)
            if status == "error":
                has_error = True
        except Exception as e:
            logger.error(f"Git check failed: {e}")
            report.add_section("Git 提交校验", "error", [str(e)], [], [])
            has_error = True
    
    if args.check in ['all', 'document']:
        try:
            status, errors, warnings, info, stats = run_document_check()
            report.add_section("文档更新校验", status, errors, warnings, info, stats)
            if status == "error":
                has_error = True
        except Exception as e:
            logger.error(f"Document check failed: {e}")
            report.add_section("文档更新校验", "error", [str(e)], [], [])
            has_error = True
    
    if args.check in ['all', 'notion']:
        try:
            status, errors, warnings, info, stats = run_notion_check()
            report.add_section("Notion 看板校验", status, errors, warnings, info, stats)
            if status == "error":
                has_error = True
        except Exception as e:
            logger.error(f"Notion check failed: {e}")
            report.add_section("Notion 看板校验", "error", [str(e)], [], [])
            has_error = True
    
    if args.check in ['all', 'retro']:
        try:
            status, errors, warnings, info, stats = run_retro_check()
            report.add_section("复盘同步校验", status, errors, warnings, info, stats)
            if status == "error":
                has_error = True
        except Exception as e:
            logger.error(f"Retrospective check failed: {e}")
            report.add_section("复盘同步校验", "error", [str(e)], [], [])
            has_error = True
    
    # Save report
    try:
        md_file, json_file = report.save(args.output)
        print(f"\n📄 Report saved:")
        print(f"   Markdown: {md_file}")
        print(f"   JSON: {json_file}")
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
    
    # Print summary
    print("\n" + "="*50)
    print("📊 检查摘要")
    print("="*50)
    print(f"总检查项: {report.summary['total_checks']}")
    print(f"通过: {report.summary['passed']} ✅")
    print(f"警告: {report.summary['warnings']} ⚠️")
    print(f"错误: {report.summary['errors']} ❌")
    print("="*50)
    
    if args.fail_on_error and has_error:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()

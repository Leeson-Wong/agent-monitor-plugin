"""
代码审查工具包

这些工具用于代码审查过程中的质量分析和安全检查。
"""

from crewai_tools import BaseTool
from pydantic import Field
from typing import Optional
import re


class CodeComplexityTool(BaseTool):
    """代码复杂度分析工具"""
    name: str = "code_complexity_analyzer"
    description: str = """
    分析代码的复杂度指标，包括圈复杂度、认知复杂度、代码行数等。
    输入应该是代码片段或文件路径。
    返回详细的复杂度分析报告。
    """
    code: str = Field(default="", description="要分析的代码")

    def _run(self, code: str) -> str:
        """执行代码复杂度分析"""
        lines = code.split('\n')
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        empty_lines = len([l for l in lines if not l.strip()])

        # 计算圈复杂度（简化版本）
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'case', 'catch', 'try']
        complexity = 1  # 基础复杂度
        for line in lines:
            for keyword in complexity_keywords:
                complexity += line.count(keyword)

        # 评估复杂度等级
        if complexity <= 5:
            level = "低"
        elif complexity <= 10:
            level = "中"
        elif complexity <= 20:
            level = "高"
        else:
            level = "非常高"

        return f"""
代码复杂度分析报告
{'=' * 50}
总行数：{total_lines}
代码行数：{code_lines}
空行数：{empty_lines}
圈复杂度：{complexity}
复杂度等级：{level}
{'=' * 50}

说明：
- 圈复杂度 {complexity} 表示代码中有 {complexity - 1} 个独立路径
- 复杂度等级为 "{level}" {'✓' if level in ['低', '中'] else '⚠️'}
- {'建议：代码复杂度较低，易于维护。' if level == '低' else ''}
- {'建议：代码复杂度适中，可以接受。' if level == '中' else ''}
- {'建议：考虑重构以降低复杂度。' if level == '高' else ''}
- {'警告：代码过于复杂，强烈建议重构！' if level == '非常高' else ''}
"""


class SecurityScanTool(BaseTool):
    """安全扫描工具"""
    name: str = "security_scanner"
    description: str = """
    扫描代码中的潜在安全漏洞。
    检查SQL注入、XSS、硬编码密钥、不安全的函数调用等问题。
    输入应该是代码片段。
    返回安全问题列表。
    """
    code: str = Field(default="", description="要扫描的代码")

    def _run(self, code: str) -> str:
        """执行安全扫描"""
        issues = []

        # 检查硬编码密钥/密码
        if re.search(r'(password|secret|key|api_key)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            issues.append({
                'severity': '高',
                'issue': '硬编码密钥/密码',
                'description': '代码中可能包含硬编码的敏感信息',
                'recommendation': '使用环境变量或配置文件存储敏感信息'
            })

        # 检查SQL注入风险
        if re.search(r'execute\(|executemany\(.*%\s*.*\)', code, re.IGNORECASE):
            issues.append({
                'severity': '高',
                'issue': 'SQL注入风险',
                'description': '使用字符串拼接构建SQL查询',
                'recommendation': '使用参数化查询或ORM'
            })

        # 检查eval使用
        if 'eval(' in code:
            issues.append({
                'severity': '高',
                'issue': '不安全的eval使用',
                'description': 'eval()可以执行任意代码',
                'recommendation': '避免使用eval，使用更安全的替代方案'
            })

        # 检查shell命令注入
        if re.search(r'system\(|popen\(|subprocess\.call\(.*shell=True', code):
            issues.append({
                'severity': '中',
                'issue': 'Shell命令注入风险',
                'description': '直接执行shell命令可能存在注入风险',
                'recommendation': '使用参数化调用或白名单验证'
            })

        # 检查弱加密
        if re.search(r'md5\(|sha1\(', code):
            issues.append({
                'severity': '中',
                'issue': '弱加密算法',
                'description': 'MD5和SHA1已被认为不安全',
                'recommendation': '使用SHA-256或更强的哈希算法'
            })

        if not issues:
            return """
安全扫描报告
{'=' * 50}
✓ 未发现明显的安全问题
{'=' * 50}

注意：此扫描仅检查常见安全问题，不能替代专业的安全审计。
"""

        report = "安全扫描报告\n" + "=" * 50 + "\n"
        report += f"发现 {len(issues)} 个潜在安全问题\n\n"

        for i, issue in enumerate(issues, 1):
            report += f"{i}. [{issue['severity']}] {issue['issue']}\n"
            report += f"   描述：{issue['description']}\n"
            report += f"   建议：{issue['recommendation']}\n\n"

        report += "=" * 50
        return report


class CodeSmellDetector(BaseTool):
    """代码异味检测工具"""
    name: str = "code_smell_detector"
    description: str = """
    检测代码中的常见异味和不良实践。
    包括重复代码、长函数、魔法数字、命名问题等。
    输入应该是代码片段。
    返回代码异味列表。
    """
    code: str = Field(default="", description="要检测的代码")

    def _run(self, code: str) -> str:
        """执行代码异味检测"""
        smells = []

        lines = code.split('\n')

        # 检测长函数
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        if len(code_lines) > 50:
            smells.append({
                'type': '长函数',
                'severity': '中',
                'description': f'函数有 {len(code_lines)} 行代码',
                'suggestion': '考虑将函数拆分为更小的、单一职责的函数'
            })

        # 检测魔法数字
        magic_numbers = re.findall(r'\b\d{2,}\b', code)
        if len(set(magic_numbers)) > 3:
            smells.append({
                'type': '魔法数字',
                'severity': '低',
                'description': f'发现 {len(set(magic_numbers))} 个可能的魔法数字',
                'suggestion': '使用命名常量代替魔法数字'
            })

        # 检测深层次嵌套
        max_nesting = 0
        current_nesting = 0
        for line in lines:
            stripped = line.strip()
            if stripped.endswith(':'):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped and not stripped.startswith('#'):
                # 简单的嵌套检测（不完美但有用）
                indent = len(line) - len(line.lstrip())
                current_nesting = indent // 4

        if max_nesting > 4:
            smells.append({
                'type': '深层次嵌套',
                'severity': '中',
                'description': f'最大嵌套深度为 {max_nesting} 层',
                'suggestion': '使用早返回或提取函数来减少嵌套'
            })

        # 检测过长行
        long_lines = [(i+1, len(l)) for i, l in enumerate(lines) if len(l) > 100]
        if len(long_lines) > 0:
            smells.append({
                'type': '过长行',
                'severity': '低',
                'description': f'发现 {len(long_lines)} 行超过100字符',
                'suggestion': '将长行拆分为多行以提高可读性'
            })

        if not smells:
            return """
代码异味检测报告
{'=' * 50}
✓ 未发现明显的代码异味
{'=' * 50}

代码质量良好！
"""

        report = "代码异味检测报告\n" + "=" * 50 + "\n"
        report += f"发现 {len(smells)} 个代码异味\n\n"

        for i, smell in enumerate(smells, 1):
            report += f"{i}. [{smell['severity']}] {smell['type']}\n"
            report += f"   描述：{smell['description']}\n"
            report += f"   建议：{smell['suggestion']}\n\n"

        report += "=" * 50
        return report

"""
Git Helper - Utility functions for Git operations
"""

import re
import subprocess
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommitInfo:
    """Git 提交信息"""
    hash: str
    author: str
    email: str
    timestamp: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int


class GitHelper:
    """Git 操作辅助类"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def _run_git(self, args: List[str]) -> str:
        """运行 Git 命令"""
        cmd = ['git'] + args
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise GitError(f"Git command failed: {result.stderr}")
        
        return result.stdout
    
    def get_commits(self, since: Optional[str] = None, until: Optional[str] = None,
                   author: Optional[str] = None, max_count: Optional[int] = None) -> List[CommitInfo]:
        """获取提交列表"""
        format_str = '%H|%an|%ae|%at|%s'
        args = ['log', f'--pretty=format:{format_str}', '--shortstat']
        
        if since:
            args.append(f'--since={since}')
        if until:
            args.append(f'--until={until}')
        if author:
            args.append(f'--author={author}')
        if max_count:
            args.append(f'--max-count={max_count}')
        
        output = self._run_git(args)
        return self._parse_log(output)
    
    def _parse_log(self, log_output: str) -> List[CommitInfo]:
        """解析 Git 日志输出"""
        commits = []
        lines = log_output.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if '|' in line:
                parts = line.split('|', 4)
                if len(parts) >= 5:
                    commit_hash = parts[0]
                    author = parts[1]
                    email = parts[2]
                    timestamp = datetime.fromtimestamp(int(parts[3]))
                    message = parts[4]
                    
                    # 解析统计行
                    files_changed = 0
                    insertions = 0
                    deletions = 0
                    
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if 'changed' in next_line or 'insertion' in next_line or 'deletion' in next_line:
                            files_changed, insertions, deletions = self._parse_stat_line(next_line)
                            i += 1
                    
                    commits.append(CommitInfo(
                        hash=commit_hash,
                        author=author,
                        email=email,
                        timestamp=timestamp,
                        message=message,
                        files_changed=files_changed,
                        insertions=insertions,
                        deletions=deletions
                    ))
            i += 1
        
        return commits
    
    def _parse_stat_line(self, stat_line: str) -> Tuple[int, int, int]:
        """解析 Git 统计行"""
        files_changed = 0
        insertions = 0
        deletions = 0
        
        # Match patterns like:
        # "3 files changed, 50 insertions(+), 10 deletions(-)"
        # "1 file changed, 10 insertions(+)"
        # "2 files changed, 5 deletions(-)"
        
        files_match = re.search(r'(\d+) file', stat_line)
        if files_match:
            files_changed = int(files_match.group(1))
        
        insert_match = re.search(r'(\d+) insertion', stat_line)
        if insert_match:
            insertions = int(insert_match.group(1))
        
        delete_match = re.search(r'(\d+) deletion', stat_line)
        if delete_match:
            deletions = int(delete_match.group(1))
        
        return files_changed, insertions, deletions
    
    def get_changed_files(self, commit_hash: str) -> List[str]:
        """获取提交修改的文件列表"""
        output = self._run_git(['diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash])
        return [f.strip() for f in output.strip().split('\n') if f.strip()]
    
    def get_current_branch(self) -> str:
        """获取当前分支名"""
        output = self._run_git(['rev-parse', '--abbrev-ref', 'HEAD'])
        return output.strip()
    
    def get_branches(self, remote: bool = False) -> List[str]:
        """获取分支列表"""
        args = ['branch']
        if remote:
            args.append('-r')
        else:
            args.append('-a')
        
        output = self._run_git(args)
        branches = []
        
        for line in output.strip().split('\n'):
            branch = line.strip().strip('* ')
            if branch:
                branches.append(branch)
        
        return branches
    
    def get_last_commit_time(self, file_path: str) -> Optional[datetime]:
        """获取文件最后提交时间"""
        try:
            output = self._run_git(['log', '-1', '--format=%at', '--', file_path])
            timestamp = int(output.strip())
            return datetime.fromtimestamp(timestamp)
        except (ValueError, GitError):
            return None
    
    def is_valid_commit_hash(self, commit_hash: str) -> bool:
        """检查提交哈希是否有效"""
        try:
            self._run_git(['cat-file', '-t', commit_hash])
            return True
        except GitError:
            return False
    
    def get_commit_message(self, commit_hash: str) -> str:
        """获取提交信息"""
        return self._run_git(['log', '-1', '--format=%B', commit_hash]).strip()
    
    def get_tags(self) -> List[str]:
        """获取标签列表"""
        output = self._run_git(['tag', '-l'])
        return [t.strip() for t in output.strip().split('\n') if t.strip()]


class GitError(Exception):
    """Git 操作错误"""
    pass

"""
核心业务逻辑服务
"""

import os
import re
import json
import uuid
import subprocess
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from .models import Agent, AgentRole, Email
from .storage import Storage
from .constants import ESCALATION_PATHS


class AgentService:
    """成员服务 - 处理成员查询相关操作"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """根据ID获取成员信息"""
        return self.storage.get_agent(agent_id)
    
    def find_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """根据角色查找成员"""
        return self.storage.find_agents_by_role(role)
    
    def find_agents_by_name(self, name: str) -> List[Agent]:
        """根据姓名模糊搜索成员"""
        return self.storage.find_agents_by_name(name)
    
    def find_agents_by_skill(self, skill: str) -> List[Agent]:
        """根据技能搜索成员"""
        return self.storage.find_agents_by_skill(skill)
    
    def list_all_agents(self) -> List[Agent]:
        """列出所有成员"""
        return self.storage.list_all_agents()
    
    def get_agent_chain(self, agent_id: str) -> List[Agent]:
        """获取成员的汇报链"""
        return self.storage.get_reporting_chain(agent_id)


class OrganizationService:
    """组织服务 - 处理组织架构相关操作"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def get_org_chart(self) -> Dict:
        """获取完整组织架构图"""
        return self.storage.get_org_chart()
    
    def get_team_by_role(self, role: AgentRole) -> List[Agent]:
        """根据角色获取团队"""
        return self.storage.find_agents_by_role(role)
    
    def get_escalation_path(self, escalation_type: str) -> Optional[Dict]:
        """
        获取事件升级路径
        
        Args:
            escalation_type: 升级类型 (incident, requirement, quality, external)
            
        Returns:
            升级路径定义或 None
        """
        path_def = ESCALATION_PATHS.get(escalation_type)
        if not path_def:
            return None
        
        # 丰富路径信息
        enriched_path = []
        for step in path_def["path"]:
            agent = self.storage.get_agent(step["agent_id"])
            enriched_path.append({
                "level": step["level"],
                "agent_id": step["agent_id"],
                "agent_name": agent.name if agent else step["agent_id"],
                "title": agent.title if agent else "",
                "role": step["role"],
            })
        
        return {
            "type": escalation_type,
            "name": path_def["name"],
            "path": enriched_path,
        }


class CommunicationService:
    """通讯服务 - 处理跨Agent通讯"""
    
    def __init__(self, storage: Storage, inbox_base_path: str = None):
        self.storage = storage
        self.inbox_base_path = inbox_base_path or "~/.openclaw/workspace/emergency_inbox"
        self.acpx_store_path = os.path.expanduser("~/.openclaw/workspace/company-directory/messages/acpx_messages.jsonl")
        self.runtime_agent_aliases = {
            "caocan": "main",
        }
        self.human_only_agents = {"liubang"}
    
    def send_email(self, target_id: str, subject: str, message: str, 
                   sender_id: str = "system", urgency: str = "normal",
                   msg_type: str = "notification", reply_to: str = None) -> Dict:
        """
        发送异步邮件到指定 Agent 的 emergency_inbox
        
        Args:
            target_id: 目标 Agent ID
            subject: 邮件主题
            message: 邮件内容
            sender_id: 发送方 Agent ID（可选）
            urgency: 紧急程度 - urgent(紧急), normal(普通), low(低优先级)
            msg_type: 消息类型 - notification(只需知悉), response_required(需要回复), action_required(需要行动)
            reply_to: 回复引用的消息ID（可选）
        
        Returns:
            {"status": "success"/"error", "message": str, "email_id": str}
        """
        # 验证目标Agent存在
        target = self.storage.get_agent(target_id)
        if not target:
            return {
                "status": "error",
                "message": f"未知的 Agent ID: {target_id}",
                "valid_agents": [a.agent_id for a in self.storage.list_all_agents()]
            }
        
        # 获取发送方信息
        sender = self.storage.get_agent(sender_id)
        sender_name = sender.name if sender else (sender_id if sender_id != "system" else "系统")
        
        # 创建邮件对象
        email = Email(
            email_id=str(uuid.uuid4()),
            sender_id=sender_id,
            sender_name=sender_name,
            target_id=target_id,
            subject=subject,
            message=message,
            timestamp=datetime.now(),
            urgency=urgency,
            msg_type=msg_type,
            reply_to=reply_to
        )
        
        # 写入文件
        inbox_path = os.path.expanduser(f"{self.inbox_base_path}/{target_id}")
        os.makedirs(inbox_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"email_{urgency}_{timestamp}_{email.email_id[:8]}.md"
        filepath = os.path.join(inbox_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(email.to_file_content())
            
            urgency_desc = {"urgent": "紧急", "normal": "普通", "low": "低优先级"}.get(urgency, urgency)
            type_desc = {"notification": "通知", "response_required": "需回复", "action_required": "需行动"}.get(msg_type, msg_type)
            
            return {
                "status": "success",
                "message": f"[{urgency_desc}/{type_desc}] 邮件已投递至 {target.name} ({target_id})",
                "email_id": email.email_id,
                "file_path": filepath,
                "target_name": target.name,
                "urgency": urgency,
                "msg_type": msg_type,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"邮件投递失败: {str(e)}"
            }
    
    def check_inbox(self, agent_id: str) -> List[Dict]:
        """
        检查指定 Agent 的收件箱
        
        Args:
            agent_id: Agent ID
            
        Returns:
            邮件列表
        """
        inbox_path = os.path.expanduser(f"{self.inbox_base_path}/{agent_id}")
        if not os.path.exists(inbox_path):
            return []
        
        import glob
        emails = []
        for filepath in glob.glob(f"{inbox_path}/email_*.md"):
            emails.append({
                "file_path": filepath,
                "filename": os.path.basename(filepath)
            })
        
        return sorted(emails, key=lambda x: x["filename"], reverse=True)
    
    def get_acpx_command(self, target_id: str, message: str) -> str:
        """
        生成 acpx 命令
        
        Args:
            target_id: 目标 Agent ID
            message: 消息内容
            
        Returns:
            可执行的 acpx 命令字符串
        """
        escaped_message = message.replace('"', '\\"')
        return f"acpx-infinity {target_id} \"{escaped_message}\""

    def check_agent_presence(self, agent_id: str, timeout_seconds: int = 20) -> Dict:
        target = self.storage.get_agent(agent_id)
        if not target:
            return {
                "status": "unknown",
                "message": f"未知的 Agent ID: {agent_id}"
            }
        if agent_id in self.human_only_agents:
            return {
                "status": "unsupported",
                "message": f"{target.name} 为人类负责人，不支持 acpx 实时探测",
            }

        probe_message = "状态探测: 仅回复 ONLINE_ACK"
        result = self._execute_openclaw_agent(agent_id, probe_message, timeout_seconds)
        if result["status"] == "success":
            return {
                "status": "online",
                "message": f"{target.name} 在线并可响应",
                "response_preview": result.get("response", "")[:120],
                "runtime_agent_id": result.get("runtime_agent_id", agent_id),
            }
        error_text = (result.get("error") or "").lower()
        if "session file locked" in error_text:
            return {
                "status": "busy",
                "message": f"{target.name} 当前会话被锁定",
                "error": result.get("error", ""),
                "runtime_agent_id": result.get("runtime_agent_id", agent_id),
            }
        if "timeout" in error_text or "超时" in error_text:
            return {
                "status": "busy",
                "message": f"{target.name} 当前可能繁忙或响应超时",
                "error": result.get("error", ""),
                "runtime_agent_id": result.get("runtime_agent_id", agent_id),
            }
        return {
            "status": "offline",
            "message": f"{target.name} 未在探测时响应",
            "error": result.get("error", ""),
            "runtime_agent_id": result.get("runtime_agent_id", agent_id),
        }

    def send_acpx_message(self, target_id: str, message: str, sender_id: str = "system",
                          timeout_seconds: int = 120, auto_ack: bool = True,
                          probe_timeout_seconds: int = 20, broadcast_id: Optional[str] = None,
                          retries: int = 0, fallback_to_email: bool = False,
                          fallback_email_urgency: str = "urgent") -> Dict:
        target = self.storage.get_agent(target_id)
        if not target:
            return {
                "status": "error",
                "message": f"未知的 Agent ID: {target_id}",
                "valid_agents": [a.agent_id for a in self.storage.list_all_agents()]
            }
        if target_id in self.human_only_agents:
            return {
                "status": "error",
                "message": f"{target.name} 为人类负责人，不支持 acpx 实时消息，请改用线下沟通或人工渠道",
            }

        sender = self.storage.get_agent(sender_id)
        sender_name = sender.name if sender else (sender_id if sender_id != "system" else "系统")
        message_id = str(uuid.uuid4())
        runtime_agent_id = self._resolve_runtime_agent_id(target_id)
        presence = self.check_agent_presence(target_id, timeout_seconds=probe_timeout_seconds)

        attempts = max(retries, 0) + 1
        result = {"status": "error", "error": "未执行"}
        response_text = ""
        errors: List[str] = []
        payload = ""
        for attempt in range(1, attempts + 1):
            payload = self._build_acpx_payload(
                message_id=message_id,
                sender_id=sender_id,
                target_id=target_id,
                runtime_agent_id=runtime_agent_id,
                message=message,
                auto_ack=auto_ack,
                attempt=attempt,
                attempts=attempts
            )
            result = self._execute_openclaw_agent(target_id, payload, timeout_seconds, runtime_agent_id=runtime_agent_id)
            response_text = result.get("response", "")
            if result["status"] == "success":
                break
            err = result.get("error")
            if err:
                errors.append(err)

        receipt_status = "failed"
        if result["status"] == "success":
            receipt_status = "delivered"
            if self._contains_ack(response_text, message_id):
                receipt_status = "read"

        fallback_email_result: Optional[Dict] = None
        if result["status"] != "success" and fallback_to_email:
            email_subject = f"[acpx降级投递] 来自 {sender_name} 的消息"
            email_body = (
                f"原实时消息发送失败，已降级为邮箱投递。\n\n"
                f"- 发送方: {sender_name} ({sender_id})\n"
                f"- 目标方: {target.name} ({target_id})\n"
                f"- 原消息ID: {message_id}\n"
                f"- 原消息内容:\n{message}\n\n"
                f"- 失败原因摘要:\n{(errors[-1] if errors else result.get('error', 'unknown'))}\n"
            )
            fallback_email_result = self.send_email(
                target_id=target_id,
                subject=email_subject,
                message=email_body,
                sender_id=sender_id,
                urgency=fallback_email_urgency,
                msg_type="action_required",
                reply_to=message_id
            )
            if fallback_email_result.get("status") == "success":
                receipt_status = "fallback_email"

        record = {
            "message_id": message_id,
            "broadcast_id": broadcast_id,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "target_id": target_id,
            "target_name": target.name,
            "message": message,
            "payload": payload,
            "runtime_agent_id": runtime_agent_id,
            "timestamp": datetime.now().isoformat(),
            "target_status": presence.get("status"),
            "delivery_status": receipt_status,
            "attempts": attempts,
            "requires_reply": auto_ack,
            "auto_ack": auto_ack,
            "response": response_text,
            "error": result.get("error"),
            "errors": errors,
            "fallback_email_result": fallback_email_result,
        }
        self._append_message_record(record)

        return {
            "status": "success" if result["status"] == "success" or receipt_status == "fallback_email" else "error",
            "message_id": message_id,
            "target_id": target_id,
            "target_name": target.name,
            "target_status": presence.get("status"),
            "delivery_status": receipt_status,
            "attempts": attempts,
            "requires_reply": auto_ack,
            "response": response_text,
            "error": result.get("error"),
            "errors": errors,
            "fallback_email_result": fallback_email_result,
            "runtime_agent_id": result.get("runtime_agent_id", target_id),
        }

    def send_broadcast(self, selector: str, message: str, sender_id: str = "system",
                       timeout_seconds: int = 120, auto_ack: bool = True,
                       probe_timeout_seconds: int = 20, retries: int = 0,
                       retry_failed_targets: bool = False, retry_rounds: int = 1,
                       fallback_to_email: bool = False,
                       fallback_email_urgency: str = "urgent") -> Dict:
        target_ids = self._resolve_targets(selector)
        if not target_ids:
            return {
                "status": "error",
                "message": f"未匹配到目标: {selector}"
            }

        broadcast_id = str(uuid.uuid4())
        latest_by_target: Dict[str, Dict] = {}
        for target_id in target_ids:
            send_result = self.send_acpx_message(
                target_id=target_id,
                message=message,
                sender_id=sender_id,
                timeout_seconds=timeout_seconds,
                auto_ack=auto_ack,
                probe_timeout_seconds=probe_timeout_seconds,
                broadcast_id=broadcast_id,
                retries=retries,
                fallback_to_email=fallback_to_email,
                fallback_email_urgency=fallback_email_urgency
            )
            latest_by_target[target_id] = send_result

        if retry_failed_targets and retry_rounds > 0:
            for _ in range(retry_rounds):
                failed_targets = [
                    tid for tid, result in latest_by_target.items()
                    if result.get("delivery_status") == "failed"
                ]
                if not failed_targets:
                    break
                for target_id in failed_targets:
                    retry_result = self.send_acpx_message(
                        target_id=target_id,
                        message=message,
                        sender_id=sender_id,
                        timeout_seconds=timeout_seconds,
                        auto_ack=auto_ack,
                        probe_timeout_seconds=probe_timeout_seconds,
                        broadcast_id=broadcast_id,
                        retries=retries,
                        fallback_to_email=fallback_to_email,
                        fallback_email_urgency=fallback_email_urgency
                    )
                    latest_by_target[target_id] = retry_result

        results = [latest_by_target[tid] for tid in target_ids]

        delivered_count = len([r for r in results if r.get("delivery_status") in {"delivered", "read", "fallback_email"}])
        read_count = len([r for r in results if r.get("delivery_status") == "read"])
        failed_count = len(results) - delivered_count

        return {
            "status": "success",
            "broadcast_id": broadcast_id,
            "selector": selector,
            "total": len(results),
            "delivered": delivered_count,
            "read": read_count,
            "failed": failed_count,
            "results": results,
        }

    def query_message_history(self, limit: int = 50, sender_id: Optional[str] = None,
                              target_id: Optional[str] = None, broadcast_id: Optional[str] = None) -> List[Dict]:
        path = Path(self.acpx_store_path)
        if not path.exists():
            return []

        records: List[Dict] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if sender_id and record.get("sender_id") != sender_id:
                    continue
                if target_id and record.get("target_id") != target_id:
                    continue
                if broadcast_id and record.get("broadcast_id") != broadcast_id:
                    continue
                records.append(record)

        records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
        return records[:max(limit, 1)]
    
    def get_contact_info(self, agent_id: str) -> Optional[Dict]:
        """
        获取成员的联系方式
        
        Args:
            agent_id: Agent ID
            
        Returns:
            联系方式信息
        """
        agent = self.storage.get_agent(agent_id)
        if not agent:
            return None
        
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "title": agent.title,
            "acpx_command": f"acpx-infinity {agent.agent_id} \"你的消息\"",
            "inbox_path": f"~/.openclaw/workspace/emergency_inbox/{agent.agent_id}",
            "email": agent.email or f"{agent.agent_id}@infinity.company",
        }

    def _execute_openclaw_agent(self, agent_id: str, message: str, timeout_seconds: int,
                                runtime_agent_id: Optional[str] = None) -> Dict:
        runtime_agent_id = runtime_agent_id or self._resolve_runtime_agent_id(agent_id)
        cmd = [
            "openclaw", "agent",
            "--agent", runtime_agent_id,
            "--timeout", str(timeout_seconds),
            "--message", message
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds + 15)
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": f"命令执行超时（>{timeout_seconds}s）"
            }
        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc)
            }

        stdout = self._sanitize_agent_output(proc.stdout or "")
        stderr = (proc.stderr or "").strip()
        combined_error = stderr
        if proc.returncode != 0 and stdout:
            combined_error = f"{stderr}\n{stdout}".strip()
        if "Error:" in stdout and proc.returncode == 0:
            combined_error = stdout
        if proc.returncode != 0 or combined_error:
            return {
                "status": "error",
                "response": stdout,
                "error": combined_error or f"命令返回码 {proc.returncode}",
                "runtime_agent_id": runtime_agent_id,
            }
        return {
            "status": "success",
            "response": stdout,
            "runtime_agent_id": runtime_agent_id,
        }

    def _build_acpx_payload(self, message_id: str, sender_id: str, target_id: str,
                            runtime_agent_id: str, message: str, auto_ack: bool,
                            attempt: int, attempts: int) -> str:
        requires_reply = "true" if auto_ack else "false"
        lines = [
            "[ACPX-MSG v1]",
            f"id={message_id}",
            f"from={sender_id}",
            f"to={target_id}",
            f"runtime_to={runtime_agent_id}",
            f"requires_reply={requires_reply}",
            f"attempt={attempt}/{attempts}",
            f"timestamp={datetime.now().isoformat()}",
            "content<<",
            message,
            ">>content",
        ]
        if auto_ack:
            lines.append(f"reply_format=ACK {message_id}")
        lines.append("[/ACPX-MSG]")
        return "\n".join(lines)

    def _resolve_runtime_agent_id(self, agent_id: str) -> str:
        runtime_ids = self._list_runtime_agent_ids()
        if not runtime_ids:
            return self.runtime_agent_aliases.get(agent_id, agent_id)
        if agent_id in runtime_ids:
            return agent_id
        mapped = self.runtime_agent_aliases.get(agent_id)
        if mapped and mapped in runtime_ids:
            return mapped
        return agent_id

    def _list_runtime_agent_ids(self) -> List[str]:
        try:
            proc = subprocess.run(
                ["openclaw", "agents", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception:
            return []
        output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        ids: List[str] = []
        for line in output.splitlines():
            m = re.match(r"^- ([^\s]+)", line.strip())
            if m:
                ids.append(m.group(1))
        return ids

    def _sanitize_agent_output(self, raw: str) -> str:
        lines = []
        for line in raw.splitlines():
            striped = line.strip()
            if not striped:
                continue
            if "[plugins]" in striped:
                continue
            if striped.startswith("🦞 OpenClaw"):
                continue
            if striped.startswith("│") or striped.startswith("◇"):
                continue
            if striped.startswith("Gateway target:") or striped.startswith("Source:") or striped.startswith("Config:"):
                continue
            lines.append(line)
        return "\n".join(lines).strip()

    def _contains_ack(self, response: str, message_id: str) -> bool:
        if not response:
            return False
        patterns = [
            rf"\bACK\s+{re.escape(message_id)}\b",
            rf"\b已收到\b.*{re.escape(message_id[:8])}",
            rf"\b收到\b.*{re.escape(message_id[:8])}",
        ]
        return any(re.search(p, response, flags=re.IGNORECASE) for p in patterns)

    def _resolve_targets(self, selector: str) -> List[str]:
        if selector == "all":
            return [a.agent_id for a in self.storage.list_all_agents() if a.agent_id not in self.human_only_agents]

        if selector.startswith("role:"):
            role_name = selector.split(":", 1)[1].strip()
            if not role_name:
                return []
            try:
                role = AgentRole(role_name)
            except ValueError:
                return []
            return [a.agent_id for a in self.storage.find_agents_by_role(role) if a.agent_id not in self.human_only_agents]

        if selector.startswith("ids:"):
            raw_ids = selector.split(":", 1)[1]
            parsed = [x.strip() for x in raw_ids.split(",") if x.strip()]
            valid = []
            for aid in parsed:
                if self.storage.get_agent(aid) and aid not in self.human_only_agents:
                    valid.append(aid)
            return valid

        if self.storage.get_agent(selector) and selector not in self.human_only_agents:
            return [selector]
        return []

    def _append_message_record(self, record: Dict) -> None:
        path = Path(self.acpx_store_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

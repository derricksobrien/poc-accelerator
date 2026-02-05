"""
Session Management for System3-RAG

Handles:
- Conversation session lifecycle
- POC generation history
- State persistence
- Session expiration and cleanup
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid


logger = logging.getLogger(__name__)


class POCStatus(str, Enum):
    """Status of a POC generation."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class POCGeneration:
    """Record of a POC generation request and result."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    query: str = ""
    solution_area: str = ""
    status: POCStatus = POCStatus.INITIATED
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class ConversationSession:
    """
    Represents a conversation session with agent.
    
    Tracks:
    - User identity
    - Conversation history
    - POC generation history
    - Session metadata
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    messages: List[Dict[str, str]] = field(default_factory=list)
    poc_generations: List[POCGeneration] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow().isoformat()
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.update_activity()
    
    def add_poc_generation(self, poc: POCGeneration) -> None:
        """Add a POC generation record."""
        self.poc_generations.append(poc)
        self.update_activity()
    
    def get_poc_generation(self, poc_id: str) -> Optional[POCGeneration]:
        """Get a POC generation by ID."""
        for poc in self.poc_generations:
            if poc.id == poc_id:
                return poc
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "message_count": len(self.messages),
            "poc_count": len(self.poc_generations),
            "metadata": self.metadata,
        }
    
    def to_detailed_dict(self) -> Dict[str, Any]:
        """Convert to detailed dictionary including all data."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "messages": self.messages,
            "poc_generations": [poc.to_dict() for poc in self.poc_generations],
            "metadata": self.metadata,
        }


class SessionManager:
    """
    Manages conversation sessions.
    
    Features:
    - Create/delete sessions
    - Track POC generations
    - Automatic cleanup
    - Thread-safe operations
    """
    
    def __init__(self, session_timeout_minutes: int = 60):
        """
        Initialize session manager.
        
        Args:
            session_timeout_minutes: Minutes of inactivity before session expires
        """
        self.sessions: Dict[str, ConversationSession] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        logger.info(f"SessionManager initialized with {session_timeout_minutes}min timeout")
    
    def create_session(
        self,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationSession:
        """
        Create a new conversation session.
        
        Args:
            user_id: Optional user identifier
            metadata: Optional metadata (solution area, preferences, etc.)
            
        Returns:
            New ConversationSession
        """
        session = ConversationSession(
            user_id=user_id,
            metadata=metadata or {},
        )
        self.sessions[session.session_id] = session
        logger.info(f"Created session {session.session_id} for user {user_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get an active session by ID."""
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session to delete
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session {session_id}")
            return True
        return False
    
    def validate_session(self, session_id: str) -> bool:
        """
        Validate that session exists and is not expired.
        
        Args:
            session_id: Session to validate
            
        Returns:
            True if valid, False if expired or not found
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        # Check expiration
        last_activity = datetime.fromisoformat(session.last_activity)
        if datetime.utcnow() - last_activity > self.session_timeout:
            logger.warning(f"Session expired: {session_id}")
            self.delete_session(session_id)
            return False
        
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.
        
        Returns:
            Number of sessions removed
        """
        expired = []
        now = datetime.utcnow()
        
        for session_id, session in self.sessions.items():
            last_activity = datetime.fromisoformat(session.last_activity)
            if now - last_activity > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            self.delete_session(session_id)
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
        
        return len(expired)
    
    def get_user_sessions(self, user_id: str) -> List[ConversationSession]:
        """Get all active sessions for a user."""
        return [
            s for s in self.sessions.values()
            if s.user_id == user_id
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get session manager statistics."""
        total_sessions = len(self.sessions)
        total_messages = sum(len(s.messages) for s in self.sessions.values())
        total_poc_gens = sum(
            len(s.poc_generations) for s in self.sessions.values()
        )
        
        # Count POCs by status
        poc_by_status = {}
        for session in self.sessions.values():
            for poc in session.poc_generations:
                status = poc.status.value
                poc_by_status[status] = poc_by_status.get(status, 0) + 1
        
        # Get unique users
        unique_users = len(set(s.user_id for s in self.sessions.values() if s.user_id))
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "total_poc_generations": total_poc_gens,
            "poc_by_status": poc_by_status,
            "unique_users": unique_users,
            "session_timeout_minutes": self.session_timeout.total_seconds() / 60,
        }
    
    def export_session(
        self,
        session_id: str,
        include_messages: bool = True,
        include_poc_details: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Export session data.
        
        Args:
            session_id: Session to export
            include_messages: Include conversation messages
            include_poc_details: Include POC generation details
            
        Returns:
            Session data as dictionary, or None if not found
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        data = session.to_dict()
        
        if include_messages:
            data["messages"] = session.messages
        
        if include_poc_details:
            data["poc_generations"] = [
                poc.to_dict() for poc in session.poc_generations
            ]
        
        return data
    
    def import_session(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Import previously exported session data.
        
        Args:
            data: Exported session dictionary
            
        Returns:
            Session ID, or None if import failed
        """
        try:
            # Create new session with imported data
            session = ConversationSession(
                session_id=data.get("session_id", str(uuid.uuid4())),
                user_id=data.get("user_id"),
                created_at=data.get("created_at", datetime.utcnow().isoformat()),
                last_activity=data.get("last_activity", datetime.utcnow().isoformat()),
                messages=data.get("messages", []),
                poc_generations=[
                    POCGeneration(**poc_data)
                    for poc_data in data.get("poc_generations", [])
                ],
                metadata=data.get("metadata", {}),
            )
            
            self.sessions[session.session_id] = session
            logger.info(f"Imported session {session.session_id}")
            return session.session_id
            
        except Exception as e:
            logger.error(f"Error importing session: {e}")
            return None


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(session_timeout_minutes: int = 60) -> SessionManager:
    """
    Get or create global session manager.
    
    Args:
        session_timeout_minutes: Timeout for sessions
        
    Returns:
        SessionManager instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(session_timeout_minutes)
    return _session_manager


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    manager = SessionManager(session_timeout_minutes=30)
    
    # Create a session
    session = manager.create_session(
        user_id="user@example.com",
        metadata={"solution_area": "AI", "level": "L400"}
    )
    
    # Add messages
    session.add_message("user", "What are the best practices for multi-agent systems?")
    session.add_message("assistant", "Multi-agent systems require careful orchestration...")
    
    # Add POC generation
    poc = POCGeneration(
        title="Enterprise AI Automation",
        query="multi-agent order processing",
        solution_area="AI",
        status=POCStatus.COMPLETED,
        result={
            "recommendations": ["Deploy on ACA", "Use Semantic Kernel"],
            "estimated_cost": "$5000/month",
        }
    )
    session.add_poc_generation(poc)
    
    # Export
    exported = manager.export_session(session.session_id)
    print(json.dumps(exported, indent=2))
    
    # Stats
    print(manager.get_statistics())

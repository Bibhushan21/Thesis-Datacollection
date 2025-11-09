from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from data.database_config import Base
from datetime import datetime
from typing import Dict, Any, Optional

class User(Base):
    """
    User authentication table.
    Stores user accounts for the Strategic Intelligence App.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    
    # Relationships
    analysis_sessions = relationship("AnalysisSession", back_populates="user", cascade="all, delete-orphan")
    analysis_templates = relationship("AnalysisTemplate", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("AgentRating", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization (excluding password)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count
        }

class AnalysisSession(Base):
    """
    Main analysis session table.
    Stores each strategic intelligence analysis request.
    """
    __tablename__ = 'analysis_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    strategic_question = Column(Text, nullable=False)
    time_frame = Column(String(50))
    region = Column(String(100))
    additional_instructions = Column(Text)
    architecture = Column(String(50))
    status = Column(String(50), default='processing')  # processing, completed, failed
    total_processing_time = Column(Float)  # in seconds
    total_token_usage = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="analysis_sessions")
    agent_results = relationship("AgentResult", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'strategic_question': self.strategic_question,
            'time_frame': self.time_frame,
            'region': self.region,
            'additional_instructions': self.additional_instructions,
            'architecture': self.architecture,
            'status': self.status,
            'total_processing_time': self.total_processing_time,
            'total_token_usage': self.total_token_usage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AgentResult(Base):
    """
    Individual agent results table.
    Stores the output from each agent in an analysis session.
    """
    __tablename__ = 'agent_results'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('analysis_sessions.id'), nullable=False)
    agent_name = Column(String(100), nullable=False)
    agent_type = Column(String(100))  # Type/category of agent
    raw_response = Column(Text)  # Raw LLM response
    formatted_output = Column(Text)  # Markdown formatted output
    structured_data = Column(JSON)  # Parsed structured data
    processing_time = Column(Float)  # Processing time in seconds
    token_usage = Column(Integer)
    status = Column(String(50), default='processing')  # processing, completed, failed, timeout
    error_message = Column(Text)  # Error details if failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    session = relationship("AnalysisSession", back_populates="agent_results")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'raw_response': self.raw_response,
            'formatted_output': self.formatted_output,
            'structured_data': self.structured_data,
            'processing_time': self.processing_time,
            'token_usage': self.token_usage,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AnalysisTemplate(Base):
    """
    Analysis templates table.
    Store commonly used analysis configurations for quick reuse.
    """
    __tablename__ = 'analysis_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable for system templates
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100), default='General')  # Template category
    strategic_question_template = Column(Text)
    default_time_frame = Column(String(50))
    default_region = Column(String(100))
    default_instructions = Column(Text)
    tags = Column(JSON)  # Array of tags for better categorization
    is_public = Column(Boolean, default=True)  # Whether template is publicly available
    created_by = Column(String(100), default='system')  # Who created the template
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analysis_templates")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'strategic_question_template': self.strategic_question_template,
            'default_time_frame': self.default_time_frame,
            'default_region': self.default_region,
            'default_instructions': self.default_instructions,
            'tags': self.tags,
            'is_public': self.is_public,
            'created_by': self.created_by,
            'usage_count': self.usage_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SystemLog(Base):
    """
    System logs table.
    Track system performance, errors, and usage statistics.
    """
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('analysis_sessions.id'), nullable=True)
    log_level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    component = Column(String(100))  # orchestrator, agent_name, database, etc.
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional structured details
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'log_level': self.log_level,
            'component': self.component,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AgentPerformance(Base):
    """
    Agent performance metrics table.
    Track performance statistics for each agent.
    """
    __tablename__ = 'agent_performance'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    timeout_executions = Column(Integer, default=0)
    average_processing_time = Column(Float)  # in seconds
    min_processing_time = Column(Float)
    max_processing_time = Column(Float)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'agent_name': self.agent_name,
            'date': self.date.isoformat() if self.date else None,
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'timeout_executions': self.timeout_executions,
            'average_processing_time': self.average_processing_time,
            'min_processing_time': self.min_processing_time,
            'max_processing_time': self.max_processing_time
        } 

class AgentRating(Base):
    """
    Agent ratings table.
    Store user ratings and reviews for agent outputs.
    """
    __tablename__ = 'agent_ratings'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('analysis_sessions.id'), nullable=False)
    agent_result_id = Column(Integer, ForeignKey('agent_results.id'), nullable=False)
    agent_name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5 star rating
    review_text = Column(Text)  # Optional text review
    helpful_aspects = Column(JSON)  # What was helpful (array of aspects)
    improvement_suggestions = Column(Text)  # What could be improved
    would_recommend = Column(Boolean, default=True)  # Would recommend this agent
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    session = relationship("AnalysisSession", backref="ratings")
    agent_result = relationship("AgentResult", backref="ratings")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'agent_result_id': self.agent_result_id,
            'agent_name': self.agent_name,
            'user_id': self.user_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'helpful_aspects': self.helpful_aspects,
            'improvement_suggestions': self.improvement_suggestions,
            'would_recommend': self.would_recommend,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AgentRatingSummary(Base):
    """
    Agent rating summary table.
    Store aggregated rating statistics for each agent.
    """
    __tablename__ = 'agent_rating_summaries'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False, unique=True)
    total_ratings = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    five_star_count = Column(Integer, default=0)
    four_star_count = Column(Integer, default=0)
    three_star_count = Column(Integer, default=0)
    two_star_count = Column(Integer, default=0)
    one_star_count = Column(Integer, default=0)
    total_reviews = Column(Integer, default=0)  # Count of ratings with review text
    recommendation_percentage = Column(Float, default=0.0)  # % who would recommend
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'agent_name': self.agent_name,
            'total_ratings': self.total_ratings,
            'average_rating': self.average_rating,
            'five_star_count': self.five_star_count,
            'four_star_count': self.four_star_count,
            'three_star_count': self.three_star_count,
            'two_star_count': self.two_star_count,
            'one_star_count': self.one_star_count,
            'total_reviews': self.total_reviews,
            'recommendation_percentage': self.recommendation_percentage,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'rating_distribution': {
                '5': self.five_star_count,
                '4': self.four_star_count,
                '3': self.three_star_count,
                '2': self.two_star_count,
                '1': self.one_star_count
            }
        } 
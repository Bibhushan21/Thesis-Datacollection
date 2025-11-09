from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_, case
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import json

from data.database_config import get_db_session, close_db_session, get_db_connection
from data.models import (
    AnalysisSession, AgentResult, AnalysisTemplate, 
    SystemLog, AgentPerformance, AgentRating, AgentRatingSummary
)

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service layer for database operations.
    Provides high-level CRUD operations for the Strategic Intelligence App.
    """
    
    @staticmethod
    def create_analysis_session(
        strategic_question: str,
        time_frame: Optional[str] = None,
        region: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        user_id: Optional[int] = None,
        architecture: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new analysis session.
        Returns the session ID if successful, None if failed.
        """
        session = get_db_session()
        try:
            analysis_session = AnalysisSession(
                strategic_question=strategic_question,
                time_frame=time_frame,
                region=region,
                additional_instructions=additional_instructions,
                user_id=user_id,
                architecture=architecture,
                status='processing'
            )
            session.add(analysis_session)
            session.commit()
            session.refresh(analysis_session)
            
            logger.info(f"Created analysis session {analysis_session.id}")
            return analysis_session.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create analysis session: {str(e)}")
            return None
        finally:
            close_db_session(session)
    
    @staticmethod
    def update_session_status(
        session_id: int, 
        status: str, 
        total_processing_time: Optional[float] = None,
        total_token_usage: Optional[int] = None
    ) -> bool:
        """
        Update analysis session status and completion time.
        """
        session = get_db_session()
        try:
            analysis_session = session.query(AnalysisSession).filter(
                AnalysisSession.id == session_id
            ).first()
            
            if not analysis_session:
                logger.warning(f"Analysis session {session_id} not found")
                return False
            
            analysis_session.status = status
            if status == 'completed':
                analysis_session.completed_at = datetime.utcnow()
            if total_processing_time:
                analysis_session.total_processing_time = total_processing_time
            if total_token_usage:
                analysis_session.total_token_usage = total_token_usage
            
            session.commit()
            logger.info(f"Updated session {session_id} status to {status}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update session status: {str(e)}")
            return False
        finally:
            close_db_session(session)
    
    @staticmethod
    def save_agent_result(
        session_id: int,
        agent_name: str,
        agent_type: str,
        raw_response: str,
        formatted_output: str,
        structured_data: Optional[Dict] = None,
        processing_time: Optional[float] = None,
        token_usage: Optional[int] = None,
        status: str = 'completed'
    ) -> Optional[int]:
        """
        Save an agent's result to the database.
        Returns the result ID if successful, None if failed.
        """
        session = get_db_session()
        try:
            agent_result = AgentResult(
                session_id=session_id,
                agent_name=agent_name,
                agent_type=agent_type,
                raw_response=raw_response,
                formatted_output=formatted_output,
                structured_data=structured_data,
                processing_time=processing_time,
                token_usage=token_usage,
                status=status,
                completed_at=datetime.utcnow()
            )
            session.add(agent_result)
            session.commit()
            session.refresh(agent_result)
            
            logger.info(f"Saved result for agent {agent_name} in session {session_id}")
            return agent_result.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save agent result: {str(e)}")
            return None
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_analysis_session(session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get analysis session with all agent results.
        """
        session = get_db_session()
        try:
            analysis_session = session.query(AnalysisSession).filter(
                AnalysisSession.id == session_id
            ).first()
            
            if not analysis_session:
                return None
            
            # Get all agent results for this session
            agent_results = session.query(AgentResult).filter(
                AgentResult.session_id == session_id
            ).order_by(AgentResult.created_at).all()
            
            result = analysis_session.to_dict()
            result['agent_results'] = [agent_result.to_dict() for agent_result in agent_results]
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get analysis session: {str(e)}")
            return None
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_agent_result_by_id(agent_result_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific agent result by its ID.
        """
        session = get_db_session()
        try:
            agent_result = session.query(AgentResult).filter(
                AgentResult.id == agent_result_id
            ).first()
            
            if not agent_result:
                return None
            
            return agent_result.to_dict()
            
        except Exception as e:
            logger.error(f"Failed to get agent result {agent_result_id}: {str(e)}")
            return None
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_recent_sessions(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent analysis sessions.
        """
        session = get_db_session()
        try:
            sessions = session.query(AnalysisSession).order_by(
                desc(AnalysisSession.created_at)
            ).limit(limit).all()
            
            return [s.to_dict() for s in sessions]
            
        except Exception as e:
            logger.error(f"Failed to get recent sessions: {str(e)}")
            return []
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_analysis_sessions(
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None,
        region_filter: Optional[str] = None,
        search_query: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get analysis sessions with comprehensive filtering for history page.
        """
        session = get_db_session()
        try:
            query = session.query(AnalysisSession)
            
            # Apply filters
            if status_filter:
                query = query.filter(AnalysisSession.status == status_filter)
            
            if region_filter:
                query = query.filter(AnalysisSession.region == region_filter)
            
            if search_query:
                search_term = f"%{search_query}%"
                query = query.filter(
                    or_(
                        AnalysisSession.strategic_question.ilike(search_term),
                        AnalysisSession.additional_instructions.ilike(search_term)
                    )
                )
            
            if date_from:
                try:
                    from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    query = query.filter(AnalysisSession.created_at >= from_date)
                except ValueError:
                    pass  # Invalid date format, ignore filter
            
            if date_to:
                try:
                    to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    query = query.filter(AnalysisSession.created_at <= to_date)
                except ValueError:
                    pass  # Invalid date format, ignore filter
            
            # Order by most recent first
            query = query.order_by(desc(AnalysisSession.created_at))
            
            # Apply pagination
            sessions = query.offset(offset).limit(limit).all()
            
            # Convert to dictionaries and add agent count
            result = []
            for session_obj in sessions:
                session_dict = session_obj.to_dict()
                
                # Add agent results count
                agent_count = session.query(AgentResult).filter(
                    AgentResult.session_id == session_obj.id
                ).count()
                session_dict['agent_results_count'] = agent_count
                
                # Add completion rate
                completed_agents = session.query(AgentResult).filter(
                    and_(
                        AgentResult.session_id == session_obj.id,
                        AgentResult.status == 'completed'
                    )
                ).count()
                session_dict['completion_rate'] = (completed_agents / agent_count * 100) if agent_count > 0 else 0
                
                result.append(session_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get analysis sessions: {str(e)}")
            return []
        finally:
            close_db_session(session)
    
    @staticmethod
    def search_sessions(
        search_term: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search analysis sessions with filters.
        """
        session = get_db_session()
        try:
            query = session.query(AnalysisSession)
            
            # Apply filters
            if search_term:
                query = query.filter(
                    or_(
                        AnalysisSession.strategic_question.ilike(f"%{search_term}%"),
                        AnalysisSession.additional_instructions.ilike(f"%{search_term}%")
                    )
                )
            
            if status:
                query = query.filter(AnalysisSession.status == status)
            
            if date_from:
                query = query.filter(AnalysisSession.created_at >= date_from)
            
            if date_to:
                query = query.filter(AnalysisSession.created_at <= date_to)
            
            sessions = query.order_by(
                desc(AnalysisSession.created_at)
            ).limit(limit).all()
            
            return [s.to_dict() for s in sessions]
            
        except Exception as e:
            logger.error(f"Failed to search sessions: {str(e)}")
            return []
        finally:
            close_db_session(session)
    
    @staticmethod
    def log_system_event(
        log_level: str,
        component: str,
        message: str,
        session_id: Optional[int] = None,
        details: Optional[Dict] = None
    ) -> bool:
        """
        Log a system event.
        """
        session = get_db_session()
        try:
            log_entry = SystemLog(
                session_id=session_id,
                log_level=log_level,
                component=component,
                message=message,
                details=details
            )
            session.add(log_entry)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log system event: {str(e)}")
            return False
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_agent_performance_stats(
        agent_name: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get agent performance statistics.
        """
        session = get_db_session()
        try:
            query = session.query(AgentResult)
            
            # Filter by date
            date_threshold = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(AgentResult.created_at >= date_threshold)
            
            if agent_name:
                query = query.filter(AgentResult.agent_name == agent_name)
            
            results = query.all()
            
            # Calculate statistics
            stats = {}
            for result in results:
                name = result.agent_name
                if name not in stats:
                    stats[name] = {
                        'agent_name': name,
                        'total_executions': 0,
                        'successful_executions': 0,
                        'failed_executions': 0,
                        'timeout_executions': 0,
                        'processing_times': []
                    }
                
                stats[name]['total_executions'] += 1
                if result.status == 'completed':
                    stats[name]['successful_executions'] += 1
                elif result.status == 'failed':
                    stats[name]['failed_executions'] += 1
                elif result.status == 'timeout':
                    stats[name]['timeout_executions'] += 1
                
                if result.processing_time:
                    stats[name]['processing_times'].append(result.processing_time)
            
            # Calculate averages
            for agent_stats in stats.values():
                times = agent_stats['processing_times']
                if times:
                    agent_stats['average_processing_time'] = sum(times) / len(times)
                    agent_stats['min_processing_time'] = min(times)
                    agent_stats['max_processing_time'] = max(times)
                else:
                    agent_stats['average_processing_time'] = None
                    agent_stats['min_processing_time'] = None
                    agent_stats['max_processing_time'] = None
                
                # Remove processing_times list from output
                del agent_stats['processing_times']
            
            return list(stats.values())
            
        except Exception as e:
            logger.error(f"Failed to get agent performance stats: {str(e)}")
            return []
        finally:
            close_db_session(session)
    
    @staticmethod
    def delete_old_sessions(days_old: int = 30) -> int:
        """
        Delete analysis sessions older than specified days.
        Returns number of deleted sessions.
        """
        session = get_db_session()
        try:
            date_threshold = datetime.utcnow() - timedelta(days=days_old)
            
            # Get sessions to delete
            old_sessions = session.query(AnalysisSession).filter(
                AnalysisSession.created_at < date_threshold
            ).all()
            
            count = len(old_sessions)
            
            # Delete sessions (cascades to agent_results)
            session.query(AnalysisSession).filter(
                AnalysisSession.created_at < date_threshold
            ).delete()
            
            session.commit()
            logger.info(f"Deleted {count} old analysis sessions")
            return count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete old sessions: {str(e)}")
            return 0
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_dashboard_stats(days_back: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive dashboard statistics for the specified time period.
        """
        session = get_db_session()
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Total sessions stats
            total_sessions = session.query(AnalysisSession).count()
            recent_sessions = session.query(AnalysisSession).filter(
                AnalysisSession.created_at >= start_date
            ).count()
            
            # Status breakdown
            status_stats = session.query(
                AnalysisSession.status,
                func.count(AnalysisSession.id).label('count')
            ).filter(
                AnalysisSession.created_at >= start_date
            ).group_by(AnalysisSession.status).all()
            
            status_breakdown = {status: count for status, count in status_stats}
            
            # Success rate calculation
            completed_sessions = status_breakdown.get('completed', 0)
            success_rate = (completed_sessions / recent_sessions * 100) if recent_sessions > 0 else 0
            
            # Region breakdown
            region_stats = session.query(
                AnalysisSession.region,
                func.count(AnalysisSession.id).label('count')
            ).filter(
                AnalysisSession.created_at >= start_date
            ).group_by(AnalysisSession.region).all()
            
            region_breakdown = {region or 'Unknown': count for region, count in region_stats}
            
            # Time frame breakdown
            timeframe_stats = session.query(
                AnalysisSession.time_frame,
                func.count(AnalysisSession.id).label('count')
            ).filter(
                AnalysisSession.created_at >= start_date
            ).group_by(AnalysisSession.time_frame).all()
            
            timeframe_breakdown = {timeframe or 'Unknown': count for timeframe, count in timeframe_stats}
            
            # Average processing time for completed sessions
            avg_processing_time = session.query(
                func.avg(AnalysisSession.total_processing_time)
            ).filter(
                and_(
                    AnalysisSession.created_at >= start_date,
                    AnalysisSession.status == 'completed',
                    AnalysisSession.total_processing_time.isnot(None)
                )
            ).scalar()
            
            # Daily activity (last 7 days)
            daily_activity = []
            for i in range(7):
                day_start = end_date - timedelta(days=i+1)
                day_end = end_date - timedelta(days=i)
                
                day_count = session.query(AnalysisSession).filter(
                    and_(
                        AnalysisSession.created_at >= day_start,
                        AnalysisSession.created_at < day_end
                    )
                ).count()
                
                daily_activity.append({
                    'date': day_start.strftime('%Y-%m-%d'),
                    'count': day_count
                })
            
            daily_activity.reverse()  # Show oldest to newest
            
            # Most active agents (by completion count)
            agent_activity = session.query(
                AgentResult.agent_name,
                func.count(AgentResult.id).label('total_runs'),
                func.avg(AgentResult.processing_time).label('avg_processing_time')
            ).filter(
                AgentResult.created_at >= start_date
            ).group_by(AgentResult.agent_name).order_by(
                desc('total_runs')
            ).limit(10).all()
            
            agent_stats = []
            for agent_name, total_runs, avg_time in agent_activity:
                # Get successful runs count separately
                successful_runs = session.query(func.count(AgentResult.id)).filter(
                    and_(
                        AgentResult.created_at >= start_date,
                        AgentResult.agent_name == agent_name,
                        AgentResult.status == 'completed'
                    )
                ).scalar()
                
                success_rate_agent = (successful_runs / total_runs * 100) if total_runs > 0 else 0
                agent_stats.append({
                    'agent_name': agent_name,
                    'total_runs': total_runs,
                    'successful_runs': successful_runs,
                    'success_rate': round(success_rate_agent, 1),
                    'avg_processing_time': round(float(avg_time or 0), 2)
                })
            
            # Recent sessions for quick access
            recent_session_list = session.query(AnalysisSession).filter(
                AnalysisSession.created_at >= start_date
            ).order_by(desc(AnalysisSession.created_at)).limit(5).all()
            
            recent_sessions_data = []
            for session_obj in recent_session_list:
                session_dict = session_obj.to_dict()
                # Add agent count
                agent_count = session.query(AgentResult).filter(
                    AgentResult.session_id == session_obj.id
                ).count()
                session_dict['agent_count'] = agent_count
                recent_sessions_data.append(session_dict)
            
            return {
                'overview': {
                    'total_sessions_all_time': total_sessions,
                    'recent_sessions': recent_sessions,
                    'success_rate': round(success_rate, 1),
                    'avg_processing_time': round(float(avg_processing_time or 0), 2),
                    'days_analyzed': days_back
                },
                'status_breakdown': status_breakdown,
                'region_breakdown': region_breakdown,
                'timeframe_breakdown': timeframe_breakdown,
                'daily_activity': daily_activity,
                'agent_performance': agent_stats,
                'recent_sessions': recent_sessions_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {str(e)}")
            return {
                'overview': {},
                'status_breakdown': {},
                'region_breakdown': {},
                'timeframe_breakdown': {},
                'daily_activity': [],
                'agent_performance': [],
                'recent_sessions': []
            }
        finally:
            close_db_session(session)

    @staticmethod
    def get_performance_analytics(days_back: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance analytics for the dashboard"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                # Daily performance trends with agent breakdown
                cursor.execute("""
                    SELECT 
                        DATE(ar.created_at) as analysis_date,
                        ar.agent_name,
                        COUNT(*) as total_runs,
                        COUNT(CASE WHEN ar.status = 'completed' THEN 1 END) as successful_runs,
                        AVG(CASE WHEN ar.processing_time IS NOT NULL THEN ar.processing_time END) as avg_processing_time,
                        AVG(CASE WHEN ar.status = 'completed' THEN 100.0 ELSE 0.0 END) as success_rate
                    FROM agent_results ar
                    WHERE ar.created_at >= %s
                    GROUP BY DATE(ar.created_at), ar.agent_name
                    ORDER BY analysis_date DESC
                """, (cutoff_date,))
                
                daily_data = cursor.fetchall()
                
                # Group by date
                performance_trends = {}
                for row in daily_data:
                    date_str = row[0].strftime('%Y-%m-%d')
                    if date_str not in performance_trends:
                        performance_trends[date_str] = {}
                    
                    performance_trends[date_str][row[1]] = {
                        'total_runs': row[2],
                        'successful_runs': row[3],
                        'avg_processing_time': float(row[4]) if row[4] else 0,
                        'success_rate': float(row[5]) if row[5] else 0
                    }
                
                # Convert to list format for frontend
                trends_list = []
                for i in range(days_back):
                    date = datetime.now() - timedelta(days=i)
                    date_str = date.strftime('%Y-%m-%d')
                    trends_list.append({
                        'date': date_str,
                        'agents': performance_trends.get(date_str, {})
                    })
                
                trends_list.reverse()  # Chronological order
                
                # Processing time analysis by agent
                cursor.execute("""
                    SELECT 
                        ar.agent_name,
                        MIN(ar.processing_time) as min_time,
                        MAX(ar.processing_time) as max_time,
                        AVG(ar.processing_time) as avg_time,
                        STDDEV(ar.processing_time) as time_variance,
                        COUNT(*) as total_runs
                    FROM agent_results ar
                    WHERE ar.created_at >= %s AND ar.processing_time IS NOT NULL
                    GROUP BY ar.agent_name
                    ORDER BY avg_time DESC
                """, (cutoff_date,))
                
                processing_analysis = []
                for row in cursor.fetchall():
                    processing_analysis.append({
                        'agent_name': row[0],
                        'min_time': float(row[1]) if row[1] else 0,
                        'max_time': float(row[2]) if row[2] else 0,
                        'avg_time': float(row[3]) if row[3] else 0,
                        'time_variance': float(row[4]) if row[4] else 0,
                        'total_runs': row[5]
                    })
                
                # System benchmarks
                cursor.execute("""
                    SELECT 
                        AVG(ar.processing_time) as avg_processing_time,
                        COUNT(*) as total_runs,
                        COUNT(CASE WHEN ar.status = 'completed' THEN 1 END) as successful_runs
                    FROM agent_results ar
                    WHERE ar.created_at >= %s AND ar.processing_time IS NOT NULL
                """, (cutoff_date,))
                
                benchmark_row = cursor.fetchone()
                system_benchmarks = {
                    'avg_processing_time': float(benchmark_row[0]) if benchmark_row[0] else 0,
                    'total_runs': benchmark_row[1],
                    'successful_runs': benchmark_row[2],
                    'success_rate': (benchmark_row[2] / benchmark_row[1] * 100) if benchmark_row[1] > 0 else 0
                }
                
                # Agent comparisons with performance scoring
                agent_comparisons = []
                system_avg = system_benchmarks['avg_processing_time']
                
                for agent in processing_analysis:
                    # Performance scoring algorithm (0-100)
                    time_score = max(0, 100 - (agent['avg_time'] / max(system_avg, 1) - 1) * 50)
                    reliability_score = (agent['total_runs'] - (agent['total_runs'] - len([a for a in daily_data if a[1] == agent['agent_name'] and a[3] > 0]))) / max(agent['total_runs'], 1) * 100
                    consistency_score = max(0, 100 - (agent['time_variance'] / max(agent['avg_time'], 1)) * 100)
                    
                    performance_score = (time_score * 0.4 + reliability_score * 0.4 + consistency_score * 0.2)
                    
                    agent_comparisons.append({
                        'agent_name': agent['agent_name'],
                        'performance_score': min(100, max(0, performance_score)),
                        'system_avg_ratio': agent['avg_time'] / max(system_avg, 1),
                        'total_runs': agent['total_runs']
                    })
                
                # Error breakdown by agent
                cursor.execute("""
                    SELECT 
                        ar.agent_name,
                        ar.status,
                        COUNT(*) as count
                    FROM agent_results ar
                    WHERE ar.created_at >= %s
                    GROUP BY ar.agent_name, ar.status
                """, (cutoff_date,))
                
                error_data = cursor.fetchall()
                error_breakdown = {}
                for row in error_data:
                    if row[0] not in error_breakdown:
                        error_breakdown[row[0]] = {}
                    error_breakdown[row[0]][row[1]] = row[2]
                
                # Generate intelligent recommendations
                recommendations = []
                
                # Performance recommendations
                for agent in agent_comparisons:
                    if agent['performance_score'] < 70:
                        recommendations.append({
                            'agent': agent['agent_name'],
                            'type': 'performance',
                            'priority': 'high' if agent['performance_score'] < 50 else 'medium',
                            'message': f"Performance score {agent['performance_score']:.1f}/100. Consider optimization."
                        })
                    
                    if agent['system_avg_ratio'] > 1.5:
                        recommendations.append({
                            'agent': agent['agent_name'],
                            'type': 'optimization',
                            'priority': 'medium',
                            'message': f"Processing time {agent['system_avg_ratio']:.1f}x system average. Optimize for speed."
                        })
                
                # Reliability recommendations
                for agent_name, statuses in error_breakdown.items():
                    total = sum(statuses.values())
                    failed = statuses.get('failed', 0)
                    if total > 0 and (failed / total) > 0.1:
                        recommendations.append({
                            'agent': agent_name,
                            'type': 'reliability',
                            'priority': 'high' if (failed / total) > 0.2 else 'medium',
                            'message': f"High failure rate ({failed/total*100:.1f}%). Investigate error patterns."
                        })
                
                return {
                    'performance_trends': trends_list,
                    'processing_analysis': processing_analysis,
                    'system_benchmarks': system_benchmarks,
                    'agent_comparisons': agent_comparisons,
                    'error_breakdown': error_breakdown,
                    'recommendations': recommendations[:10]  # Limit to top 10
                }
                
        except Exception as e:
            print(f"Error getting performance analytics: {e}")
            return {
                'performance_trends': [],
                'processing_analysis': [],
                'system_benchmarks': {},
                'agent_comparisons': [],
                'error_breakdown': {},
                'recommendations': []
            }

    # Template Management Methods
    @staticmethod
    def create_template(
        name: str,
        description: str,
        category: str,
        strategic_question: str,
        default_time_frame: Optional[str] = None,
        default_region: Optional[str] = None,
        additional_instructions: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_public: bool = True,
        created_by: str = 'system'
    ) -> Optional[int]:
        """Create a new analysis template"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Create templates table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_templates (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        category VARCHAR(100) NOT NULL,
                        strategic_question TEXT NOT NULL,
                        default_time_frame VARCHAR(100),
                        default_region VARCHAR(100),
                        additional_instructions TEXT,
                        tags TEXT,
                        is_public BOOLEAN DEFAULT true,
                        created_by VARCHAR(100) DEFAULT 'system',
                        usage_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert the template
                cursor.execute("""
                    INSERT INTO analysis_templates 
                    (name, description, category, strategic_question, default_time_frame, 
                     default_region, additional_instructions, tags, is_public, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    name, description, category, strategic_question,
                    default_time_frame, default_region, additional_instructions,
                    ','.join(tags) if tags else None,
                    is_public, created_by
                ))
                
                template_id = cursor.fetchone()[0]
                conn.commit()
                return template_id
                
        except Exception as e:
            print(f"Error creating template: {e}")
            return None

    @staticmethod
    def get_templates(
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get analysis templates with filtering"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Build query with filters
                query = """
                    SELECT id, name, description, category, strategic_question,
                           default_time_frame, default_region, additional_instructions,
                           tags, usage_count, created_by, created_at
                    FROM analysis_templates 
                    WHERE is_public = true
                """
                params = []
                
                if category:
                    query += " AND category = %s"
                    params.append(category)
                
                if search_query:
                    query += " AND (name ILIKE %s OR description ILIKE %s OR strategic_question ILIKE %s)"
                    search_param = f"%{search_query}%"
                    params.extend([search_param, search_param, search_param])
                
                query += " ORDER BY usage_count DESC, created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                templates = []
                for row in cursor.fetchall():
                    templates.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'category': row[3],
                        'strategic_question': row[4],
                        'default_time_frame': row[5],
                        'default_region': row[6],
                        'additional_instructions': row[7],
                        'tags': row[8].split(',') if row[8] else [],
                        'usage_count': row[9],
                        'created_by': row[10],
                        'created_at': row[11].isoformat()
                    })
                
                return templates
                
        except Exception as e:
            print(f"Error getting templates: {e}")
            return []

    @staticmethod
    def get_template_by_id(template_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, description, category, strategic_question,
                           default_time_frame, default_region, additional_instructions,
                           tags, usage_count, created_by, created_at
                    FROM analysis_templates 
                    WHERE id = %s AND is_public = true
                """, (template_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'category': row[3],
                    'strategic_question': row[4],
                    'default_time_frame': row[5],
                    'default_region': row[6],
                    'additional_instructions': row[7],
                    'tags': row[8].split(',') if row[8] else [],
                    'usage_count': row[9],
                    'created_by': row[10],
                    'created_at': row[11].isoformat()
                }
                
        except Exception as e:
            print(f"Error getting template: {e}")
            return None

    @staticmethod
    def increment_template_usage(template_id: int) -> bool:
        """Increment usage count when template is used"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE analysis_templates 
                    SET usage_count = usage_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (template_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error incrementing template usage: {e}")
            return False

    @staticmethod
    def get_template_categories() -> List[Dict[str, Any]]:
        """Get all template categories with counts"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT category, COUNT(*) as count
                    FROM analysis_templates 
                    WHERE is_public = true
                    GROUP BY category
                    ORDER BY count DESC, category
                """)
                
                categories = []
                for row in cursor.fetchall():
                    categories.append({
                        'name': row[0],
                        'count': row[1]
                    })
                
                return categories
                
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    @staticmethod
    def populate_default_templates():
        """Populate the database with default strategic analysis templates"""
        try:
            # Check if templates already exist
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM analysis_templates")
                if cursor.fetchone()[0] > 0:
                    return  # Templates already exist
            
            # Default templates to create
            default_templates = [
                {
                    'name': 'Market Entry Analysis',
                    'description': 'Comprehensive analysis for entering new markets, including competitive landscape, regulatory environment, and market size assessment.',
                    'category': 'Market Analysis',
                    'strategic_question': 'What are the opportunities, challenges, and strategic considerations for entering [market/region]? Analyze market size, competitive landscape, regulatory requirements, cultural factors, and entry strategies.',
                    'default_time_frame': 'Next 12-18 months',
                    'default_region': 'Global',
                    'additional_instructions': 'Focus on actionable insights, quantifiable market opportunities, competitive positioning, and risk mitigation strategies.',
                    'tags': ['market-entry', 'competitive-analysis', 'market-sizing', 'strategic-planning']
                },
                {
                    'name': 'Competitive Intelligence Assessment',
                    'description': 'Deep-dive analysis of key competitors, their strategies, strengths, weaknesses, and market positioning.',
                    'category': 'Competitive Intelligence',
                    'strategic_question': 'Who are our main competitors in [industry/market] and what are their strategic moves, competitive advantages, market positioning, and potential vulnerabilities?',
                    'default_time_frame': 'Current and next 6 months',
                    'default_region': 'North America',
                    'additional_instructions': 'Include competitor SWOT analysis, recent strategic moves, market share data, and emerging competitive threats.',
                    'tags': ['competitive-intelligence', 'competitor-analysis', 'market-positioning', 'strategic-threats']
                },
                {
                    'name': 'Technology Impact Assessment',
                    'description': 'Analysis of how emerging technologies will impact industry, business models, and strategic positioning.',
                    'category': 'Technology Assessment',
                    'strategic_question': 'How will [emerging technology] impact our industry, business model, and competitive landscape? What are the strategic implications and adaptation requirements?',
                    'default_time_frame': 'Next 2-5 years',
                    'default_region': 'Global',
                    'additional_instructions': 'Focus on technology adoption curves, industry disruption potential, investment requirements, and strategic responses.',
                    'tags': ['technology-assessment', 'digital-transformation', 'innovation', 'disruption-analysis']
                },
                {
                    'name': 'Risk Assessment Framework',
                    'description': 'Comprehensive risk analysis covering operational, strategic, regulatory, and market risks.',
                    'category': 'Risk Assessment',
                    'strategic_question': 'What are the key risks facing our organization in [specific area/timeframe] and what mitigation strategies should we implement?',
                    'default_time_frame': 'Next 12 months',
                    'default_region': 'Regional',
                    'additional_instructions': 'Categorize risks by impact and probability, provide mitigation strategies, and identify risk interdependencies.',
                    'tags': ['risk-assessment', 'risk-management', 'strategic-risks', 'operational-risks']
                },
                {
                    'name': 'SWOT Strategic Analysis',
                    'description': 'Structured analysis of Strengths, Weaknesses, Opportunities, and Threats for strategic planning.',
                    'category': 'Strategic Planning',
                    'strategic_question': 'What are our organization\'s key strengths, weaknesses, opportunities, and threats in [context], and how should these inform our strategic direction?',
                    'default_time_frame': 'Current state and next 12 months',
                    'default_region': 'Organizational scope',
                    'additional_instructions': 'Provide specific, actionable insights for each SWOT category and identify strategic priorities based on the analysis.',
                    'tags': ['swot-analysis', 'strategic-planning', 'organizational-assessment', 'strategic-priorities']
                },
                {
                    'name': 'Scenario Planning Exercise',
                    'description': 'Multi-scenario analysis to prepare for different future outcomes and strategic contingencies.',
                    'category': 'Strategic Planning',
                    'strategic_question': 'What are the most likely future scenarios for [industry/market/situation] and how should we prepare strategically for each outcome?',
                    'default_time_frame': 'Next 2-5 years',
                    'default_region': 'Global',
                    'additional_instructions': 'Develop 3-4 distinct scenarios with probability assessments and strategic response plans for each.',
                    'tags': ['scenario-planning', 'future-strategy', 'contingency-planning', 'strategic-flexibility']
                },
                {
                    'name': 'Geopolitical Risk Analysis',
                    'description': 'Assessment of political, economic, and social risks in specific regions or globally.',
                    'category': 'Geopolitical Analysis',
                    'strategic_question': 'What are the current and emerging geopolitical risks in [region/globally] that could impact our business operations and strategic objectives?',
                    'default_time_frame': 'Next 6-18 months',
                    'default_region': 'Specified region',
                    'additional_instructions': 'Include political stability analysis, regulatory changes, economic factors, and social trends.',
                    'tags': ['geopolitical-risk', 'political-analysis', 'regulatory-environment', 'regional-analysis']
                },
                {
                    'name': 'Market Sizing & Opportunity',
                    'description': 'Quantitative analysis of market size, growth potential, and revenue opportunities.',
                    'category': 'Market Analysis',
                    'strategic_question': 'What is the total addressable market (TAM), serviceable addressable market (SAM), and serviceable obtainable market (SOM) for [product/service] in [target market]?',
                    'default_time_frame': 'Current and next 3 years',
                    'default_region': 'Target market region',
                    'additional_instructions': 'Provide quantitative market sizing with supporting data, growth projections, and market segment analysis.',
                    'tags': ['market-sizing', 'market-opportunity', 'revenue-analysis', 'growth-potential']
                }
            ]
            
            # Create all default templates
            for template in default_templates:
                DatabaseService.create_template(**template)
            
            print(f"Created {len(default_templates)} default templates")
            
        except Exception as e:
            print(f"Error populating default templates: {e}")

    @staticmethod
    def get_analysis_sessions_count(
        status_filter: Optional[str] = None,
        region_filter: Optional[str] = None,
        search_query: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> int:
        """
        Get total count of analysis sessions with filtering (for pagination).
        """
        session = get_db_session()
        try:
            query = session.query(AnalysisSession)
            
            # Apply the same filters as get_analysis_sessions
            if status_filter:
                query = query.filter(AnalysisSession.status == status_filter)
            
            if region_filter:
                query = query.filter(AnalysisSession.region == region_filter)
            
            if search_query:
                search_term = f"%{search_query}%"
                query = query.filter(
                    or_(
                        AnalysisSession.strategic_question.ilike(search_term),
                        AnalysisSession.additional_instructions.ilike(search_term)
                    )
                )
            
            if date_from:
                try:
                    from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    query = query.filter(AnalysisSession.created_at >= from_date)
                except ValueError:
                    pass  # Invalid date format, ignore filter
            
            if date_to:
                try:
                    to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    query = query.filter(AnalysisSession.created_at <= to_date)
                except ValueError:
                    pass  # Invalid date format, ignore filter
            
            return query.count()
            
        except Exception as e:
            logger.error(f"Failed to get analysis sessions count: {str(e)}")
            return 0
        finally:
            close_db_session(session)

    # User History & Pattern Analytics
    @staticmethod
    def track_user_query_pattern(
        strategic_question: str,
        time_frame: str,
        region: str,
        additional_instructions: Optional[str] = None,
        user_id: Optional[str] = 'anonymous'
    ) -> bool:
        """Track user query patterns for template generation"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Create user query patterns table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_query_patterns (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(100) DEFAULT 'anonymous',
                        strategic_question TEXT NOT NULL,
                        time_frame VARCHAR(100),
                        region VARCHAR(100),
                        additional_instructions TEXT,
                        question_keywords TEXT,
                        extracted_domain VARCHAR(200),
                        extracted_intent VARCHAR(200),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Extract keywords and domain from strategic question
                keywords = DatabaseService._extract_keywords(strategic_question)
                domain = DatabaseService._extract_domain(strategic_question)
                intent = DatabaseService._extract_intent(strategic_question)
                
                # Insert pattern record
                cursor.execute("""
                    INSERT INTO user_query_patterns 
                    (user_id, strategic_question, time_frame, region, additional_instructions,
                     question_keywords, extracted_domain, extracted_intent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, strategic_question, time_frame, region, 
                    additional_instructions, keywords, domain, intent
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error tracking user query pattern: {e}")
            return False

    @staticmethod
    def get_popular_query_patterns(limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular query patterns for template generation"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        extracted_domain,
                        extracted_intent,
                        time_frame,
                        region,
                        COUNT(*) as frequency,
                        STRING_AGG(DISTINCT question_keywords, ', ') as common_keywords,
                        AVG(LENGTH(strategic_question)) as avg_question_length
                    FROM user_query_patterns
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY extracted_domain, extracted_intent, time_frame, region
                    HAVING COUNT(*) >= 2
                    ORDER BY frequency DESC
                    LIMIT %s
                """, (limit,))
                
                patterns = []
                for row in cursor.fetchall():
                    patterns.append({
                        'domain': row[0],
                        'intent': row[1],
                        'time_frame': row[2],
                        'region': row[3],
                        'frequency': row[4],
                        'keywords': row[5],
                        'avg_question_length': row[6]
                    })
                
                return patterns
                
        except Exception as e:
            print(f"Error getting popular query patterns: {e}")
            return []

    @staticmethod
    def save_analysis_as_template(
        session_id: int,
        template_name: str,
        template_description: str,
        category: str,
        user_id: str = 'anonymous'
    ) -> Optional[int]:
        """Save a completed analysis as a reusable template"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get the original analysis session
                cursor.execute("""
                    SELECT strategic_question, time_frame, region, additional_instructions
                    FROM analysis_sessions
                    WHERE id = %s
                """, (session_id,))
                
                session_data = cursor.fetchone()
                if not session_data:
                    return None
                
                strategic_question, time_frame, region, additional_instructions = session_data
                
                # Generate tags from the strategic question
                tags = DatabaseService._generate_tags_from_question(strategic_question)
                
                # Create the template
                template_id = DatabaseService.create_template(
                    name=template_name,
                    description=template_description,
                    category=category,
                    strategic_question=strategic_question,
                    default_time_frame=time_frame,
                    default_region=region,
                    additional_instructions=additional_instructions,
                    tags=tags,
                    is_public=True,
                    created_by=user_id
                )
                
                # Track this as a user-generated template
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_generated_templates (
                        id SERIAL PRIMARY KEY,
                        template_id INTEGER REFERENCES analysis_templates(id),
                        source_session_id INTEGER REFERENCES analysis_sessions(id),
                        user_id VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO user_generated_templates (template_id, source_session_id, user_id)
                    VALUES (%s, %s, %s)
                """, (template_id, session_id, user_id))
                
                conn.commit()
                return template_id
                
        except Exception as e:
            print(f"Error saving analysis as template: {e}")
            return None

    @staticmethod
    def generate_ai_template_suggestions(
        user_id: str = 'anonymous',
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered template suggestions based on user history"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get user's historical patterns
                cursor.execute("""
                    SELECT 
                        strategic_question,
                        time_frame,
                        region,
                        additional_instructions,
                        question_keywords,
                        extracted_domain,
                        extracted_intent
                    FROM user_query_patterns
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 20
                """, (user_id,))
                
                user_patterns = cursor.fetchall()
                
                if not user_patterns:
                    # Return popular patterns if no user history
                    return DatabaseService._get_trending_template_suggestions(limit)
                
                # Analyze patterns to generate suggestions
                suggestions = DatabaseService._analyze_patterns_for_suggestions(user_patterns, limit)
                
                return suggestions
                
        except Exception as e:
            print(f"Error generating AI template suggestions: {e}")
            return []

    @staticmethod
    def get_template_recommendations_for_user(
        strategic_question: str,
        user_id: str = 'anonymous'
    ) -> List[Dict[str, Any]]:
        """Get template recommendations based on current question and user history"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Extract features from current question
                keywords = DatabaseService._extract_keywords(strategic_question)
                domain = DatabaseService._extract_domain(strategic_question)
                intent = DatabaseService._extract_intent(strategic_question)
                
                # Find similar templates based on keywords and domain
                cursor.execute("""
                    SELECT 
                        t.id, t.name, t.description, t.category, t.strategic_question,
                        t.default_time_frame, t.default_region, t.additional_instructions,
                        t.tags, t.usage_count,
                        CASE 
                            WHEN t.tags ILIKE %s THEN 3
                            WHEN t.category ILIKE %s THEN 2
                            WHEN t.strategic_question ILIKE %s THEN 1
                            ELSE 0
                        END as relevance_score
                    FROM analysis_templates t
                    WHERE t.is_public = true
                    AND (
                        t.tags ILIKE %s OR
                        t.category ILIKE %s OR
                        t.strategic_question ILIKE %s
                    )
                    ORDER BY relevance_score DESC, usage_count DESC
                    LIMIT 5
                """, (
                    f"%{domain}%", f"%{domain}%", f"%{keywords}%",
                    f"%{domain}%", f"%{domain}%", f"%{keywords}%"
                ))
                
                recommendations = []
                for row in cursor.fetchall():
                    recommendations.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'category': row[3],
                        'strategic_question': row[4],
                        'default_time_frame': row[5],
                        'default_region': row[6],
                        'additional_instructions': row[7],
                        'tags': row[8].split(',') if row[8] else [],
                        'usage_count': row[9],
                        'relevance_score': row[10]
                    })
                
                return recommendations
                
        except Exception as e:
            print(f"Error getting template recommendations: {e}")
            return []

    # Helper methods for AI analysis
    @staticmethod
    def _extract_keywords(text: str) -> str:
        """Extract key terms from strategic question"""
        if not text:
            return ""
        
        # Simple keyword extraction (in production, use NLP libraries)
        import re
        
        # Remove common question words and extract meaningful terms
        stop_words = {'what', 'how', 'why', 'when', 'where', 'who', 'which', 'should', 'can', 'will', 'are', 'is', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        return ', '.join(keywords[:10])  # Top 10 keywords

    @staticmethod
    def _extract_domain(text: str) -> str:
        """Extract business domain from strategic question"""
        if not text:
            return "general"
        
        text_lower = text.lower()
        
        # Domain mapping based on keywords
        domain_keywords = {
            'market': ['market', 'customer', 'competitor', 'competition', 'segment'],
            'technology': ['technology', 'digital', 'ai', 'automation', 'innovation', 'tech'],
            'finance': ['financial', 'revenue', 'cost', 'investment', 'budget', 'roi'],
            'risk': ['risk', 'threat', 'vulnerability', 'security', 'compliance'],
            'strategy': ['strategy', 'strategic', 'planning', 'direction', 'vision'],
            'operations': ['operations', 'process', 'efficiency', 'productivity', 'supply'],
            'geopolitical': ['geopolitical', 'political', 'regulatory', 'government', 'policy']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain
        
        return 'general'

    @staticmethod
    def _extract_intent(text: str) -> str:
        """Extract analysis intent from strategic question"""
        if not text:
            return "analysis"
        
        text_lower = text.lower()
        
        # Intent mapping based on question patterns
        if any(word in text_lower for word in ['enter', 'entry', 'expansion', 'expand']):
            return 'market_entry'
        elif any(word in text_lower for word in ['competitor', 'competition', 'competitive']):
            return 'competitive_analysis'
        elif any(word in text_lower for word in ['risk', 'threat', 'vulnerability']):
            return 'risk_assessment'
        elif any(word in text_lower for word in ['opportunity', 'potential', 'growth']):
            return 'opportunity_analysis'
        elif any(word in text_lower for word in ['swot', 'strength', 'weakness']):
            return 'swot_analysis'
        elif any(word in text_lower for word in ['scenario', 'future', 'forecast']):
            return 'scenario_planning'
        else:
            return 'general_analysis'

    @staticmethod
    def _generate_tags_from_question(strategic_question: str) -> List[str]:
        """Generate relevant tags from strategic question"""
        keywords = DatabaseService._extract_keywords(strategic_question)
        domain = DatabaseService._extract_domain(strategic_question)
        intent = DatabaseService._extract_intent(strategic_question)
        
        tags = [domain, intent]
        
        # Add specific keywords as tags
        keyword_list = keywords.split(', ')[:5]  # Top 5 keywords
        tags.extend(keyword_list)
        
        return [tag for tag in tags if tag and len(tag) > 2]

    @staticmethod
    def _get_trending_template_suggestions(limit: int) -> List[Dict[str, Any]]:
        """Get trending template suggestions when no user history exists"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT name, category, 'Based on popular usage' as reason
                    FROM analysis_templates
                    WHERE is_public = true
                    ORDER BY usage_count DESC, created_at DESC
                    LIMIT %s
                """, (limit,))
                
                suggestions = []
                for row in cursor.fetchall():
                    suggestions.append({
                        'name': row[0],
                        'category': row[1],
                        'reason': row[2],
                        'confidence': 0.7
                    })
                
                return suggestions
                
        except Exception as e:
            print(f"Error getting trending suggestions: {e}")
            return []

    @staticmethod
    def _analyze_patterns_for_suggestions(patterns: List, limit: int) -> List[Dict[str, Any]]:
        """Analyze user patterns to generate intelligent suggestions"""
        domain_counts = {}
        intent_counts = {}
        
        for pattern in patterns:
            domain = pattern[5]  # extracted_domain
            intent = pattern[6]  # extracted_intent
            
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        # Generate suggestions based on patterns
        suggestions = []
        
        # Most common domain
        if domain_counts:
            top_domain = max(domain_counts, key=domain_counts.get)
            suggestions.append({
                'name': f'Advanced {top_domain.title()} Analysis',
                'category': top_domain.title(),
                'reason': f'Based on your frequent {top_domain} analyses',
                'confidence': 0.9
            })
        
        # Most common intent
        if intent_counts:
            top_intent = max(intent_counts, key=intent_counts.get)
            suggestions.append({
                'name': f'{top_intent.replace("_", " ").title()} Framework',
                'category': 'Personalized',
                'reason': f'Based on your {top_intent.replace("_", " ")} focus',
                'confidence': 0.8
            })
        
        # Trending combination
        if len(suggestions) < limit:
            suggestions.append({
                'name': 'Cross-Domain Strategic Assessment',
                'category': 'Advanced',
                'reason': 'Recommended for comprehensive analysis',
                'confidence': 0.6
            })
        
        return suggestions[:limit]

    @staticmethod
    def _generate_smart_question_template(domain: str, intent: str, keywords: str) -> str:
        """Generate a smart strategic question template based on patterns"""
        
        # Domain-specific question starters
        domain_starters = {
            'market': 'What are the key market opportunities and challenges for',
            'technology': 'How will emerging technologies impact',
            'finance': 'What are the financial implications and opportunities of',
            'risk': 'What are the primary risks and mitigation strategies for',
            'strategy': 'What strategic approach should we take for',
            'operations': 'How can we optimize operational efficiency in',
            'geopolitical': 'What are the geopolitical risks and considerations for',
            'general': 'What are the strategic considerations for'
        }
        
        # Intent-specific question patterns
        intent_patterns = {
            'market_entry': '[market entry/expansion] in [target market/region]? Analyze market size, competitive landscape, regulatory requirements, and entry strategies.',
            'competitive_analysis': '[competitive positioning] against key players in [industry/market]? Assess competitor strengths, weaknesses, and strategic moves.',
            'risk_assessment': '[risk management] in [specific area/context]? Identify key risks, assess impact probability, and recommend mitigation strategies.',
            'opportunity_analysis': '[opportunity identification and evaluation] in [market/sector]? Analyze growth potential, market dynamics, and strategic advantages.',
            'swot_analysis': '[organizational assessment] of our [business unit/company]? Analyze strengths, weaknesses, opportunities, and threats.',
            'scenario_planning': '[future scenario planning] for [industry/business] over [timeframe]? Develop multiple scenarios and strategic responses.',
            'general_analysis': '[strategic analysis] of [business situation/challenge]? Provide comprehensive insights and actionable recommendations.'
        }
        
        # Build the question
        starter = domain_starters.get(domain, domain_starters['general'])
        pattern = intent_patterns.get(intent, intent_patterns['general_analysis'])
        
        # Extract key terms from keywords for placeholders
        if keywords:
            key_terms = keywords.split(', ')[:3]  # Use top 3 keywords
            placeholder_context = f"[{'/'.join(key_terms)}]"
        else:
            placeholder_context = "[specific context]"
        
        # Combine and format
        question = f"{starter} {pattern}"
        
        # Replace generic placeholders with more specific ones based on keywords
        if keywords:
            if 'market' in keywords.lower():
                question = question.replace('[target market/region]', '[market/region]')
                question = question.replace('[market/sector]', '[market/sector]')
            if 'technology' in keywords.lower() or 'digital' in keywords.lower():
                question = question.replace('[specific area/context]', '[technology implementation/digital transformation]')
        
        return question 

    # ==========================================
    # AGENT RATING METHODS
    # ==========================================

    @staticmethod
    def submit_agent_rating(
        session_id: int,
        agent_result_id: int,
        agent_name: str,
        rating: int,
        review_text: Optional[str] = None,
        helpful_aspects: Optional[List[str]] = None,
        improvement_suggestions: Optional[str] = None,
        would_recommend: bool = True,
        user_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Submit a rating for an agent result.
        Returns the rating ID if successful, None if failed.
        """
        session = get_db_session()
        try:
            # Validate rating range
            if rating < 1 or rating > 5:
                logger.error(f"Invalid rating value: {rating}. Must be between 1 and 5.")
                return None

            existing_rating = None
            if user_id is not None:
                # Check if user has already rated this result
                existing_rating = session.query(AgentRating).filter(
                    and_(
                        AgentRating.agent_result_id == agent_result_id,
                        AgentRating.user_id == user_id
                    )
                ).first()

            if existing_rating:
                # Update existing rating
                existing_rating.rating = rating
                existing_rating.review_text = review_text
                existing_rating.helpful_aspects = helpful_aspects
                existing_rating.improvement_suggestions = improvement_suggestions
                existing_rating.would_recommend = would_recommend
                # updated_at will be set automatically by SQLAlchemy onupdate trigger
                
                session.commit()
                logger.info(f"Updated rating {existing_rating.id} for agent {agent_name}")
                
                # Update rating summary
                DatabaseService._update_rating_summary(agent_name, session)
                return existing_rating.id
            else:
                # Create new rating
                agent_rating = AgentRating(
                    session_id=session_id,
                    agent_result_id=agent_result_id,
                    agent_name=agent_name,
                    user_id=user_id,
                    rating=rating,
                    review_text=review_text,
                    helpful_aspects=helpful_aspects,
                    improvement_suggestions=improvement_suggestions,
                    would_recommend=would_recommend
                )
                session.add(agent_rating)
                session.commit()
                session.refresh(agent_rating)
                
                logger.info(f"Created new rating {agent_rating.id} for agent {agent_name}")
                
                # Update rating summary
                DatabaseService._update_rating_summary(agent_name, session)
                return agent_rating.id
                
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to submit agent rating: {str(e)}")
            return None
        finally:
            close_db_session(session)

    @staticmethod
    def get_agent_ratings(
        agent_name: Optional[str] = None,
        session_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get agent ratings with optional filtering.
        """
        session = get_db_session()
        try:
            query = session.query(AgentRating)
            
            if agent_name:
                query = query.filter(AgentRating.agent_name == agent_name)
            if session_id:
                query = query.filter(AgentRating.session_id == session_id)
            
            ratings = query.order_by(desc(AgentRating.created_at)).offset(offset).limit(limit).all()
            
            return [rating.to_dict() for rating in ratings]
            
        except Exception as e:
            logger.error(f"Failed to get agent ratings: {str(e)}")
            return []
        finally:
            close_db_session(session)

    @staticmethod
    def get_agent_rating_summary(agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get rating summary for a specific agent.
        """
        session = get_db_session()
        try:
            summary = session.query(AgentRatingSummary).filter(
                AgentRatingSummary.agent_name == agent_name
            ).first()
            
            if summary:
                return summary.to_dict()
            else:
                # Create default summary if doesn't exist
                DatabaseService._update_rating_summary(agent_name, session)
                return {
                    'agent_name': agent_name,
                    'total_ratings': 0,
                    'average_rating': 0.0,
                    'rating_distribution': {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0},
                    'total_reviews': 0,
                    'recommendation_percentage': 0.0
                }
                
        except Exception as e:
            logger.error(f"Failed to get agent rating summary: {str(e)}")
            return None
        finally:
            close_db_session(session)

    @staticmethod
    def get_all_agent_rating_summaries() -> List[Dict[str, Any]]:
        """
        Get rating summaries for all agents.
        """
        session = get_db_session()
        try:
            summaries = session.query(AgentRatingSummary).order_by(
                desc(AgentRatingSummary.average_rating)
            ).all()
            
            return [summary.to_dict() for summary in summaries]
            
        except Exception as e:
            logger.error(f"Failed to get all agent rating summaries: {str(e)}")
            return []
        finally:
            close_db_session(session)

    @staticmethod
    def get_user_rating_for_result(agent_result_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get user's existing rating for a specific agent result.
        """
        if user_id is None:
            return None # Cannot get a rating if user is not specified

        session = get_db_session()
        try:
            rating = session.query(AgentRating).filter(
                and_(
                    AgentRating.agent_result_id == agent_result_id,
                    AgentRating.user_id == user_id
                )
            ).first()
            
            return rating.to_dict() if rating else None
            
        except Exception as e:
            logger.error(f"Failed to get user rating: {str(e)}")
            return None
        finally:
            close_db_session(session)

    @staticmethod
    def get_top_rated_agents(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top-rated agents based on average rating and number of ratings.
        """
        session = get_db_session()
        try:
            summaries = session.query(AgentRatingSummary).filter(
                AgentRatingSummary.total_ratings >= 5  # Minimum ratings for reliability
            ).order_by(
                desc(AgentRatingSummary.average_rating),
                desc(AgentRatingSummary.total_ratings)
            ).limit(limit).all()
            
            return [summary.to_dict() for summary in summaries]
            
        except Exception as e:
            logger.error(f"Failed to get top rated agents: {str(e)}")
            return []
        finally:
            close_db_session(session)

    @staticmethod
    def _update_rating_summary(agent_name: str, db_session: Session) -> bool:
        """
        Recalculate and update the rating summary for an agent.
        This should be called within an existing session.
        """
        try:
            # Aggregate rating data
            result = db_session.query(
                func.count(AgentRating.id).label('total_ratings'),
                func.avg(AgentRating.rating).label('average_rating'),
                func.count(AgentRating.review_text).label('total_reviews'),
                func.sum(case((AgentRating.would_recommend == True, 1), else_=0)).label('total_recommendations')
            ).filter(AgentRating.agent_name == agent_name).one()

            # Rating distribution
            distribution_result = db_session.query(
                AgentRating.rating, func.count(AgentRating.id)
            ).filter(
                AgentRating.agent_name == agent_name
            ).group_by(AgentRating.rating).all()

            distribution = {str(i): 0 for i in range(1, 6)}
            for rating, count in distribution_result:
                distribution[str(rating)] = count

            # Find or create summary
            summary = db_session.query(AgentRatingSummary).filter(
                AgentRatingSummary.agent_name == agent_name
            ).first()

            if not summary:
                summary = AgentRatingSummary(agent_name=agent_name)
                db_session.add(summary)

            # Update summary fields
            summary.total_ratings = result.total_ratings
            summary.average_rating = float(result.average_rating) if result.average_rating else 0.0
            summary.total_reviews = result.total_reviews
            summary.rating_distribution = distribution
            
            if result.total_ratings > 0:
                summary.recommendation_percentage = (result.total_recommendations / summary.total_ratings) * 100
            else:
                summary.recommendation_percentage = 0.0
            
            # The calling function will commit
            logger.info(f"Updated rating summary for {agent_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to update rating summary for {agent_name}: {str(e)}")
            # The calling function should handle rollback
            raise e

    @staticmethod
    def get_rating_analytics(days_back: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive rating analytics for the past N days.
        """
        session = get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get total ratings count
            total_ratings = session.query(AgentRating).filter(
                AgentRating.created_at >= cutoff_date
            ).count()
            
            # Get average rating across all agents
            avg_rating = session.query(func.avg(AgentRating.rating)).filter(
                AgentRating.created_at >= cutoff_date
            ).scalar() or 0
            
            # Get ratings distribution
            ratings_distribution = session.query(
                AgentRating.rating,
                func.count(AgentRating.id).label('count')
            ).filter(
                AgentRating.created_at >= cutoff_date
            ).group_by(AgentRating.rating).all()
            
            distribution = {f"{rating}_star": count for rating, count in ratings_distribution}
            
            # Get agent performance comparison
            agent_performance = session.query(
                AgentRating.agent_name,
                func.avg(AgentRating.rating).label('avg_rating'),
                func.count(AgentRating.id).label('total_ratings')
            ).filter(
                AgentRating.created_at >= cutoff_date
            ).group_by(AgentRating.agent_name).all()
            
            agent_stats = [
                {
                    'agent_name': agent_name,
                    'average_rating': float(avg_rating) if avg_rating else 0,
                    'total_ratings': total_ratings
                }
                for agent_name, avg_rating, total_ratings in agent_performance
            ]
            
            # Get recent feedback trends
            daily_ratings = session.query(
                func.date(AgentRating.created_at).label('date'),
                func.avg(AgentRating.rating).label('avg_rating'),
                func.count(AgentRating.id).label('count')
            ).filter(
                AgentRating.created_at >= cutoff_date
            ).group_by(func.date(AgentRating.created_at)).order_by('date').all()
            
            trends = [
                {
                    'date': str(date),
                    'average_rating': float(avg_rating) if avg_rating else 0,
                    'rating_count': count
                }
                for date, avg_rating, count in daily_ratings
            ]
            
            return {
                'total_ratings': total_ratings,
                'average_rating': round(float(avg_rating), 2) if avg_rating else 0,
                'ratings_distribution': distribution,
                'agent_performance': agent_stats,
                'daily_trends': trends,
                'period_days': days_back
            }
            
        except Exception as e:
            logger.error(f"Failed to get rating analytics: {str(e)}")
            return {
                'total_ratings': 0,
                'average_rating': 0,
                'ratings_distribution': {},
                'agent_performance': [],
                'daily_trends': [],
                'period_days': days_back
            }
        finally:
            close_db_session(session)

    # USER-SPECIFIC METHODS FOR DATA ISOLATION
    
    @staticmethod
    def get_analysis_sessions_for_user(
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None,
        region_filter: Optional[str] = None,
        search_query: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get analysis sessions for a specific user with filtering and pagination.
        """
        session = get_db_session()
        try:
            query = session.query(AnalysisSession).filter(
                AnalysisSession.user_id == user_id
            )
            
            # Apply filters
            if status_filter:
                query = query.filter(AnalysisSession.status == status_filter)
            
            if region_filter:
                query = query.filter(AnalysisSession.region == region_filter)
            
            if search_query:
                query = query.filter(
                    or_(
                        AnalysisSession.strategic_question.ilike(f'%{search_query}%'),
                        AnalysisSession.additional_instructions.ilike(f'%{search_query}%')
                    )
                )
            
            if date_from:
                try:
                    from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    query = query.filter(AnalysisSession.created_at >= from_date)
                except:
                    pass
            
            if date_to:
                try:
                    to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    query = query.filter(AnalysisSession.created_at <= to_date)
                except:
                    pass
            
            # Apply pagination and ordering
            sessions = query.order_by(desc(AnalysisSession.created_at)).offset(offset).limit(limit).all()
            
            return [session.to_dict() for session in sessions]
            
        except Exception as e:
            logger.error(f"Failed to get user analysis sessions: {str(e)}")
            return []
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_analysis_sessions_count_for_user(
        user_id: int,
        status_filter: Optional[str] = None,
        region_filter: Optional[str] = None,
        search_query: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> int:
        """
        Get total count of analysis sessions for a specific user with filtering.
        """
        session = get_db_session()
        try:
            query = session.query(AnalysisSession).filter(
                AnalysisSession.user_id == user_id
            )
            
            # Apply same filters as get_analysis_sessions_for_user
            if status_filter:
                query = query.filter(AnalysisSession.status == status_filter)
            
            if region_filter:
                query = query.filter(AnalysisSession.region == region_filter)
            
            if search_query:
                query = query.filter(
                    or_(
                        AnalysisSession.strategic_question.ilike(f'%{search_query}%'),
                        AnalysisSession.additional_instructions.ilike(f'%{search_query}%')
                    )
                )
            
            if date_from:
                try:
                    from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    query = query.filter(AnalysisSession.created_at >= from_date)
                except:
                    pass
            
            if date_to:
                try:
                    to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    query = query.filter(AnalysisSession.created_at <= to_date)
                except:
                    pass
            
            return query.count()
            
        except Exception as e:
            logger.error(f"Failed to get user sessions count: {str(e)}")
            return 0
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_dashboard_stats_for_user(user_id: int, days_back: int = 30) -> Dict[str, Any]:
        """
        Get dashboard statistics for a specific user.
        """
        session = get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Total sessions for this user
            total_sessions = session.query(AnalysisSession).filter(
                and_(
                    AnalysisSession.user_id == user_id,
                    AnalysisSession.created_at >= cutoff_date
                )
            ).count()
            
            # Completed sessions for this user
            completed_sessions = session.query(AnalysisSession).filter(
                and_(
                    AnalysisSession.user_id == user_id,
                    AnalysisSession.status == 'completed',
                    AnalysisSession.created_at >= cutoff_date
                )
            ).count()
            
            # Failed sessions for this user
            failed_sessions = session.query(AnalysisSession).filter(
                and_(
                    AnalysisSession.user_id == user_id,
                    AnalysisSession.status == 'failed',
                    AnalysisSession.created_at >= cutoff_date
                )
            ).count()
            
            # Processing sessions for this user
            processing_sessions = session.query(AnalysisSession).filter(
                and_(
                    AnalysisSession.user_id == user_id,
                    AnalysisSession.status == 'processing',
                    AnalysisSession.created_at >= cutoff_date
                )
            ).count()
            
            # Average processing time for this user's completed sessions
            avg_processing_time = session.query(func.avg(AnalysisSession.total_processing_time)).filter(
                and_(
                    AnalysisSession.user_id == user_id,
                    AnalysisSession.status == 'completed',
                    AnalysisSession.total_processing_time.isnot(None),
                    AnalysisSession.created_at >= cutoff_date
                )
            ).scalar()
            
            # Recent sessions for this user
            recent_sessions = session.query(AnalysisSession).filter(
                AnalysisSession.user_id == user_id
            ).order_by(desc(AnalysisSession.created_at)).limit(5).all()
            
            # Sessions by day for chart (last 7 days) for this user
            sessions_by_day = []
            for i in range(6, -1, -1):
                day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                
                day_count = session.query(AnalysisSession).filter(
                    and_(
                        AnalysisSession.user_id == user_id,
                        AnalysisSession.created_at >= day_start,
                        AnalysisSession.created_at < day_end
                    )
                ).count()
                
                sessions_by_day.append({
                    'date': day_start.strftime('%Y-%m-%d'),
                    'count': day_count
                })
            
            return {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'failed_sessions': failed_sessions,
                'processing_sessions': processing_sessions,
                'success_rate': round((completed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 1),
                'average_processing_time': round(float(avg_processing_time), 2) if avg_processing_time else 0,
                'recent_sessions': [session.to_dict() for session in recent_sessions],
                'sessions_by_day': sessions_by_day,
                'period_days': days_back
            }
            
        except Exception as e:
            logger.error(f"Failed to get user dashboard stats: {str(e)}")
            return {
                'total_sessions': 0,
                'completed_sessions': 0,
                'failed_sessions': 0,
                'processing_sessions': 0,
                'success_rate': 0,
                'average_processing_time': 0,
                'recent_sessions': [],
                'sessions_by_day': [],
                'period_days': days_back
            }
        finally:
            close_db_session(session)

    @staticmethod
    def get_total_token_usage_for_session(session_id: int) -> int:
        """Calculate the sum of token_usage for all agent results in a session."""
        session = get_db_session()
        try:
            total_tokens = session.query(func.sum(AgentResult.token_usage)).filter(
                AgentResult.session_id == session_id
            ).scalar()
            return total_tokens or 0
        except Exception as e:
            logger.error(f"Failed to calculate total token usage for session {session_id}: {str(e)}")
            return 0
        finally:
            close_db_session(session)
  
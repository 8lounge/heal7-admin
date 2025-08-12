"""
프론트엔드 아카데미 API 라우터
heal7.com에서 사용하는 아카데미 조회 전용 API
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# 라우터 생성 (프론트엔드 전용)
router = APIRouter(prefix="/api/academy")

class EnrollmentRequest(BaseModel):
    user_name: str
    user_email: str
    user_phone: str
    payment_method: Optional[str] = None

# 데이터베이스 연결 함수
def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="livedb",
            user="liveuser",
            password="livepass2024",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@router.get("/projects")
async def get_projects(
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """아카데미 프로젝트 목록 조회 (프론트엔드용)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        base_query = """
        SELECT id, title, description, category, instructor_name, 
               target_amount, current_amount, target_participants, 
               current_participants, duration_days, price, image_url, 
               difficulty_level, status, created_at, updated_at,
               start_date, end_date,
               CASE 
                   WHEN target_amount > 0 THEN ROUND((current_amount::float / target_amount * 100), 2)
                   ELSE 0 
               END as funding_percentage,
               CASE 
                   WHEN end_date > CURRENT_DATE THEN (end_date - CURRENT_DATE)
                   ELSE 0 
               END as days_remaining
        FROM academy_projects 
        WHERE 1=1
        """
        
        params = []
        
        if category:
            base_query += " AND category = %s"
            params.append(category)
            
        if status:
            base_query += " AND status = %s"
            params.append(status)
        else:
            # 기본적으로 활성 상태만 조회
            base_query += " AND status = 'active'"
            
        base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        projects = cursor.fetchall()
        
        # 총 개수 조회
        count_query = "SELECT COUNT(*) FROM academy_projects WHERE 1=1"
        count_params = []
        
        if category:
            count_query += " AND category = %s"
            count_params.append(category)
            
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        else:
            count_query += " AND status = 'active'"
            
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "projects": projects,
            "total": total,
            "limit": limit,
            "offset": offset,
            "category": category,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error fetching academy projects: {e}")
        raise HTTPException(status_code=500, detail=f"아카데미 프로젝트 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/projects/{project_id}")
async def get_project(project_id: int):
    """아카데미 프로젝트 상세 조회 (프론트엔드용)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, title, description, category, instructor_name, 
               target_amount, current_amount, target_participants, 
               current_participants, duration_days, price, image_url, 
               difficulty_level, status, created_at, updated_at,
               start_date, end_date,
               CASE 
                   WHEN target_amount > 0 THEN ROUND((current_amount::float / target_amount * 100), 2)
                   ELSE 0 
               END as funding_percentage,
               CASE 
                   WHEN end_date > CURRENT_DATE THEN (end_date - CURRENT_DATE)
                   ELSE 0 
               END as days_remaining
        FROM academy_projects 
        WHERE id = %s AND status = 'active'
        """, (project_id,))
        
        project = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not project:
            raise HTTPException(status_code=404, detail="아카데미 프로젝트를 찾을 수 없습니다")
        
        return {
            "success": True,
            "project": project
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching academy project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"아카데미 프로젝트 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/categories")
async def get_categories():
    """아카데미 카테고리 목록 조회 (프론트엔드용)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT category as name, COUNT(*) as project_count
        FROM academy_projects 
        WHERE status = 'active'
        GROUP BY category
        ORDER BY project_count DESC
        """)
        
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error fetching academy categories: {e}")
        raise HTTPException(status_code=500, detail=f"아카데미 카테고리 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/stats")
async def get_stats():
    """아카데미 통계 조회 (프론트엔드용)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 전체 통계
        cursor.execute("""
        SELECT 
            COUNT(*) as total_projects,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_projects,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_projects,
            COALESCE(SUM(current_amount), 0) as total_funding,
            COALESCE(SUM(current_participants), 0) as total_participants
        FROM academy_projects
        """)
        
        stats = cursor.fetchone()
        
        # 카테고리별 통계
        cursor.execute("""
        SELECT 
            category,
            COUNT(*) as project_count,
            COALESCE(SUM(current_amount), 0) as total_funding
        FROM academy_projects
        WHERE status = 'active'
        GROUP BY category
        ORDER BY project_count DESC
        """)
        
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "total_projects": stats['total_projects'],
                "active_projects": stats['active_projects'],
                "completed_projects": stats['completed_projects'],
                "total_funding": int(stats['total_funding']),
                "total_participants": int(stats['total_participants']),
                "categories": categories
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching academy stats: {e}")
        raise HTTPException(status_code=500, detail=f"아카데미 통계 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/projects/{project_id}/enroll")
async def enroll_project(project_id: int, enrollment_data: EnrollmentRequest):
    """아카데미 프로젝트 등록/후원 (프론트엔드용)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 프로젝트 존재 및 상태 확인
        cursor.execute("""
        SELECT id, title, price, current_participants, target_participants, status
        FROM academy_projects 
        WHERE id = %s
        """, (project_id,))
        
        project = cursor.fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="아카데미 프로젝트를 찾을 수 없습니다")
        
        if project['status'] != 'active':
            raise HTTPException(status_code=400, detail="현재 등록할 수 없는 프로젝트입니다")
        
        if project['current_participants'] >= project['target_participants']:
            raise HTTPException(status_code=400, detail="정원이 마감된 프로젝트입니다")
        
        # 중복 등록 확인 (이메일 기준)
        cursor.execute("""
        SELECT id FROM academy_enrollments 
        WHERE project_id = %s AND user_email = %s
        """, (project_id, enrollment_data.user_email))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="이미 등록하신 프로젝트입니다")
        
        # 등록 처리
        enrollment_id = f"ACADEMY_{project_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
        INSERT INTO academy_enrollments (
            enrollment_id, project_id, user_name, user_email, user_phone,
            payment_method, enrollment_date, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            enrollment_id, project_id, enrollment_data.user_name,
            enrollment_data.user_email, enrollment_data.user_phone,
            enrollment_data.payment_method or 'pending',
            datetime.now(), 'enrolled'
        ))
        
        # 참여자 수 증가
        cursor.execute("""
        UPDATE academy_projects 
        SET current_participants = current_participants + 1,
            current_amount = current_amount + %s,
            updated_at = %s
        WHERE id = %s
        """, (project['price'], datetime.now(), project_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "enrollment_id": enrollment_id,
            "message": "아카데미 프로젝트 등록이 완료되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling academy project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"아카데미 프로젝트 등록 중 오류가 발생했습니다: {str(e)}")
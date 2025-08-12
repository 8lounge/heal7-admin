"""
아카데미(크라우드펀딩) 관리 API 라우터
HEAL7 크라우드펀딩 프로젝트 관리 기능
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Pydantic 모델 정의
class ProjectCreateRequest(BaseModel):
    title: str
    description: str
    category: str
    instructor_name: str
    target_amount: int
    target_participants: int
    duration_days: int
    price: int
    image_url: Optional[str] = None
    difficulty_level: str = 'beginner'  # beginner, intermediate, advanced

class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    instructor_name: Optional[str] = None
    target_amount: Optional[int] = None
    target_participants: Optional[int] = None
    duration_days: Optional[int] = None
    price: Optional[int] = None
    image_url: Optional[str] = None
    difficulty_level: Optional[str] = None
    status: Optional[str] = None

class EnrollmentRequest(BaseModel):
    user_name: str
    user_email: str
    user_phone: str
    payment_method: str = 'card'

# 라우터 생성
router = APIRouter(prefix="/admin-api/academy")

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

@router.get("/health")
async def academy_health():
    """아카데미 관리 시스템 상태 확인"""
    return {
        "service": "Academy Management",
        "status": "healthy",
        "version": "1.0.0"
    }

@router.get("/projects")
async def get_projects(
    category: Optional[str] = Query(None, description="프로젝트 카테고리 필터"),
    status: Optional[str] = Query(None, description="프로젝트 상태 필터"),
    limit: int = Query(20, description="조회할 프로젝트 수"),
    offset: int = Query(0, description="페이지네이션 오프셋")
):
    """프로젝트 목록 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 쿼리 구성
        base_query = """
        SELECT p.id, p.title, p.description, p.category, p.instructor_name,
               p.target_amount, p.current_amount, p.target_participants, p.current_participants,
               p.duration_days, p.price, p.image_url, p.difficulty_level, p.status,
               p.created_at, p.updated_at, p.start_date, p.end_date,
               CASE 
                   WHEN p.target_amount > 0 THEN ROUND(((p.current_amount::numeric / p.target_amount::numeric) * 100)::numeric, 2)
                   ELSE 0 
               END as funding_percentage,
               CASE 
                   WHEN p.end_date > NOW() THEN EXTRACT(DAY FROM p.end_date - NOW())::int
                   ELSE 0
               END as days_remaining
        FROM academy_projects p
        WHERE 1=1
        """
        
        params = []
        if category:
            base_query += " AND p.category = %s"
            params.append(category)
        
        if status:
            base_query += " AND p.status = %s"
            params.append(status)
        
        base_query += " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        projects = cursor.fetchall()
        
        # 전체 개수 조회
        count_query = "SELECT COUNT(*) FROM academy_projects WHERE 1=1"
        count_params = []
        if category:
            count_query += " AND category = %s"
            count_params.append(category)
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
            
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        # 데이터 포맷팅
        formatted_projects = []
        for project in projects:
            formatted_projects.append({
                "id": project['id'],
                "title": project['title'],
                "description": project['description'],
                "category": project['category'],
                "instructor_name": project['instructor_name'],
                "target_amount": project['target_amount'],
                "current_amount": project['current_amount'],
                "target_participants": project['target_participants'],
                "current_participants": project['current_participants'],
                "duration_days": project['duration_days'],
                "price": project['price'],
                "image_url": project['image_url'],
                "difficulty_level": project['difficulty_level'],
                "status": project['status'],
                "funding_percentage": float(project['funding_percentage']),
                "days_remaining": project['days_remaining'],
                "created_at": project['created_at'].isoformat() if project['created_at'] else None,
                "updated_at": project['updated_at'].isoformat() if project['updated_at'] else None,
                "start_date": project['start_date'].isoformat() if project['start_date'] else None,
                "end_date": project['end_date'].isoformat() if project['end_date'] else None,
            })
        
        return {
            "success": True,
            "projects": formatted_projects,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "category": category,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        raise HTTPException(status_code=500, detail=f"프로젝트 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/projects/{project_id}")
async def get_project(project_id: int):
    """특정 프로젝트 상세 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT p.id, p.title, p.description, p.category, p.instructor_name,
               p.target_amount, p.current_amount, p.target_participants, p.current_participants,
               p.duration_days, p.price, p.image_url, p.difficulty_level, p.status,
               p.created_at, p.updated_at, p.start_date, p.end_date,
               CASE 
                   WHEN p.target_amount > 0 THEN ROUND(((p.current_amount::numeric / p.target_amount::numeric) * 100)::numeric, 2)
                   ELSE 0 
               END as funding_percentage,
               CASE 
                   WHEN p.end_date > NOW() THEN EXTRACT(DAY FROM p.end_date - NOW())::int
                   ELSE 0
               END as days_remaining
        FROM academy_projects p
        WHERE p.id = %s
        """, (project_id,))
        
        project = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not project:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")
        
        return {
            "success": True,
            "project": {
                "id": project['id'],
                "title": project['title'],
                "description": project['description'],
                "category": project['category'],
                "instructor_name": project['instructor_name'],
                "target_amount": project['target_amount'],
                "current_amount": project['current_amount'],
                "target_participants": project['target_participants'],
                "current_participants": project['current_participants'],
                "duration_days": project['duration_days'],
                "price": project['price'],
                "image_url": project['image_url'],
                "difficulty_level": project['difficulty_level'],
                "status": project['status'],
                "funding_percentage": float(project['funding_percentage']),
                "days_remaining": project['days_remaining'],
                "created_at": project['created_at'].isoformat() if project['created_at'] else None,
                "updated_at": project['updated_at'].isoformat() if project['updated_at'] else None,
                "start_date": project['start_date'].isoformat() if project['start_date'] else None,
                "end_date": project['end_date'].isoformat() if project['end_date'] else None,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"프로젝트 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/categories")
async def get_categories():
    """프로젝트 카테고리 목록 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT category, COUNT(*) as project_count
        FROM academy_projects 
        WHERE status != 'deleted'
        GROUP BY category
        ORDER BY category
        """)
        
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "categories": [
                {
                    "name": cat['category'],
                    "project_count": cat['project_count']
                }
                for cat in categories
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=f"카테고리 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/projects")
async def create_project(project_request: ProjectCreateRequest):
    """새 프로젝트 생성"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 종료일 계산
        end_date = datetime.now() + timedelta(days=project_request.duration_days)
        
        cursor.execute("""
        INSERT INTO academy_projects (
            title, description, category, instructor_name,
            target_amount, current_amount, target_participants, current_participants,
            duration_days, price, image_url, difficulty_level, status,
            created_at, updated_at, start_date, end_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (
            project_request.title,
            project_request.description,
            project_request.category,
            project_request.instructor_name,
            project_request.target_amount,
            0,  # current_amount
            project_request.target_participants,
            0,  # current_participants
            project_request.duration_days,
            project_request.price,
            project_request.image_url,
            project_request.difficulty_level,
            'active',
            datetime.now(),
            datetime.now(),
            datetime.now(),
            end_date
        ))
        
        project_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "project_id": project_id,
            "message": "프로젝트가 성공적으로 생성되었습니다"
        }
        
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=f"프로젝트 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/projects/{project_id}")
async def update_project(project_id: int, project_request: ProjectUpdateRequest):
    """프로젝트 정보 업데이트"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 업데이트할 필드들 동적으로 구성
        update_fields = []
        params = []
        
        for field, value in project_request.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                params.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="업데이트할 필드가 없습니다")
        
        update_fields.append("updated_at = %s")
        params.append(datetime.now())
        params.append(project_id)
        
        query = f"""
        UPDATE academy_projects 
        SET {', '.join(update_fields)}
        WHERE id = %s
        """
        
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "프로젝트가 성공적으로 업데이트되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"프로젝트 업데이트 중 오류가 발생했습니다: {str(e)}")

@router.post("/projects/{project_id}/enroll")
async def enroll_project(project_id: int, enrollment_request: EnrollmentRequest):
    """프로젝트 등록/후원"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 프로젝트 정보 조회
        cursor.execute("""
        SELECT id, title, price, current_participants, target_participants, status, end_date
        FROM academy_projects 
        WHERE id = %s
        """, (project_id,))
        
        project = cursor.fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")
        
        if project['status'] != 'active':
            raise HTTPException(status_code=400, detail="활성화되지 않은 프로젝트입니다")
        
        if project['end_date'] <= datetime.now():
            raise HTTPException(status_code=400, detail="마감된 프로젝트입니다")
        
        if project['current_participants'] >= project['target_participants']:
            raise HTTPException(status_code=400, detail="정원이 마감된 프로젝트입니다")
        
        # 등록 ID 생성
        enrollment_id = f"ENROLL_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
        
        # 등록 정보 저장
        cursor.execute("""
        INSERT INTO academy_enrollments (
            enrollment_id, project_id, user_name, user_email, user_phone,
            amount, payment_method, status, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            enrollment_id,
            project_id,
            enrollment_request.user_name,
            enrollment_request.user_email,
            enrollment_request.user_phone,
            project['price'],
            enrollment_request.payment_method,
            'pending',
            datetime.now(),
            datetime.now()
        ))
        
        # 프로젝트 통계 업데이트
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
            "enrollment": {
                "enrollment_id": enrollment_id,
                "project_title": project['title'],
                "user_name": enrollment_request.user_name,
                "amount": project['price'],
                "status": "pending"
            },
            "message": "프로젝트 등록이 성공적으로 완료되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"프로젝트 등록 중 오류가 발생했습니다: {str(e)}")

@router.get("/stats")
async def get_academy_stats():
    """아카데미 통계 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 프로젝트 통계
        cursor.execute("""
        SELECT 
            COUNT(*) as total_projects,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_projects,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_projects,
            COALESCE(SUM(current_amount), 0) as total_funding,
            COALESCE(SUM(current_participants), 0) as total_participants
        FROM academy_projects
        """)
        
        project_stats = cursor.fetchone()
        
        # 카테고리별 통계
        cursor.execute("""
        SELECT category, COUNT(*) as count, COALESCE(SUM(current_amount), 0) as funding
        FROM academy_projects 
        WHERE status != 'deleted'
        GROUP BY category
        ORDER BY count DESC
        """)
        
        category_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "total_projects": project_stats['total_projects'],
                "active_projects": project_stats['active_projects'],
                "completed_projects": project_stats['completed_projects'],
                "total_funding": float(project_stats['total_funding']),
                "total_participants": project_stats['total_participants'],
                "categories": [
                    {
                        "category": stat['category'],
                        "project_count": stat['count'],
                        "total_funding": float(stat['funding'])
                    }
                    for stat in category_stats
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching academy stats: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")
"""
커뮤니티 관리 API 라우터
HEAL7 커뮤니티 (공지사항, 1:1문의) 관리 기능
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Pydantic 모델 정의
class NoticeCreateRequest(BaseModel):
    title: str
    content: str
    author_name: str = "HEAL7 관리자"
    is_pinned: bool = False

class NoticeUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author_name: Optional[str] = None
    is_pinned: Optional[bool] = None

class InquiryCreateRequest(BaseModel):
    title: str
    content: str
    user_name: str
    user_email: str
    user_phone: Optional[str] = None
    category: str = "general"  # general, technical, billing, other

class InquiryReplyRequest(BaseModel):
    reply_content: str
    admin_name: str = "HEAL7 관리자"

# 라우터 생성
router = APIRouter(prefix="/admin-api/community")

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
async def community_health():
    """커뮤니티 관리 시스템 상태 확인"""
    return {
        "service": "Community Management",
        "status": "healthy",
        "version": "1.0.0"
    }

# ========== 공지사항 API ==========
@router.get("/notices")
async def get_notices(
    limit: int = Query(20, description="조회할 공지사항 수"),
    offset: int = Query(0, description="페이지네이션 오프셋")
):
    """공지사항 목록 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, title, content, author_name, views, is_pinned,
               created_at, updated_at
        FROM notices 
        ORDER BY is_pinned DESC, created_at DESC 
        LIMIT %s OFFSET %s
        """, (limit, offset))
        
        notices = cursor.fetchall()
        
        # 전체 개수 조회
        cursor.execute("SELECT COUNT(*) FROM notices")
        total_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        # 데이터 포맷팅
        formatted_notices = []
        for notice in notices:
            formatted_notices.append({
                "id": notice['id'],
                "title": notice['title'],
                "content": notice['content'],
                "author_name": notice['author_name'],
                "views": notice['views'],
                "is_pinned": notice['is_pinned'],
                "created_at": notice['created_at'].isoformat() if notice['created_at'] else None,
                "updated_at": notice['updated_at'].isoformat() if notice['updated_at'] else None,
            })
        
        return {
            "success": True,
            "notices": formatted_notices,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching notices: {e}")
        raise HTTPException(status_code=500, detail=f"공지사항 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/notices/{notice_id}")
async def get_notice(notice_id: int):
    """특정 공지사항 상세 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 조회수 증가
        cursor.execute("""
        UPDATE notices 
        SET views = views + 1, updated_at = %s
        WHERE id = %s
        """, (datetime.now(), notice_id))
        
        # 공지사항 조회
        cursor.execute("""
        SELECT id, title, content, author_name, views, is_pinned,
               created_at, updated_at
        FROM notices 
        WHERE id = %s
        """, (notice_id,))
        
        notice = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if not notice:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
        
        return {
            "success": True,
            "notice": {
                "id": notice['id'],
                "title": notice['title'],
                "content": notice['content'],
                "author_name": notice['author_name'],
                "views": notice['views'],
                "is_pinned": notice['is_pinned'],
                "created_at": notice['created_at'].isoformat() if notice['created_at'] else None,
                "updated_at": notice['updated_at'].isoformat() if notice['updated_at'] else None,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notice {notice_id}: {e}")
        raise HTTPException(status_code=500, detail=f"공지사항 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/notices")
async def create_notice(notice_request: NoticeCreateRequest):
    """새 공지사항 생성"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO notices (title, content, author_name, is_pinned, views, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (
            notice_request.title,
            notice_request.content,
            notice_request.author_name,
            notice_request.is_pinned,
            0,  # views
            datetime.now(),
            datetime.now()
        ))
        
        notice_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "notice_id": notice_id,
            "message": "공지사항이 성공적으로 생성되었습니다"
        }
        
    except Exception as e:
        logger.error(f"Error creating notice: {e}")
        raise HTTPException(status_code=500, detail=f"공지사항 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/notices/{notice_id}")
async def update_notice(notice_id: int, notice_request: NoticeUpdateRequest):
    """공지사항 수정"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 업데이트할 필드들 동적으로 구성
        update_fields = []
        params = []
        
        for field, value in notice_request.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                params.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="업데이트할 필드가 없습니다")
        
        update_fields.append("updated_at = %s")
        params.append(datetime.now())
        params.append(notice_id)
        
        query = f"""
        UPDATE notices 
        SET {', '.join(update_fields)}
        WHERE id = %s
        """
        
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "공지사항이 성공적으로 업데이트되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notice {notice_id}: {e}")
        raise HTTPException(status_code=500, detail=f"공지사항 업데이트 중 오류가 발생했습니다: {str(e)}")

@router.delete("/notices/{notice_id}")
async def delete_notice(notice_id: int):
    """공지사항 삭제"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM notices WHERE id = %s", (notice_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "공지사항이 성공적으로 삭제되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notice {notice_id}: {e}")
        raise HTTPException(status_code=500, detail=f"공지사항 삭제 중 오류가 발생했습니다: {str(e)}")

# ========== 1:1 문의 API ==========
@router.get("/inquiries")
async def get_inquiries(
    status: Optional[str] = Query(None, description="답변 상태 필터 (pending, answered)"),
    category: Optional[str] = Query(None, description="문의 카테고리 필터"),
    limit: int = Query(20, description="조회할 문의 수"),
    offset: int = Query(0, description="페이지네이션 오프셋")
):
    """1:1 문의 목록 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 쿼리 구성
        base_query = """
        SELECT id, title, content, user_name, user_email, user_phone, category,
               status, admin_reply, admin_name, replied_at, created_at, updated_at
        FROM inquiries 
        WHERE 1=1
        """
        
        params = []
        if status:
            base_query += " AND status = %s"
            params.append(status)
        
        if category:
            base_query += " AND category = %s"
            params.append(category)
        
        base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        inquiries = cursor.fetchall()
        
        # 전체 개수 조회
        count_query = "SELECT COUNT(*) FROM inquiries WHERE 1=1"
        count_params = []
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        if category:
            count_query += " AND category = %s"
            count_params.append(category)
            
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        # 데이터 포맷팅
        formatted_inquiries = []
        for inquiry in inquiries:
            formatted_inquiries.append({
                "id": inquiry['id'],
                "title": inquiry['title'],
                "content": inquiry['content'],
                "user_name": inquiry['user_name'],
                "user_email": inquiry['user_email'],
                "user_phone": inquiry['user_phone'],
                "category": inquiry['category'],
                "status": inquiry['status'],
                "admin_reply": inquiry['admin_reply'],
                "admin_name": inquiry['admin_name'],
                "replied_at": inquiry['replied_at'].isoformat() if inquiry['replied_at'] else None,
                "created_at": inquiry['created_at'].isoformat() if inquiry['created_at'] else None,
                "updated_at": inquiry['updated_at'].isoformat() if inquiry['updated_at'] else None,
            })
        
        return {
            "success": True,
            "inquiries": formatted_inquiries,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "status": status,
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Error fetching inquiries: {e}")
        raise HTTPException(status_code=500, detail=f"문의 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/inquiries/{inquiry_id}")
async def get_inquiry(inquiry_id: int):
    """특정 1:1 문의 상세 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, title, content, user_name, user_email, user_phone, category,
               status, admin_reply, admin_name, replied_at, created_at, updated_at
        FROM inquiries 
        WHERE id = %s
        """, (inquiry_id,))
        
        inquiry = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not inquiry:
            raise HTTPException(status_code=404, detail="문의를 찾을 수 없습니다")
        
        return {
            "success": True,
            "inquiry": {
                "id": inquiry['id'],
                "title": inquiry['title'],
                "content": inquiry['content'],
                "user_name": inquiry['user_name'],
                "user_email": inquiry['user_email'],
                "user_phone": inquiry['user_phone'],
                "category": inquiry['category'],
                "status": inquiry['status'],
                "admin_reply": inquiry['admin_reply'],
                "admin_name": inquiry['admin_name'],
                "replied_at": inquiry['replied_at'].isoformat() if inquiry['replied_at'] else None,
                "created_at": inquiry['created_at'].isoformat() if inquiry['created_at'] else None,
                "updated_at": inquiry['updated_at'].isoformat() if inquiry['updated_at'] else None,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inquiry {inquiry_id}: {e}")
        raise HTTPException(status_code=500, detail=f"문의 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/inquiries")
async def create_inquiry(inquiry_request: InquiryCreateRequest):
    """새 1:1 문의 생성"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO inquiries (
            title, content, user_name, user_email, user_phone, category,
            status, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (
            inquiry_request.title,
            inquiry_request.content,
            inquiry_request.user_name,
            inquiry_request.user_email,
            inquiry_request.user_phone,
            inquiry_request.category,
            'pending',
            datetime.now(),
            datetime.now()
        ))
        
        inquiry_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "inquiry_id": inquiry_id,
            "message": "문의가 성공적으로 접수되었습니다"
        }
        
    except Exception as e:
        logger.error(f"Error creating inquiry: {e}")
        raise HTTPException(status_code=500, detail=f"문의 생성 중 오류가 발생했습니다: {str(e)}")

@router.post("/inquiries/{inquiry_id}/reply")
async def reply_inquiry(inquiry_id: int, reply_request: InquiryReplyRequest):
    """1:1 문의 답변"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 문의 존재 확인
        cursor.execute("SELECT id FROM inquiries WHERE id = %s", (inquiry_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="문의를 찾을 수 없습니다")
        
        # 답변 업데이트
        cursor.execute("""
        UPDATE inquiries 
        SET admin_reply = %s, admin_name = %s, status = %s, 
            replied_at = %s, updated_at = %s
        WHERE id = %s
        """, (
            reply_request.reply_content,
            reply_request.admin_name,
            'answered',
            datetime.now(),
            datetime.now(),
            inquiry_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "답변이 성공적으로 등록되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error replying to inquiry {inquiry_id}: {e}")
        raise HTTPException(status_code=500, detail=f"답변 등록 중 오류가 발생했습니다: {str(e)}")

@router.get("/stats")
async def get_community_stats():
    """커뮤니티 통계 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 공지사항 통계
        cursor.execute("SELECT COUNT(*) as count FROM notices")
        total_notices = cursor.fetchone()['count']
        
        # 문의 통계
        cursor.execute("""
        SELECT 
            COUNT(*) as total_inquiries,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_inquiries,
            COUNT(CASE WHEN status = 'answered' THEN 1 END) as answered_inquiries
        FROM inquiries
        """)
        
        inquiry_stats = cursor.fetchone()
        
        # 카테고리별 문의 통계
        cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM inquiries 
        GROUP BY category
        ORDER BY count DESC
        """)
        
        category_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "total_notices": total_notices,
                "total_inquiries": inquiry_stats['total_inquiries'],
                "pending_inquiries": inquiry_stats['pending_inquiries'],
                "answered_inquiries": inquiry_stats['answered_inquiries'],
                "categories": [
                    {
                        "category": stat['category'],
                        "count": stat['count']
                    }
                    for stat in category_stats
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching community stats: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")
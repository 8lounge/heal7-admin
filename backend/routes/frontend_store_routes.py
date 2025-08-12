"""
프론트엔드 스토어 API 라우터
heal7.com에서 사용하는 상품 조회 전용 API
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# 라우터 생성 (프론트엔드 전용)
router = APIRouter(prefix="/api/store")

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

@router.get("/products")
async def get_products(category: Optional[str] = None):
    """상품 목록 조회 (프론트엔드용)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
            SELECT id, name, price, description, category, stock_quantity, 
                   is_active, created_at, updated_at, image_url, 
                   featured_badge as badge, is_featured, shipping_info
            FROM products 
            WHERE category = %s AND is_active = true
            ORDER BY created_at DESC
            """, (category,))
        else:
            cursor.execute("""
            SELECT id, name, price, description, category, stock_quantity, 
                   is_active, created_at, updated_at, image_url, 
                   featured_badge as badge, is_featured, shipping_info
            FROM products 
            WHERE is_active = true
            ORDER BY created_at DESC
            """)
        
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "products": products,
            "count": len(products)
        }
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=f"상품 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/products/{product_id}")
async def get_product(product_id: int):
    """상품 상세 조회 (프론트엔드용)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, price, description, category, stock_quantity, 
               is_active, created_at, updated_at, image_url, 
               featured_badge as badge, is_featured, shipping_info
        FROM products 
        WHERE id = %s AND is_active = true
        """, (product_id,))
        
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not product:
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
        
        return {
            "success": True,
            "product": product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"상품 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/products/featured")
async def get_featured_products():
    """추천 상품 조회 (프론트엔드용)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, price, description, category, stock_quantity, 
               is_active, created_at, updated_at, image_url, 
               featured_badge as badge, is_featured, shipping_info
        FROM products 
        WHERE is_featured = true AND is_active = true
        ORDER BY created_at DESC
        """)
        
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "products": products,
            "count": len(products)
        }
        
    except Exception as e:
        logger.error(f"Error fetching featured products: {e}")
        raise HTTPException(status_code=500, detail=f"추천 상품 조회 중 오류가 발생했습니다: {str(e)}")
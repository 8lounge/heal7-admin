"""
스토어 관리 API 라우터
HEAL7 전자상거래 스토어 관리 기능
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
class OrderCreateRequest(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    product_id: int
    quantity: int = 1

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    product_type: str
    price: int
    description: str
    duration: Optional[str] = None

# 라우터 생성 (관리자 백엔드용)
router = APIRouter(prefix="/admin-api/store")

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
async def store_health():
    """스토어 관리 시스템 상태 확인"""
    return {
        "service": "Store Management",
        "status": "healthy",
        "version": "2.0.0"
    }

@router.get("/products")
async def get_products(
    category: Optional[str] = Query(None, description="상품 카테고리 필터"),
    limit: int = Query(20, description="조회할 상품 수"),
    offset: int = Query(0, description="페이지네이션 오프셋")
):
    """상품 목록 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 쿼리 구성
        base_query = """
        SELECT id, name, description, price, category, image_url, 
               stock_quantity, is_active, shipping_info, created_at, updated_at
        FROM products 
        WHERE is_active = true
        """
        
        params = []
        if category:
            base_query += " AND category = %s"
            params.append(category)
        
        base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        products = cursor.fetchall()
        
        # 전체 개수 조회
        count_query = "SELECT COUNT(*) FROM products WHERE is_active = true"
        count_params = []
        if category:
            count_query += " AND category = %s"
            count_params.append(category)
            
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        # 데이터 포맷팅
        formatted_products = []
        for product in products:
            formatted_products.append({
                "id": product['id'],
                "name": product['name'],
                "description": product['description'],
                "price": float(product['price']),
                "category": product['category'],
                "image_url": product['image_url'],
                "stock_quantity": product['stock_quantity'],
                "is_active": product['is_active'],
                "shipping_info": product['shipping_info'],
                "created_at": product['created_at'].isoformat() if product['created_at'] else None,
                "updated_at": product['updated_at'].isoformat() if product['updated_at'] else None
            })
        
        return {
            "success": True,
            "products": formatted_products,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=f"상품 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/products/featured")
async def get_featured_products():
    """추천 상품 목록 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, description, price, category, image_url, 
               stock_quantity, is_active, shipping_info, featured_badge,
               created_at, updated_at
        FROM products 
        WHERE is_featured = true AND is_active = true
        ORDER BY 
            CASE featured_badge 
                WHEN 'BESTSELLER' THEN 1
                WHEN 'HOT' THEN 2
                WHEN 'PREMIUM' THEN 3
                ELSE 4
            END,
            created_at DESC
        """)
        
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # 데이터 포맷팅
        formatted_products = []
        for product in products:
            formatted_products.append({
                "id": product['id'],
                "name": product['name'],
                "description": product['description'],
                "price": float(product['price']),
                "category": product['category'],
                "image_url": product['image_url'],
                "stock_quantity": product['stock_quantity'],
                "is_active": product['is_active'],
                "shipping_info": product['shipping_info'],
                "featured_badge": product['featured_badge'],
                "created_at": product['created_at'].isoformat() if product['created_at'] else None,
                "updated_at": product['updated_at'].isoformat() if product['updated_at'] else None
            })
        
        return {
            "success": True,
            "products": formatted_products,
            "total": len(formatted_products)
        }
        
    except Exception as e:
        logger.error(f"Error fetching featured products: {e}")
        raise HTTPException(status_code=500, detail=f"추천 상품 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/products/{product_id}")
async def get_product(product_id: int):
    """특정 상품 상세 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, description, price, category, image_url, 
               stock_quantity, is_active, shipping_info, created_at, updated_at
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
            "product": {
                "id": product['id'],
                "name": product['name'],
                "description": product['description'],
                "price": float(product['price']),
                "category": product['category'],
                "image_url": product['image_url'],
                "stock_quantity": product['stock_quantity'],
                "is_active": product['is_active'],
                "shipping_info": product['shipping_info'],
                "created_at": product['created_at'].isoformat() if product['created_at'] else None,
                "updated_at": product['updated_at'].isoformat() if product['updated_at'] else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"상품 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/categories")
async def get_categories():
    """상품 카테고리 목록 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT category, COUNT(*) as product_count
        FROM products 
        WHERE is_active = true
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
                    "product_count": cat['product_count']
                }
                for cat in categories
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=f"카테고리 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/orders")
async def get_orders():
    """주문 목록 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT o.id, o.order_id, o.customer_name, o.customer_email, o.customer_phone,
               o.total_amount, o.order_name, o.status, o.payment_key, o.payment_method,
               o.created_at, o.updated_at
        FROM orders o
        ORDER BY o.created_at DESC
        """)
        
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        
        formatted_orders = []
        for order in orders:
            formatted_orders.append({
                "id": order['id'],
                "order_id": order['order_id'],
                "customer_name": order['customer_name'],
                "customer_email": order['customer_email'],
                "customer_phone": order['customer_phone'],
                "total_amount": float(order['total_amount']) if order['total_amount'] else 0,
                "order_name": order['order_name'],
                "status": order['status'],
                "payment_key": order['payment_key'],
                "payment_method": order['payment_method'],
                "created_at": order['created_at'].isoformat() if order['created_at'] else None,
                "updated_at": order['updated_at'].isoformat() if order['updated_at'] else None
            })
        
        return {
            "success": True,
            "orders": formatted_orders,
            "total": len(formatted_orders)
        }
        
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=f"주문 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/stats")
async def get_store_stats():
    """스토어 통계 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 상품 통계
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE is_active = true")
        total_products = cursor.fetchone()['count']
        
        # 주문 통계
        cursor.execute("SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as revenue FROM orders")
        order_stats = cursor.fetchone()
        total_orders = order_stats['count']
        total_revenue = float(order_stats['revenue']) if order_stats['revenue'] else 0
        
        # 카테고리별 상품 수
        cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM products WHERE is_active = true 
        GROUP BY category
        """)
        category_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "total_products": total_products,
                "total_orders": total_orders,
                "total_revenue": total_revenue,
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
        logger.error(f"Error fetching store stats: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/orders")
async def create_order(order_request: OrderCreateRequest):
    """주문 생성"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 상품 정보 조회
        cursor.execute("""
        SELECT id, name, price, stock_quantity, category
        FROM products 
        WHERE id = %s AND is_active = true
        """, (order_request.product_id,))
        
        product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
        
        if product['stock_quantity'] < order_request.quantity:
            raise HTTPException(status_code=400, detail="재고가 부족합니다")
        
        # 주문 ID 생성
        order_id = f"ORDER_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
        
        # 총 금액 계산
        total_amount = int(product['price'] * order_request.quantity)
        
        # 주문 생성
        cursor.execute("""
        INSERT INTO orders (order_id, customer_name, customer_email, customer_phone, 
                           total_amount, order_name, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id,
            order_request.customer_name,
            order_request.customer_email,
            order_request.customer_phone,
            total_amount,
            f"{product['name']} - {order_request.quantity}개",
            'PENDING',
            datetime.now(),
            datetime.now()
        ))
        
        # 주문 아이템 생성
        cursor.execute("""
        INSERT INTO order_items (order_id, product_id, product_name, product_type, 
                                price, description, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id,
            order_request.product_id,
            product['name'],
            product['category'],
            int(product['price']),
            f"수량: {order_request.quantity}개",
            datetime.now()
        ))
        
        # 재고 차감
        cursor.execute("""
        UPDATE products 
        SET stock_quantity = stock_quantity - %s, updated_at = %s
        WHERE id = %s
        """, (order_request.quantity, datetime.now(), order_request.product_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "order": {
                "order_id": order_id,
                "customer_name": order_request.customer_name,
                "customer_email": order_request.customer_email,
                "total_amount": total_amount,
                "product_name": product['name'],
                "quantity": order_request.quantity,
                "status": "PENDING"
            },
            "message": "주문이 성공적으로 생성되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=f"주문 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/products/{product_id}/set-featured")
async def toggle_featured_product(product_id: int, is_featured: bool, badge: str = None):
    """상품 추천 설정/해제"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 상품 존재 확인
        cursor.execute("SELECT id, name FROM products WHERE id = %s AND is_active = true", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
        
        # 추천 상품 설정 업데이트
        if is_featured and badge:
            cursor.execute("""
                UPDATE products 
                SET is_featured = %s, featured_badge = %s, updated_at = %s
                WHERE id = %s
            """, (is_featured, badge, datetime.now(), product_id))
        else:
            cursor.execute("""
                UPDATE products 
                SET is_featured = %s, featured_badge = NULL, updated_at = %s
                WHERE id = %s
            """, (is_featured, datetime.now(), product_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        action = "추천 상품으로 설정" if is_featured else "추천 상품에서 해제"
        return {
            "success": True,
            "message": f"'{product['name']}' 상품이 {action}되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling featured product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"추천 상품 설정 중 오류가 발생했습니다: {str(e)}")

@router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    """주문 상태 업데이트"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 유효한 상태값 검증
        valid_statuses = ["PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"유효하지 않은 상태값입니다. 사용 가능한 값: {valid_statuses}")
        
        cursor.execute("""
        UPDATE orders 
        SET status = %s, updated_at = %s
        WHERE order_id = %s
        """, (status, datetime.now(), order_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"주문 상태가 {status}로 업데이트되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=500, detail=f"주문 상태 업데이트 중 오류가 발생했습니다: {str(e)}")
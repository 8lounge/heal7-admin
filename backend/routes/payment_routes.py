"""
결제 시스템 API 라우터
HEAL7 토스페이먼츠 결제 시스템
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
import requests
import base64
from datetime import datetime
import json
import secrets

logger = logging.getLogger(__name__)

# Pydantic 모델 정의
class PaymentRequest(BaseModel):
    order_type: str  # "store", "academy", or "subscription"
    item_id: int
    item_name: str
    amount: int
    quantity: int = 1
    customer_name: str
    customer_email: str
    customer_phone: str

class PaymentConfirmRequest(BaseModel):
    payment_key: str
    order_id: str
    amount: int

class PaymentCancelRequest(BaseModel):
    payment_key: str
    cancel_reason: str

# 라우터 생성
router = APIRouter(prefix="/api/payment")

# 토스페이먼츠 설정 (테스트 환경)
TOSS_CLIENT_KEY = "test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eoq"
TOSS_SECRET_KEY = "test_sk_zXLkKEypNArWmo50nX3lmeaxYG5R"
TOSS_API_BASE_URL = "https://api.tosspayments.com/v1"

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

def get_toss_headers():
    """토스페이먼츠 API 헤더 생성"""
    credentials = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode()).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }

@router.get("/health")
async def payment_health():
    """결제 시스템 상태 확인"""
    return {
        "service": "Payment System",
        "status": "healthy",
        "version": "1.0.0",
        "provider": "TossPayments"
    }

@router.post("/prepare")
async def prepare_payment(payment_request: PaymentRequest):
    """결제 준비 (주문 생성)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 주문 ID 생성
        order_id = f"HEAL7_{payment_request.order_type.upper()}_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
        
        # 상품/서비스 정보 조회 및 검증
        if payment_request.order_type == "store":
            cursor.execute("""
            SELECT id, name, price, stock_quantity, is_active
            FROM products 
            WHERE id = %s AND is_active = true
            """, (payment_request.item_id,))
            
            item = cursor.fetchone()
            if not item:
                raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
            
            if item['stock_quantity'] < payment_request.quantity:
                raise HTTPException(status_code=400, detail="재고가 부족합니다")
                
        elif payment_request.order_type == "academy":
            cursor.execute("""
            SELECT id, title, price, current_participants, target_participants, status, end_date
            FROM academy_projects 
            WHERE id = %s AND status = 'active'
            """, (payment_request.item_id,))
            
            item = cursor.fetchone()
            if not item:
                raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")
                
            if item['end_date'] <= datetime.now():
                raise HTTPException(status_code=400, detail="마감된 프로젝트입니다")
                
            if item['current_participants'] >= item['target_participants']:
                raise HTTPException(status_code=400, detail="정원이 마감된 프로젝트입니다")
                
        elif payment_request.order_type == "subscription":
            # 구독 플랜 정보 (하드코딩된 플랜 정보 사용)
            subscription_plans = {
                1: {"name": "월간 힐링 플랜", "price": 29000, "duration": 30},
                2: {"name": "분기 프리미엄 플랜", "price": 75000, "duration": 90},
                3: {"name": "연간 마스터 플랜", "price": 240000, "duration": 365}
            }
            
            if payment_request.item_id not in subscription_plans:
                raise HTTPException(status_code=404, detail="구독 플랜을 찾을 수 없습니다")
                
            item = subscription_plans[payment_request.item_id]
            # 구독 플랜은 재고나 참여자 제한이 없음
        else:
            raise HTTPException(status_code=400, detail="올바르지 않은 주문 유형입니다")
        
        # 금액 검증
        expected_amount = int(item['price']) * payment_request.quantity
        if payment_request.amount != expected_amount:
            raise HTTPException(status_code=400, detail="결제 금액이 올바르지 않습니다")
        
        # 주문 정보 저장
        cursor.execute("""
        INSERT INTO orders (
            order_id, order_type, item_id, item_name, order_name,
            customer_name, customer_email, customer_phone,
            total_amount, quantity, status, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id,
            payment_request.order_type,
            payment_request.item_id,
            payment_request.item_name,
            payment_request.item_name,  # order_name과 item_name을 동일하게 설정
            payment_request.customer_name,
            payment_request.customer_email,
            payment_request.customer_phone,
            payment_request.amount,
            payment_request.quantity,
            'PENDING',
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "order_id": order_id,
            "amount": payment_request.amount,
            "customer_name": payment_request.customer_name,
            "item_name": payment_request.item_name,
            "client_key": TOSS_CLIENT_KEY,
            "message": "결제 준비가 완료되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error preparing payment: {e}")
        raise HTTPException(status_code=500, detail=f"결제 준비 중 오류가 발생했습니다: {str(e)}")

@router.post("/confirm")
async def confirm_payment(confirm_request: PaymentConfirmRequest):
    """결제 승인"""
    try:
        # 토스페이먼츠 결제 승인 API 호출
        confirm_data = {
            "paymentKey": confirm_request.payment_key,
            "orderId": confirm_request.order_id,
            "amount": confirm_request.amount
        }
        
        response = requests.post(
            f"{TOSS_API_BASE_URL}/payments/confirm",
            headers=get_toss_headers(),
            json=confirm_data
        )
        
        if response.status_code != 200:
            error_data = response.json()
            logger.error(f"Toss payment confirm failed: {error_data}")
            raise HTTPException(
                status_code=400, 
                detail=f"결제 승인 실패: {error_data.get('message', '알 수 없는 오류')}"
            )
        
        payment_result = response.json()
        
        # 데이터베이스 업데이트
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 주문 상태 업데이트
        cursor.execute("""
        UPDATE orders 
        SET status = %s, payment_key = %s, payment_method = %s,
            payment_approved_at = %s, updated_at = %s
        WHERE order_id = %s
        """, (
            'PAID',
            confirm_request.payment_key,
            payment_result.get('method'),
            datetime.now(),
            datetime.now(),
            confirm_request.order_id
        ))
        
        # 주문 정보 조회
        cursor.execute("""
        SELECT order_type, item_id, quantity
        FROM orders 
        WHERE order_id = %s
        """, (confirm_request.order_id,))
        
        order = cursor.fetchone()
        
        if order:
            # 재고 차감 또는 참여자 수 증가
            if order['order_type'] == 'store':
                cursor.execute("""
                UPDATE products 
                SET stock_quantity = stock_quantity - %s, updated_at = %s
                WHERE id = %s
                """, (order['quantity'], datetime.now(), order['item_id']))
                
            elif order['order_type'] == 'academy':
                cursor.execute("""
                UPDATE academy_projects 
                SET current_participants = current_participants + %s,
                    current_amount = current_amount + %s,
                    updated_at = %s
                WHERE id = %s
                """, (order['quantity'], confirm_request.amount, datetime.now(), order['item_id']))
                
            elif order['order_type'] == 'subscription':
                # 구독의 경우 별도의 구독 테이블에 기록 (현재는 로깅만)
                logger.info(f"Subscription confirmed: order_id={confirm_request.order_id}, amount={confirm_request.amount}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "payment_key": confirm_request.payment_key,
            "order_id": confirm_request.order_id,
            "status": "PAID",
            "payment_result": payment_result,
            "message": "결제가 성공적으로 완료되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(status_code=500, detail=f"결제 승인 중 오류가 발생했습니다: {str(e)}")

@router.post("/cancel")
async def cancel_payment(cancel_request: PaymentCancelRequest):
    """결제 취소"""
    try:
        # 토스페이먼츠 결제 취소 API 호출
        cancel_data = {
            "cancelReason": cancel_request.cancel_reason
        }
        
        response = requests.post(
            f"{TOSS_API_BASE_URL}/payments/{cancel_request.payment_key}/cancel",
            headers=get_toss_headers(),
            json=cancel_data
        )
        
        if response.status_code != 200:
            error_data = response.json()
            logger.error(f"Toss payment cancel failed: {error_data}")
            raise HTTPException(
                status_code=400,
                detail=f"결제 취소 실패: {error_data.get('message', '알 수 없는 오류')}"
            )
        
        cancel_result = response.json()
        
        # 데이터베이스 업데이트
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 주문 상태 업데이트
        cursor.execute("""
        UPDATE orders 
        SET status = %s, cancel_reason = %s, cancelled_at = %s, updated_at = %s
        WHERE payment_key = %s
        """, (
            'CANCELLED',
            cancel_request.cancel_reason,
            datetime.now(),
            datetime.now(),
            cancel_request.payment_key
        ))
        
        # 재고 복구 또는 참여자 수 감소 로직 필요시 추가
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "payment_key": cancel_request.payment_key,
            "status": "CANCELLED",
            "cancel_result": cancel_result,
            "message": "결제가 성공적으로 취소되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling payment: {e}")
        raise HTTPException(status_code=500, detail=f"결제 취소 중 오류가 발생했습니다: {str(e)}")

@router.get("/orders/{order_id}")
async def get_order_status(order_id: str):
    """주문 상태 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT order_id, order_type, item_id, item_name, customer_name, customer_email,
               total_amount, quantity, status, payment_key, payment_method,
               created_at, payment_approved_at, cancelled_at
        FROM orders 
        WHERE order_id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not order:
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
        
        return {
            "success": True,
            "order": {
                "order_id": order['order_id'],
                "order_type": order['order_type'],
                "item_id": order['item_id'],
                "item_name": order['item_name'],
                "customer_name": order['customer_name'],
                "customer_email": order['customer_email'],
                "total_amount": order['total_amount'],
                "quantity": order['quantity'],
                "status": order['status'],
                "payment_key": order['payment_key'],
                "payment_method": order['payment_method'],
                "created_at": order['created_at'].isoformat() if order['created_at'] else None,
                "payment_approved_at": order['payment_approved_at'].isoformat() if order['payment_approved_at'] else None,
                "cancelled_at": order['cancelled_at'].isoformat() if order['cancelled_at'] else None,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        raise HTTPException(status_code=500, detail=f"주문 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/webhook")
async def payment_webhook(request: Request):
    """토스페이먼츠 웹훅 처리 (GET 방식 테스트용)"""
    return {"message": "Payment webhook endpoint is active"}

@router.post("/webhook") 
async def payment_webhook_post(request: Request):
    """토스페이먼츠 웹훅 처리"""
    try:
        webhook_data = await request.json()
        logger.info(f"Payment webhook received: {webhook_data}")
        
        # 웹훅 데이터 처리 로직
        # 실제 운영 환경에서는 웹훅 서명 검증 필요
        
        return {"success": True, "message": "Webhook processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="웹훅 처리 중 오류가 발생했습니다")
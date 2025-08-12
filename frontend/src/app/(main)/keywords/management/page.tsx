'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  ExternalLink,
  Network,
  Settings,
  ArrowLeft
} from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function KeywordManagementPage() {
  const router = useRouter()

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center gap-4">
        <Button
          onClick={() => router.back()}
          variant="outline"
          size="sm"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          뒤로가기
        </Button>
        <div>
          <h1 className="text-3xl font-bold">키워드 관리</h1>
          <p className="text-muted-foreground mt-2">
            키워드 데이터 관리 - 마이크로서비스 분리 완료
          </p>
        </div>
      </div>

      {/* 서비스 분리 안내 */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Network className="h-5 w-5 text-blue-500" />
            <CardTitle>키워드 관리 서비스 분리 완료</CardTitle>
          </div>
          <CardDescription>
            키워드 관리 기능이 독립적인 마이크로서비스로 분리되었습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              키워드 관리 기능은 성능 최적화를 위해 독립적인 서비스로 분리되었습니다.
              이제 keywords.heal7.com에서 모든 키워드 관련 작업을 수행할 수 있습니다.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-900 mb-2">✅ 완료된 기능</h3>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• 키워드 매트릭스 3D 시각화</li>
                  <li>• 442개 키워드 네트워크 분석</li>
                  <li>• 독립적인 캐싱 시스템</li>
                  <li>• PostgreSQL 직접 연결</li>
                </ul>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">🚀 성능 향상</h3>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• 관리자 대시보드 메모리 절약</li>
                  <li>• three.js 의존성 분리</li>
                  <li>• 독립적인 서비스 최적화</li>
                  <li>• 빌드 시간 단축</li>
                </ul>
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                onClick={() => window.open('https://keywords.heal7.com', '_blank')}
                variant="default"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                키워드 서비스로 이동
              </Button>
              <Button
                onClick={() => router.push('/keywords/matrix')}
                variant="outline"
              >
                <Network className="h-4 w-4 mr-2" />
                매트릭스 보기
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 기술적 세부사항 */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-gray-500" />
            <CardTitle>기술적 세부사항</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-muted-foreground">
            <div>
              <strong>서비스 URL:</strong> keywords.heal7.com (포트 8003)
            </div>
            <div>
              <strong>기술 스택:</strong> Next.js + PostgreSQL + Redis + three.js
            </div>
            <div>
              <strong>데이터:</strong> 442개 키워드, 9개 카테고리, 1247개 연결
            </div>
            <div>
              <strong>성능:</strong> 독립적인 빌드, 캐싱, 메모리 최적화
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
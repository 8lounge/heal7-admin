'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import { 
  Database,
  ExternalLink,
  Network,
  Settings
} from 'lucide-react'

export default function KeywordsPage() {
  const router = useRouter()

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">키워드 관리</h1>
          <p className="text-muted-foreground mt-2">
            HEAL7 키워드 시스템 - 마이크로서비스로 분리됨
          </p>
        </div>
      </div>

      {/* 키워드 서비스 카드들 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* 키워드 매트릭스 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Network className="h-5 w-5 text-blue-500" />
              <CardTitle>키워드 매트릭스</CardTitle>
            </div>
            <CardDescription>
              442개 키워드의 3D 네트워크 시각화
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                키워드 매트릭스는 독립적인 마이크로서비스로 분리되어 
                더 빠르고 안정적으로 동작합니다.
              </p>
              <div className="flex gap-2">
                <Button
                  onClick={() => router.push('/keywords/matrix')}
                  variant="default"
                  size="sm"
                >
                  <Network className="h-4 w-4 mr-2" />
                  매트릭스 보기
                </Button>
                <Button
                  onClick={() => window.open('https://keywords.heal7.com', '_blank')}
                  variant="outline"
                  size="sm"
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  새 창에서 열기
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 키워드 관리 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-green-500" />
              <CardTitle>키워드 관리</CardTitle>
            </div>
            <CardDescription>
              키워드 데이터 추가, 수정, 삭제
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                키워드 관리 기능도 독립 서비스로 분리될 예정입니다.
                현재는 매트릭스 서비스를 통해 확인 가능합니다.
              </p>
              <Button
                onClick={() => router.push('/keywords/management')}
                variant="default"
                size="sm"
              >
                <Settings className="h-4 w-4 mr-2" />
                관리 페이지
              </Button>
            </div>
          </CardContent>
        </Card>

      </div>

      {/* 안내 메시지 */}
      <Card>
        <CardContent className="pt-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Database className="h-5 w-5 text-blue-500 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">
                  키워드 시스템 마이크로서비스화 완료
                </h3>
                <p className="text-sm text-blue-700 mb-2">
                  키워드 관련 기능들이 독립적인 서비스로 분리되어 시스템 성능이 향상되었습니다.
                </p>
                <ul className="text-xs text-blue-600 space-y-1">
                  <li>• <strong>keywords.heal7.com</strong>: 키워드 매트릭스 3D 시각화</li>
                  <li>• <strong>성능 향상</strong>: 관리자 대시보드 메모리 사용량 대폭 절약</li>
                  <li>• <strong>독립 운영</strong>: 각 서비스가 독립적으로 최적화</li>
                  <li>• <strong>안정성 증대</strong>: 서비스별 장애 격리</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
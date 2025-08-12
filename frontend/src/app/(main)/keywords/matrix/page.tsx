'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  ExternalLink,
  Maximize2,
  RefreshCw,
  Network
} from 'lucide-react'

export default function KeywordMatrixPage() {
  const [isFullscreen, setIsFullscreen] = useState(false)
  
  // keywords.heal7.com으로 새 창 열기
  const openInNewWindow = () => {
    window.open('https://keywords.heal7.com', '_blank', 'width=1200,height=800')
  }

  // 전체화면 토글
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">키워드 매트릭스</h1>
          <p className="text-muted-foreground mt-2">
            442개 키워드의 3D 네트워크 시각화 - 독립 서비스로 분리됨
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            onClick={toggleFullscreen}
            variant="outline"
            size="sm"
          >
            <Maximize2 className="h-4 w-4 mr-2" />
            {isFullscreen ? '일반 보기' : '전체 화면'}
          </Button>
          
          <Button
            onClick={openInNewWindow}
            variant="default"
            size="sm"
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            새 창에서 열기
          </Button>
        </div>
      </div>

      {/* 키워드 매트릭스 iframe */}
      <Card className={isFullscreen ? 'fixed inset-0 z-50 rounded-none' : ''}>
        <CardHeader className={isFullscreen ? 'pb-2' : ''}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Network className="h-5 w-5 text-blue-500" />
              <CardTitle>키워드 3D 매트릭스</CardTitle>
            </div>
            
            <div className="text-sm text-muted-foreground">
              서비스: keywords.heal7.com
            </div>
          </div>
          
          {!isFullscreen && (
            <CardDescription>
              키워드 매트릭스는 독립적인 마이크로서비스로 분리되어 더 빠르고 안정적으로 동작합니다.
            </CardDescription>
          )}
        </CardHeader>
        
        <CardContent className="p-0">
          <div className={`relative ${isFullscreen ? 'h-[calc(100vh-8rem)]' : 'h-[600px]'}`}>
            <iframe
              src="https://keywords.heal7.com"
              className="w-full h-full border-0 rounded-lg"
              title="HEAL7 키워드 매트릭스"
              loading="lazy"
              allow="accelerometer; gyroscope"
              sandbox="allow-same-origin allow-scripts allow-forms"
            />
            
            {/* 로딩 오버레이 */}
            <div className="absolute inset-0 bg-white/80 flex items-center justify-center rounded-lg backdrop-blur-sm">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-sm text-muted-foreground">키워드 매트릭스 로딩 중...</p>
                <p className="text-xs text-muted-foreground mt-1">keywords.heal7.com</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 안내 메시지 */}
      {!isFullscreen && (
        <Card>
          <CardContent className="pt-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Network className="h-5 w-5 text-blue-500 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-blue-900 mb-1">
                    키워드 매트릭스 서비스 분리 완료
                  </h3>
                  <p className="text-sm text-blue-700">
                    키워드 매트릭스는 독립적인 마이크로서비스(keywords.heal7.com)로 분리되어
                    더 빠른 성능과 안정성을 제공합니다. 무거운 3D 렌더링 라이브러리가 관리자 
                    대시보드에서 분리되어 전체 시스템이 더 가벼워졌습니다.
                  </p>
                  <ul className="text-xs text-blue-600 mt-2 space-y-1">
                    <li>• three.js 3D 시각화 최적화</li>
                    <li>• 442개 키워드 실시간 네트워크 분석</li>
                    <li>• 독립적인 캐싱 및 성능 최적화</li>
                    <li>• 관리자 대시보드 메모리 사용량 절약</li>
                  </ul>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
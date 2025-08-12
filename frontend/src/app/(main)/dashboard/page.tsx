'use client'

import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Calendar, 
  Users, 
  Database, 
  BarChart3, 
  CheckCircle, 
  AlertCircle,
  TrendingUp,
  Clock,
  Activity,
  Server,
  Cpu,
  Zap,
  Wifi
} from 'lucide-react'

interface ServiceStatus {
  name: string
  status: 'online' | 'offline' | 'warning'
  port: number
  latency: number
}

export default function DashboardPage() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'heal7.com', status: 'online', port: 8000, latency: 45 },
    { name: 'admin.heal7.com', status: 'online', port: 8001, latency: 23 },
    { name: 'marketing.heal7.com', status: 'online', port: 8002, latency: 67 },
    { name: 'test.heal7.com', status: 'online', port: 8003, latency: 38 }
  ])
  
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 18,
    memory: 65,
    disk: 42,
    network: 85
  })
  
  const [realtimeData, setRealtimeData] = useState({
    activeUsers: 234,
    apiCalls: 1892,
    avgResponseTime: 5.4,
    cacheHitRate: 89
  })
  
  // 실시간 데이터 시뮬레이션
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        cpu: Math.min(100, Math.max(10, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.min(100, Math.max(50, prev.memory + (Math.random() - 0.5) * 5)),
        disk: prev.disk,
        network: Math.min(100, Math.max(60, prev.network + (Math.random() - 0.5) * 15))
      }))
      
      setRealtimeData(prev => ({
        activeUsers: Math.max(100, prev.activeUsers + Math.floor((Math.random() - 0.5) * 20)),
        apiCalls: prev.apiCalls + Math.floor(Math.random() * 10),
        avgResponseTime: Math.max(1, prev.avgResponseTime + (Math.random() - 0.5) * 0.5),
        cacheHitRate: Math.round((Math.min(100, Math.max(80, prev.cacheHitRate + (Math.random() - 0.5) * 2))) * 10) / 10
      }))
    }, 3000)
    
    return () => clearInterval(interval)
  }, [])
  
  return (
    <div className="p-6 space-y-6">
      {/* Page Header with Live Status */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">관리자 대시보드</h1>
          <p className="text-gray-600">HEAL7 시스템 현황 및 주요 지표를 실시간으로 모니터링합니다.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1 bg-green-50 border border-green-200 rounded-full">
            <div className="relative">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="absolute top-0 left-0 w-2 h-2 bg-green-500 rounded-full animate-ping"></div>
            </div>
            <span className="text-sm font-medium text-green-700">실시간 모니터링</span>
          </div>
        </div>
      </div>

      {/* Service Status Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-4">
        {services.map((service, index) => (
          <Card key={index} className="overflow-hidden">
            <div className={`h-1 ${service.status === 'online' ? 'bg-green-500' : 'bg-red-500'}`} />
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-sm font-medium">{service.name}</CardTitle>
                  <p className="text-xs text-gray-500 mt-1">포트 {service.port}</p>
                </div>
                <Badge 
                  variant={service.status === 'online' ? 'secondary' : 'destructive'}
                  className={`text-xs ${
                    service.status === 'online' 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {service.status === 'online' ? '정상' : '오프라인'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600">응답속도</span>
                <span className="font-medium">{service.latency}ms</span>
              </div>
              <Progress value={100 - (service.latency / 100) * 100} className="h-1 mt-2" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Real-time Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">실시간 사용자</CardTitle>
            <Activity className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{realtimeData.activeUsers}</div>
            <p className="text-xs text-gray-600">현재 접속 중</p>
            <div className="flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3 text-green-600" />
              <span className="text-xs text-green-600">실시간 업데이트</span>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API 호출</CardTitle>
            <Zap className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{realtimeData.apiCalls.toLocaleString()}</div>
            <p className="text-xs text-gray-600">오늘 총 호출</p>
            <div className="flex items-center gap-1 mt-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
              <span className="text-xs text-gray-600">평균 {realtimeData.avgResponseTime.toFixed(1)}초</span>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">캐시 효율</CardTitle>
            <Database className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{realtimeData.cacheHitRate.toFixed(1)}%</div>
            <p className="text-xs text-gray-600">캐시 적중률</p>
            <Progress value={realtimeData.cacheHitRate} className="h-1 mt-2" />
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">시스템 상태</CardTitle>
            <Server className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">99.9%</div>
            <p className="text-xs text-gray-600">가동 시간</p>
            <div className="flex items-center gap-1 mt-1">
              <CheckCircle className="h-3 w-3 text-green-600" />
              <span className="text-xs text-green-600">모든 서비스 정상</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Resources Monitoring */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-purple-600" />
            시스템 리소스 모니터링
          </CardTitle>
          <CardDescription>
            서버 리소스 사용률을 실시간으로 모니터링합니다.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium flex items-center gap-2">
                <Cpu className="h-4 w-4" />
                CPU 사용률
              </span>
              <span className="text-sm font-bold">{systemMetrics.cpu.toFixed(1)}%</span>
            </div>
            <Progress value={systemMetrics.cpu} className="h-2" />
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium flex items-center gap-2">
                <Server className="h-4 w-4" />
                메모리 사용률
              </span>
              <span className="text-sm font-bold">{systemMetrics.memory.toFixed(1)}%</span>
            </div>
            <Progress value={systemMetrics.memory} className="h-2" />
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium flex items-center gap-2">
                <Server className="h-4 w-4" />
                디스크 사용률
              </span>
              <span className="text-sm font-bold">{systemMetrics.disk}%</span>
            </div>
            <Progress value={systemMetrics.disk} className="h-2" />
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium flex items-center gap-2">
                <Wifi className="h-4 w-4" />
                네트워크 사용률
              </span>
              <span className="text-sm font-bold">{systemMetrics.network.toFixed(1)}%</span>
            </div>
            <Progress value={systemMetrics.network} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity & System Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              최근 활동
            </CardTitle>
            <CardDescription>
              시스템의 최근 활동 내역입니다.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-green-600 mt-2"></div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">사주 분석 완료</p>
                <p className="text-xs text-gray-600">1985-02-24 22:20 생년월일시 분석</p>
                <p className="text-xs text-gray-500">5분 전</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-blue-600 mt-2"></div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">AI 검수 실행</p>
                <p className="text-xs text-gray-600">Gemini 2.0 Flash 모델 검수 완료</p>
                <p className="text-xs text-gray-500">12분 전</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-purple-600 mt-2"></div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">키워드 업데이트</p>
                <p className="text-xs text-gray-600">M-PIS 프레임워크 캐시 갱신</p>
                <p className="text-xs text-gray-500">1시간 전</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-orange-600 mt-2"></div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">데이터베이스 최적화</p>
                <p className="text-xs text-gray-600">PostgreSQL 데드 튜플 정리 완료</p>
                <p className="text-xs text-gray-500">2시간 전</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-purple-600" />
              시스템 정보
            </CardTitle>
            <CardDescription>
              현재 시스템 상태 및 버전 정보입니다.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="font-medium text-gray-900">사주 엔진</p>
                <p className="text-gray-600">v4.0 완전 복구</p>
              </div>
              <div>
                <p className="font-medium text-gray-900">KASI API</p>
                <p className="text-gray-600">100% 정상 연동</p>
              </div>
              <div>
                <p className="font-medium text-gray-900">데이터베이스</p>
                <p className="text-gray-600">PostgreSQL 14</p>
              </div>
              <div>
                <p className="font-medium text-gray-900">캐시 시스템</p>
                <p className="text-gray-600">Redis 6.0</p>
              </div>
              <div>
                <p className="font-medium text-gray-900">AI 모델</p>
                <p className="text-gray-600">3단계 폴백</p>
              </div>
              <div>
                <p className="font-medium text-gray-900">업데이트</p>
                <p className="text-gray-600">2025-08-02</p>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">전체 완성도</span>
                <Badge variant="secondary" className="bg-green-100 text-green-800">100%</Badge>
              </div>
              <div className="mt-2 space-y-2 text-xs text-gray-600">
                <div className="flex justify-between">
                  <span>• 명리학 분석 엔진</span>
                  <span className="text-green-600">완료</span>
                </div>
                <div className="flex justify-between">
                  <span>• M-PIS 진단 프레임워크</span>
                  <span className="text-green-600">완료</span>
                </div>
                <div className="flex justify-between">
                  <span>• AI 검수 시스템</span>
                  <span className="text-green-600">완료</span>
                </div>
                <div className="flex justify-between">
                  <span>• 데이터베이스 최적화</span>
                  <span className="text-green-600">완료</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-orange-600" />
            빠른 작업
          </CardTitle>
          <CardDescription>
            자주 사용하는 관리 기능에 빠르게 접근하세요.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <a href="/saju" className="flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all hover:scale-105 cursor-pointer">
              <Calendar className="h-6 w-6 text-purple-600" />
              <span className="text-sm font-medium">사주 분석</span>
              <Badge variant="secondary" className="text-xs">v4.0</Badge>
            </a>
            
            <a href="/keywords" className="flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all hover:scale-105 cursor-pointer">
              <Database className="h-6 w-6 text-blue-600" />
              <span className="text-sm font-medium">키워드 관리</span>
              <span className="text-xs text-gray-500">442개</span>
            </a>
            
            <a href="/trend-ai" className="flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50 transition-all hover:scale-105 cursor-pointer">
              <TrendingUp className="h-6 w-6 text-yellow-600" />
              <span className="text-sm font-medium">AI 트랜드</span>
              <Badge variant="secondary" className="text-xs bg-yellow-100 text-yellow-700">NEW</Badge>
            </a>
            
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
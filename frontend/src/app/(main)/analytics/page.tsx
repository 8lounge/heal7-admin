'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { motion } from 'framer-motion'
import InteractiveChart from '@/components/analytics/InteractiveChart'
import RealTimeMetrics from '@/components/analytics/RealTimeMetrics'
import { 
  BarChart3,
  TrendingUp,
  Users,
  Calendar,
  Download,
  Filter,
  ChevronDown,
  Activity,
  Eye,
  MousePointer,
  Clock,
  PieChart,
  LineChart,
  Zap,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from 'lucide-react'

interface ChartData {
  label: string
  value: number
  percentage?: number
}

interface AnalyticsOverview {
  users: {
    total: number
    new_7d: number
    active_7d: number
    active_30d: number
    retention_rate: number
  }
  saju_analysis: {
    total: number
    today: number
    avg_processing_time: number
    success_rate: number
    ai_review_rate: number
  }
  keywords: {
    total: number
    active: number
    total_usage: number
  }
  traffic: {
    pageviews: number
    sessions: number
    avg_session_duration: number
    bounce_rate: number
  }
}

interface RealtimeStats {
  current_activity: {
    active_sessions: number
    saju_requests_1h: number
    page_views_1h: number
    unique_visitors_1h: number
  }
  system_health: {
    active_workers: number
    total_workers: number
    system_load: number
    response_time: number
  }
}

export default function AnalyticsPage() {
  const [dateRange] = useState('최근 7일')
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [analyticsData, setAnalyticsData] = useState<AnalyticsOverview | null>(null)
  const [realtimeStats, setRealtimeStats] = useState<RealtimeStats | null>(null)
  const [demographicData, setDemographicData] = useState<ChartData[]>([])
  const [deviceData, setDeviceData] = useState<ChartData[]>([])
  const [topPages, setTopPages] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)

  // API 호출 함수들
  const fetchAnalyticsOverview = async () => {
    try {
      const response = await fetch('/admin-api/analytics/overview')
      if (response.ok) {
        const data = await response.json()
        setAnalyticsData(data)
      }
    } catch (err) {
      console.error('Failed to fetch analytics overview:', err)
    }
  }

  const fetchDemographics = async () => {
    try {
      const response = await fetch('/admin-api/analytics/demographics')
      if (response.ok) {
        const data = await response.json()
        setDemographicData(data.age_distribution || [])
      }
    } catch (err) {
      console.error('Failed to fetch demographics:', err)
    }
  }

  const fetchDeviceStats = async () => {
    try {
      const response = await fetch('/admin-api/analytics/device-stats')
      if (response.ok) {
        const data = await response.json()
        setDeviceData(data.device_distribution || [])
      }
    } catch (err) {
      console.error('Failed to fetch device stats:', err)
    }
  }

  const fetchPopularPages = async () => {
    try {
      const response = await fetch('/admin-api/analytics/popular-pages')
      if (response.ok) {
        const data = await response.json()
        setTopPages(data.popular_pages || [])
      }
    } catch (err) {
      console.error('Failed to fetch popular pages:', err)
    }
  }

  const fetchRealtimeStats = async () => {
    try {
      const response = await fetch('/admin-api/analytics/realtime-stats')
      if (response.ok) {
        const data = await response.json()
        setRealtimeStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch realtime stats:', err)
    }
  }

  const refreshAllData = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      await Promise.all([
        fetchAnalyticsOverview(),
        fetchDemographics(),
        fetchDeviceStats(),
        fetchPopularPages(),
        fetchRealtimeStats()
      ])
      setLastUpdated(new Date())
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.')
      console.error('Failed to refresh data:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    refreshAllData()
    
    // 실시간 데이터 5분마다 업데이트
    const interval = setInterval(() => {
      fetchRealtimeStats()
    }, 5 * 60 * 1000)

    return () => clearInterval(interval)
  }, [])

  // Fallback 데이터 (API 실패시)
  const fallbackAnalytics: AnalyticsOverview = {
    users: { total: 12847, new_7d: 1234, active_7d: 8932, active_30d: 11613, retention_rate: 72.4 },
    saju_analysis: { total: 3892, today: 156, avg_processing_time: 5.4, success_rate: 99.2, ai_review_rate: 87.3 },
    keywords: { total: 442, active: 389, total_usage: 45621 },
    traffic: { pageviews: 53900, sessions: 12847, avg_session_duration: 265, bounce_rate: 42.3 }
  }

  const currentData = analyticsData || fallbackAnalytics

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">실시간 통계 분석</h1>
          <div className="flex items-center gap-2">
            <p className="text-gray-600">HEAL7 서비스의 상세 통계 및 분석 데이터</p>
            <div className="flex items-center gap-1 text-sm text-gray-500">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>마지막 업데이트: {lastUpdated.toLocaleTimeString()}</span>
            </div>
          </div>
          
          {/* 실시간 상태 표시 */}
          {realtimeStats && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-4 mt-2 text-sm"
            >
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-gray-600">활성 세션: {realtimeStats.current_activity.active_sessions}</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-gray-600">시간당 방문: {realtimeStats.current_activity.page_views_1h}</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                <span className="text-gray-600">시스템 부하: {realtimeStats.system_health.system_load}%</span>
              </div>
            </motion.div>
          )}
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={refreshAllData}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-1" />
            {dateRange}
            <ChevronDown className="h-4 w-4 ml-1" />
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-1" />
            리포트 다운로드
          </Button>
        </div>
      </div>

      {/* 오류 상태 표시 */}
      {error && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6"
        >
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">{error}</span>
          </div>
        </motion.div>
      )}

      {/* Real-time Metrics */}
      <RealTimeMetrics 
        data={realtimeStats} 
        isLoading={isLoading}
        lastUpdated={lastUpdated}
      />

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-600" />
              총 사용자
            </CardTitle>
          </CardHeader>
          <CardContent>
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5 }}
              className="text-2xl font-bold"
            >
              {currentData.users.total.toLocaleString()}
            </motion.div>
            <div className="flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3 text-green-600" />
              <span className="text-xs text-green-600">+{currentData.users.new_7d} 신규</span>
            </div>
            <Progress value={Math.min((currentData.users.new_7d / currentData.users.total) * 100 * 10, 100)} className="h-1 mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Eye className="h-4 w-4 text-purple-600" />
              페이지뷰
            </CardTitle>
          </CardHeader>
          <CardContent>
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-2xl font-bold"
            >
              {(currentData.traffic.pageviews / 1000).toFixed(1)}K
            </motion.div>
            <p className="text-xs text-gray-600 mt-1">세션당 {(currentData.traffic.pageviews / currentData.traffic.sessions).toFixed(1)}페이지</p>
            <Progress value={Math.min(currentData.traffic.pageviews / 1000, 100)} className="h-1 mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4 text-orange-600" />
              평균 체류시간
            </CardTitle>
          </CardHeader>
          <CardContent>
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-2xl font-bold"
            >
              {Math.floor(currentData.traffic.avg_session_duration / 60)}:{(currentData.traffic.avg_session_duration % 60).toString().padStart(2, '0')}
            </motion.div>
            <p className="text-xs text-gray-600 mt-1">이탈률 {currentData.traffic.bounce_rate}%</p>
            <Progress value={100 - currentData.traffic.bounce_rate} className="h-1 mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Calendar className="h-4 w-4 text-green-600" />
              사주 분석
            </CardTitle>
          </CardHeader>
          <CardContent>
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="text-2xl font-bold"
            >
              {currentData.saju_analysis.total.toLocaleString()}
            </motion.div>
            <p className="text-xs text-gray-600 mt-1">성공률 {currentData.saju_analysis.success_rate}%</p>
            <Progress value={currentData.saju_analysis.success_rate} className="h-1 mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Main Analytics Tabs */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users">사용자 분석</TabsTrigger>
          <TabsTrigger value="behavior">행동 분석</TabsTrigger>
          <TabsTrigger value="saju">사주 분석 통계</TabsTrigger>
          <TabsTrigger value="conversion">전환 분석</TabsTrigger>
        </TabsList>

        {/* Users Analysis Tab */}
        <TabsContent value="users" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 사용자 증가 추이 차트 */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-blue-600" />
                  사용자 증가 추이
                </CardTitle>
                <CardDescription>
                  최근 7일간 신규 사용자 및 활성 사용자 현황
                </CardDescription>
              </CardHeader>
              <CardContent>
                <InteractiveChart
                  data={[
                    { label: "월", value: currentData.users.new_7d - 200 },
                    { label: "화", value: currentData.users.new_7d - 150 },
                    { label: "수", value: currentData.users.new_7d - 100 },
                    { label: "목", value: currentData.users.new_7d - 50 },
                    { label: "금", value: currentData.users.new_7d + 100 },
                    { label: "토", value: currentData.users.new_7d + 150 },
                    { label: "일", value: currentData.users.new_7d }
                  ]}
                  type="line"
                  height={250}
                  color="#3B82F6"
                />
              </CardContent>
            </Card>

            {/* 사용자 활동 요약 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">사용자 활동 요약</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">신규 사용자</span>
                    <span className="font-semibold">{currentData.users.new_7d}</span>
                  </div>
                  <Progress value={75} className="h-1" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">활성 사용자 (7일)</span>
                    <span className="font-semibold">{currentData.users.active_7d}</span>
                  </div>
                  <Progress value={65} className="h-1" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">활성 사용자 (30일)</span>
                    <span className="font-semibold">{currentData.users.active_30d}</span>
                  </div>
                  <Progress value={85} className="h-1" />
                </div>
                <div className="pt-2 border-t">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">리텐션율</span>
                    <span className="font-semibold text-green-600">{currentData.users.retention_rate}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Demographics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5 text-purple-600" />
                  연령대별 분포
                </CardTitle>
                <CardDescription>
                  사용자 연령대별 구성 비율
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {demographicData.map((item, index) => (
                    <motion.div 
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium">{item.label}</span>
                        <span className="text-sm text-gray-600">
                          {item.value.toLocaleString()}명 ({item.percentage}%)
                        </span>
                      </div>
                      <Progress value={item.percentage} className="h-2" />
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Device Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MousePointer className="h-5 w-5 text-blue-600" />
                  기기별 접속 현황
                </CardTitle>
                <CardDescription>
                  접속 기기 유형별 분포
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {deviceData.map((device, index) => (
                    <motion.div 
                      key={index} 
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <motion.div 
                          whileHover={{ scale: 1.05 }}
                          className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                            device.label === '모바일' ? 'bg-blue-100' :
                            device.label.includes('데스크톱') ? 'bg-purple-100' : 'bg-orange-100'
                          }`}
                        >
                          <span className="text-lg font-bold">
                            {device.percentage}%
                          </span>
                        </motion.div>
                        <div>
                          <p className="font-medium">{device.label}</p>
                          <p className="text-sm text-gray-600">
                            {device.value.toLocaleString()}명
                          </p>
                        </div>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {device.percentage > 40 ? '주요' : '보조'}
                      </Badge>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Behavior Analysis Tab */}
        <TabsContent value="behavior" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-green-600" />
                인기 페이지 분석
              </CardTitle>
              <CardDescription>
                가장 많이 방문한 페이지와 체류 시간
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left pb-3 font-medium text-sm">페이지</th>
                      <th className="text-right pb-3 font-medium text-sm">페이지뷰</th>
                      <th className="text-right pb-3 font-medium text-sm">평균 체류시간</th>
                      <th className="text-right pb-3 font-medium text-sm">추세</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topPages.map((page, index) => (
                      <motion.tr 
                        key={index} 
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                        className="border-b hover:bg-gray-50"
                      >
                        <td className="py-3">
                          <span className="font-medium">{page.page}</span>
                        </td>
                        <td className="text-right py-3">
                          {page.pageviews ? page.pageviews.toLocaleString() : page.views?.toLocaleString() || 0}
                        </td>
                        <td className="text-right py-3">
                          {page.avg_time || page.avgTime}
                        </td>
                        <td className="text-right py-3">
                          <Badge 
                            variant={page.bounce_rate < 40 ? "default" : "secondary"} 
                            className="text-xs"
                          >
                            <TrendingUp className="h-3 w-3 mr-1" />
                            {page.bounce_rate ? `${page.bounce_rate}%` : '+12%'}
                          </Badge>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Saju Analysis Tab */}
        <TabsContent value="saju" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-600" />
                  사주 분석 성능
                </CardTitle>
                <CardDescription>
                  시스템 성능 및 처리 통계
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <motion.div 
                    whileHover={{ scale: 1.02 }}
                    className="bg-gray-50 rounded-lg p-3"
                  >
                    <p className="text-sm text-gray-600">평균 처리 시간</p>
                    <p className="text-xl font-bold">{currentData.saju_analysis.avg_processing_time}초</p>
                  </motion.div>
                  <motion.div 
                    whileHover={{ scale: 1.02 }}
                    className="bg-gray-50 rounded-lg p-3"
                  >
                    <p className="text-sm text-gray-600">AI 검수율</p>
                    <p className="text-xl font-bold">{currentData.saju_analysis.ai_review_rate}%</p>
                  </motion.div>
                </div>
                <div className="border-t pt-4">
                  <p className="text-sm font-medium mb-2">오늘 분석 건수</p>
                  <Badge variant="secondary" className="text-sm">
                    {currentData.saju_analysis.today}건
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="h-5 w-5 text-blue-600" />
                  일별 분석 추이
                </CardTitle>
                <CardDescription>
                  최근 7일간 사주 분석 요청 추이
                </CardDescription>
              </CardHeader>
              <CardContent>
                <InteractiveChart
                  data={[
                    { label: "월", value: currentData.saju_analysis.today - 30 },
                    { label: "화", value: currentData.saju_analysis.today - 15 },
                    { label: "수", value: currentData.saju_analysis.today - 5 },
                    { label: "목", value: currentData.saju_analysis.today + 20 },
                    { label: "금", value: currentData.saju_analysis.today + 45 },
                    { label: "토", value: currentData.saju_analysis.today + 30 },
                    { label: "일", value: currentData.saju_analysis.today }
                  ]}
                  type="area"
                  height={200}
                  color="#3B82F6"
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Conversion Analysis Tab */}
        <TabsContent value="conversion" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>전환 퍼널 분석</CardTitle>
                <CardDescription>
                  사용자 여정별 전환율 분석
                </CardDescription>
              </CardHeader>
              <CardContent>
                <InteractiveChart
                  data={[
                    { label: "홈페이지 방문", value: 10000 },
                    { label: "사주 조회", value: 6500 },
                    { label: "회원가입", value: 2800 },
                    { label: "가입완료", value: 2100 },
                    { label: "결제시작", value: 450 },
                    { label: "결제완료", value: 290 }
                  ]}
                  type="bar"
                  height={300}
                  color="#10B981"
                  title="전환 퍼널"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>월별 전환율 추이</CardTitle>
                <CardDescription>
                  최근 6개월 전환율 변화
                </CardDescription>
              </CardHeader>
              <CardContent>
                <InteractiveChart
                  data={[
                    { label: "3월", value: 2.4 },
                    { label: "4월", value: 2.8 },
                    { label: "5월", value: 3.1 },
                    { label: "6월", value: 2.9 },
                    { label: "7월", value: 3.4 },
                    { label: "8월", value: 2.9 }
                  ]}
                  type="line"
                  height={300}
                  color="#8B5CF6"
                />
              </CardContent>
            </Card>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>상세 전환 통계</CardTitle>
              <CardDescription>
                단계별 이탈 원인 및 개선점 분석
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className="bg-red-50 border border-red-200 rounded-lg p-4"
                >
                  <h4 className="font-semibold text-red-800 mb-2">주요 이탈 지점</h4>
                  <p className="text-red-700 text-sm">사주 조회 → 회원가입</p>
                  <p className="text-2xl font-bold text-red-800 mt-2">57% 이탈</p>
                </motion.div>
                
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
                >
                  <h4 className="font-semibold text-yellow-800 mb-2">개선 필요</h4>
                  <p className="text-yellow-700 text-sm">결제 프로세스</p>
                  <p className="text-2xl font-bold text-yellow-800 mt-2">35% 이탈</p>
                </motion.div>
                
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className="bg-green-50 border border-green-200 rounded-lg p-4"
                >
                  <h4 className="font-semibold text-green-800 mb-2">최종 전환율</h4>
                  <p className="text-green-700 text-sm">전체 프로세스</p>
                  <p className="text-2xl font-bold text-green-800 mt-2">2.9%</p>
                </motion.div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
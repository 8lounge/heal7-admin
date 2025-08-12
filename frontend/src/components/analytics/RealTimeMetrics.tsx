'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Activity, 
  Users, 
  Eye, 
  Zap, 
  Server,
  Clock
} from 'lucide-react'

interface RealTimeData {
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

interface MetricCardProps {
  title: string
  value: number | string
  unit?: string
  icon: React.ReactNode
  color: string
  trend?: number
  isLoading?: boolean
}

function MetricCard({ title, value, unit = '', icon, color, trend, isLoading }: MetricCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card className="border-l-4 hover:shadow-md transition-shadow" style={{ borderLeftColor: color }}>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2 text-gray-600">
            {icon}
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-baseline gap-1">
            {isLoading ? (
              <div className="w-12 h-8 bg-gray-200 animate-pulse rounded"></div>
            ) : (
              <motion.span 
                key={value}
                initial={{ scale: 1.1 }}
                animate={{ scale: 1 }}
                className="text-2xl font-bold"
                style={{ color }}
              >
                {typeof value === 'number' ? value.toLocaleString() : value}
              </motion.span>
            )}
            <span className="text-sm text-gray-500">{unit}</span>
          </div>
          
          {trend !== undefined && (
            <motion.div 
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className={`text-xs mt-1 ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}
            >
              {trend >= 0 ? '+' : ''}{trend.toFixed(1)}% (1시간 전 대비)
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

interface RealTimeMetricsProps {
  data?: RealTimeData | null
  isLoading?: boolean
  lastUpdated?: Date
}

export default function RealTimeMetrics({ data, isLoading = false, lastUpdated }: RealTimeMetricsProps) {
  const [animationKey, setAnimationKey] = useState(0)

  useEffect(() => {
    if (data) {
      setAnimationKey(prev => prev + 1)
    }
  }, [data])

  if (!data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/3"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const metrics = [
    {
      title: '활성 세션',
      value: data.current_activity.active_sessions,
      icon: <Users className="h-4 w-4" />,
      color: '#3B82F6',
      trend: Math.random() * 20 - 10 // 임시 트렌드 데이터
    },
    {
      title: '시간당 페이지뷰',
      value: data.current_activity.page_views_1h,
      icon: <Eye className="h-4 w-4" />,
      color: '#8B5CF6',
      trend: Math.random() * 15 - 5
    },
    {
      title: '명리학 분석',
      value: data.current_activity.saju_requests_1h,
      unit: '/h',
      icon: <Zap className="h-4 w-4" />,
      color: '#EF4444',
      trend: Math.random() * 25 - 12
    },
    {
      title: '순 방문자',
      value: data.current_activity.unique_visitors_1h,
      icon: <Activity className="h-4 w-4" />,
      color: '#10B981',
      trend: Math.random() * 18 - 8
    },
    {
      title: '시스템 부하',
      value: data.system_health.system_load,
      unit: '%',
      icon: <Server className="h-4 w-4" />,
      color: data.system_health.system_load > 80 ? '#EF4444' : data.system_health.system_load > 60 ? '#F59E0B' : '#10B981'
    },
    {
      title: '응답시간',
      value: data.system_health.response_time,
      unit: 'ms',
      icon: <Clock className="h-4 w-4" />,
      color: data.system_health.response_time > 500 ? '#EF4444' : data.system_health.response_time > 200 ? '#F59E0B' : '#10B981'
    }
  ]

  return (
    <div className="space-y-4">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-gray-900">실시간 메트릭</h2>
          <div className="flex items-center gap-1">
            <motion.div 
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-2 h-2 bg-green-400 rounded-full"
            />
            <span className="text-sm text-gray-500">라이브</span>
          </div>
        </div>
        
        {lastUpdated && (
          <div className="text-sm text-gray-500">
            마지막 업데이트: {lastUpdated.toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* 메트릭 카드들 */}
      <motion.div 
        key={animationKey}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4"
      >
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <MetricCard
              title={metric.title}
              value={metric.value}
              unit={metric.unit}
              icon={metric.icon}
              color={metric.color}
              trend={metric.trend}
              isLoading={isLoading}
            />
          </motion.div>
        ))}
      </motion.div>

      {/* 시스템 상태 요약 */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="bg-gray-50 rounded-lg p-4"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${
              data.system_health.active_workers === data.system_health.total_workers 
                ? 'bg-green-400' 
                : 'bg-yellow-400'
            }`}></div>
            <span className="text-sm font-medium">
              워커 시스템: {data.system_health.active_workers}/{data.system_health.total_workers} 활성
            </span>
          </div>
          
          <div className="text-sm text-gray-600">
            전체 시스템 상태: {
              data.system_health.system_load < 60 && data.system_health.response_time < 200
                ? '양호' 
                : data.system_health.system_load < 80 && data.system_health.response_time < 500
                ? '보통'
                : '주의'
            }
          </div>
        </div>
      </motion.div>
    </div>
  )
}
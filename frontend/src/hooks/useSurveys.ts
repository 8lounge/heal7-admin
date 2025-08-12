'use client'

import { useState, useEffect, useCallback } from 'react'

export interface SurveyTemplate {
  id: number
  name: string
  description: string
  category: 'mpis' | 'saju_psychology' | 'custom'
  status: 'active' | 'draft' | 'closed'
  responses: number
  created: string
  completion: number
  is_adaptive: boolean
  max_questions: number
  min_completion_rate: number
  target_keywords: number[]
  mpis_weights: Record<string, number>
}

export interface SurveyStats {
  total_surveys: number
  total_responses: number
  average_completion: number
  active_surveys: number
  weekly_growth: number
}

interface UseSurveysReturn {
  surveys: SurveyTemplate[]
  stats: SurveyStats | null
  isLoading: boolean
  error: string | null
  fetchSurveys: () => Promise<void>
  fetchStats: () => Promise<void>
  createSurvey: (surveyData: any) => Promise<boolean>
  updateSurvey: (id: number, surveyData: any) => Promise<boolean>
  deleteSurvey: (id: number) => Promise<boolean>
}

export function useSurveys(): UseSurveysReturn {
  const [surveys, setSurveys] = useState<SurveyTemplate[]>([])
  const [stats, setStats] = useState<SurveyStats | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchSurveys = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch('/admin-api/surveys/templates?limit=100')
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '설문 목록을 불러오는데 실패했습니다')
      }

      const result = await response.json()
      
      if (result.success) {
        // 백엔드 데이터를 프론트엔드 형식으로 변환
        const formattedSurveys: SurveyTemplate[] = result.data.templates.map((template: any) => ({
          id: template.id,
          name: template.name,
          description: template.description || '',
          category: template.category,
          status: template.is_active ? 'active' : 'draft',
          responses: template.total_responses || 0,
          created: template.created_at ? new Date(template.created_at).toISOString().split('T')[0] : '',
          completion: template.average_completion_rate || 0,
          is_adaptive: template.is_adaptive,
          max_questions: template.max_questions,
          min_completion_rate: template.min_completion_rate,
          target_keywords: template.target_keywords || [],
          mpis_weights: template.mpis_weights || {}
        }))
        
        setSurveys(formattedSurveys)
      } else {
        throw new Error(result.message || '설문 목록을 불러오는데 실패했습니다')
      }
    } catch (err) {
      console.error('설문 목록 조회 오류:', err)
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const fetchStats = useCallback(async () => {
    try {
      setError(null)

      const response = await fetch('/admin-api/surveys/dashboard/stats?period=week')
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '통계를 불러오는데 실패했습니다')
      }

      const result = await response.json()
      
      if (result.success) {
        const statsData = result.data.statistics
        const formattedStats: SurveyStats = {
          total_surveys: statsData.total_templates || 0,
          total_responses: statsData.total_responses || 0,
          average_completion: statsData.average_completion_rate || 0,
          active_surveys: statsData.active_templates || 0,
          weekly_growth: statsData.weekly_growth_rate || 0
        }
        
        setStats(formattedStats)
      } else {
        throw new Error(result.message || '통계를 불러오는데 실패했습니다')
      }
    } catch (err) {
      console.error('통계 조회 오류:', err)
      setError(err instanceof Error ? err.message : '통계 조회에 실패했습니다')
    }
  }, [])

  const createSurvey = useCallback(async (surveyData: any): Promise<boolean> => {
    try {
      setError(null)

      const response = await fetch('/admin-api/surveys/templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(surveyData)
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '설문 생성에 실패했습니다')
      }

      const result = await response.json()
      
      if (result.success) {
        // 성공 시 목록 새로고침
        await fetchSurveys()
        return true
      } else {
        throw new Error(result.message || '설문 생성에 실패했습니다')
      }
    } catch (err) {
      console.error('설문 생성 오류:', err)
      setError(err instanceof Error ? err.message : '설문 생성에 실패했습니다')
      return false
    }
  }, [fetchSurveys])

  const updateSurvey = useCallback(async (id: number, surveyData: any): Promise<boolean> => {
    try {
      setError(null)

      const response = await fetch(`/admin-api/surveys/templates/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(surveyData)
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '설문 수정에 실패했습니다')
      }

      const result = await response.json()
      
      if (result.success) {
        // 성공 시 목록 새로고침
        await fetchSurveys()
        return true
      } else {
        throw new Error(result.message || '설문 수정에 실패했습니다')
      }
    } catch (err) {
      console.error('설문 수정 오류:', err)
      setError(err instanceof Error ? err.message : '설문 수정에 실패했습니다')
      return false
    }
  }, [fetchSurveys])

  const deleteSurvey = useCallback(async (id: number): Promise<boolean> => {
    try {
      setError(null)

      const response = await fetch(`/admin-api/surveys/templates/${id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '설문 삭제에 실패했습니다')
      }

      const result = await response.json()
      
      if (result.success) {
        // 성공 시 목록 새로고침
        await fetchSurveys()
        return true
      } else {
        throw new Error(result.message || '설문 삭제에 실패했습니다')
      }
    } catch (err) {
      console.error('설문 삭제 오류:', err)
      setError(err instanceof Error ? err.message : '설문 삭제에 실패했습니다')
      return false
    }
  }, [fetchSurveys])

  // 컴포넌트 마운트 시 데이터 로드
  useEffect(() => {
    fetchSurveys()
    fetchStats()
  }, [fetchSurveys, fetchStats])

  return {
    surveys,
    stats,
    isLoading,
    error,
    fetchSurveys,
    fetchStats,
    createSurvey,
    updateSurvey,
    deleteSurvey
  }
}
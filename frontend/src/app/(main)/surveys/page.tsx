'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  FileQuestion,
  Plus,
  BarChart3,
  Users,
  Eye,
  Edit,
  TrendingUp,
  Clock,
  Loader2,
  AlertCircle,
  Trash2,
  RefreshCw
} from 'lucide-react'
import { toast } from 'sonner'
import CreateSurveyModal from '@/components/surveys/CreateSurveyModal'
import { useSurveys } from '@/hooks/useSurveys'

export default function SurveysPage() {
  const {
    surveys,
    stats,
    isLoading,
    error,
    fetchSurveys,
    deleteSurvey
  } = useSurveys()
  
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-700'
      case 'draft': return 'bg-gray-100 text-gray-700'
      case 'closed': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const handleDeleteSurvey = async (id: number, name: string) => {
    if (!confirm(`"${name}" 설문을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`)) {
      return
    }

    setDeletingId(id)
    try {
      const success = await deleteSurvey(id)
      if (success) {
        toast.success('설문이 성공적으로 삭제되었습니다')
      }
    } catch (error) {
      toast.error('설문 삭제에 실패했습니다')
    } finally {
      setDeletingId(null)
    }
  }

  const handleViewResults = (survey: any) => {
    toast.info(`${survey.name} 결과 보기 기능은 개발 중입니다`)
  }

  const handleEditSurvey = (survey: any) => {
    toast.info(`${survey.name} 편집 기능은 개발 중입니다`)
  }

  const handleRefresh = () => {
    fetchSurveys()
    toast.success('설문 목록을 새로고침했습니다')
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">설문 관리</h1>
          <p className="text-gray-600">사용자 설문 및 피드백 관리 시스템</p>
        </div>
        <div className="flex gap-2">
          <Button 
            size="sm" 
            variant="outline"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          <CreateSurveyModal onSurveyCreated={fetchSurveys}>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-1" />
              새 설문 만들기
            </Button>
          </CreateSurveyModal>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <FileQuestion className="h-4 w-4 text-blue-600" />
              총 설문
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-gray-500">로딩 중...</span>
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{stats?.total_surveys || surveys.length}</div>
                <p className="text-xs text-gray-600 mt-1">활성 설문 포함</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="h-4 w-4 text-green-600" />
              총 응답
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-gray-500">로딩 중...</span>
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {(stats?.total_responses || surveys.reduce((sum, s) => sum + s.responses, 0)).toLocaleString()}
                </div>
                <div className="flex items-center gap-1 mt-1">
                  <TrendingUp className="h-3 w-3 text-green-600" />
                  <span className="text-xs text-green-600">
                    {stats?.weekly_growth ? `+${stats.weekly_growth.toFixed(1)}%` : '+12%'} 이번 주
                  </span>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-purple-600" />
              평균 완료율
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-gray-500">로딩 중...</span>
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {stats?.average_completion 
                    ? `${stats.average_completion.toFixed(1)}%`
                    : surveys.length > 0 
                      ? `${(surveys.reduce((sum, s) => sum + s.completion, 0) / surveys.length).toFixed(1)}%`
                      : '0%'
                  }
                </div>
                <p className="text-xs text-gray-600 mt-1">설문별 평균</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4 text-orange-600" />
              활성 설문
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-gray-500">로딩 중...</span>
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {stats?.active_surveys || surveys.filter(s => s.status === 'active').length}
                </div>
                <p className="text-xs text-gray-600 mt-1">현재 진행 중</p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Surveys List */}
      <Card>
        <CardHeader>
          <CardTitle>설문 목록</CardTitle>
          <CardDescription>
            생성된 설문들을 관리하고 결과를 확인할 수 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center gap-2">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>설문 목록을 불러오는 중...</span>
              </div>
            </div>
          ) : surveys.length === 0 ? (
            <div className="text-center py-8">
              <FileQuestion className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">설문이 없습니다</h3>
              <p className="text-gray-600 mb-4">첫 번째 설문 템플릿을 만들어보세요</p>
              <CreateSurveyModal onSurveyCreated={fetchSurveys}>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  새 설문 만들기
                </Button>
              </CreateSurveyModal>
            </div>
          ) : (
            <div className="space-y-4">
              {surveys.map((survey) => (
                <div key={survey.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium text-lg">{survey.name}</h3>
                        <Badge variant="secondary" className={getStatusColor(survey.status)}>
                          {survey.status === 'active' ? '활성' : 
                           survey.status === 'draft' ? '초안' : '종료'}
                        </Badge>
                        {survey.category && (
                          <Badge variant="outline" className="text-xs">
                            {survey.category === 'mpis' ? 'M-PIS' :
                             survey.category === 'saju_psychology' ? '사주 심리' : '커스텀'}
                          </Badge>
                        )}
                      </div>
                      
                      {survey.description && (
                        <p className="text-sm text-gray-600 mb-3">{survey.description}</p>
                      )}
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">응답 수</p>
                          <p className="font-medium">{survey.responses.toLocaleString()}개</p>
                        </div>
                        <div>
                          <p className="text-gray-500">완료율</p>
                          <p className="font-medium">{survey.completion.toFixed(1)}%</p>
                        </div>
                        <div>
                          <p className="text-gray-500">생성일</p>
                          <p className="font-medium">{survey.created || '-'}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">최대 질문</p>
                          <p className="font-medium">{survey.max_questions || 20}개</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 ml-4">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleViewResults(survey)}
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        결과 보기
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEditSurvey(survey)}
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        편집
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteSurvey(survey.id, survey.name)}
                        disabled={deletingId === survey.id}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        {deletingId === survey.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CreateSurveyModal onSurveyCreated={fetchSurveys}>
          <Card className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardContent className="pt-6">
              <div className="text-center">
                <FileQuestion className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <h3 className="font-medium mb-2">새 설문 만들기</h3>
                <p className="text-sm text-gray-600">처음부터 새로운 설문을 생성합니다</p>
              </div>
            </CardContent>
          </Card>
        </CreateSurveyModal>

        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => toast.info('분석 리포트 기능은 개발 중입니다')}
        >
          <CardContent className="pt-6">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 text-green-600 mx-auto mb-4" />
              <h3 className="font-medium mb-2">분석 리포트</h3>
              <p className="text-sm text-gray-600">설문 결과를 종합 분석합니다</p>
            </div>
          </CardContent>
        </Card>

        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => toast.info('응답자 관리 기능은 개발 중입니다')}
        >
          <CardContent className="pt-6">
            <div className="text-center">
              <Users className="h-12 w-12 text-purple-600 mx-auto mb-4" />
              <h3 className="font-medium mb-2">응답자 관리</h3>
              <p className="text-sm text-gray-600">설문 응답자를 관리합니다</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
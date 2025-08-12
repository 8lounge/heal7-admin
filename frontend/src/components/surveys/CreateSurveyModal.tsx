'use client'

import React, { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, FileQuestion, Target, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'

interface CreateSurveyModalProps {
  children: React.ReactNode
  onSurveyCreated?: () => void
}

interface SurveyTemplateForm {
  name: string
  description: string
  category: 'basic' | 'advanced' | 'custom'
  max_questions: number
}

const SURVEY_TYPES = [
  {
    value: 'basic',
    name: '기본 설문',
    description: '간단한 설문 템플릿',
    icon: FileQuestion,
    color: 'bg-blue-100 text-blue-700'
  },
  {
    value: 'advanced',
    name: '고급 설문',
    description: '상세한 설문 템플릿',
    icon: Target,
    color: 'bg-green-100 text-green-700'
  },
  {
    value: 'custom',
    name: '사용자 정의',
    description: '맞춤형 설문 템플릿',
    icon: CheckCircle,
    color: 'bg-purple-100 text-purple-700'
  }
]

export default function CreateSurveyModal({ children, onSurveyCreated }: CreateSurveyModalProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState<'select' | 'configure' | 'creating'>('select')
  const [selectedType, setSelectedType] = useState<string>('')
  const [formData, setFormData] = useState<SurveyTemplateForm>({
    name: '',
    description: '',
    category: 'basic',
    max_questions: 10
  })

  const handleClose = () => {
    setOpen(false)
    setStep('select')
    setSelectedType('')
    setFormData({
      name: '',
      description: '',
      category: 'basic',
      max_questions: 10
    })
  }

  const handleTypeSelect = (typeValue: string) => {
    setSelectedType(typeValue)
    const selectedSurvey = SURVEY_TYPES.find(t => t.value === typeValue)
    if (selectedSurvey) {
      setFormData(prev => ({
        ...prev,
        category: typeValue as any,
        name: selectedSurvey.name
      }))
      setStep('configure')
    }
  }

  const handleCreateSurvey = async () => {
    if (!formData.name.trim()) {
      toast.error('설문 이름을 입력해주세요')
      return
    }

    setLoading(true)
    setStep('creating')

    try {
      const response = await fetch('/admin-api/surveys/templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error('설문 생성 실패')
      }

      const result = await response.json()
      toast.success('설문이 성공적으로 생성되었습니다!')
      onSurveyCreated?.()
      handleClose()
    } catch (error) {
      console.error('설문 생성 오류:', error)
      toast.error('설문 생성 중 오류가 발생했습니다')
      setStep('configure')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileQuestion className="h-5 w-5" />
            새 설문 만들기
          </DialogTitle>
          <DialogDescription>
            설문 템플릿을 선택하고 설정하세요.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {step === 'select' && (
            <div className="space-y-4">
              <h3 className="font-medium">설문 유형 선택</h3>
              <div className="grid grid-cols-1 gap-3">
                {SURVEY_TYPES.map((surveyType) => {
                  const IconComponent = surveyType.icon
                  return (
                    <Card 
                      key={surveyType.value}
                      className="cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => handleTypeSelect(surveyType.value)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <div className={`p-2 rounded-lg ${surveyType.color}`}>
                            <IconComponent className="h-4 w-4" />
                          </div>
                          <div className="flex-1">
                            <h4 className="font-medium">{surveyType.name}</h4>
                            <p className="text-sm text-muted-foreground mt-1">
                              {surveyType.description}
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </div>
          )}

          {step === 'configure' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">설문 설정</h3>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setStep('select')}
                >
                  뒤로
                </Button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">설문 이름</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({...prev, name: e.target.value}))}
                    placeholder="설문 이름을 입력하세요"
                  />
                </div>
                
                <div>
                  <Label htmlFor="description">설명</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({...prev, description: e.target.value}))}
                    placeholder="설문 설명을 입력하세요"
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="maxQuestions">최대 문항 수</Label>
                  <Input
                    id="maxQuestions"
                    type="number"
                    min="5"
                    max="50"
                    value={formData.max_questions}
                    onChange={(e) => setFormData(prev => ({...prev, max_questions: parseInt(e.target.value) || 10}))}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={handleClose}>
                  취소
                </Button>
                <Button onClick={handleCreateSurvey} disabled={loading}>
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  설문 생성
                </Button>
              </div>
            </div>
          )}

          {step === 'creating' && (
            <div className="space-y-4 text-center">
              <div className="flex justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
              <div>
                <h3 className="font-medium">설문을 생성하고 있습니다...</h3>
                <p className="text-sm text-muted-foreground">잠시만 기다려주세요.</p>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
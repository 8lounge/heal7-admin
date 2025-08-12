'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Settings,
  Database,
  Bell,
  Shield,
  Globe,
  Save,
  RefreshCw
} from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    siteName: 'HEAL7',
    siteDescription: 'AI 기반 명리학 및 성향 분석 서비스',
    maintenanceMode: false,
    enableNotifications: true,
    enableAnalytics: true,
    cacheEnabled: true,
    debugMode: false,
    maxApiCalls: 1000,
    sessionTimeout: 3600
  })

  const handleSave = () => {
    // 저장 로직
    console.log('Settings saved:', settings)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">시스템 설정</h1>
          <p className="text-gray-600">전체 시스템 구성 및 설정 관리</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-1" />
            초기화
          </Button>
          <Button size="sm" onClick={handleSave}>
            <Save className="h-4 w-4 mr-1" />
            저장
          </Button>
        </div>
      </div>

      {/* Settings Tabs */}
      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general">일반 설정</TabsTrigger>
          <TabsTrigger value="system">시스템</TabsTrigger>
          <TabsTrigger value="api">API 설정</TabsTrigger>
          <TabsTrigger value="notifications">알림</TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-blue-600" />
                사이트 기본 정보
              </CardTitle>
              <CardDescription>
                웹사이트의 기본 정보를 설정합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">사이트 이름</label>
                <Input
                  value={settings.siteName}
                  onChange={(e) => setSettings({...settings, siteName: e.target.value})}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">사이트 설명</label>
                <Input
                  value={settings.siteDescription}
                  onChange={(e) => setSettings({...settings, siteDescription: e.target.value})}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">유지보수 모드</label>
                  <p className="text-xs text-gray-500">활성화 시 사이트에 유지보수 메시지가 표시됩니다</p>
                </div>
                <Switch
                  checked={settings.maintenanceMode}
                  onCheckedChange={(checked) => setSettings({...settings, maintenanceMode: checked})}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* System Settings */}
        <TabsContent value="system" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-purple-600" />
                시스템 성능
              </CardTitle>
              <CardDescription>
                시스템 성능 및 캐시 설정
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">캐시 활성화</label>
                  <p className="text-xs text-gray-500">Redis 캐시를 사용하여 성능을 향상시킵니다</p>
                </div>
                <Switch
                  checked={settings.cacheEnabled}
                  onCheckedChange={(checked) => setSettings({...settings, cacheEnabled: checked})}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">디버그 모드</label>
                  <p className="text-xs text-gray-500">개발 환경에서만 활성화하세요</p>
                </div>
                <Switch
                  checked={settings.debugMode}
                  onCheckedChange={(checked) => setSettings({...settings, debugMode: checked})}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">세션 타임아웃 (초)</label>
                <Input
                  type="number"
                  value={settings.sessionTimeout}
                  onChange={(e) => setSettings({...settings, sessionTimeout: parseInt(e.target.value)})}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Settings */}
        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-green-600" />
                API 제한
              </CardTitle>
              <CardDescription>
                API 호출 제한 및 보안 설정
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">최대 API 호출 수 (시간당)</label>
                <Input
                  type="number"
                  value={settings.maxApiCalls}
                  onChange={(e) => setSettings({...settings, maxApiCalls: parseInt(e.target.value)})}
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium">KASI API</p>
                  <p className="text-xs text-green-600">✓ 연결됨</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Gemini API</p>
                  <p className="text-xs text-green-600">✓ 연결됨</p>
                </div>
                <div>
                  <p className="text-sm font-medium">GPT API</p>
                  <p className="text-xs text-green-600">✓ 연결됨</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Claude API</p>
                  <p className="text-xs text-green-600">✓ 연결됨</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications */}
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-orange-600" />
                알림 설정
              </CardTitle>
              <CardDescription>
                시스템 알림 및 이메일 설정
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">이메일 알림</label>
                  <p className="text-xs text-gray-500">중요한 이벤트 발생 시 이메일을 발송합니다</p>
                </div>
                <Switch
                  checked={settings.enableNotifications}
                  onCheckedChange={(checked) => setSettings({...settings, enableNotifications: checked})}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">분석 데이터 수집</label>
                  <p className="text-xs text-gray-500">서비스 개선을 위한 사용 통계를 수집합니다</p>
                </div>
                <Switch
                  checked={settings.enableAnalytics}
                  onCheckedChange={(checked) => setSettings({...settings, enableAnalytics: checked})}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-red-600" />
            시스템 상태
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-green-600 font-bold text-lg">99.9%</div>
              <div className="text-sm text-gray-600">가동 시간</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-blue-600 font-bold text-lg">442</div>
              <div className="text-sm text-gray-600">활성 키워드</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-purple-600 font-bold text-lg">3,067</div>
              <div className="text-sm text-gray-600">네트워크 연결</div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-orange-600 font-bold text-lg">v4.0</div>
              <div className="text-sm text-gray-600">사주 엔진</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
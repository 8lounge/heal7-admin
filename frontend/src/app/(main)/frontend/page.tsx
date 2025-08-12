'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Layout,
  Monitor,
  Smartphone,
  Globe,
  Settings,
  Eye,
  RefreshCw,
  ExternalLink,
  ShoppingCart,
  Users,
  GraduationCap,
  BarChart3,
  Plus,
  Edit,
  Trash2
} from 'lucide-react'

export default function FrontendPage() {
  const [services] = React.useState([
    {
      id: '1',
      name: 'heal7.com',
      description: '메인 서비스 (React 19 + Vite)',
      status: 'active',
      port: 8000,
      version: 'v2.1.0',
      lastDeploy: '2025-08-04 01:00'
    },
    {
      id: '2',
      name: 'admin.heal7.com',
      description: '관리자 대시보드 (Next.js 14)',
      status: 'active',
      port: 80,
      version: 'v1.0.0',
      lastDeploy: '2025-08-04 01:00'
    },
    {
      id: '3',
      name: 'marketing.heal7.com',
      description: '마케팅 서비스',
      status: 'active',
      port: 8002,
      version: 'v1.2.0',
      lastDeploy: '2025-08-01 09:15'
    }
  ])

  // 아카데미 데이터
  const [academyPrograms] = useState([
    {
      id: 1,
      name: '사주 명리학 기초 과정',
      description: 'KASI API 기반 전통 명리학 학습',
      students: 28,
      duration: '8주',
      completionRate: 85,
      status: 'active'
    },
    {
      id: 2,
      name: 'M-PIS 성향 분석 전문가',
      description: '442개 키워드 기반 심층 성향 분석',
      students: 35,
      duration: '12주',
      completionRate: 92,
      status: 'active'
    },
    {
      id: 3,
      name: '키워드 매트릭스 마스터',
      description: '3D 시각화 및 동적 균형 모델',
      students: 18,
      duration: '6주',
      completionRate: 78,
      status: 'active'
    }
  ])

  // 스토어 데이터
  const [storeData] = useState({
    products: [
      {
        id: 4,
        name: '성향분석 워크북',
        category: 'books',
        price: 29000,
        stock: 49,
        sales: 479,
        revenue: 13901000
      }
    ],
    stats: {
      totalProducts: 1,
      totalOrders: 479,
      totalRevenue: 13901000,
      avgOrderValue: 29000
    }
  })

  // 회원 데이터
  const [members] = useState([
    {
      id: 1,
      name: '김명리',
      email: 'myungri@heal7.com',
      plan: '프리미엄',
      joinDate: '2025-01-15',
      lastActive: '2025-08-03',
      status: 'active'
    },
    {
      id: 2,
      name: '이성향',
      email: 'sunghyang@heal7.com',
      plan: '아카데미',
      joinDate: '2025-02-20',
      lastActive: '2025-08-02',
      status: 'active'
    },
    {
      id: 3,
      name: '박균형',
      email: 'kyunhyung@heal7.com',
      plan: '기본',
      joinDate: '2025-07-10',
      lastActive: '2025-08-04',
      status: 'active'
    }
  ])

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ko-KR').format(price) + '원'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">프론트엔드 관리</h1>
          <p className="text-gray-600">웹 서비스, 아카데미, 스토어, 회원 통합 관리</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-1" />
            상태 새로고침
          </Button>
          <Button size="sm">
            <Settings className="h-4 w-4 mr-1" />
            배포 설정
          </Button>
        </div>
      </div>

      {/* Tabs for different management areas */}
      <Tabs defaultValue="services" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="services" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            서비스 관리
          </TabsTrigger>
          <TabsTrigger value="academy" className="flex items-center gap-2">
            <GraduationCap className="h-4 w-4" />
            아카데미 관리
          </TabsTrigger>
          <TabsTrigger value="store" className="flex items-center gap-2">
            <ShoppingCart className="h-4 w-4" />
            스토어 관리
          </TabsTrigger>
          <TabsTrigger value="members" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            회원 관리
          </TabsTrigger>
        </TabsList>

        {/* 서비스 관리 탭 */}
        <TabsContent value="services" className="space-y-6">
          {/* Services Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Globe className="h-4 w-4 text-blue-600" />
                  활성 서비스
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {services.filter(s => s.status === 'active').length}
                </div>
                <p className="text-xs text-gray-600 mt-1">운영 중</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Monitor className="h-4 w-4 text-green-600" />
                  React 19
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">메인</div>
                <p className="text-xs text-gray-600 mt-1">최신 기술 스택</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Layout className="h-4 w-4 text-purple-600" />
                  Next.js 14
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">Admin</div>
                <p className="text-xs text-gray-600 mt-1">App Router</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Smartphone className="h-4 w-4 text-orange-600" />
                  반응형
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">100%</div>
                <p className="text-xs text-gray-600 mt-1">모바일 지원</p>
              </CardContent>
            </Card>
          </div>

          {/* Services List */}
          <Card>
            <CardHeader>
              <CardTitle>서비스 목록</CardTitle>
              <CardDescription>
                운영 중인 프론트엔드 서비스들을 관리합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {services.map((service) => (
                  <div key={service.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-medium text-lg">{service.name}</h3>
                          <Badge 
                            variant="secondary" 
                            className="bg-green-100 text-green-700"
                          >
                            운영 중
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            포트 {service.port}
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-3">{service.description}</p>
                        
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500">버전</p>
                            <p className="font-medium">{service.version}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">마지막 배포</p>
                            <p className="font-medium">{service.lastDeploy}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">상태</p>
                            <p className="font-medium">정상 운영</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex gap-2 ml-4">
                        <Button variant="outline" size="sm" asChild>
                          <a href={`https://${service.name}`} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4 mr-1" />
                            접속
                          </a>
                        </Button>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          로그
                        </Button>
                        <Button variant="outline" size="sm">
                          <Settings className="h-4 w-4 mr-1" />
                          설정
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 아카데미 관리 탭 */}
        <TabsContent value="academy" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <GraduationCap className="h-4 w-4 text-blue-600" />
                  진행 프로그램
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{academyPrograms.length}</div>
                <p className="text-xs text-gray-600 mt-1">개</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Users className="h-4 w-4 text-green-600" />
                  총 수강생
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {academyPrograms.reduce((sum, p) => sum + p.students, 0)}
                </div>
                <p className="text-xs text-gray-600 mt-1">명</p>
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
                <div className="text-2xl font-bold">
                  {Math.round(academyPrograms.reduce((sum, p) => sum + p.completionRate, 0) / academyPrograms.length)}%
                </div>
                <p className="text-xs text-gray-600 mt-1">완료</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>교육 프로그램</CardTitle>
                  <CardDescription>진행 중인 아카데미 프로그램 현황</CardDescription>
                </div>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-1" />
                  프로그램 추가
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {academyPrograms.map((program) => (
                  <div key={program.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium text-lg mb-1">{program.name}</h3>
                        <p className="text-sm text-gray-600 mb-3">{program.description}</p>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500">수강생</p>
                            <p className="font-medium">{program.students}명</p>
                          </div>
                          <div>
                            <p className="text-gray-500">기간</p>
                            <p className="font-medium">{program.duration}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">완료율</p>
                            <p className="font-medium">{program.completionRate}%</p>
                          </div>
                          <div>
                            <p className="text-gray-500">상태</p>
                            <Badge className="bg-green-100 text-green-700">진행중</Badge>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4 mr-1" />
                          수정
                        </Button>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          상세
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 스토어 관리 탭 */}
        <TabsContent value="store" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <ShoppingCart className="h-4 w-4 text-blue-600" />
                  등록 상품
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{storeData.stats.totalProducts}</div>
                <p className="text-xs text-gray-600 mt-1">개</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-green-600" />
                  총 판매
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{storeData.stats.totalOrders}</div>
                <p className="text-xs text-gray-600 mt-1">건</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-purple-600" />
                  총 매출
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{Math.round(storeData.stats.totalRevenue / 1000000)}M</div>
                <p className="text-xs text-gray-600 mt-1">원</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-orange-600" />
                  평균 주문
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{Math.round(storeData.stats.avgOrderValue / 1000)}K</div>
                <p className="text-xs text-gray-600 mt-1">원</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>상품 관리</CardTitle>
                  <CardDescription>등록된 상품 현황 및 판매 데이터</CardDescription>
                </div>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-1" />
                  상품 추가
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {storeData.products.map((product) => (
                  <div key={product.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-medium text-lg">{product.name}</h3>
                          <Badge variant="outline">{product.category}</Badge>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500">가격</p>
                            <p className="font-medium">{formatPrice(product.price)}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">재고</p>
                            <p className="font-medium">{product.stock}권</p>
                          </div>
                          <div>
                            <p className="text-gray-500">판매량</p>
                            <p className="font-medium">{product.sales}건</p>
                          </div>
                          <div>
                            <p className="text-gray-500">매출</p>
                            <p className="font-medium">{formatPrice(product.revenue)}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">상태</p>
                            <Badge className="bg-green-100 text-green-700">판매중</Badge>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4 mr-1" />
                          수정
                        </Button>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          주문조회
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 회원 관리 탭 */}
        <TabsContent value="members" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Users className="h-4 w-4 text-blue-600" />
                  총 회원
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{members.length}</div>
                <p className="text-xs text-gray-600 mt-1">명</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Users className="h-4 w-4 text-green-600" />
                  프리미엄 회원
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {members.filter(m => m.plan === '프리미엄').length}
                </div>
                <p className="text-xs text-gray-600 mt-1">명</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Users className="h-4 w-4 text-purple-600" />
                  활성 회원
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {members.filter(m => m.status === 'active').length}
                </div>
                <p className="text-xs text-gray-600 mt-1">명</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>회원 목록</CardTitle>
                  <CardDescription>등록된 회원 현황 및 활동 상태</CardDescription>
                </div>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-1" />
                  회원 초대
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {members.map((member) => (
                  <div key={member.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-medium text-lg">{member.name}</h3>
                          <Badge 
                            variant="outline"
                            className={
                              member.plan === '프리미엄' ? 'bg-purple-100 text-purple-700' :
                              member.plan === '아카데미' ? 'bg-blue-100 text-blue-700' :
                              'bg-gray-100 text-gray-700'
                            }
                          >
                            {member.plan}
                          </Badge>
                          <Badge className="bg-green-100 text-green-700">활성</Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{member.email}</p>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500">가입일</p>
                            <p className="font-medium">{member.joinDate}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">최근 활동</p>
                            <p className="font-medium">{member.lastActive}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">상태</p>
                            <p className="font-medium">정상</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4 mr-1" />
                          수정
                        </Button>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          상세
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Users,
  Search,
  Plus,
  Filter,
  UserCheck,
  UserX,
  Mail,
  Calendar,
  Activity
} from 'lucide-react'

interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'user' | 'moderator'
  status: 'active' | 'inactive' | 'suspended'
  lastLogin: string
  joinDate: string
}

export default function UsersPage() {
  const [searchTerm, setSearchTerm] = useState('')
  
  const [users] = useState<User[]>([
    { id: '1', name: '김희정', email: 'arne40@heal7.com', role: 'admin', status: 'active', lastLogin: '2시간 전', joinDate: '2024-01-15' },
    { id: '2', name: '관리자1', email: 'admin1@heal7.com', role: 'admin', status: 'active', lastLogin: '1일 전', joinDate: '2024-02-01' },
    { id: '3', name: '테스트유저', email: 'test@heal7.com', role: 'user', status: 'active', lastLogin: '3일 전', joinDate: '2024-07-20' },
    { id: '4', name: '모더레이터1', email: 'mod1@heal7.com', role: 'moderator', status: 'active', lastLogin: '5시간 전', joinDate: '2024-03-10' }
  ])

  const [stats] = useState({
    total: 1234,
    active: 1187,
    newThisMonth: 89,
    adminCount: 3
  })

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-700'
      case 'moderator': return 'bg-blue-100 text-blue-700'
      case 'user': return 'bg-gray-100 text-gray-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-700'
      case 'inactive': return 'bg-gray-100 text-gray-700'
      case 'suspended': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">사용자 관리</h1>
          <p className="text-gray-600">시스템 사용자 및 권한 관리</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-1" />
            필터
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-1" />
            사용자 추가
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-600" />
              총 사용자
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total.toLocaleString()}</div>
            <p className="text-xs text-gray-600 mt-1">등록된 사용자</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <UserCheck className="h-4 w-4 text-green-600" />
              활성 사용자
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active.toLocaleString()}</div>
            <p className="text-xs text-green-600 mt-1">
              {((stats.active / stats.total) * 100).toFixed(1)}% 활성
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4 text-purple-600" />
              이번 달 신규
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.newThisMonth}</div>
            <p className="text-xs text-gray-600 mt-1">신규 가입자</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <UserX className="h-4 w-4 text-orange-600" />
              관리자
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.adminCount}</div>
            <p className="text-xs text-gray-600 mt-1">시스템 관리자</p>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="사용자 검색 (이름, 이메일)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      <Card>
        <CardHeader>
          <CardTitle>사용자 목록</CardTitle>
          <CardDescription>
            시스템에 등록된 사용자들을 관리하고 권한을 설정할 수 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left pb-3 font-medium">사용자</th>
                  <th className="text-left pb-3 font-medium">권한</th>
                  <th className="text-left pb-3 font-medium">상태</th>
                  <th className="text-left pb-3 font-medium">마지막 로그인</th>
                  <th className="text-left pb-3 font-medium">가입일</th>
                  <th className="text-right pb-3 font-medium">작업</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b">
                    <td className="py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-purple-600">
                            {user.name.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium">{user.name}</p>
                          <p className="text-sm text-gray-600 flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            {user.email}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4">
                      <Badge variant="secondary" className={getRoleColor(user.role)}>
                        {user.role === 'admin' ? '관리자' : 
                         user.role === 'moderator' ? '모더레이터' : '일반사용자'}
                      </Badge>
                    </td>
                    <td className="py-4">
                      <Badge variant="secondary" className={getStatusColor(user.status)}>
                        {user.status === 'active' ? '활성' : 
                         user.status === 'inactive' ? '비활성' : '정지'}
                      </Badge>
                    </td>
                    <td className="py-4 text-sm text-gray-600">{user.lastLogin}</td>
                    <td className="py-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {user.joinDate}
                      </div>
                    </td>
                    <td className="py-4 text-right">
                      <div className="flex gap-1 justify-end">
                        <Button variant="ghost" size="sm">편집</Button>
                        <Button variant="ghost" size="sm">정지</Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
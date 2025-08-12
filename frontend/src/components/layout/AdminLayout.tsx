'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Menu, 
  X, 
  Calendar, 
  Home, 
  Users, 
  Settings, 
  BarChart3, 
  Database,
  TrendingUp,
  Heart,
  ChevronDown,
  ChevronRight,
  Sparkles,
  FileQuestion,
  Layout,
  Brain
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface NavItem {
  name: string
  href?: string
  icon: any
  badge?: string
  children?: NavItem[]
}

const navigation: NavItem[] = [
  { name: '대시보드', href: '/dashboard', icon: Home },
  { name: '통계 분석', href: '/analytics', icon: BarChart3 },
  { 
    name: '힐링스페이스', 
    icon: Heart,
    children: [
      { name: '키워드 관리', href: '/keywords', icon: Database },
      { name: '그룹별 관리', href: '/keywords/management', icon: Settings },
      { name: '키워드 메트릭스', href: '/keywords/matrix', icon: Sparkles },
      { name: '설문 관리', href: '/surveys', icon: FileQuestion },
      { name: '프론트 관리', href: '/frontend', icon: Layout },
    ]
  },
  { name: '시스템 설정', href: '/settings', icon: Settings },
  { name: '사용자 관리', href: '/users', icon: Users },
]

interface AdminLayoutProps {
  children: React.ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [expandedItems, setExpandedItems] = useState<string[]>(['힐링스페이스'])
  const pathname = usePathname()


  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev => 
      prev.includes(itemName) 
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
    )
  }

  const renderNavItem = (item: NavItem) => {
    const isExpanded = expandedItems.includes(item.name)
    const Icon = item.icon
    const hasChildren = item.children && item.children.length > 0
    const isActive = item.href ? pathname === item.href : false
    const isChildActive = hasChildren && item.children.some(child => pathname === child.href)

    if (hasChildren) {
      return (
        <div key={item.name}>
          <button
            onClick={() => toggleExpanded(item.name)}
            className={`
              w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors
              ${isChildActive 
                ? 'bg-purple-50 text-purple-700' 
                : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }
            `}
          >
            <Icon className={`h-5 w-5 ${isChildActive ? 'text-purple-600' : 'text-gray-500'}`} />
            <span className="flex-1 text-left">{item.name}</span>
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-gray-400" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-400" />
            )}
          </button>
          {isExpanded && (
            <div className="ml-8 mt-1 space-y-1">
              {item.children.map(child => renderNavItem(child))}
            </div>
          )}
        </div>
      )
    }

    return (
      <Link
        key={item.name}
        href={item.href || '#'}
        className={`
          flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors
          ${isActive 
            ? 'bg-purple-50 text-purple-700 border border-purple-200' 
            : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
          }
        `}
      >
        <Icon className={`h-5 w-5 ${isActive ? 'text-purple-600' : 'text-gray-500'}`} />
        <span>{item.name}</span>
        {item.badge && (
          <Badge variant="secondary" className="ml-auto text-xs">{item.badge}</Badge>
        )}
      </Link>
    )
  }

  return (
    <>
          <div className="flex h-screen bg-gray-50">
      {/* Sidebar for desktop */}
      <div className="hidden md:flex md:w-64 md:flex-col">
        <div className="flex min-h-0 flex-1 flex-col bg-white border-r border-gray-200">
          {/* Logo/Brand */}
          <div className="flex h-16 flex-shrink-0 items-center px-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                <Calendar className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">HEAL7</h1>
                <p className="text-xs text-gray-500">관리자 대시보드</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {navigation.map(item => renderNavItem(item))}
          </nav>

          {/* Footer */}
          <div className="flex-shrink-0 p-4 border-t border-gray-200">
            <div className="text-xs text-gray-500 space-y-1">
              <p>© 2025 (주)노마드컴퍼니</p>
              <p>HEAL7 Admin v1.0</p>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
          <div className="relative flex w-full max-w-xs flex-1 flex-col bg-white">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(false)}
                className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              >
                <X className="h-6 w-6 text-white" />
              </Button>
            </div>

            {/* Mobile navigation - same as desktop */}
            <div className="flex h-16 flex-shrink-0 items-center px-6 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                  <Calendar className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-gray-900">HEAL7</h1>
                  <p className="text-xs text-gray-500">관리자 대시보드</p>
                </div>
              </div>
            </div>

            <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
              {navigation.map(item => renderNavItem(item))}
            </nav>
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <div className="flex h-16 flex-shrink-0 items-center gap-4 border-b border-gray-200 bg-white px-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(true)}
            className="md:hidden"
          >
            <Menu className="h-6 w-6" />
          </Button>

          {/* Breadcrumb/Page title */}
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-gray-900">
              {(() => {
                // 먼저 1단계 메뉴에서 찾기
                const topLevel = navigation.find(item => item.href === pathname)
                if (topLevel) return topLevel.name
                
                // 2단계 메뉴에서 찾기
                for (const item of navigation) {
                  if (item.children) {
                    const child = item.children.find(child => child.href === pathname)
                    if (child) return `${item.name} > ${child.name}`
                  }
                }
                
                return '관리자 대시보드'
              })()}
            </h2>
          </div>

          {/* User info */}
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="text-xs">관리자</Badge>
            <div className="h-8 w-8 rounded-full bg-purple-600 flex items-center justify-center">
              <span className="text-xs font-medium text-white">관</span>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          {children}
        </main>
      </div>
    </div>
    </>
  )
}


'use client'

import React from 'react'

export default function TestPage() {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-8 rounded-lg">
        <h1 className="text-3xl font-bold mb-4">🎯 Next.js 테스트 페이지</h1>
        <p className="text-lg mb-4">
          이 페이지가 정상적으로 보이면 Next.js가 올바르게 작동하고 있습니다.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <div className="bg-white/20 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">✅ JavaScript 작동 확인</h3>
            <button 
              onClick={() => alert('JavaScript가 정상 작동합니다!')} 
              className="bg-white/30 hover:bg-white/40 px-4 py-2 rounded transition-colors"
            >
              클릭 테스트
            </button>
          </div>
          
          <div className="bg-white/20 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">🔧 현재 상태</h3>
            <ul className="text-sm space-y-1">
              <li>• Next.js 서버: 실행 중</li>
              <li>• 포트: 5173</li>
              <li>• 레거시 텍스트: 제거 완료</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-6 p-4 bg-red-500/30 rounded-lg border border-red-300">
          <h3 className="font-semibold mb-2">❌ 제거된 레거시 텍스트</h3>
          <div className="text-sm space-y-1 opacity-75">
            <p>• "레거시 고급 3D 시스템" - 삭제됨</p>
            <p>• "Three.js + OrbitControls + 의존성 네트워크" - 삭제됨</p>
            <p>• "지구본 시각화 | 마우스 드래그 | 키워드 관계 분석" - 삭제됨</p>
            <p>• "클릭: 키워드 선택" - 삭제됨</p>
            <p>• "마우스 드래그: 회전 | 휠: 확대/축소" - 삭제됨</p>
          </div>
        </div>
      </div>
      
      <div className="text-center">
        <a href="/keywords/matrix/" className="inline-block bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-colors">
          키워드 매트릭스로 이동
        </a>
      </div>
    </div>
  )
}
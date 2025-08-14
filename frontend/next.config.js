/** @type {import('next').NextConfig} */
const nextConfig = {
  // Server Actions를 사용하므로 static export 비활성화
  // output: 'export', // Server Actions와 호환되지 않음
  
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  
  // 추가 메모리 최적화 (저사양 서버용)
  experimental: {
    workerThreads: false, // 스레드 비활성화로 메모리 오버헤드 감소
    cpus: 1, // CPU 코어 수 제한
  },
  
  // 최적화된 청크 분할 설정 (브라우저 IPC 플러딩 방지)
  webpack: (config, { isServer }) => {
    // 브라우저 네비게이션 throttling 해결을 위한 청크 최적화
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        chunks: 'all',
        minSize: 20000,
        maxSize: 800000, // 800KB로 증가하여 청크 수 감소
        maxAsyncRequests: 8, // 동시 요청 수 제한
        maxInitialRequests: 6, // 초기 요청 수 제한
        cacheGroups: {
          // React 관련 라이브러리를 하나의 청크로 묶음
          react: {
            test: /[\\/]node_modules[\\/](react|react-dom|react-router)[\\/]/,
            name: 'react-vendor',
            priority: 10,
            chunks: 'all',
            enforce: true
          },
          // UI 라이브러리들을 하나의 청크로 묶음 (Radix UI, Framer Motion 등)
          ui: {
            test: /[\\/]node_modules[\\/](@radix-ui|framer-motion|lucide-react|sonner)[\\/]/,
            name: 'ui-vendor',
            priority: 9,
            chunks: 'all',
            enforce: true
          },
          // 차트 및 기타 라이브러리
          libs: {
            test: /[\\/]node_modules[\\/](recharts|axios|clsx|class-variance-authority|tailwind-merge)[\\/]/,
            name: 'libs-vendor',
            priority: 8,
            chunks: 'all',
            enforce: true
          },
          // 기본 vendor 청크 (나머지 node_modules)
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendor',
            priority: 5,
            chunks: 'all',
            minChunks: 1,
            reuseExistingChunk: true
          },
          // 기본 청크
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true
          }
        }
      }
    }
    
    // 메모리 부족 시 병렬 처리 비활성화
    config.optimization.minimizer = config.optimization.minimizer || []
    
    return config
  },
  
  // 빌드 최적화
  compress: true,
  swcMinify: true,
  poweredByHeader: false,
  generateEtags: false,
  
  // PostgreSQL 직접 연결을 사용하므로 API 리라이트 불필요
  // FastAPI 백엔드 연동 완전 제거됨
}

module.exports = nextConfig
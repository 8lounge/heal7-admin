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
  
  // 메모리 최적화 설정
  webpack: (config, { isServer }) => {
    // 메모리 사용량 최적화
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        chunks: 'all',
        maxSize: 200000, // 200KB로 청크 크기 제한
        cacheGroups: {
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true
          },
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: -10,
            chunks: 'all',
            maxSize: 200000
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
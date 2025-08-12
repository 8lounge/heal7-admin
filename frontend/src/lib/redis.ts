import Redis from 'ioredis'

// Redis 클라이언트 싱글톤
let redis: Redis | null = null

export function getRedisClient(): Redis {
  if (!redis) {
    redis = new Redis({
      host: process.env.REDIS_HOST || '127.0.0.1',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      db: 0,
      lazyConnect: true,
      maxRetriesPerRequest: 3,
      connectTimeout: 5000
    })

    redis.on('connect', () => {
      console.log('✅ Redis 연결 성공')
    })

    redis.on('error', (error) => {
      console.error('❌ Redis 연결 오류:', error)
    })
  }
  
  return redis
}

// 키워드 캐시 키 생성
export const CACHE_KEYS = {
  ALL_KEYWORDS: 'keywords:all',
  KEYWORD_BY_ID: (id: number) => `keyword:${id}`,
  KEYWORD_DEPENDENCIES: (id: number) => `keyword:${id}:deps`,
  KEYWORD_STATS: 'keywords:stats',
  KEYWORD_SEARCH: (query: string) => `keywords:search:${query}`,
  KEYWORD_CATEGORY: (category: string) => `keywords:category:${category}`,
  LAST_SYNC: 'keywords:last_sync'
} as const

// Redis 키워드 데이터 타입 정의
export interface CachedKeywordData {
  id: number
  name: string
  text: string
  category: 'A' | 'B' | 'C'
  subcategory: string
  subcategory_name: string
  weight: number
  connections: number
  status: string
  dependencies: number[]
  color?: string
  position?: [number, number, number]
  created_at?: string
  updated_at?: string
}

export interface KeywordStats {
  total_keywords: number
  active_keywords: number
  total_connections: number
  network_density: number
  category_distribution: {
    A: number
    B: number
    C: number
  }
  last_updated: string
  data_source: string
}

// Redis 연결 테스트
export async function testRedisConnection(): Promise<boolean> {
  try {
    const client = getRedisClient()
    await client.ping()
    return true
  } catch (error) {
    console.error('Redis 연결 테스트 실패:', error)
    return false
  }
}

// Redis 연결 종료
export function closeRedisConnection(): void {
  if (redis) {
    redis.disconnect()
    redis = null
  }
}
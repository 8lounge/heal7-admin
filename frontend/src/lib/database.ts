import { Pool, PoolClient } from 'pg'

// PostgreSQL 연결 풀 (싱글톤 패턴) - Next.js Server Actions 최적화
class DatabasePool {
  private static instance: Pool | null = null
  
  public static getInstance(): Pool {
    if (!DatabasePool.instance) {
      // Next.js Server Actions용 PostgreSQL 연결 설정 (여러 방법 시도)
      const connectionConfigs = [
        // 1. Unix domain socket 연결 (peer authentication)
        {
          host: '/var/run/postgresql',
          user: 'postgres',
          database: 'livedb',
          max: 10,
          idleTimeoutMillis: 10000,
          connectionTimeoutMillis: 5000
        },
        // 2. TCP 연결 (패스워드 없음)
        {
          host: 'localhost',
          port: 5432,
          user: 'postgres',
          database: 'livedb', 
          max: 10,
          idleTimeoutMillis: 10000,
          connectionTimeoutMillis: 5000
        },
        // 3. 환경변수 연결 문자열
        {
          connectionString: process.env.DATABASE_URL || 'postgresql://postgres@localhost/livedb',
          max: 10,
          idleTimeoutMillis: 10000,
          connectionTimeoutMillis: 5000
        }
      ]

      // 연결 시도
      for (let i = 0; i < connectionConfigs.length; i++) {
        try {
          console.log(`🔄 PostgreSQL 연결 시도 ${i + 1}: ${JSON.stringify(connectionConfigs[i])}`)
          DatabasePool.instance = new Pool(connectionConfigs[i])
          
          // 연결 풀 이벤트 리스너
          DatabasePool.instance.on('error', (err) => {
            console.error(`❌ PostgreSQL 연결 풀 오류 (설정 ${i + 1}):`, err)
          })
          
          DatabasePool.instance.on('connect', () => {
            console.log(`✅ PostgreSQL 연결 성공 (설정 ${i + 1})`)
          })
          
          break // 성공하면 루프 종료
        } catch (error) {
          console.warn(`⚠️ PostgreSQL 연결 설정 ${i + 1} 실패:`, error)
          DatabasePool.instance = null
          continue
        }
      }

      // 모든 설정이 실패한 경우 기본 설정 사용
      if (!DatabasePool.instance) {
        console.warn('⚠️ 모든 PostgreSQL 연결 설정 실패 - 기본 설정 사용')
        DatabasePool.instance = new Pool({
          host: 'localhost',
          port: 5432,
          user: 'postgres',
          database: 'livedb',
          max: 5,
          idleTimeoutMillis: 5000,
          connectionTimeoutMillis: 3000
        })
      }
    }
    
    return DatabasePool.instance
  }
}

// 데이터베이스 쿼리 실행 헬퍼 함수
export async function executeQuery<T = any>(
  text: string, 
  params: any[] = []
): Promise<T[]> {
  const pool = DatabasePool.getInstance()
  const client: PoolClient = await pool.connect()
  
  try {
    console.log('🔍 SQL 쿼리 실행:', text.substring(0, 100) + '...')
    const start = Date.now()
    const result = await client.query(text, params)
    const duration = Date.now() - start
    console.log(`✅ 쿼리 완료 (${duration}ms, ${result.rows.length}개 결과)`)
    
    return result.rows as T[]
  } catch (error) {
    console.error('❌ SQL 쿼리 실행 오류:', error)
    throw error
  } finally {
    client.release()
  }
}

// 데이터베이스 연결 테스트 함수
export async function testDatabaseConnection(): Promise<boolean> {
  try {
    const result = await executeQuery('SELECT NOW() as current_time')
    console.log('✅ 데이터베이스 연결 테스트 성공:', result[0])
    return true
  } catch (error) {
    console.error('❌ 데이터베이스 연결 테스트 실패:', error)
    return false
  }
}

// 키워드 데이터 타입 정의
export interface KeywordRow {
  id: number
  text: string
  subcategory_id: number
  is_active: boolean
  created_at: string
  updated_at: string
  category_name?: string
  subcategory_name?: string
  weight?: number
  usage_count?: number
}

export interface KeywordDependencyRow {
  parent_keyword_id: number
  dependent_keyword_id: number
  weight: number
  is_active: boolean
  parent_name: string
  dependent_name: string
}

// 싱글톤 패턴으로 풀 인스턴스 내보내기
export const pool = DatabasePool.getInstance()
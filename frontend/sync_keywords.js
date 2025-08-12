const { Pool } = require('pg')
const Redis = require('ioredis')

const pool = new Pool({
  connectionString: 'postgresql://liveuser:livepass2024@localhost:5432/livedb'
})

const redis = new Redis({
  host: '127.0.0.1',
  port: 6379,
  db: 0
})

async function syncKeywords() {
  try {
    console.log('🔄 PostgreSQL에서 키워드 조회 시작...')
    
    const query = `
      SELECT 
        k.id, 
        k.text as name,
        k.text,
        ksc.name as subcategory_name,
        CASE 
          WHEN ksc.name LIKE 'A-%' THEN 'A'
          WHEN ksc.name LIKE 'B-%' THEN 'B'
          WHEN ksc.name LIKE 'C-%' THEN 'C'
          ELSE 'A'
        END as category,
        COALESCE(
          (SELECT COUNT(*) FROM keyword_dependencies kd WHERE kd.parent_keyword_id = k.id OR kd.dependent_keyword_id = k.id),
          0
        ) as connections,
        CASE WHEN k.is_active THEN 'active' ELSE 'inactive' END as status
      FROM keywords k
      JOIN keyword_subcategories ksc ON k.subcategory_id = ksc.id
      WHERE k.is_active = true
      ORDER BY k.id
    `
    
    const result = await pool.query(query)
    console.log(`✅ PostgreSQL에서 ${result.rows.length}개 키워드 조회 완료`)
    
    // Redis에 키워드 저장
    const keywords = result.rows.map((row, index) => ({
      id: row.id,
      name: row.name || row.text,
      text: row.text,
      category: row.category,
      subcategory: row.subcategory_name,
      subcategory_name: row.subcategory_name,
      weight: Math.random() * 8 + 4, // 임시 가중치 (4-12 범위)
      connections: parseInt(row.connections) || 0,
      status: row.status,
      dependencies: [],
      color: row.category === 'A' ? '#3B82F6' : row.category === 'B' ? '#8B5CF6' : '#F97316',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }))

    // Redis에 전체 키워드 저장
    await redis.set('keywords:all', JSON.stringify(keywords))
    await redis.expire('keywords:all', 3600)
    
    // 통계 저장
    const stats = {
      total_keywords: keywords.length,
      active_keywords: keywords.filter(k => k.status === 'active').length,
      total_connections: keywords.reduce((sum, k) => sum + k.connections, 0),
      network_density: keywords.length > 0 ? (keywords.reduce((sum, k) => sum + k.connections, 0) / keywords.length) : 0,
      category_distribution: {
        A: keywords.filter(k => k.category === 'A').length,
        B: keywords.filter(k => k.category === 'B').length,
        C: keywords.filter(k => k.category === 'C').length
      },
      last_updated: new Date().toISOString(),
      data_source: 'PostgreSQL → Redis Sync'
    }
    
    await redis.set('keywords:stats', JSON.stringify(stats))
    await redis.expire('keywords:stats', 3600)
    await redis.set('keywords:last_sync', new Date().toISOString())
    
    console.log(`🚀 Redis 동기화 완료:`, {
      총_키워드: stats.total_keywords,
      활성_키워드: stats.active_keywords,
      총_연결: stats.total_connections,
      네트워크_밀도: stats.network_density.toFixed(1),
      A그룹: stats.category_distribution.A,
      B그룹: stats.category_distribution.B,
      C그룹: stats.category_distribution.C
    })
    
    // 검증
    const cachedKeywords = await redis.get('keywords:all')
    const parsedKeywords = JSON.parse(cachedKeywords)
    console.log(`✅ Redis 검증: ${parsedKeywords.length}개 키워드 저장됨`)
    
  } catch (error) {
    console.error('❌ 동기화 실패:', error)
  } finally {
    await pool.end()
    await redis.disconnect()
  }
}

syncKeywords()

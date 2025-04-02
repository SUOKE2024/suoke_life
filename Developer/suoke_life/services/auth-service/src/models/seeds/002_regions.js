/**
 * 区域配置种子数据
 */
exports.seed = async function(knex) {
  // 清空表
  await knex('regions').del();
  
  // 插入默认区域配置
  return knex('regions').insert([
    {
      code: 'cn-east',
      name: '华东区域',
      api_url: process.env.CN_EAST_API_URL || 'http://auth-service.cn-east.svc.cluster.local:3000',
      is_active: true,
      is_primary: true,
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      code: 'cn-north',
      name: '华北区域',
      api_url: process.env.CN_NORTH_API_URL || 'http://auth-service.cn-north.svc.cluster.local:3000',
      is_active: true,
      is_primary: false,
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      code: 'cn-south',
      name: '华南区域',
      api_url: process.env.CN_SOUTH_API_URL || 'http://auth-service.cn-south.svc.cluster.local:3000',
      is_active: true,
      is_primary: false,
      created_at: new Date(),
      updated_at: new Date()
    }
  ]);
}; 
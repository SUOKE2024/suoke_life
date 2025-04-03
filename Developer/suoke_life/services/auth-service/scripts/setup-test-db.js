/**
 * 设置测试数据库
 */
const knex = require('knex');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// 加载环境变量
dotenv.config({ path: path.join(__dirname, '../.env.test') });

// 数据库配置
const dbConfig = {
  client: 'sqlite3',
  connection: {
    filename: ':memory:' // 使用内存数据库进行测试
  },
  useNullAsDefault: true
};

// 创建数据库连接
const db = knex(dbConfig);

// SQL文件路径
const schemaSqlPath = path.join(__dirname, '../src/database/schema.sql');

// 主函数
async function setupTestDb() {
  try {
    console.log('开始设置测试数据库...');
    
    // 读取模式SQL文件
    const schemaSql = fs.readFileSync(schemaSqlPath, 'utf8');
    
    // 执行建表语句
    await db.raw(schemaSql);
    
    console.log('创建表结构完成');
    
    // 添加测试数据
    await seedTestData();
    
    console.log('测试数据库设置完成');
    
    // 导出数据库连接
    global.testDb = db;
    
    return db;
  } catch (error) {
    console.error('设置测试数据库失败:', error);
    throw error;
  }
}

// 添加测试数据
async function seedTestData() {
  console.log('开始添加测试数据...');
  
  // 添加测试用户
  await db('users').insert([
    {
      id: '1',
      username: 'testadmin',
      email: 'admin@example.com',
      password: '$2b$10$eCNrAJ0dyBKTQ5Vj.iyZW.XYNMW3WVjt5MgpgfhW1xWsDnzm0O07K', // Password123!
      role: 'admin',
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '2',
      username: 'testuser',
      email: 'user@example.com',
      password: '$2b$10$eCNrAJ0dyBKTQ5Vj.iyZW.XYNMW3WVjt5MgpgfhW1xWsDnzm0O07K', // Password123!
      role: 'user',
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '3',
      username: 'disableduser',
      email: 'disabled@example.com',
      password: '$2b$10$eCNrAJ0dyBKTQ5Vj.iyZW.XYNMW3WVjt5MgpgfhW1xWsDnzm0O07K', // Password123!
      role: 'user',
      status: 'disabled',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ]);
  
  // 添加知识库权限
  await db('knowledge_permissions').insert([
    {
      id: '1',
      user_id: '1',
      permission_type: 'knowledge:read',
      resource_scope: '*',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '2',
      user_id: '1',
      permission_type: 'knowledge:write',
      resource_scope: '*',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '3',
      user_id: '2',
      permission_type: 'knowledge:read',
      resource_scope: 'public',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ]);
  
  console.log('测试数据添加完成');
}

// 如果直接运行此脚本
if (require.main === module) {
  setupTestDb()
    .then(() => {
      console.log('测试数据库设置完成。运行测试中...');
    })
    .catch(error => {
      console.error('设置失败:', error);
      process.exit(1);
    });
}

module.exports = setupTestDb;
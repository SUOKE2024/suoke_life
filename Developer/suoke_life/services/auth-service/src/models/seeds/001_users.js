/**
 * 用户种子数据
 */
const bcrypt = require('bcrypt');

exports.seed = async function(knex) {
  // 首先清空users表
  await knex('users').del();
  
  // 生成测试用户的密码哈希（密码: password123）
  const salt = await bcrypt.genSalt(10);
  const adminPassword = await bcrypt.hash('admin123', salt);
  const userPassword = await bcrypt.hash('password123', salt);
  
  // 插入种子数据
  return knex('users').insert([
    {
      id: 1,
      username: 'admin',
      email: 'admin@suoke.life',
      password: adminPassword,
      role: 'admin',
      bio: '索克生活APP管理员',
      is_active: true,
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: 2,
      username: 'testuser',
      email: 'test@suoke.life',
      password: userPassword,
      role: 'user',
      bio: '测试用户',
      is_active: true,
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: 3,
      username: 'zhangsan',
      email: 'zhangsan@suoke.life',
      password: userPassword,
      role: 'user',
      bio: '张三，普通用户',
      is_active: true,
      created_at: new Date(),
      updated_at: new Date()
    }
  ]);
}; 
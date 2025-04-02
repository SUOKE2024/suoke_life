/**
 * 生物识别凭据表迁移文件
 */
exports.up = function(knex) {
  return knex.schema.createTable('biometric_credentials', function(table) {
    // 主键
    table.string('id', 36).primary().notNullable().comment('凭据ID');
    
    // 关联用户
    table.string('user_id', 36).notNullable().index().comment('用户ID');
    
    // 设备信息
    table.string('device_id', 100).notNullable().comment('设备ID');
    table.string('biometric_type', 50).notNullable().comment('生物识别类型');
    
    // 凭据数据
    table.text('public_key').notNullable().comment('公钥');
    table.text('device_info').comment('设备信息（JSON格式）');
    table.text('attestation').nullable().comment('设备证明信息（JSON格式）');
    
    // 时间戳
    table.timestamp('created_at').notNullable().defaultTo(knex.fn.now()).comment('创建时间');
    table.timestamp('updated_at').notNullable().defaultTo(knex.fn.now()).comment('更新时间');
    table.timestamp('last_used_at').nullable().comment('最后使用时间');
    table.timestamp('expires_at').notNullable().comment('过期时间');
    
    // 索引
    table.index(['user_id', 'device_id', 'biometric_type'], 'idx_biometric_user_device_type');
    
    // 外键关联
    table.foreign('user_id').references('id').inTable('users').onDelete('CASCADE');
  });
};

exports.down = function(knex) {
  return knex.schema.dropTableIfExists('biometric_credentials');
}; 
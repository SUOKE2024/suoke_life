/**
 * 数据库迁移：添加手机号字段
 */
exports.up = function(knex) {
  return knex.schema.hasTable('users').then(function(exists) {
    if (exists) {
      return knex.schema.alterTable('users', function(table) {
        // 添加手机号字段
        table.string('phone', 20).nullable().unique().comment('用户手机号');
        
        // 添加索引
        table.index('phone', 'idx_users_phone');
      });
    }
  });
};

exports.down = function(knex) {
  return knex.schema.hasTable('users').then(function(exists) {
    if (exists) {
      return knex.schema.alterTable('users', function(table) {
        // 删除索引
        table.dropIndex('phone', 'idx_users_phone');
        
        // 删除手机号字段
        table.dropColumn('phone');
      });
    }
  });
}; 
/**
 * 添加跨区域同步所需的字段
 */
exports.up = function(knex) {
  return Promise.all([
    // 向用户表添加跨区域同步字段
    knex.schema.table('users', table => {
      // 添加数据版本号，用于冲突解决
      table.bigInteger('data_version').nullable();
      // 添加最后修改区域
      table.string('last_region', 50).nullable();
      // 添加最后同步时间
      table.timestamp('last_synced_at').nullable();
    }),
    
    // 创建同步日志表
    knex.schema.createTable('sync_logs', table => {
      table.uuid('id').primary();
      table.string('table_name', 100).notNullable();
      table.string('operation', 20).notNullable(); // insert, update, delete
      table.uuid('record_id').notNullable();
      table.json('data').nullable();
      table.string('source_region', 50).notNullable();
      table.string('status', 20).notNullable().defaultTo('pending'); // pending, processing, completed, failed
      table.integer('retry_count').unsigned().notNullable().defaultTo(0);
      table.text('error_message').nullable();
      table.timestamp('created_at').notNullable().defaultTo(knex.fn.now());
      table.timestamp('updated_at').notNullable().defaultTo(knex.fn.now());
      table.timestamp('completed_at').nullable();
      
      // 索引
      table.index('table_name');
      table.index('status');
      table.index('source_region');
      table.index(['table_name', 'record_id']);
    }),
    
    // 创建区域配置表
    knex.schema.createTable('regions', table => {
      table.string('code', 50).primary();
      table.string('name', 100).notNullable();
      table.string('api_url', 255).notNullable();
      table.boolean('is_active').notNullable().defaultTo(true);
      table.boolean('is_primary').notNullable().defaultTo(false);
      table.timestamp('created_at').notNullable().defaultTo(knex.fn.now());
      table.timestamp('updated_at').notNullable().defaultTo(knex.fn.now());
    })
  ]);
};

exports.down = function(knex) {
  return Promise.all([
    // 移除用户表中的跨区域同步字段
    knex.schema.table('users', table => {
      table.dropColumn('data_version');
      table.dropColumn('last_region');
      table.dropColumn('last_synced_at');
    }),
    
    // 删除同步日志表
    knex.schema.dropTable('sync_logs'),
    
    // 删除区域配置表
    knex.schema.dropTable('regions')
  ]);
}; 
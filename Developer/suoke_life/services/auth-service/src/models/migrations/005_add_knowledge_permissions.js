/**
 * 添加知识库与知识图谱权限字段迁移文件
 */

exports.up = function(knex) {
  return knex.schema
    .table('user_permissions', function(table) {
      // 添加知识库相关权限
      table.boolean('knowledge_read').defaultTo(false);
      table.boolean('knowledge_write').defaultTo(false);
      table.boolean('graph_read').defaultTo(false);
      table.boolean('graph_write').defaultTo(false);
      table.boolean('sensitive_read').defaultTo(false);
      
      // 领域特定权限
      table.boolean('tcm_read').defaultTo(false);
      table.boolean('nutrition_read').defaultTo(false);
      table.boolean('mental_health_read').defaultTo(false);
      table.boolean('environmental_health_read').defaultTo(false);
      table.boolean('precision_medicine_read').defaultTo(false);
      
      // 索引
      table.index('knowledge_read');
      table.index('knowledge_write');
      table.index('graph_read');
      table.index('graph_write');
      table.index('sensitive_read');
    })
    .createTableIfNotExists('knowledge_access_logs', function(table) {
      table.increments('id').primary();
      table.integer('user_id').notNullable().references('id').inTable('users');
      table.string('resource_type', 30).notNullable(); // 'knowledge_base', 'knowledge_graph', etc.
      table.string('resource_id', 100).notNullable();
      table.string('action', 20).notNullable(); // 'read', 'write', 'query', etc.
      table.timestamp('accessed_at').notNullable().defaultTo(knex.fn.now());
      table.string('ip_address', 45).nullable();
      table.string('user_agent', 255).nullable();
      
      // 索引
      table.index('user_id');
      table.index('resource_type');
      table.index('resource_id');
      table.index('action');
      table.index('accessed_at');
    });
};

exports.down = function(knex) {
  return knex.schema
    .table('user_permissions', function(table) {
      // 删除知识库相关权限
      table.dropColumn('knowledge_read');
      table.dropColumn('knowledge_write');
      table.dropColumn('graph_read');
      table.dropColumn('graph_write');
      table.dropColumn('sensitive_read');
      
      // 删除领域特定权限
      table.dropColumn('tcm_read');
      table.dropColumn('nutrition_read');
      table.dropColumn('mental_health_read');
      table.dropColumn('environmental_health_read');
      table.dropColumn('precision_medicine_read');
    })
    .dropTableIfExists('knowledge_access_logs');
};
/**
 * 创建用户表迁移文件
 */

exports.up = function(knex) {
  return knex.schema.createTable('users', function(table) {
    table.increments('id').primary();
    table.string('username', 30).notNullable().unique();
    table.string('email', 100).notNullable().unique();
    table.string('password', 100).notNullable();
    table.string('role', 20).notNullable().defaultTo('user');
    table.string('avatar_url', 255).nullable();
    table.text('bio').nullable();
    table.boolean('is_active').notNullable().defaultTo(true);
    table.timestamp('last_login_at').nullable();
    table.timestamp('created_at').notNullable().defaultTo(knex.fn.now());
    table.timestamp('updated_at').notNullable().defaultTo(knex.fn.now());
    
    // 索引
    table.index('username');
    table.index('email');
    table.index('role');
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('users');
}; 
/**
 * 添加双因素认证和安全日志相关的数据库表结构
 */

exports.up = async function(knex) {
  // 添加双因素认证相关字段到用户表
  await knex.schema.table('users', (table) => {
    if (!await knex.schema.hasColumn('users', 'two_factor_enabled')) {
      table.boolean('two_factor_enabled').defaultTo(false);
    }
    if (!await knex.schema.hasColumn('users', 'two_factor_secret')) {
      table.string('two_factor_secret', 255).nullable();
    }
    if (!await knex.schema.hasColumn('users', 'two_factor_method')) {
      table.string('two_factor_method', 20).nullable();
    }
    if (!await knex.schema.hasColumn('users', 'two_factor_backup_codes')) {
      table.json('two_factor_backup_codes').nullable();
    }
  });

  // 创建二因素认证恢复码表
  if (!await knex.schema.hasTable('two_factor_recovery_codes')) {
    await knex.schema.createTable('two_factor_recovery_codes', (table) => {
      table.uuid('id').primary().defaultTo(knex.raw('UUID()'));
      table.uuid('user_id').notNullable();
      table.string('code_hash', 255).notNullable();
      table.boolean('used').defaultTo(false);
      table.timestamp('created_at').defaultTo(knex.fn.now());
      table.timestamp('used_at').nullable();
      
      table.foreign('user_id').references('id').inTable('users').onDelete('CASCADE');
      table.index(['user_id', 'used']);
    });
  }

  // 创建用户安全事件表
  if (!await knex.schema.hasTable('security_events')) {
    await knex.schema.createTable('security_events', (table) => {
      table.uuid('id').primary().defaultTo(knex.raw('UUID()'));
      table.uuid('user_id').notNullable();
      table.string('type', 50).notNullable();
      table.string('ip_address', 45).nullable();
      table.string('user_agent', 255).nullable();
      table.json('metadata').nullable();
      table.timestamp('created_at').defaultTo(knex.fn.now());
      
      table.foreign('user_id').references('id').inTable('users').onDelete('CASCADE');
      table.index(['user_id', 'type']);
      table.index('created_at');
    });
  }

  // 创建安全设置表
  if (!await knex.schema.hasTable('user_security_settings')) {
    await knex.schema.createTable('user_security_settings', (table) => {
      table.uuid('user_id').primary();
      table.boolean('login_notifications_enabled').defaultTo(true);
      table.boolean('suspicious_activity_notifications_enabled').defaultTo(true);
      table.boolean('password_change_required').defaultTo(false);
      table.timestamp('password_changed_at').nullable();
      table.timestamp('created_at').defaultTo(knex.fn.now());
      table.timestamp('updated_at').defaultTo(knex.fn.now());
      
      table.foreign('user_id').references('id').inTable('users').onDelete('CASCADE');
    });
  }

  // 创建用户会话表
  if (!await knex.schema.hasTable('user_sessions')) {
    await knex.schema.createTable('user_sessions', (table) => {
      table.uuid('id').primary().defaultTo(knex.raw('UUID()'));
      table.uuid('user_id').notNullable();
      table.string('token_id', 100).notNullable();
      table.string('device_info', 255).nullable();
      table.string('ip_address', 45).nullable();
      table.string('user_agent', 255).nullable();
      table.string('location', 100).nullable();
      table.boolean('is_current').defaultTo(false);
      table.timestamp('created_at').defaultTo(knex.fn.now());
      table.timestamp('last_active_at').defaultTo(knex.fn.now());
      table.timestamp('expires_at').nullable();
      
      table.foreign('user_id').references('id').inTable('users').onDelete('CASCADE');
      table.index(['user_id', 'is_current']);
      table.index('token_id');
    });
  }
};

exports.down = async function(knex) {
  // 删除用户会话表
  if (await knex.schema.hasTable('user_sessions')) {
    await knex.schema.dropTable('user_sessions');
  }
  
  // 删除安全设置表
  if (await knex.schema.hasTable('user_security_settings')) {
    await knex.schema.dropTable('user_security_settings');
  }
  
  // 删除安全事件表
  if (await knex.schema.hasTable('security_events')) {
    await knex.schema.dropTable('security_events');
  }
  
  // 删除二因素认证恢复码表
  if (await knex.schema.hasTable('two_factor_recovery_codes')) {
    await knex.schema.dropTable('two_factor_recovery_codes');
  }
  
  // 删除用户表中的双因素认证字段
  await knex.schema.table('users', (table) => {
    if (await knex.schema.hasColumn('users', 'two_factor_enabled')) {
      table.dropColumn('two_factor_enabled');
    }
    if (await knex.schema.hasColumn('users', 'two_factor_secret')) {
      table.dropColumn('two_factor_secret');
    }
    if (await knex.schema.hasColumn('users', 'two_factor_method')) {
      table.dropColumn('two_factor_method');
    }
    if (await knex.schema.hasColumn('users', 'two_factor_backup_codes')) {
      table.dropColumn('two_factor_backup_codes');
    }
  });
};
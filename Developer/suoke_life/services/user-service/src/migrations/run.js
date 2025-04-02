/**
 * 数据库迁移执行脚本
 */
const fs = require('fs');
const path = require('path');
const knex = require('../utils/db');
const logger = require('../utils/logger');

// 获取迁移文件目录
const migrationsDir = path.join(__dirname);

/**
 * 运行迁移
 */
async function runMigrations() {
  try {
    // 确保迁移记录表存在
    await ensureMigrationsTable();
    
    // 获取已执行的迁移
    const executedMigrations = await getExecutedMigrations();
    
    // 获取所有迁移文件
    const migrationFiles = fs.readdirSync(migrationsDir)
      .filter(file => file.match(/^\d{12}_.*\.js$/))
      .sort();
    
    // 筛选未执行的迁移
    const pendingMigrations = migrationFiles.filter(file => !executedMigrations.includes(file));
    
    if (pendingMigrations.length === 0) {
      logger.info('没有待执行的迁移');
      process.exit(0);
    }
    
    logger.info(`发现 ${pendingMigrations.length} 个待执行的迁移`);
    
    // 执行迁移
    for (const file of pendingMigrations) {
      logger.info(`执行迁移: ${file}`);
      
      const migration = require(path.join(migrationsDir, file));
      
      try {
        await migration.up(knex);
        await recordMigration(file);
        logger.info(`迁移 ${file} 成功`);
      } catch (err) {
        logger.error(`迁移 ${file} 失败: ${err.message}`);
        process.exit(1);
      }
    }
    
    logger.info('所有迁移执行完成');
    process.exit(0);
  } catch (err) {
    logger.error(`执行迁移时出错: ${err.message}`);
    process.exit(1);
  }
}

/**
 * 确保迁移记录表存在
 */
async function ensureMigrationsTable() {
  const exists = await knex.schema.hasTable('migrations');
  
  if (!exists) {
    logger.info('创建迁移记录表');
    await knex.schema.createTable('migrations', table => {
      table.increments('id').primary();
      table.string('name').notNullable();
      table.timestamp('executed_at').defaultTo(knex.fn.now());
    });
  }
}

/**
 * 获取已执行的迁移
 */
async function getExecutedMigrations() {
  const migrations = await knex('migrations').select('name');
  return migrations.map(m => m.name);
}

/**
 * 记录迁移
 */
async function recordMigration(name) {
  await knex('migrations').insert({ name });
}

// 执行迁移
runMigrations();
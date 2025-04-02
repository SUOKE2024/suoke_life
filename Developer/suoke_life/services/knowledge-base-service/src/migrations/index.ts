/**
 * 数据库迁移管理
 */
import mongoose from 'mongoose';
import { readdir } from 'fs/promises';
import { join } from 'path';
import logger from '../utils/logger';

interface Migration {
  version: number;
  name: string;
  up: () => Promise<void>;
  down: () => Promise<void>;
}

interface MigrationRecord {
  version: number;
  name: string;
  appliedAt: Date;
}

// 定义迁移记录模型
const MigrationModel = mongoose.model<MigrationRecord & mongoose.Document>(
  'Migration',
  new mongoose.Schema({
    version: { type: Number, required: true, unique: true },
    name: { type: String, required: true },
    appliedAt: { type: Date, default: Date.now }
  })
);

/**
 * 迁移管理器
 */
export class MigrationManager {
  private migrations: Migration[] = [];
  private migrationsDir: string;
  
  constructor(migrationsDir: string = join(__dirname)) {
    this.migrationsDir = migrationsDir;
  }
  
  /**
   * 加载迁移脚本
   */
  async loadMigrations(): Promise<void> {
    try {
      // 读取迁移目录中的所有文件
      const files = await readdir(this.migrationsDir);
      
      // 过滤出迁移脚本文件
      const migrationFiles = files.filter(file => 
        file.endsWith('.js') && 
        file !== 'index.js' && 
        !file.endsWith('.map.js') &&
        !file.endsWith('.test.js')
      );
      
      // 加载每个迁移脚本
      this.migrations = [];
      for (const file of migrationFiles) {
        const migrationModule = await import(join(this.migrationsDir, file));
        const migration = migrationModule.default as Migration;
        
        if (migration && typeof migration.up === 'function' && typeof migration.down === 'function') {
          this.migrations.push(migration);
        } else {
          logger.warn(`无效的迁移脚本: ${file}`);
        }
      }
      
      // 根据版本号排序
      this.migrations.sort((a, b) => a.version - b.version);
      
      logger.info(`已加载 ${this.migrations.length} 个迁移脚本`);
    } catch (error) {
      logger.error('加载迁移脚本失败', { error: (error as Error).message });
      throw error;
    }
  }
  
  /**
   * 获取已应用的迁移列表
   */
  async getAppliedMigrations(): Promise<MigrationRecord[]> {
    return MigrationModel.find().sort({ version: 1 });
  }
  
  /**
   * 应用待处理的迁移
   */
  async migrate(): Promise<void> {
    try {
      // 加载迁移脚本
      await this.loadMigrations();
      
      // 获取已应用的迁移
      const appliedMigrations = await this.getAppliedMigrations();
      const appliedVersions = new Set(appliedMigrations.map(m => m.version));
      
      // 找出待应用的迁移
      const pendingMigrations = this.migrations.filter(m => !appliedVersions.has(m.version));
      
      if (pendingMigrations.length === 0) {
        logger.info('没有待应用的迁移');
        return;
      }
      
      logger.info(`开始应用 ${pendingMigrations.length} 个迁移`);
      
      // 依次应用迁移
      for (const migration of pendingMigrations) {
        logger.info(`应用迁移: ${migration.name} (${migration.version})`);
        
        // 执行迁移
        await migration.up();
        
        // 记录已应用的迁移
        await MigrationModel.create({
          version: migration.version,
          name: migration.name,
          appliedAt: new Date()
        });
        
        logger.info(`迁移 ${migration.name} 已应用`);
      }
      
      logger.info('所有迁移已成功应用');
    } catch (error) {
      logger.error('迁移失败', { error: (error as Error).message });
      throw error;
    }
  }
  
  /**
   * 回滚迁移
   * @param steps 回滚的步数，默认为1
   */
  async rollback(steps: number = 1): Promise<void> {
    try {
      // 加载迁移脚本
      await this.loadMigrations();
      
      // 获取已应用的迁移
      const appliedMigrations = await this.getAppliedMigrations();
      
      // 确定要回滚的迁移
      const migrationsToRollback = appliedMigrations
        .slice(-steps)
        .sort((a, b) => b.version - a.version); // 倒序，先回滚最新的
      
      if (migrationsToRollback.length === 0) {
        logger.info('没有可回滚的迁移');
        return;
      }
      
      logger.info(`开始回滚 ${migrationsToRollback.length} 个迁移`);
      
      // 依次回滚迁移
      for (const record of migrationsToRollback) {
        const migration = this.migrations.find(m => m.version === record.version);
        
        if (!migration) {
          logger.warn(`未找到迁移脚本: ${record.name} (${record.version})`);
          continue;
        }
        
        logger.info(`回滚迁移: ${migration.name} (${migration.version})`);
        
        // 执行回滚
        await migration.down();
        
        // 删除迁移记录
        await MigrationModel.deleteOne({ version: record.version });
        
        logger.info(`迁移 ${migration.name} 已回滚`);
      }
      
      logger.info('所有指定的迁移已成功回滚');
    } catch (error) {
      logger.error('回滚失败', { error: (error as Error).message });
      throw error;
    }
  }
}

export default new MigrationManager();
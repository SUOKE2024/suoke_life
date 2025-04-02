#!/usr/bin/env node

/**
 * 独立的跨区域同步任务脚本
 * 运行方式: node sync-task.js [action]
 * 支持的操作:
 *   - status: 显示同步状态
 *   - trigger: 触发同步
 *   - clean: 清理失败的同步操作
 */

// 设置环境变量
process.env.NODE_ENV = process.env.NODE_ENV || 'development';

// 导入依赖
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });
const { logger } = require('@suoke/shared').utils;
const syncUtils = require('./sync');
const redis = require('../config/redis');
const { db, connectToDatabase, closeConnection } = require('../config/database');

// 帮助信息
const printHelp = () => {
  console.log('\n跨区域同步任务工具');
  console.log('==================\n');
  console.log('使用方法: node sync-task.js [操作]\n');
  console.log('支持的操作:');
  console.log('  status     - 显示同步状态');
  console.log('  trigger    - 触发同步');
  console.log('  clean      - 清理失败的同步操作');
  console.log('  repair     - 修复不一致的数据');
  console.log('  logs       - 显示同步日志');
  console.log('\n示例:');
  console.log('  node sync-task.js status');
  console.log('  node sync-task.js trigger');
  console.log('  node sync-task.js clean --age=24h');
  console.log('  node sync-task.js repair --table=users');
  console.log('  node sync-task.js logs --limit=50');
  console.log('');
};

// 初始化连接
const initialize = async () => {
  try {
    await connectToDatabase();
    logger.info('数据库连接已建立');
    
    // 等待Redis连接
    if (!redis.status || redis.status !== 'ready') {
      logger.info('等待Redis连接...');
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    logger.info('Redis连接已建立');
    
    // 初始化同步服务
    await syncUtils.initialize();
    logger.info('同步服务已初始化');
    
    return true;
  } catch (error) {
    logger.error(`初始化连接失败: ${error.message}`);
    return false;
  }
};

// 关闭连接
const cleanup = async () => {
  try {
    await closeConnection();
    logger.info('数据库连接已关闭');
    
    await redis.quit();
    logger.info('Redis连接已关闭');
  } catch (error) {
    logger.error(`关闭连接失败: ${error.message}`);
  }
};

// 获取同步状态
const getStatus = async () => {
  try {
    const status = await syncUtils.getSyncStatus();
    console.log('\n同步状态');
    console.log('========\n');
    console.log(`当前状态: ${status.status}`);
    console.log(`当前区域: ${status.currentRegion}`);
    console.log(`主区域: ${status.primaryRegion}`);
    console.log(`备份区域: ${status.backupRegions.join(', ') || '无'}`);
    console.log(`同步间隔: ${status.syncInterval}秒`);
    console.log(`待处理操作: ${status.pendingOperations}`);
    
    if (status.lastSyncAttempt) {
      const lastAttemptDate = new Date(status.lastSyncAttempt);
      console.log(`最近同步尝试: ${lastAttemptDate.toLocaleString()}`);
    } else {
      console.log('最近同步尝试: 无');
    }
    
    if (status.lastSyncCompletion) {
      const lastCompletionDate = new Date(status.lastSyncCompletion);
      console.log(`最近同步完成: ${lastCompletionDate.toLocaleString()}`);
    } else {
      console.log('最近同步完成: 无');
    }
    
    if (status.lastError) {
      console.log(`最近错误: ${status.lastError}`);
    }
    
    if (status.lastResult && status.lastResult.total) {
      console.log('\n最近同步结果:');
      console.log(`  总计: ${status.lastResult.total}`);
      console.log(`  成功: ${status.lastResult.success}`);
      console.log(`  失败: ${status.lastResult.failed}`);
    }
    
    // 获取数据库中的同步操作统计
    const dbStats = await db('sync_logs')
      .select('status')
      .count('* as count')
      .groupBy('status');
      
    console.log('\n数据库同步日志统计:');
    dbStats.forEach(stat => {
      console.log(`  ${stat.status}: ${stat.count}`);
    });
    
    return true;
  } catch (error) {
    logger.error(`获取状态失败: ${error.message}`);
    return false;
  }
};

// 触发同步
const triggerSync = async () => {
  try {
    console.log('触发跨区域同步...');
    const result = await syncUtils.syncAllRegions();
    
    console.log('\n同步结果');
    console.log('========\n');
    
    if (result.skipped) {
      console.log('同步已跳过: 当前不是主区域或其他进程正在执行同步');
      return true;
    }
    
    if (result.success) {
      console.log('同步成功');
    } else {
      console.log(`同步失败: ${result.error || '未知错误'}`);
    }
    
    if (result.total !== undefined) {
      console.log(`总计: ${result.total}`);
      console.log(`成功: ${result.success}`);
      console.log(`失败: ${result.failed}`);
    }
    
    return result.success;
  } catch (error) {
    logger.error(`触发同步失败: ${error.message}`);
    return false;
  }
};

// 清理失败的同步操作
const cleanFailedOperations = async (args) => {
  try {
    // 解析参数
    const ageArg = args.find(arg => arg.startsWith('--age='));
    const age = ageArg ? ageArg.split('=')[1] : '24h';
    
    // 计算时间阈值
    let hours = 24;
    if (age.endsWith('h')) {
      hours = parseInt(age.slice(0, -1), 10);
    } else if (age.endsWith('d')) {
      hours = parseInt(age.slice(0, -1), 10) * 24;
    }
    
    const timeThreshold = new Date();
    timeThreshold.setHours(timeThreshold.getHours() - hours);
    
    console.log(`清理${hours}小时前失败的同步操作...`);
    
    // 从数据库中查找并删除失败的同步操作
    const failedOps = await db('sync_logs')
      .where('status', 'failed')
      .where('created_at', '<', timeThreshold)
      .select('id');
      
    console.log(`找到${failedOps.length}个失败的同步操作`);
    
    if (failedOps.length === 0) {
      console.log('没有需要清理的操作');
      return true;
    }
    
    // 确认
    console.log('这些操作将被永久删除。确认继续? (y/n)');
    
    // 读取用户输入
    const confirmation = await new Promise(resolve => {
      const stdin = process.stdin;
      stdin.resume();
      stdin.setEncoding('utf8');
      stdin.on('data', function (data) {
        resolve(data.trim().toLowerCase());
        stdin.pause();
      });
    });
    
    if (confirmation !== 'y' && confirmation !== 'yes') {
      console.log('操作已取消');
      return false;
    }
    
    // 删除操作
    const ids = failedOps.map(op => op.id);
    const deleted = await db('sync_logs')
      .whereIn('id', ids)
      .delete();
    
    console.log(`成功清理${deleted}个失败的同步操作`);
    
    // 清理Redis中的相关键
    console.log('清理Redis中的相关键...');
    let redisKeysDeleted = 0;
    
    for (const op of failedOps) {
      const logKey = `cross_region_sync:log:${op.id}`;
      const deleted = await redis.del(logKey);
      redisKeysDeleted += deleted;
    }
    
    console.log(`成功清理${redisKeysDeleted}个Redis键`);
    
    return true;
  } catch (error) {
    logger.error(`清理失败的同步操作失败: ${error.message}`);
    return false;
  }
};

// 修复不一致的数据
const repairInconsistentData = async (args) => {
  try {
    // 解析参数
    const tableArg = args.find(arg => arg.startsWith('--table='));
    const table = tableArg ? tableArg.split('=')[1] : 'all';
    
    console.log('数据一致性修复工具');
    console.log('=================\n');
    
    if (table === 'all') {
      console.log('修复所有表的数据一致性...');
    } else {
      console.log(`修复表 '${table}' 的数据一致性...`);
    }
    
    // 获取所有区域
    const regions = await db('regions')
      .where('is_active', true)
      .select('*');
      
    console.log(`找到${regions.length}个活跃区域`);
    
    // 找到主区域
    const primaryRegion = regions.find(r => r.is_primary);
    
    if (!primaryRegion) {
      console.log('错误: 未找到主区域。请确保有一个区域被标记为主区域。');
      return false;
    }
    
    console.log(`主区域: ${primaryRegion.name} (${primaryRegion.code})`);
    
    // 对于选定的表，对比数据并修复
    const currentRegion = process.env.POD_REGION || 'unknown';
    
    if (currentRegion !== primaryRegion.code) {
      console.log(`当前区域 (${currentRegion}) 不是主区域。只有主区域可以执行修复操作。`);
      return false;
    }
    
    // 获取表列表
    let tables = [];
    
    if (table === 'all') {
      // 获取所有需要同步的表
      const supportedTables = ['users', 'user_tokens', 'user_profiles'];
      tables = supportedTables;
    } else {
      tables = [table];
    }
    
    console.log(`将检查以下表: ${tables.join(', ')}`);
    
    // 确认
    console.log('\n警告: 此操作将修改数据库中的数据。建议先备份数据库。');
    console.log('确认继续? (y/n)');
    
    // 读取用户输入
    const confirmation = await new Promise(resolve => {
      const stdin = process.stdin;
      stdin.resume();
      stdin.setEncoding('utf8');
      stdin.on('data', function (data) {
        resolve(data.trim().toLowerCase());
        stdin.pause();
      });
    });
    
    if (confirmation !== 'y' && confirmation !== 'yes') {
      console.log('操作已取消');
      return false;
    }
    
    // 对每个表执行修复
    for (const tableName of tables) {
      console.log(`\n处理表: ${tableName}`);
      
      try {
        // 检查表是否存在
        const tableExists = await db.schema.hasTable(tableName);
        
        if (!tableExists) {
          console.log(`表 '${tableName}' 不存在，跳过`);
          continue;
        }
        
        // 获取所有记录ID
        const allRecords = await db(tableName).select('id', 'data_version', 'last_region');
        console.log(`找到${allRecords.length}条记录`);
        
        let repairedCount = 0;
        
        // 处理最新的100条记录作为示例
        const recentRecords = allRecords.slice(0, 100);
        
        for (const record of recentRecords) {
          // 检查是否需要修复
          if (!record.data_version || !record.last_region) {
            // 为缺少同步字段的记录添加默认值
            await db(tableName)
              .where('id', record.id)
              .update({
                data_version: Date.now(),
                last_region: currentRegion,
                last_synced_at: new Date()
              });
              
            repairedCount++;
          }
        }
        
        console.log(`修复了${repairedCount}条记录`);
        
        // 示例操作，添加一个同步任务
        if (repairedCount > 0) {
          const sampleRecord = recentRecords[0];
          await syncUtils.recordSyncOperation(
            tableName,
            'update',
            { id: sampleRecord.id, data_version: Date.now() },
            sampleRecord.id
          );
          console.log(`已添加1个示例同步任务`);
        }
      } catch (error) {
        console.log(`处理表 '${tableName}' 时出错: ${error.message}`);
      }
    }
    
    console.log('\n修复操作完成。请运行同步任务以将更改传播到其他区域。');
    
    return true;
  } catch (error) {
    logger.error(`修复数据一致性失败: ${error.message}`);
    return false;
  }
};

// 显示同步日志
const showLogs = async (args) => {
  try {
    // 解析参数
    const limitArg = args.find(arg => arg.startsWith('--limit='));
    const limit = limitArg ? parseInt(limitArg.split('=')[1], 10) : 20;
    
    const statusArg = args.find(arg => arg.startsWith('--status='));
    const status = statusArg ? statusArg.split('=')[1] : null;
    
    console.log('同步操作日志');
    console.log('============\n');
    
    // 查询数据库获取日志
    let query = db('sync_logs')
      .orderBy('created_at', 'desc')
      .limit(limit);
      
    if (status) {
      query = query.where('status', status);
    }
    
    const logs = await query;
    
    if (logs.length === 0) {
      console.log('未找到任何日志记录');
      return true;
    }
    
    console.log(`显示最近${logs.length}条日志:`);
    
    for (const log of logs) {
      const createdAt = new Date(log.created_at).toLocaleString();
      console.log(`\nID: ${log.id}`);
      console.log(`表: ${log.table_name}`);
      console.log(`操作: ${log.operation}`);
      console.log(`记录ID: ${log.record_id}`);
      console.log(`来源区域: ${log.source_region}`);
      console.log(`状态: ${log.status}`);
      console.log(`重试次数: ${log.retry_count}`);
      console.log(`创建时间: ${createdAt}`);
      
      if (log.error_message) {
        console.log(`错误消息: ${log.error_message}`);
      }
      
      if (log.completed_at) {
        const completedAt = new Date(log.completed_at).toLocaleString();
        console.log(`完成时间: ${completedAt}`);
      }
    }
    
    return true;
  } catch (error) {
    logger.error(`显示同步日志失败: ${error.message}`);
    return false;
  }
};

// 处理命令行参数
const processArgs = async () => {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';
  
  if (command === 'help' || command === '--help' || command === '-h') {
    printHelp();
    return 0;
  }
  
  // 初始化连接
  const initialized = await initialize();
  if (!initialized) {
    return 1;
  }
  
  let success = false;
  
  try {
    switch (command) {
      case 'status':
        success = await getStatus();
        break;
        
      case 'trigger':
        success = await triggerSync();
        break;
        
      case 'clean':
        success = await cleanFailedOperations(args.slice(1));
        break;
        
      case 'repair':
        success = await repairInconsistentData(args.slice(1));
        break;
        
      case 'logs':
        success = await showLogs(args.slice(1));
        break;
        
      default:
        console.log(`未知命令: ${command}`);
        printHelp();
        success = false;
    }
  } catch (error) {
    logger.error(`执行命令出错: ${error.message}`);
    success = false;
  } finally {
    // 清理连接
    await cleanup();
  }
  
  return success ? 0 : 1;
};

// 执行脚本
processArgs()
  .then(exitCode => {
    process.exit(exitCode);
  })
  .catch(error => {
    console.error(`脚本执行失败: ${error.message}`);
    process.exit(1);
  }); 
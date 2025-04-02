/**
 * 数据库服务单元测试
 */
const dbService = require('../../../src/models/db.service');

// 模拟mysql2/promise
jest.mock('mysql2/promise', () => {
  const mockConnection = {
    execute: jest.fn(),
    beginTransaction: jest.fn(),
    commit: jest.fn(),
    rollback: jest.fn(),
    release: jest.fn()
  };
  
  return {
    createPool: jest.fn().mockReturnValue({
      getConnection: jest.fn().mockResolvedValue(mockConnection),
      execute: jest.fn(),
      end: jest.fn().mockResolvedValue(true)
    })
  };
});

jest.mock('../../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
  }
}));

jest.mock('../../../src/config', () => ({
  database: {
    host: 'localhost',
    port: 3306,
    user: 'test',
    password: 'test',
    name: 'test_db',
    connectionLimit: 5
  }
}));

describe('数据库服务', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // 重置服务状态
    dbService.pool = null;
    dbService.initialized = false;
  });

  describe('connect', () => {
    test('应成功连接数据库', async () => {
      await dbService.connect();
      
      // 验证连接池是否已创建
      const mysql = require('mysql2/promise');
      expect(mysql.createPool).toHaveBeenCalledWith(expect.objectContaining({
        host: 'localhost',
        user: 'test',
        database: 'test_db'
      }));
      
      // 验证是否测试了连接
      expect(dbService.pool.getConnection).toHaveBeenCalled();
      
      // 验证初始化标志
      expect(dbService.initialized).toBe(true);
    });
    
    test('已初始化时不应重新连接', async () => {
      // 首次连接
      await dbService.connect();
      const mysql = require('mysql2/promise');
      expect(mysql.createPool).toHaveBeenCalledTimes(1);
      
      // 重置计数
      mysql.createPool.mockClear();
      
      // 再次连接
      await dbService.connect();
      
      // 应该不再创建连接池
      expect(mysql.createPool).not.toHaveBeenCalled();
    });
  });

  describe('disconnect', () => {
    test('应成功断开连接', async () => {
      // 首先连接
      await dbService.connect();
      
      // 然后断开
      await dbService.disconnect();
      
      // 验证调用了end方法
      expect(dbService.pool.end).toHaveBeenCalled();
      
      // 验证状态重置
      expect(dbService.pool).toBeNull();
      expect(dbService.initialized).toBe(false);
    });
    
    test('未连接时应静默处理', async () => {
      // 确保未连接
      dbService.pool = null;
      
      // 尝试断开连接
      await dbService.disconnect();
      
      // 不应引发错误
      const { logger } = require('../../../src/utils/logger');
      expect(logger.error).not.toHaveBeenCalled();
    });
  });

  describe('query', () => {
    test('应执行SQL查询并返回结果', async () => {
      // 模拟执行结果
      const mockRows = [{ id: 1, name: '测试' }];
      dbService.pool = {
        execute: jest.fn().mockResolvedValue([mockRows, null])
      };
      dbService.initialized = true;
      
      // 执行查询
      const result = await dbService.query('SELECT * FROM test WHERE id = ?', [1]);
      
      // 验证结果
      expect(result).toEqual(mockRows);
      expect(dbService.pool.execute).toHaveBeenCalledWith('SELECT * FROM test WHERE id = ?', [1]);
    });
    
    test('未初始化时应自动连接', async () => {
      // 确保未初始化
      dbService.initialized = false;
      dbService.pool = null;
      
      // 模拟连接和查询
      dbService.connect = jest.fn().mockResolvedValue();
      const mockExecute = jest.fn().mockResolvedValue([[], null]);
      dbService.pool = { execute: mockExecute };
      
      // 执行查询
      await dbService.query('SELECT 1');
      
      // 验证连接被调用
      expect(dbService.connect).toHaveBeenCalled();
    });
    
    test('查询错误时应抛出异常', async () => {
      // 模拟查询错误
      dbService.initialized = true;
      const mockError = new Error('数据库错误');
      dbService.pool = {
        execute: jest.fn().mockRejectedValue(mockError)
      };
      
      // 执行查询并捕获错误
      await expect(dbService.query('SELECT bad query')).rejects.toThrow('数据库错误');
      
      // 验证错误日志
      const { logger } = require('../../../src/utils/logger');
      expect(logger.error).toHaveBeenCalledWith('SQL查询执行失败', expect.any(Object));
    });
  });

  describe('CRUD操作', () => {
    beforeEach(() => {
      // 设置已初始化状态
      dbService.initialized = true;
      
      // 模拟query方法
      dbService.query = jest.fn();
    });
    
    test('getById应查询单条记录', async () => {
      // 模拟查询结果
      const mockRecord = { id: 'test1', name: '测试记录' };
      dbService.query.mockResolvedValue([mockRecord]);
      
      // 执行方法
      const result = await dbService.getById('test_table', 'test1');
      
      // 验证查询和结果
      expect(dbService.query).toHaveBeenCalledWith(
        expect.stringContaining('SELECT * FROM test_table WHERE id = ?'),
        ['test1']
      );
      expect(result).toEqual(mockRecord);
    });
    
    test('create应插入记录并返回', async () => {
      // 模拟数据
      const mockData = { name: '新记录', value: 123 };
      
      // 执行方法
      await dbService.create('test_table', mockData);
      
      // 验证查询
      expect(dbService.query).toHaveBeenCalledWith(
        expect.stringContaining('INSERT INTO test_table'),
        expect.any(Array)
      );
      
      // 验证UUID和时间戳
      const queryCall = dbService.query.mock.calls[0];
      const values = queryCall[1];
      expect(values).toContain(mockData.name);
      expect(values).toContain(mockData.value);
    });
    
    test('update应更新记录并返回', async () => {
      // 模拟数据
      const mockData = { name: '更新的名称', value: 456 };
      
      // 执行方法
      await dbService.update('test_table', 'test1', mockData);
      
      // 验证查询
      expect(dbService.query).toHaveBeenCalledWith(
        expect.stringContaining('UPDATE test_table SET'),
        expect.any(Array)
      );
      
      // 验证更新数据和ID
      const queryCall = dbService.query.mock.calls[0];
      const values = queryCall[1];
      expect(values).toContain(mockData.name);
      expect(values).toContain(mockData.value);
      expect(values).toContain('test1'); // ID
    });
    
    test('delete应删除记录并返回布尔值', async () => {
      // 模拟删除成功
      dbService.query.mockResolvedValue({ affectedRows: 1 });
      
      // 执行方法
      const result = await dbService.delete('test_table', 'test1');
      
      // 验证查询和结果
      expect(dbService.query).toHaveBeenCalledWith(
        expect.stringContaining('DELETE FROM test_table WHERE id = ?'),
        ['test1']
      );
      expect(result).toBe(true);
      
      // 模拟删除失败
      dbService.query.mockResolvedValue({ affectedRows: 0 });
      const result2 = await dbService.delete('test_table', 'nonexistent');
      expect(result2).toBe(false);
    });
    
    test('find应根据条件查询记录', async () => {
      // 模拟条件和选项
      const conditions = { status: 'active', type: 'user' };
      const options = { sort: 'created_at DESC', limit: 10, offset: 20 };
      
      // 执行方法
      await dbService.find('test_table', conditions, options);
      
      // 验证查询包含WHERE条件
      expect(dbService.query).toHaveBeenCalledWith(
        expect.stringMatching(/WHERE.*status.*AND.*type/),
        expect.arrayContaining(['active', 'user'])
      );
      
      // 验证排序和分页
      const query = dbService.query.mock.calls[0][0];
      expect(query).toMatch(/ORDER BY created_at DESC/);
      expect(query).toMatch(/LIMIT 10/);
      expect(query).toMatch(/OFFSET 20/);
    });
  });

  describe('transaction', () => {
    test('应在事务中执行回调', async () => {
      // 模拟连接和事务方法
      const mockConnection = {
        beginTransaction: jest.fn().mockResolvedValue(undefined),
        commit: jest.fn().mockResolvedValue(undefined),
        rollback: jest.fn().mockResolvedValue(undefined),
        release: jest.fn()
      };
      
      dbService.pool = {
        getConnection: jest.fn().mockResolvedValue(mockConnection)
      };
      dbService.initialized = true;
      
      // 模拟回调
      const mockCallback = jest.fn().mockResolvedValue('事务结果');
      
      // 执行事务
      const result = await dbService.transaction(mockCallback);
      
      // 验证事务流程
      expect(dbService.pool.getConnection).toHaveBeenCalled();
      expect(mockConnection.beginTransaction).toHaveBeenCalled();
      expect(mockCallback).toHaveBeenCalledWith(mockConnection);
      expect(mockConnection.commit).toHaveBeenCalled();
      expect(mockConnection.release).toHaveBeenCalled();
      expect(result).toBe('事务结果');
    });
    
    test('事务失败时应回滚', async () => {
      // 模拟连接
      const mockConnection = {
        beginTransaction: jest.fn().mockResolvedValue(undefined),
        commit: jest.fn().mockResolvedValue(undefined),
        rollback: jest.fn().mockResolvedValue(undefined),
        release: jest.fn()
      };
      
      dbService.pool = {
        getConnection: jest.fn().mockResolvedValue(mockConnection)
      };
      dbService.initialized = true;
      
      // 模拟回调失败
      const mockError = new Error('事务错误');
      const mockCallback = jest.fn().mockRejectedValue(mockError);
      
      // 执行事务并捕获错误
      await expect(dbService.transaction(mockCallback)).rejects.toThrow('事务错误');
      
      // 验证回滚
      expect(mockConnection.rollback).toHaveBeenCalled();
      expect(mockConnection.commit).not.toHaveBeenCalled();
      expect(mockConnection.release).toHaveBeenCalled();
    });
  });
}); 
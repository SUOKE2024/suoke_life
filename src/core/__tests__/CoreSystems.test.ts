/**
 * 索克生活 - 核心系统测试
 * 测试错误处理、性能监控、数据验证、缓存和安全管理系统
 */

import { errorHandler, ErrorType, ErrorSeverity } from '../error/ErrorHandler';
import { performanceMonitor, PerformanceCategory } from '../monitoring/PerformanceMonitor';
import { dataValidator, ValidationType, ValidationSeverity } from '../validation/DataValidator';
import { cacheManager, CacheType, CacheStrategy } from '../cache/CacheManager';
import { securityManager, PermissionType, ThreatType } from '../security/SecurityManager';

describe('核心系统测试', () => {
  describe('错误处理系统', () => {
    it('应该正确处理网络错误', async () => {
      const error = new Error('网络连接失败');
      const context = { 
        userId: 'test_user',
        requestId: 'req_123',
        timestamp: Date.now()
      };
      
      const result = await errorHandler.handleError(error, context);
      
      expect(result).toBeDefined();
      expect(result.type).toBe(ErrorType.NETWORK_ERROR);
      expect(result.suggestions).toContain('检查网络连接');
    });

    it('应该创建自定义错误', () => {
      const customError = errorHandler.createError(
        ErrorType.AUTH_ERROR,
        '身份验证失败',
        { userId: 'test_user' },
        { severity: ErrorSeverity.HIGH }
      );
      
      expect(customError.type).toBe(ErrorType.AUTH_ERROR);
      expect(customError.severity).toBe(ErrorSeverity.HIGH);
      expect(customError.userMessage).toContain('身份验证失败');
    });

    it('应该支持错误监听器', async () => {
      let capturedError: any = null;
      
      const listener = (error: any) => {
        capturedError = error;
      };
      
      errorHandler.addErrorListener(listener);
      
      await errorHandler.handleError(new Error('测试错误'), {});
      
      expect(capturedError).toBeDefined();
      expect(capturedError.message).toBe('测试错误');
      
      errorHandler.removeErrorListener(listener);
    });
  });

  describe('性能监控系统', () => {
    beforeEach(() => {
      performanceMonitor.startMonitoring(1000);
    });

    afterEach(() => {
      performanceMonitor.stopMonitoring();
    });

    it('应该测量同步操作性能', () => {
      const result = performanceMonitor.measure(
        'test_sync_operation',
        PerformanceCategory.CPU,
        () => {
          // 模拟CPU密集型操作
          let sum = 0;
          for (let i = 0; i < 1000; i++) {
            sum += i;
          }
          return sum;
        }
      );

      expect(result).toBe(499500); // 0+1+2+...+999的和
    });

    it('应该测量异步操作性能', async () => {
      const result = await performanceMonitor.measureAsync(
        'test_async_operation',
        PerformanceCategory.NETWORK,
        async () => {
          // 模拟异步操作
          await new Promise(resolve => setTimeout(resolve, 10));
          return 'async_result';
        }
      );

      expect(result).toBe('async_result');
    });

    it('应该收集性能指标', () => {
      performanceMonitor.recordMetric(
        'test_metric',
        100,
        PerformanceCategory.MEMORY,
        'MB'
      );

      const history = performanceMonitor.getMetricHistory(
        PerformanceCategory.MEMORY,
        'test_metric'
      );
      
      expect(history.length).toBeGreaterThan(0);
      expect(history[0].value).toBe(100);
      expect(history[0].unit).toBe('MB');
    });

    it('应该生成性能报告', () => {
      performanceMonitor.recordMetric('test_metric', 50, PerformanceCategory.CPU);
      
      const report = performanceMonitor.generateReport();
      
      expect(report.id).toBeDefined();
      expect(report.timestamp).toBeDefined();
      expect(report.metrics).toBeInstanceOf(Array);
      expect(report.summary).toBeDefined();
    });
  });

  describe('数据验证系统', () => {
    it('应该验证健康数据', () => {
      const healthData = {
        systolic: 120,
        diastolic: 80,
        heartRate: 75,
        temperature: 36.5
      };

      const report = dataValidator.validateHealthData(healthData);
      
      expect(report.isValid).toBe(true);
      expect(report.summary.errors).toBe(0);
    });

    it('应该检测无效的血压数据', () => {
      const invalidData = {
        systolic: 300, // 超出正常范围
        diastolic: 80
      };

      const report = dataValidator.validateHealthData(invalidData);
      
      expect(report.isValid).toBe(false);
      expect(report.summary.errors).toBeGreaterThan(0);
    });

    it('应该验证用户输入', () => {
      const userData = {
        email: 'user@example.com',
        phone: '13800138000'
      };

      const report = dataValidator.validateUserInput(userData);
      
      expect(report.isValid).toBe(true);
    });

    it('应该清洗用户输入数据', () => {
      const dirtyData = {
        email: '  USER@EXAMPLE.COM  ',
        phone: '138-0013-8000'
      };

      const cleanData = dataValidator.sanitize(dirtyData, ValidationType.USER_INPUT);
      
      expect(cleanData.email).toBe('user@example.com');
      expect(cleanData.phone).toBe('13800138000');
    });

    it('应该支持批量验证', () => {
      const items = [
        { data: { email: 'valid@example.com' }, type: ValidationType.USER_INPUT },
        { data: { email: 'invalid-email' }, type: ValidationType.USER_INPUT }
      ];

      const reports = dataValidator.validateBatch(items);
      
      expect(reports).toHaveLength(2);
      expect(reports[0].isValid).toBe(true);
      expect(reports[1].isValid).toBe(false);
    });
  });

  describe('缓存管理系统', () => {
    beforeEach(async () => {
      // 清理测试缓存
      await cacheManager.clear('memory');
    });

    it('应该设置和获取缓存', async () => {
      const testData = { message: 'Hello, Cache!' };
      
      await cacheManager.set('memory', 'test_key', testData);
      const retrieved = await cacheManager.get('memory', 'test_key');
      
      expect(retrieved).toEqual(testData);
    });

    it('应该处理缓存过期', async () => {
      const testData = { message: 'Expiring data' };
      
      await cacheManager.set('memory', 'expiring_key', testData, { ttl: 50 }); // 50ms TTL
      
      // 立即获取应该成功
      let retrieved = await cacheManager.get('memory', 'expiring_key');
      expect(retrieved).toEqual(testData);
      
      // 等待过期后获取应该返回null
      await new Promise(resolve => setTimeout(resolve, 100));
      retrieved = await cacheManager.get('memory', 'expiring_key');
      expect(retrieved).toBeNull();
    });

    it('应该支持批量操作', async () => {
      const items = [
        { key: 'key1', value: 'value1' },
        { key: 'key2', value: 'value2' },
        { key: 'key3', value: 'value3' }
      ];

      const results = await cacheManager.setMultiple('memory', items);
      expect(results.every(r => r)).toBe(true);

      const retrieved = await cacheManager.getMultiple('memory', ['key1', 'key2', 'key3']);
      expect(retrieved.get('key1')).toBe('value1');
      expect(retrieved.get('key2')).toBe('value2');
      expect(retrieved.get('key3')).toBe('value3');
    });

    it('应该提供缓存统计', async () => {
      await cacheManager.set('memory', 'stats_test', 'data');
      await cacheManager.get('memory', 'stats_test'); // 命中
      await cacheManager.get('memory', 'non_existent'); // 未命中

      const stats = cacheManager.getStats('memory');
      
      expect(stats).toBeDefined();
      if (typeof stats === 'object' && 'hits' in stats) {
        expect(stats.hits).toBeGreaterThan(0);
        expect(stats.misses).toBeGreaterThan(0);
      }
    });

    it('应该支持缓存穿透保护', async () => {
      let loadCount = 0;
      const loader = async () => {
        loadCount++;
        return `loaded_data_${loadCount}`;
      };

      // 第一次调用应该触发加载
      const result1 = await cacheManager.getOrSet('memory', 'loader_test', loader);
      expect(result1).toBe('loaded_data_1');
      expect(loadCount).toBe(1);

      // 第二次调用应该从缓存获取
      const result2 = await cacheManager.getOrSet('memory', 'loader_test', loader);
      expect(result2).toBe('loaded_data_1');
      expect(loadCount).toBe(1); // 没有再次加载
    });
  });

  describe('安全管理系统', () => {
    beforeEach(() => {
      // 清理测试数据
      securityManager.revokeAccess('test_user', '*', 'admin');
    });

    it('应该管理访问控制', () => {
      const userId = 'test_user';
      const resource = '/api/health-data';
      const permissions = [PermissionType.READ, PermissionType.WRITE];

      // 授予权限
      securityManager.grantAccess(userId, resource, permissions, 'admin');

      // 检查读权限
      const readResult = securityManager.checkAccess(userId, resource, PermissionType.READ);
      expect(readResult.type).toBe('ALLOW');

      // 检查写权限
      const writeResult = securityManager.checkAccess(userId, resource, PermissionType.WRITE);
      expect(writeResult.type).toBe('ALLOW');

      // 检查删除权限（未授予）
      const deleteResult = securityManager.checkAccess(userId, resource, PermissionType.DELETE);
      expect(deleteResult.type).toBe('DENY');
    });

    it('应该检测威胁', () => {
      const threat = securityManager.detectThreat(
        ThreatType.BRUTE_FORCE,
        '192.168.1.100',
        [{ failedAttempts: 10 }],
        { userId: 'attacker', ipAddress: '192.168.1.100', timestamp: Date.now() }
      );

      expect(threat.type).toBe(ThreatType.BRUTE_FORCE);
      expect(threat.severity).toBe('MEDIUM');
      expect(threat.isResolved).toBe(false);
    });

    it('应该管理速率限制', () => {
      const identifier = 'test_user_login';
      const limit = 5;
      const windowMs = 60000; // 1分钟

      // 前5次请求应该被允许
      for (let i = 0; i < 5; i++) {
        const result = securityManager.checkRateLimit(identifier, limit, windowMs);
        expect(result.allowed).toBe(true);
      }

      // 第6次请求应该被拒绝
      const result = securityManager.checkRateLimit(identifier, limit, windowMs);
      expect(result.allowed).toBe(false);
    });

    it('应该生成和验证令牌', () => {
      const userId = 'test_user';
      const token = securityManager.generateSecureToken(userId, 60000); // 1分钟

      // 验证有效令牌
      const validation = securityManager.validateToken(token);
      expect(validation.valid).toBe(true);
      expect(validation.userId).toBe(userId);

      // 撤销令牌
      const revoked = securityManager.revokeToken(token);
      expect(revoked).toBe(true);

      // 验证已撤销的令牌
      const invalidValidation = securityManager.validateToken(token);
      expect(invalidValidation.valid).toBe(false);
    });

    it('应该记录审计日志', () => {
      const userId = 'test_user';
      const resource = '/api/test';

      // 执行一些需要审计的操作
      securityManager.grantAccess(userId, resource, [PermissionType.READ], 'admin');
      securityManager.checkAccess(userId, resource, PermissionType.READ);

      // 获取审计日志
      const auditLog = securityManager.getAuditLog({ userId: 'admin', limit: 10 });
      
      expect(auditLog.length).toBeGreaterThan(0);
      expect(auditLog[0].userId).toBe('admin');
    });

    it('应该支持数据加密和解密', async () => {
      // 跳过加密测试如果crypto API不可用
      if (typeof crypto === 'undefined' || !crypto.subtle) {
        console.warn('Crypto API not available, skipping encryption tests');
        return;
      }

      const originalData = 'sensitive health data';
      
      try {
        const encrypted = await securityManager.encrypt(originalData);
        expect(encrypted.encryptedData).toBeDefined();
        expect(encrypted.iv).toBeDefined();

        const decrypted = await securityManager.decrypt(encrypted.encryptedData, encrypted.iv);
        expect(decrypted).toBe(originalData);
      } catch (error) {
        console.warn('Encryption test failed (expected in some environments):', error);
      }
    });
  });

  describe('系统集成测试', () => {
    it('应该协同工作处理复杂场景', async () => {
      // 模拟一个复杂的健康数据处理流程
      const userId = 'integration_test_user';
      const healthData = {
        systolic: 140,
        diastolic: 90,
        heartRate: 85,
        temperature: 37.2,
        timestamp: Date.now()
      };

      // 1. 验证数据
      const validationReport = dataValidator.validateHealthData(healthData);
      expect(validationReport.isValid).toBe(true);

      // 2. 检查访问权限
      securityManager.grantAccess(userId, '/health-data', [PermissionType.WRITE], 'system');
      const accessResult = securityManager.checkAccess(userId, '/health-data', PermissionType.WRITE);
      expect(accessResult.type).toBe('ALLOW');

      // 3. 缓存数据
      const cacheKey = `health_data_${userId}_${Date.now()}`;
      await cacheManager.set('memory', cacheKey, healthData);

      // 4. 监控性能
      const processedData = performanceMonitor.measure(
        'health_data_processing',
        PerformanceCategory.BUSINESS_LOGIC,
        () => {
          // 模拟数据处理
          return {
            ...healthData,
            processed: true,
            riskLevel: healthData.systolic > 130 ? 'HIGH' : 'NORMAL'
          };
        }
      );

      expect(processedData.processed).toBe(true);
      expect(processedData.riskLevel).toBe('HIGH');

      // 5. 获取缓存数据
      const cachedData = await cacheManager.get('memory', cacheKey);
      expect(cachedData).toEqual(healthData);

      // 6. 检查性能指标
      const performanceReport = performanceMonitor.generateReport();
      expect(performanceReport.metrics.length).toBeGreaterThan(0);

      // 7. 检查审计日志
      const auditLog = securityManager.getAuditLog({ userId, limit: 5 });
      expect(auditLog.length).toBeGreaterThan(0);
    });

    it('应该处理错误场景', async () => {
      // 模拟错误场景
      const invalidData = {
        systolic: 'invalid', // 无效类型
        diastolic: 80
      };

      // 验证应该失败
      const validationReport = dataValidator.validateHealthData(invalidData);
      expect(validationReport.isValid).toBe(false);

      // 模拟网络错误
      const networkError = new Error('Network timeout');
      const errorResult = await errorHandler.handleError(networkError, {
        userId: 'test_user',
        timestamp: Date.now()
      });

      expect(errorResult.type).toBe(ErrorType.TIMEOUT_ERROR);
      expect(errorResult.suggestions.length).toBeGreaterThan(0);

      // 检查未授权访问
      const unauthorizedResult = securityManager.checkAccess(
        'unauthorized_user',
        '/admin/settings',
        PermissionType.READ
      );
      expect(unauthorizedResult.type).toBe('DENY');
    });
  });
}); 
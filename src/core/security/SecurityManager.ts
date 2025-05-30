/**
 * 索克生活 - 安全管理系统
 * 提供数据加密、访问控制、安全审计、威胁检测和合规性管理
 */

import { errorHandler, ErrorType } from '../error/ErrorHandler';
import { performanceMonitor, PerformanceCategory } from '../monitoring/PerformanceMonitor';

export enum SecurityLevel {
  PUBLIC = 'PUBLIC',
  INTERNAL = 'INTERNAL',
  CONFIDENTIAL = 'CONFIDENTIAL',
  RESTRICTED = 'RESTRICTED',
  TOP_SECRET = 'TOP_SECRET'
}

export enum PermissionType {
  READ = 'READ',
  WRITE = 'WRITE',
  DELETE = 'DELETE',
  EXECUTE = 'EXECUTE',
  ADMIN = 'ADMIN'
}

export enum ThreatType {
  BRUTE_FORCE = 'BRUTE_FORCE',
  SQL_INJECTION = 'SQL_INJECTION',
  XSS = 'XSS',
  CSRF = 'CSRF',
  DATA_BREACH = 'DATA_BREACH',
  UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS',
  SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY',
  MALWARE = 'MALWARE'
}

export enum AuditEventType {
  LOGIN = 'LOGIN',
  LOGOUT = 'LOGOUT',
  DATA_ACCESS = 'DATA_ACCESS',
  DATA_MODIFICATION = 'DATA_MODIFICATION',
  PERMISSION_CHANGE = 'PERMISSION_CHANGE',
  SECURITY_VIOLATION = 'SECURITY_VIOLATION',
  SYSTEM_CHANGE = 'SYSTEM_CHANGE'
}

export interface SecurityPolicy {
  id: string;
  name: string;
  description: string;
  rules: SecurityRule[];
  isActive: boolean;
  priority: number;
  createdAt: number;
  updatedAt: number;
}

export interface SecurityRule {
  id: string;
  type: 'ACCESS_CONTROL' | 'DATA_PROTECTION' | 'THREAT_DETECTION' | 'COMPLIANCE';
  condition: (context: SecurityContext) => boolean;
  action: (context: SecurityContext) => SecurityAction;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  isEnabled: boolean;
}

export interface SecurityContext {
  userId?: string;
  userRole?: string;
  resource?: string;
  action?: string;
  ipAddress?: string;
  userAgent?: string;
  timestamp: number;
  sessionId?: string;
  metadata?: Record<string, any>;
}

export interface SecurityAction {
  type: 'ALLOW' | 'DENY' | 'WARN' | 'LOG' | 'BLOCK' | 'QUARANTINE';
  message: string;
  details?: any;
  requiresApproval?: boolean;
  notifyAdmin?: boolean;
}

export interface AuditEvent {
  id: string;
  type: AuditEventType;
  userId?: string;
  resource?: string;
  action: string;
  result: 'SUCCESS' | 'FAILURE' | 'BLOCKED';
  timestamp: number;
  ipAddress?: string;
  userAgent?: string;
  details?: any;
  riskScore?: number;
}

export interface ThreatDetection {
  id: string;
  type: ThreatType;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  source: string;
  timestamp: number;
  isResolved: boolean;
  evidence: any[];
  mitigationSteps: string[];
}

export interface EncryptionConfig {
  algorithm: 'AES-256-GCM' | 'ChaCha20-Poly1305' | 'RSA-OAEP';
  keySize: number;
  ivSize?: number;
  tagSize?: number;
}

export interface AccessControlEntry {
  userId: string;
  resource: string;
  permissions: PermissionType[];
  conditions?: Record<string, any>;
  expiresAt?: number;
  grantedBy: string;
  grantedAt: number;
}

export class SecurityManager {
  private static instance: SecurityManager;
  private policies: Map<string, SecurityPolicy> = new Map();
  private auditLog: AuditEvent[] = [];
  private threatDetections: Map<string, ThreatDetection> = new Map();
  private accessControlList: Map<string, AccessControlEntry[]> = new Map();
  private encryptionKeys: Map<string, any> = new Map();
  private sessionTokens: Map<string, { userId: string; expiresAt: number }> = new Map();
  private rateLimits: Map<string, { count: number; resetTime: number }> = new Map();

  private constructor() {
    this.setupDefaultPolicies();
    this.startSecurityMonitoring();
  }

  public static getInstance(): SecurityManager {
    if (!SecurityManager.instance) {
      SecurityManager.instance = new SecurityManager();
    }
    return SecurityManager.instance;
  }

  /**
   * 数据加密
   */
  public async encrypt(
    data: string | ArrayBuffer,
    keyId: string = 'default',
    config?: EncryptionConfig
  ): Promise<{
    encryptedData: ArrayBuffer;
    iv: ArrayBuffer;
    tag?: ArrayBuffer;
  }> {
    return performanceMonitor.measureAsync(
      'data_encryption',
      PerformanceCategory.CPU,
      async () => {
        try {
          const key = await this.getOrCreateEncryptionKey(keyId, config);
          const iv = crypto.getRandomValues(new Uint8Array(12)); // 96-bit IV for GCM
          
          const encoder = new TextEncoder();
          const dataBuffer = typeof data === 'string' ? encoder.encode(data) : data;

          const encryptedData = await crypto.subtle.encrypt(
            {
              name: 'AES-GCM',
              iv: iv
            },
            key,
            dataBuffer
          );

          return {
            encryptedData,
            iv: iv.buffer,
            tag: encryptedData.slice(-16) // Last 16 bytes are the authentication tag
          };
        } catch (error) {
          await errorHandler.handleError(error as Error, {
            keyId
          } as any);
          throw error;
        }
      }
    );
  }

  /**
   * 数据解密
   */
  public async decrypt(
    encryptedData: ArrayBuffer,
    iv: ArrayBuffer,
    keyId: string = 'default'
  ): Promise<string> {
    return performanceMonitor.measureAsync(
      'data_decryption',
      PerformanceCategory.CPU,
      async () => {
        try {
          const key = await this.getOrCreateEncryptionKey(keyId);
          
          const decryptedData = await crypto.subtle.decrypt(
            {
              name: 'AES-GCM',
              iv: iv
            },
            key,
            encryptedData
          );

          const decoder = new TextDecoder();
          return decoder.decode(decryptedData);
        } catch (error) {
          await errorHandler.handleError(error as Error, {
            keyId
          } as any);
          throw error;
        }
      }
    );
  }

  /**
   * 访问控制检查
   */
  public checkAccess(
    userId: string,
    resource: string,
    permission: PermissionType,
    context?: SecurityContext
  ): SecurityAction {
    try {
      const userACL = this.accessControlList.get(userId) || [];
      const resourceACL = userACL.find(acl => 
        acl.resource === resource || acl.resource === '*'
      );

      if (!resourceACL) {
        this.logAuditEvent({
          type: AuditEventType.SECURITY_VIOLATION,
          userId,
          resource,
          action: `ACCESS_DENIED_NO_ACL_${permission}`,
          result: 'BLOCKED',
          timestamp: Date.now(),
          ipAddress: context?.ipAddress,
          userAgent: context?.userAgent
        });

        return {
          type: 'DENY',
          message: '访问被拒绝：没有访问权限',
          notifyAdmin: true
        };
      }

      // 检查权限是否过期
      if (resourceACL.expiresAt && Date.now() > resourceACL.expiresAt) {
        return {
          type: 'DENY',
          message: '访问被拒绝：权限已过期',
          notifyAdmin: true
        };
      }

      // 检查是否有所需权限
      if (!resourceACL.permissions.includes(permission) && 
          !resourceACL.permissions.includes(PermissionType.ADMIN)) {
        return {
          type: 'DENY',
          message: '访问被拒绝：权限不足',
          notifyAdmin: true
        };
      }

      // 应用安全策略
      const policyResult = this.applySecurityPolicies({
        userId,
        resource,
        action: permission,
        timestamp: Date.now(),
        ...context
      });

      if (policyResult.type === 'DENY' || policyResult.type === 'BLOCK') {
        return policyResult;
      }

      this.logAuditEvent({
        type: AuditEventType.DATA_ACCESS,
        userId,
        resource,
        action: `ACCESS_GRANTED_${permission}`,
        result: 'SUCCESS',
        timestamp: Date.now(),
        ipAddress: context?.ipAddress,
        userAgent: context?.userAgent
      });

      return {
        type: 'ALLOW',
        message: '访问已授权'
      };
    } catch (error) {
      console.error('Access control check failed:', error);
      return {
        type: 'DENY',
        message: '访问控制检查失败',
        notifyAdmin: true
      };
    }
  }

  /**
   * 授予访问权限
   */
  public grantAccess(
    userId: string,
    resource: string,
    permissions: PermissionType[],
    grantedBy: string,
    options: {
      expiresAt?: number;
      conditions?: Record<string, any>;
    } = {}
  ): void {
    const acl: AccessControlEntry = {
      userId,
      resource,
      permissions,
      conditions: options.conditions,
      expiresAt: options.expiresAt,
      grantedBy,
      grantedAt: Date.now()
    };

    if (!this.accessControlList.has(userId)) {
      this.accessControlList.set(userId, []);
    }

    const userACL = this.accessControlList.get(userId)!;
    const existingIndex = userACL.findIndex(entry => entry.resource === resource);

    if (existingIndex > -1) {
      userACL[existingIndex] = acl;
    } else {
      userACL.push(acl);
    }

    this.logAuditEvent({
      type: AuditEventType.PERMISSION_CHANGE,
      userId: grantedBy,
      resource,
      action: `GRANT_ACCESS_${permissions.join(',')}`,
      result: 'SUCCESS',
      timestamp: Date.now(),
      details: { targetUserId: userId, permissions }
    });

    console.log(`🔐 Access granted: ${userId} -> ${resource} (${permissions.join(', ')})`);
  }

  /**
   * 撤销访问权限
   */
  public revokeAccess(
    userId: string,
    resource: string,
    revokedBy: string
  ): boolean {
    const userACL = this.accessControlList.get(userId);
    if (!userACL) {
      return false;
    }

    const index = userACL.findIndex(acl => acl.resource === resource);
    if (index === -1) {
      return false;
    }

    userACL.splice(index, 1);

    this.logAuditEvent({
      type: AuditEventType.PERMISSION_CHANGE,
      userId: revokedBy,
      resource,
      action: 'REVOKE_ACCESS',
      result: 'SUCCESS',
      timestamp: Date.now(),
      details: { targetUserId: userId }
    });

    console.log(`🔒 Access revoked: ${userId} -> ${resource}`);
    return true;
  }

  /**
   * 威胁检测
   */
  public detectThreat(
    type: ThreatType,
    source: string,
    evidence: any[],
    context?: SecurityContext
  ): ThreatDetection {
    const threatId = this.generateThreatId();
    const severity = this.calculateThreatSeverity(type, evidence);
    
    const threat: ThreatDetection = {
      id: threatId,
      type,
      severity,
      description: this.getThreatDescription(type),
      source,
      timestamp: Date.now(),
      isResolved: false,
      evidence,
      mitigationSteps: this.getMitigationSteps(type)
    };

    this.threatDetections.set(threatId, threat);

    // 记录安全事件
    this.logAuditEvent({
      type: AuditEventType.SECURITY_VIOLATION,
      userId: context?.userId,
      resource: source,
      action: `THREAT_DETECTED_${type}`,
      result: 'BLOCKED',
      timestamp: Date.now(),
      ipAddress: context?.ipAddress,
      userAgent: context?.userAgent,
      details: { threatId, severity, evidence }
    });

    // 自动响应
    this.autoRespondToThreat(threat, context);

    console.warn(`🚨 Threat detected: ${type} (${severity}) from ${source}`);
    return threat;
  }

  /**
   * 速率限制检查
   */
  public checkRateLimit(
    identifier: string,
    limit: number,
    windowMs: number
  ): { allowed: boolean; remaining: number; resetTime: number } {
    const now = Date.now();
    const key = `${identifier}_${Math.floor(now / windowMs)}`;
    
    let rateLimit = this.rateLimits.get(key);
    
    if (!rateLimit) {
      rateLimit = {
        count: 0,
        resetTime: now + windowMs
      };
      this.rateLimits.set(key, rateLimit);
    }

    if (now > rateLimit.resetTime) {
      rateLimit.count = 0;
      rateLimit.resetTime = now + windowMs;
    }

    const allowed = rateLimit.count < limit;
    
    if (allowed) {
      rateLimit.count++;
    } else {
      // 检测潜在的暴力攻击
      this.detectThreat(
        ThreatType.BRUTE_FORCE,
        identifier,
        [{ rateLimitExceeded: true, limit, count: rateLimit.count }]
      );
    }

    return {
      allowed,
      remaining: Math.max(0, limit - rateLimit.count),
      resetTime: rateLimit.resetTime
    };
  }

  /**
   * 生成安全令牌
   */
  public generateSecureToken(
    userId: string,
    expiresInMs: number = 24 * 60 * 60 * 1000 // 24小时
  ): string {
    const tokenId = this.generateTokenId();
    const expiresAt = Date.now() + expiresInMs;
    
    this.sessionTokens.set(tokenId, {
      userId,
      expiresAt
    });

    this.logAuditEvent({
      type: AuditEventType.LOGIN,
      userId,
      action: 'TOKEN_GENERATED',
      result: 'SUCCESS',
      timestamp: Date.now(),
      details: { tokenId, expiresAt }
    });

    return tokenId;
  }

  /**
   * 验证安全令牌
   */
  public validateToken(token: string): { valid: boolean; userId?: string } {
    const session = this.sessionTokens.get(token);
    
    if (!session) {
      return { valid: false };
    }

    if (Date.now() > session.expiresAt) {
      this.sessionTokens.delete(token);
      return { valid: false };
    }

    return {
      valid: true,
      userId: session.userId
    };
  }

  /**
   * 撤销令牌
   */
  public revokeToken(token: string): boolean {
    const session = this.sessionTokens.get(token);
    
    if (session) {
      this.sessionTokens.delete(token);
      
      this.logAuditEvent({
        type: AuditEventType.LOGOUT,
        userId: session.userId,
        action: 'TOKEN_REVOKED',
        result: 'SUCCESS',
        timestamp: Date.now(),
        details: { token }
      });
      
      return true;
    }
    
    return false;
  }

  /**
   * 获取审计日志
   */
  public getAuditLog(
    filters: {
      userId?: string;
      type?: AuditEventType;
      startTime?: number;
      endTime?: number;
      limit?: number;
    } = {}
  ): AuditEvent[] {
    let filteredLog = this.auditLog;

    if (filters.userId) {
      filteredLog = filteredLog.filter(event => event.userId === filters.userId);
    }

    if (filters.type) {
      filteredLog = filteredLog.filter(event => event.type === filters.type);
    }

    if (filters.startTime) {
      filteredLog = filteredLog.filter(event => event.timestamp >= filters.startTime!);
    }

    if (filters.endTime) {
      filteredLog = filteredLog.filter(event => event.timestamp <= filters.endTime!);
    }

    // 按时间倒序排列
    filteredLog.sort((a, b) => b.timestamp - a.timestamp);

    if (filters.limit) {
      filteredLog = filteredLog.slice(0, filters.limit);
    }

    return filteredLog;
  }

  /**
   * 获取威胁检测列表
   */
  public getThreats(
    filters: {
      type?: ThreatType;
      severity?: string;
      isResolved?: boolean;
      limit?: number;
    } = {}
  ): ThreatDetection[] {
    let threats = Array.from(this.threatDetections.values());

    if (filters.type) {
      threats = threats.filter(threat => threat.type === filters.type);
    }

    if (filters.severity) {
      threats = threats.filter(threat => threat.severity === filters.severity);
    }

    if (filters.isResolved !== undefined) {
      threats = threats.filter(threat => threat.isResolved === filters.isResolved);
    }

    // 按时间倒序排列
    threats.sort((a, b) => b.timestamp - a.timestamp);

    if (filters.limit) {
      threats = threats.slice(0, filters.limit);
    }

    return threats;
  }

  /**
   * 解决威胁
   */
  public resolveThreat(threatId: string, resolution: string): boolean {
    const threat = this.threatDetections.get(threatId);
    
    if (threat) {
      threat.isResolved = true;
      
      this.logAuditEvent({
        type: AuditEventType.SECURITY_VIOLATION,
        action: 'THREAT_RESOLVED',
        result: 'SUCCESS',
        timestamp: Date.now(),
        details: { threatId, resolution }
      });
      
      console.log(`✅ Threat resolved: ${threatId}`);
      return true;
    }
    
    return false;
  }

  private async getOrCreateEncryptionKey(
    keyId: string,
    config?: EncryptionConfig
  ): Promise<any> {
    let key = this.encryptionKeys.get(keyId);
    
    if (!key) {
      key = await crypto.subtle.generateKey(
        {
          name: 'AES-GCM',
          length: config?.keySize || 256
        },
        true,
        ['encrypt', 'decrypt']
      );
      
      this.encryptionKeys.set(keyId, key);
      console.log(`🔑 Encryption key generated: ${keyId}`);
    }
    
    return key;
  }

  private applySecurityPolicies(context: SecurityContext): SecurityAction {
    for (const policy of this.policies.values()) {
      if (!policy.isActive) continue;

      for (const rule of policy.rules) {
        if (!rule.isEnabled) continue;

        try {
          if (rule.condition(context)) {
            const action = rule.action(context);
            
            if (action.type === 'DENY' || action.type === 'BLOCK') {
              this.logAuditEvent({
                type: AuditEventType.SECURITY_VIOLATION,
                userId: context.userId,
                resource: context.resource,
                action: `POLICY_VIOLATION_${policy.id}_${rule.id}`,
                result: 'BLOCKED',
                timestamp: Date.now(),
                details: { policyId: policy.id, ruleId: rule.id, action }
              });
            }
            
            return action;
          }
        } catch (error) {
          console.error(`Security policy execution failed: ${policy.id}/${rule.id}`, error);
        }
      }
    }

    return {
      type: 'ALLOW',
      message: '通过安全策略检查'
    };
  }

  private logAuditEvent(event: Omit<AuditEvent, 'id'>): void {
    const auditEvent: AuditEvent = {
      id: this.generateAuditId(),
      ...event
    };

    this.auditLog.push(auditEvent);

    // 保持审计日志大小在合理范围内
    if (this.auditLog.length > 10000) {
      this.auditLog = this.auditLog.slice(-5000);
    }
  }

  private calculateThreatSeverity(type: ThreatType, evidence: any[]): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' {
    const severityMap: Record<ThreatType, 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'> = {
      [ThreatType.BRUTE_FORCE]: 'MEDIUM',
      [ThreatType.SQL_INJECTION]: 'HIGH',
      [ThreatType.XSS]: 'MEDIUM',
      [ThreatType.CSRF]: 'MEDIUM',
      [ThreatType.DATA_BREACH]: 'CRITICAL',
      [ThreatType.UNAUTHORIZED_ACCESS]: 'HIGH',
      [ThreatType.SUSPICIOUS_ACTIVITY]: 'LOW',
      [ThreatType.MALWARE]: 'CRITICAL'
    };

    return severityMap[type] || 'MEDIUM';
  }

  private getThreatDescription(type: ThreatType): string {
    const descriptions: Record<ThreatType, string> = {
      [ThreatType.BRUTE_FORCE]: '检测到暴力破解攻击尝试',
      [ThreatType.SQL_INJECTION]: '检测到SQL注入攻击尝试',
      [ThreatType.XSS]: '检测到跨站脚本攻击尝试',
      [ThreatType.CSRF]: '检测到跨站请求伪造攻击',
      [ThreatType.DATA_BREACH]: '检测到数据泄露事件',
      [ThreatType.UNAUTHORIZED_ACCESS]: '检测到未授权访问尝试',
      [ThreatType.SUSPICIOUS_ACTIVITY]: '检测到可疑活动',
      [ThreatType.MALWARE]: '检测到恶意软件'
    };

    return descriptions[type] || '检测到未知威胁';
  }

  private getMitigationSteps(type: ThreatType): string[] {
    const steps: Record<ThreatType, string[]> = {
      [ThreatType.BRUTE_FORCE]: [
        '临时封禁IP地址',
        '增强密码策略',
        '启用多因素认证',
        '监控后续攻击尝试'
      ],
      [ThreatType.SQL_INJECTION]: [
        '阻止恶意请求',
        '检查数据库完整性',
        '更新输入验证规则',
        '审查相关代码'
      ],
      [ThreatType.XSS]: [
        '清理恶意脚本',
        '更新内容安全策略',
        '检查用户输入过滤',
        '扫描相关页面'
      ],
      [ThreatType.CSRF]: [
        '验证请求来源',
        '检查CSRF令牌',
        '更新安全头设置',
        '审查表单处理'
      ],
      [ThreatType.DATA_BREACH]: [
        '立即隔离受影响系统',
        '评估数据泄露范围',
        '通知相关用户',
        '启动事件响应流程'
      ],
      [ThreatType.UNAUTHORIZED_ACCESS]: [
        '撤销相关访问权限',
        '重置受影响账户',
        '审查访问日志',
        '加强访问控制'
      ],
      [ThreatType.SUSPICIOUS_ACTIVITY]: [
        '增强监控',
        '收集更多证据',
        '分析行为模式',
        '准备响应措施'
      ],
      [ThreatType.MALWARE]: [
        '隔离受感染系统',
        '运行恶意软件扫描',
        '清理恶意文件',
        '更新安全软件'
      ]
    };

    return steps[type] || ['联系安全团队', '启动事件响应流程'];
  }

  private autoRespondToThreat(threat: ThreatDetection, context?: SecurityContext): void {
    switch (threat.type) {
      case ThreatType.BRUTE_FORCE:
        if (context?.ipAddress) {
          // 临时封禁IP（这里应该调用实际的IP封禁服务）
          console.log(`🚫 Auto-blocking IP: ${context.ipAddress}`);
        }
        break;

      case ThreatType.DATA_BREACH:
        // 立即通知管理员
        console.log('🚨 CRITICAL: Data breach detected - notifying administrators');
        break;

      case ThreatType.MALWARE:
        // 隔离相关资源
        console.log('🔒 Auto-quarantining potentially infected resources');
        break;
    }
  }

  private setupDefaultPolicies(): void {
    // 默认访问控制策略
    const accessControlPolicy: SecurityPolicy = {
      id: 'default_access_control',
      name: '默认访问控制策略',
      description: '基本的访问控制和权限验证',
      rules: [
        {
          id: 'require_authentication',
          type: 'ACCESS_CONTROL',
          condition: (context) => !context.userId,
          action: () => ({
            type: 'DENY',
            message: '需要身份验证',
            requiresApproval: false
          }),
          severity: 'MEDIUM',
          isEnabled: true
        },
        {
          id: 'admin_resource_protection',
          type: 'ACCESS_CONTROL',
          condition: (context) => 
            Boolean(context.resource?.startsWith('/admin') && context.userRole !== 'admin'),
          action: () => ({
            type: 'DENY',
            message: '需要管理员权限',
            notifyAdmin: true
          }),
          severity: 'HIGH',
          isEnabled: true
        }
      ],
      isActive: true,
      priority: 1,
      createdAt: Date.now(),
      updatedAt: Date.now()
    };

    this.policies.set(accessControlPolicy.id, accessControlPolicy);

    // 威胁检测策略
    const threatDetectionPolicy: SecurityPolicy = {
      id: 'threat_detection',
      name: '威胁检测策略',
      description: '自动威胁检测和响应',
      rules: [
        {
          id: 'suspicious_login_pattern',
          type: 'THREAT_DETECTION',
          condition: (context) => {
            // 检测可疑登录模式（这里是简化版本）
            return context.action === 'login' && 
                   context.metadata?.failedAttempts > 5;
          },
          action: (context) => {
            this.detectThreat(
              ThreatType.BRUTE_FORCE,
              context.ipAddress || 'unknown',
              [{ failedAttempts: context.metadata?.failedAttempts }],
              context
            );
            return {
              type: 'BLOCK',
              message: '检测到可疑登录活动',
              notifyAdmin: true
            };
          },
          severity: 'HIGH',
          isEnabled: true
        }
      ],
      isActive: true,
      priority: 2,
      createdAt: Date.now(),
      updatedAt: Date.now()
    };

    this.policies.set(threatDetectionPolicy.id, threatDetectionPolicy);
  }

  private startSecurityMonitoring(): void {
    // 定期清理过期的会话令牌
    setInterval(() => {
      const now = Date.now();
      for (const [token, session] of this.sessionTokens.entries()) {
        if (now > session.expiresAt) {
          this.sessionTokens.delete(token);
        }
      }
    }, 5 * 60 * 1000); // 每5分钟清理一次

    // 定期清理过期的速率限制记录
    setInterval(() => {
      const now = Date.now();
      for (const [key, rateLimit] of this.rateLimits.entries()) {
        if (now > rateLimit.resetTime) {
          this.rateLimits.delete(key);
        }
      }
    }, 10 * 60 * 1000); // 每10分钟清理一次

    console.log('🛡️ Security monitoring started');
  }

  private generateAuditId(): string {
    return `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateThreatId(): string {
    return `threat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateTokenId(): string {
    return `token_${Date.now()}_${Math.random().toString(36).substr(2, 16)}`;
  }
}

// 导出单例实例
export const securityManager = SecurityManager.getInstance();

// 便捷函数
export const encrypt = (data: string | ArrayBuffer, keyId?: string, config?: EncryptionConfig) =>
  securityManager.encrypt(data, keyId, config);

export const decrypt = (encryptedData: ArrayBuffer, iv: ArrayBuffer, keyId?: string) =>
  securityManager.decrypt(encryptedData, iv, keyId);

export const checkAccess = (
  userId: string,
  resource: string,
  permission: PermissionType,
  context?: SecurityContext
) => securityManager.checkAccess(userId, resource, permission, context);

export const grantAccess = (
  userId: string,
  resource: string,
  permissions: PermissionType[],
  grantedBy: string,
  options?: any
) => securityManager.grantAccess(userId, resource, permissions, grantedBy, options);

export const checkRateLimit = (identifier: string, limit: number, windowMs: number) =>
  securityManager.checkRateLimit(identifier, limit, windowMs);

export const generateSecureToken = (userId: string, expiresInMs?: number) =>
  securityManager.generateSecureToken(userId, expiresInMs);

export const validateToken = (token: string) =>
  securityManager.validateToken(token); 
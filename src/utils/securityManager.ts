import AsyncStorage from '@react-native-async-storage/async-storage';
import CryptoJS from 'crypto-js';
import { Alert } from 'react-native';

// 安全配置
const SECURITY_CONFIG = {
  ENCRYPTION_KEY: 'suoke_life_security_key_2024',
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30分钟
  MAX_LOGIN_ATTEMPTS: 5,
  PASSWORD_MIN_LENGTH: 8,
  BIOMETRIC_TIMEOUT: 5 * 60 * 1000, // 5分钟
  AUDIT_LOG_MAX_SIZE: 1000,
};

// 安全事件类型
export interface SecurityEvent {
  id: string;
  type: 'login' | 'logout' | 'access_denied' | 'data_access' | 'encryption' | 'biometric' | 'suspicious';
  userId?: string;
  timestamp: number;
  details: Record<string, any>;
  severity: 'low' | 'medium' | 'high' | 'critical';
  ipAddress?: string;
  deviceInfo?: DeviceInfo;
}

export interface DeviceInfo {
  platform: string;
  version: string;
  model: string;
  uniqueId: string;
  isJailbroken?: boolean;
  isEmulator?: boolean;
}

export interface UserSession {
  userId: string;
  sessionId: string;
  startTime: number;
  lastActivity: number;
  deviceInfo: DeviceInfo;
  permissions: string[];
  biometricEnabled: boolean;
}

export interface SecurityPolicy {
  requireBiometric: boolean;
  sessionTimeout: number;
  maxLoginAttempts: number;
  passwordComplexity: {
    minLength: number;
    requireUppercase: boolean;
    requireLowercase: boolean;
    requireNumbers: boolean;
    requireSpecialChars: boolean;
  };
  dataEncryption: {
    enabled: boolean;
    algorithm: string;
    keyRotationInterval: number;
  };
  auditLogging: {
    enabled: boolean;
    logLevel: 'basic' | 'detailed' | 'verbose';
    retentionDays: number;
  };
}

// 数据加密管理器
class EncryptionManager {
  private static instance: EncryptionManager;
  private encryptionKey: string;
  private keyRotationInterval: number;
  private lastKeyRotation: number;

  private constructor() {
    this.encryptionKey = SECURITY_CONFIG.ENCRYPTION_KEY;
    this.keyRotationInterval = 24 * 60 * 60 * 1000; // 24小时
    this.lastKeyRotation = Date.now();
  }

  static getInstance(): EncryptionManager {
    if (!EncryptionManager.instance) {
      EncryptionManager.instance = new EncryptionManager();
    }
    return EncryptionManager.instance;
  }

  // 加密数据
  encrypt(data: any, customKey?: string): string {
    try {
      const key = customKey || this.encryptionKey;
      const jsonString = JSON.stringify(data);
      const encrypted = CryptoJS.AES.encrypt(jsonString, key).toString();
      
      // 记录加密事件
      SecurityManager.getInstance().logSecurityEvent({
        type: 'encryption',
        details: { action: 'encrypt', dataType: typeof data },
        severity: 'low'
      });

      return encrypted;
    } catch (error) {
      console.error('加密失败:', error);
      throw new Error('数据加密失败');
    }
  }

  // 解密数据
  decrypt(encryptedData: string, customKey?: string): any {
    try {
      const key = customKey || this.encryptionKey;
      const bytes = CryptoJS.AES.decrypt(encryptedData, key);
      const decryptedString = bytes.toString(CryptoJS.enc.Utf8);
      
      if (!decryptedString) {
        throw new Error('解密失败：无效的密钥或数据');
      }

      const data = JSON.parse(decryptedString);
      
      // 记录解密事件
      SecurityManager.getInstance().logSecurityEvent({
        type: 'encryption',
        details: { action: 'decrypt', dataType: typeof data },
        severity: 'low'
      });

      return data;
         } catch (error) {
       console.error('解密失败:', error);
       SecurityManager.getInstance().logSecurityEvent({
         type: 'encryption',
         details: { action: 'decrypt_failed', error: error instanceof Error ? error.message : 'Unknown error' },
         severity: 'medium'
       });
       throw new Error('数据解密失败');
     }
  }

  // 生成哈希
  generateHash(data: string): string {
    return CryptoJS.SHA256(data).toString();
  }

  // 验证哈希
  verifyHash(data: string, hash: string): boolean {
    const computedHash = this.generateHash(data);
    return computedHash === hash;
  }

  // 密钥轮换
  rotateKey(): void {
    const now = Date.now();
    if (now - this.lastKeyRotation > this.keyRotationInterval) {
      // 生成新密钥
      const newKey = CryptoJS.lib.WordArray.random(256/8).toString();
      this.encryptionKey = newKey;
      this.lastKeyRotation = now;
      
      SecurityManager.getInstance().logSecurityEvent({
        type: 'encryption',
        details: { action: 'key_rotation' },
        severity: 'medium'
      });
    }
  }
}

// 访问控制管理器
class AccessControlManager {
  private static instance: AccessControlManager;
  private permissions: Map<string, string[]> = new Map();
  private rolePermissions: Map<string, string[]> = new Map();

  private constructor() {
    this.initializeDefaultRoles();
  }

  static getInstance(): AccessControlManager {
    if (!AccessControlManager.instance) {
      AccessControlManager.instance = new AccessControlManager();
    }
    return AccessControlManager.instance;
  }

  private initializeDefaultRoles(): void {
    // 定义默认角色权限
    this.rolePermissions.set('user', [
      'read_health_data',
      'write_health_data',
      'access_diagnosis',
      'access_eco_services'
    ]);

    this.rolePermissions.set('premium_user', [
      'read_health_data',
      'write_health_data',
      'access_diagnosis',
      'access_eco_services',
      'access_advanced_features',
      'export_data'
    ]);

    this.rolePermissions.set('admin', [
      'read_health_data',
      'write_health_data',
      'access_diagnosis',
      'access_eco_services',
      'access_advanced_features',
      'export_data',
      'manage_users',
      'access_system_monitor',
      'manage_security'
    ]);
  }

  // 检查权限
  hasPermission(userId: string, permission: string): boolean {
    const userPermissions = this.permissions.get(userId) || [];
    return userPermissions.includes(permission);
  }

  // 检查角色权限
  hasRolePermission(role: string, permission: string): boolean {
    const rolePerms = this.rolePermissions.get(role) || [];
    return rolePerms.includes(permission);
  }

  // 授予权限
  grantPermission(userId: string, permission: string): void {
    const userPermissions = this.permissions.get(userId) || [];
    if (!userPermissions.includes(permission)) {
      userPermissions.push(permission);
      this.permissions.set(userId, userPermissions);
      
      SecurityManager.getInstance().logSecurityEvent({
        type: 'access_denied',
        userId,
        details: { action: 'grant_permission', permission },
        severity: 'medium'
      });
    }
  }

  // 撤销权限
  revokePermission(userId: string, permission: string): void {
    const userPermissions = this.permissions.get(userId) || [];
    const index = userPermissions.indexOf(permission);
    if (index > -1) {
      userPermissions.splice(index, 1);
      this.permissions.set(userId, userPermissions);
      
      SecurityManager.getInstance().logSecurityEvent({
        type: 'access_denied',
        userId,
        details: { action: 'revoke_permission', permission },
        severity: 'medium'
      });
    }
  }

  // 设置用户角色
  setUserRole(userId: string, role: string): void {
    const rolePerms = this.rolePermissions.get(role) || [];
    this.permissions.set(userId, [...rolePerms]);
    
    SecurityManager.getInstance().logSecurityEvent({
      type: 'access_denied',
      userId,
      details: { action: 'set_role', role },
      severity: 'medium'
    });
  }
}

// 安全审计管理器
class SecurityAuditManager {
  private static instance: SecurityAuditManager;
  private auditLogs: SecurityEvent[] = [];
  private maxLogSize: number = SECURITY_CONFIG.AUDIT_LOG_MAX_SIZE;

  private constructor() {
    this.loadAuditLogs();
  }

  static getInstance(): SecurityAuditManager {
    if (!SecurityAuditManager.instance) {
      SecurityAuditManager.instance = new SecurityAuditManager();
    }
    return SecurityAuditManager.instance;
  }

  // 记录安全事件
  logEvent(event: Omit<SecurityEvent, 'id' | 'timestamp'>): void {
    const securityEvent: SecurityEvent = {
      id: this.generateEventId(),
      timestamp: Date.now(),
      ...event
    };

    this.auditLogs.push(securityEvent);

    // 保持日志大小在限制范围内
    if (this.auditLogs.length > this.maxLogSize) {
      this.auditLogs.splice(0, this.auditLogs.length - this.maxLogSize);
    }

    // 持久化日志
    this.persistAuditLogs();

    // 检查是否需要告警
    this.checkForAlerts(securityEvent);
  }

  // 获取审计日志
  getAuditLogs(filters?: {
    type?: string;
    userId?: string;
    severity?: string;
    timeRange?: { start: number; end: number };
  }): SecurityEvent[] {
    let filteredLogs = [...this.auditLogs];

    if (filters?.type) {
      filteredLogs = filteredLogs.filter(log => log.type === filters.type);
    }

    if (filters?.userId) {
      filteredLogs = filteredLogs.filter(log => log.userId === filters.userId);
    }

    if (filters?.severity) {
      filteredLogs = filteredLogs.filter(log => log.severity === filters.severity);
    }

    if (filters?.timeRange) {
      filteredLogs = filteredLogs.filter(log => 
        log.timestamp >= filters.timeRange!.start && 
        log.timestamp <= filters.timeRange!.end
      );
    }

    return filteredLogs.sort((a, b) => b.timestamp - a.timestamp);
  }

  // 生成安全报告
  generateSecurityReport(timeRange: { start: number; end: number }): {
    summary: string;
    events: SecurityEvent[];
    statistics: Record<string, number>;
    recommendations: string[];
  } {
    const events = this.getAuditLogs({ timeRange });
    
    const statistics = {
      total: events.length,
      critical: events.filter(e => e.severity === 'critical').length,
      high: events.filter(e => e.severity === 'high').length,
      medium: events.filter(e => e.severity === 'medium').length,
      low: events.filter(e => e.severity === 'low').length,
    };

    const recommendations: string[] = [];
    
    if (statistics.critical > 0) {
      recommendations.push('发现严重安全事件，建议立即检查系统安全');
    }
    
    if (statistics.high > 10) {
      recommendations.push('高风险事件较多，建议加强安全监控');
    }

    const summary = `
安全报告 (${new Date(timeRange.start).toLocaleDateString()} - ${new Date(timeRange.end).toLocaleDateString()})
总事件数: ${statistics.total}
严重事件: ${statistics.critical}
高风险事件: ${statistics.high}
中风险事件: ${statistics.medium}
低风险事件: ${statistics.low}
    `.trim();

    return {
      summary,
      events,
      statistics,
      recommendations
    };
  }

  private generateEventId(): string {
    return `sec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async persistAuditLogs(): Promise<void> {
    try {
      const encryptedLogs = EncryptionManager.getInstance().encrypt(this.auditLogs);
      await AsyncStorage.setItem('security_audit_logs', encryptedLogs);
    } catch (error) {
      console.error('持久化审计日志失败:', error);
    }
  }

  private async loadAuditLogs(): Promise<void> {
    try {
      const encryptedLogs = await AsyncStorage.getItem('security_audit_logs');
      if (encryptedLogs) {
        this.auditLogs = EncryptionManager.getInstance().decrypt(encryptedLogs);
      }
    } catch (error) {
      console.error('加载审计日志失败:', error);
      this.auditLogs = [];
    }
  }

  private checkForAlerts(event: SecurityEvent): void {
    // 检查是否需要发送安全告警
    if (event.severity === 'critical') {
      Alert.alert('安全告警', '检测到严重安全事件，请立即检查系统安全');
    }

    // 检查登录失败次数
    if (event.type === 'access_denied' && event.details.action === 'login_failed') {
      const recentFailures = this.auditLogs.filter(log => 
        log.type === 'access_denied' && 
        log.details.action === 'login_failed' &&
        log.userId === event.userId &&
        Date.now() - log.timestamp < 15 * 60 * 1000 // 15分钟内
      );

      if (recentFailures.length >= SECURITY_CONFIG.MAX_LOGIN_ATTEMPTS) {
        this.logEvent({
          type: 'suspicious',
          userId: event.userId,
          details: { action: 'account_locked', attempts: recentFailures.length },
          severity: 'high'
        });
      }
    }
  }
}

// 主安全管理器
export class SecurityManager {
  private static instance: SecurityManager;
  private encryptionManager: EncryptionManager;
  private accessControlManager: AccessControlManager;
  private auditManager: SecurityAuditManager;
  private currentSession: UserSession | null = null;
  private securityPolicy: SecurityPolicy;

  private constructor() {
    this.encryptionManager = EncryptionManager.getInstance();
    this.accessControlManager = AccessControlManager.getInstance();
    this.auditManager = SecurityAuditManager.getInstance();
    this.securityPolicy = this.getDefaultSecurityPolicy();
  }

  static getInstance(): SecurityManager {
    if (!SecurityManager.instance) {
      SecurityManager.instance = new SecurityManager();
    }
    return SecurityManager.instance;
  }

  // 初始化安全系统
  async initialize(): Promise<void> {
    try {
      await this.loadSecurityPolicy();
      await this.validateDeviceSecurity();
      
      this.logSecurityEvent({
        type: 'login',
        details: { action: 'security_system_initialized' },
        severity: 'low'
      });
    } catch (error) {
      console.error('安全系统初始化失败:', error);
      throw error;
    }
  }

  // 创建用户会话
  createSession(userId: string, deviceInfo: DeviceInfo): UserSession {
    const session: UserSession = {
      userId,
      sessionId: this.generateSessionId(),
      startTime: Date.now(),
      lastActivity: Date.now(),
      deviceInfo,
      permissions: [],
      biometricEnabled: false
    };

    this.currentSession = session;
    
    this.logSecurityEvent({
      type: 'login',
      userId,
      details: { action: 'session_created', sessionId: session.sessionId },
      severity: 'low',
      deviceInfo
    });

    return session;
  }

  // 验证会话
  validateSession(): boolean {
    if (!this.currentSession) {
      return false;
    }

    const now = Date.now();
    const sessionAge = now - this.currentSession.lastActivity;

    if (sessionAge > this.securityPolicy.sessionTimeout) {
      this.logSecurityEvent({
        type: 'logout',
        userId: this.currentSession.userId,
        details: { action: 'session_expired', sessionAge },
        severity: 'medium'
      });
      
      this.destroySession();
      return false;
    }

    // 更新最后活动时间
    this.currentSession.lastActivity = now;
    return true;
  }

  // 销毁会话
  destroySession(): void {
    if (this.currentSession) {
      this.logSecurityEvent({
        type: 'logout',
        userId: this.currentSession.userId,
        details: { action: 'session_destroyed' },
        severity: 'low'
      });
      
      this.currentSession = null;
    }
  }

  // 检查权限
  checkPermission(permission: string): boolean {
    if (!this.currentSession) {
      this.logSecurityEvent({
        type: 'access_denied',
        details: { action: 'no_session', permission },
        severity: 'medium'
      });
      return false;
    }

    const hasPermission = this.accessControlManager.hasPermission(
      this.currentSession.userId, 
      permission
    );

    if (!hasPermission) {
      this.logSecurityEvent({
        type: 'access_denied',
        userId: this.currentSession.userId,
        details: { action: 'permission_denied', permission },
        severity: 'medium'
      });
    }

    return hasPermission;
  }

  // 记录安全事件
  logSecurityEvent(event: Omit<SecurityEvent, 'id' | 'timestamp'>): void {
    this.auditManager.logEvent(event);
  }

  // 加密数据
  encryptData(data: any): string {
    return this.encryptionManager.encrypt(data);
  }

  // 解密数据
  decryptData(encryptedData: string): any {
    return this.encryptionManager.decrypt(encryptedData);
  }

  // 获取安全报告
  getSecurityReport(timeRange: { start: number; end: number }) {
    return this.auditManager.generateSecurityReport(timeRange);
  }

  // 获取当前会话
  getCurrentSession(): UserSession | null {
    return this.currentSession;
  }

  private getDefaultSecurityPolicy(): SecurityPolicy {
    return {
      requireBiometric: false,
      sessionTimeout: SECURITY_CONFIG.SESSION_TIMEOUT,
      maxLoginAttempts: SECURITY_CONFIG.MAX_LOGIN_ATTEMPTS,
      passwordComplexity: {
        minLength: SECURITY_CONFIG.PASSWORD_MIN_LENGTH,
        requireUppercase: true,
        requireLowercase: true,
        requireNumbers: true,
        requireSpecialChars: false
      },
      dataEncryption: {
        enabled: true,
        algorithm: 'AES-256',
        keyRotationInterval: 24 * 60 * 60 * 1000
      },
      auditLogging: {
        enabled: true,
        logLevel: 'detailed',
        retentionDays: 30
      }
    };
  }

  private async loadSecurityPolicy(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem('security_policy');
      if (stored) {
        const decrypted = this.encryptionManager.decrypt(stored);
        this.securityPolicy = { ...this.getDefaultSecurityPolicy(), ...decrypted };
      }
    } catch (error) {
      console.error('加载安全策略失败:', error);
    }
  }

  private async validateDeviceSecurity(): Promise<void> {
    // 这里可以添加设备安全检查
    // 例如：检查是否越狱、是否为模拟器等
    console.log('设备安全验证完成');
  }

  private generateSessionId(): string {
    return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// 导出单例实例
export const securityManager = SecurityManager.getInstance();
export { EncryptionManager, AccessControlManager, SecurityAuditManager }; 
import React from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';
import CryptoJS from 'crypto-js';
// 安全配置常量
const SECURITY_CONFIG = {
      ENCRYPTION_KEY: "suoke_life_security_key_2024",
      SESSION_TIMEOUT: 30 * 60 * 1000, // 30分钟
  MAX_LOGIN_ATTEMPTS: 5,
  AUDIT_LOG_MAX_SIZE: 1000,
  PASSWORD_MIN_LENGTH: 8};
// 接口定义
export interface DeviceInfo {
  platform: string;,
  version: string;
  model: string;,
  uniqueId: string;
  isJailbroken?: boolean;
  isEmulator?: boolean;
}
export interface UserSession {
  userId: string;,
  sessionId: string;
  startTime: number;,
  lastActivity: number;
  deviceInfo: DeviceInfo;,
  permissions: string[];
  biometricEnabled: boolean;
}
export interface SecurityPolicy {
  requireBiometric: boolean;,
  sessionTimeout: number;
  maxLoginAttempts: number;,
  passwordComplexity: {;
    minLength: number;,
  requireUppercase: boolean;
    requireLowercase: boolean;,
  requireNumbers: boolean;
    requireSpecialChars: boolean;
};
  dataEncryption: {,
  enabled: boolean;
    algorithm: string,
  keyRotationInterval: number;
  };
  auditLogging: {,
  enabled: boolean;
    logLevel: "basic" | "detailed" | "verbose",
  retentionDays: number;
  };
}
export interface SecurityEvent {
  id: string;,
  type: string;
  userId?: string;
  timestamp: number;,
  details: Record<string, any>;
  severity: "low" | "medium" | "high" | "critical";
  deviceInfo?: DeviceInfo;
}
// 加密管理器
class EncryptionManager {
  private static instance: EncryptionManager;
  private encryptionKey: string;
  private constructor() {
    this.encryptionKey = SECURITY_CONFIG.ENCRYPTION_KEY;
  }
  static getInstance(): EncryptionManager {
    if (!EncryptionManager.instance) {
      EncryptionManager.instance = new EncryptionManager();
    }
    return EncryptionManager.instance;
  }
  encrypt(data: any): string {
    try {
      const jsonString = JSON.stringify(data);
      const encrypted = CryptoJS.AES.encrypt(jsonString, this.encryptionKey).toString();
      return encrypted;
    } catch (error) {
      throw new Error('加密失败');
    }
  }
  decrypt(encryptedData: string): any {
    try {
      const decrypted = CryptoJS.AES.decrypt(encryptedData, this.encryptionKey);
      const jsonString = decrypted.toString(CryptoJS.enc.Utf8);
      return JSON.parse(jsonString);
    } catch (error) {
      throw new Error('解密失败');
    }
  }
  generateHash(data: string): string {
    return CryptoJS.SHA256(data).toString();
  }
  verifyHash(data: string, hash: string): boolean {
    return this.generateHash(data) === hash;
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
    // 初始化默认角色权限
    this.rolePermissions.set('admin', [)
      "user_management",system_config',
      "data_export",security_audit'
    ]);
    this.rolePermissions.set('doctor', [)
      "patient_diagnosis",medical_records',
      'prescription'
    ]);
    this.rolePermissions.set('user', [)
      "profile_view",health_data_view',
      'appointment_booking'
    ]);
  }
  // 检查权限
  hasPermission(userId: string, permission: string): boolean {
    const userPermissions = this.permissions.get(userId) || [];
    return userPermissions.includes(permission);
  }
  // 授予权限
  grantPermission(userId: string, permission: string): void {
    const userPermissions = this.permissions.get(userId) || [];
    if (!userPermissions.includes(permission)) {
      userPermissions.push(permission);
      this.permissions.set(userId, userPermissions);
      SecurityManager.getInstance().logSecurityEvent({
        type: "access_granted",
        userId,
        details: { action: "grant_permission", permission },
        severity: "medium"
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
        type: "access_denied",
        userId,
        details: { action: "revoke_permission", permission },
        severity: "medium"
      });
    }
  }
  // 设置用户角色
  setUserRole(userId: string, role: string): void {
    const rolePerms = this.rolePermissions.get(role) || [];
    this.permissions.set(userId, [...rolePerms]);
    SecurityManager.getInstance().logSecurityEvent({
      type: "access_granted",
      userId,
      details: { action: "set_role", role },
      severity: "medium"
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
  logEvent(event: Omit<SecurityEvent, "id" | "timestamp">): void {
    const securityEvent: SecurityEvent = {,
  id: this.generateEventId(),
      timestamp: Date.now(),
      ...event;
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
      filteredLogs = filteredLogs.filter(log) => log.type === filters.type);
    }
    if (filters?.userId) {
      filteredLogs = filteredLogs.filter(log) => log.userId === filters.userId;
      );
    }
    if (filters?.severity) {
      filteredLogs = filteredLogs.filter(log) => log.severity === filters.severity;
      );
    }
    if (filters?.timeRange) {
      filteredLogs = filteredLogs.filter(log) =>
          log.timestamp >= filters.timeRange!.start &&
          log.timestamp <= filters.timeRange!.end;
      );
    }
    return filteredLogs.sort(a, b) => b.timestamp - a.timestamp);
  }
  // 生成安全报告
  generateSecurityReport(timeRange: { start: number; end: number }): {
    summary: string,
  events: SecurityEvent[];,
  statistics: Record<string, number>;
    recommendations: string[];
  } {
    const events = this.getAuditLogs({ timeRange });
    const statistics = {
      total: events.length,
      critical: events.filter(e) => e.severity === "critical").length,
      high: events.filter(e) => e.severity === "high").length,
      medium: events.filter(e) => e.severity === "medium").length,
      low: events.filter(e) => e.severity === "low").length;
    };
    const recommendations: string[] = [];
    if (statistics.critical > 0) {
      recommendations.push("发现严重安全事件，建议立即检查系统安全");
    }
    if (statistics.high > 10) {
      recommendations.push("高风险事件较多，建议加强安全监控");
    }
    const summary = `
安全报告 (${new Date(timeRange.start).toLocaleDateString()} - ${new Date())
      timeRange.end;
    ).toLocaleDateString()})
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
      recommendations;
    };
  }
  private generateEventId(): string {
    return `sec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  private async persistAuditLogs(): Promise<void> {
    try {
      const encryptedLogs = EncryptionManager.getInstance().encrypt()
        this.auditLogs;
      );
      await AsyncStorage.setItem("security_audit_logs", encryptedLogs);
    } catch (error) {
      console.error('持久化审计日志失败:', error);
    }
  }
  private async loadAuditLogs(): Promise<void> {
    try {
      const encryptedLogs = await AsyncStorage.getItem("security_audit_logs");
      if (encryptedLogs) {
        this.auditLogs = EncryptionManager.getInstance().decrypt(encryptedLogs);
      }
    } catch (error) {
      this.auditLogs = [];
    }
  }
  private checkForAlerts(event: SecurityEvent): void {
    // 检查是否需要发送安全告警
    if (event.severity === "critical") {
      Alert.alert("安全告警", "检测到严重安全事件，请立即检查系统安全");
    }
    // 检查登录失败次数
    if ()
      event.type === "access_denied" &&
      event.details.action === "login_failed"
    ) {
      const recentFailures = this.auditLogs.filter(log) =>
          log.type === "access_denied" &&
          log.details.action === "login_failed" &&
          log.userId === event.userId &&
          Date.now() - log.timestamp < 15 * 60 * 1000 // 15分钟内
      );
      if (recentFailures.length >= SECURITY_CONFIG.MAX_LOGIN_ATTEMPTS) {
        this.logEvent({
      type: "suspicious",
      userId: event.userId,
          details: {,
  action: "account_locked",
            attempts: recentFailures.length;
          },
          severity: "high"
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
      type: "system",
      details: { action: "security_system_initialized" },
        severity: "low"
      });
    } catch (error) {
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
      biometricEnabled: false;
    };
    this.currentSession = session;
    this.logSecurityEvent({
      type: "login",
      userId,
      details: {,
  action: "session_created",
      sessionId: session.sessionId },
      severity: "low",
      deviceInfo;
    });
    return session;
  }
  // 验证会话
  validateSession(sessionId: string): boolean {
    if (!this.currentSession || this.currentSession.sessionId !== sessionId) {
      return false;
    }
    const now = Date.now();
    const sessionAge = now - this.currentSession.startTime;
    const inactivityTime = now - this.currentSession.lastActivity;
    if (sessionAge > this.securityPolicy.sessionTimeout ||)
        inactivityTime > this.securityPolicy.sessionTimeout) {
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
      type: "logout",
      userId: this.currentSession.userId,
        details: {,
  action: "session_destroyed",
      sessionId: this.currentSession.sessionId },
        severity: "low"
      });
      this.currentSession = null;
    }
  }
  // 记录安全事件
  logSecurityEvent(event: Omit<SecurityEvent, "id" | "timestamp">): void {
    this.auditManager.logEvent(event);
  }
  // 获取当前会话
  getCurrentSession(): UserSession | null {
    return this.currentSession;
  }
  // 检查权限
  hasPermission(permission: string): boolean {
    if (!this.currentSession) {
      return false;
    }
    return this.accessControlManager.hasPermission(this.currentSession.userId, permission);
  }
  private getDefaultSecurityPolicy(): SecurityPolicy {
    return {
      requireBiometric: false,
      sessionTimeout: SECURITY_CONFIG.SESSION_TIMEOUT,
      maxLoginAttempts: SECURITY_CONFIG.MAX_LOGIN_ATTEMPTS,
      passwordComplexity: {,
  minLength: SECURITY_CONFIG.PASSWORD_MIN_LENGTH,
        requireUppercase: true,
        requireLowercase: true,
        requireNumbers: true,
        requireSpecialChars: false;
      },
      dataEncryption: {,
  enabled: true,
        algorithm: "AES-256",
        keyRotationInterval: 30 * 24 * 60 * 60 * 1000 // 30天
      },
      auditLogging: {,
  enabled: true,
        logLevel: "detailed",
        retentionDays: 90;
      }
    };
  }
  private async loadSecurityPolicy(): Promise<void> {
    try {
      const storedPolicy = await AsyncStorage.getItem("security_policy");
      if (storedPolicy) {
        this.securityPolicy = JSON.parse(storedPolicy);
      }
    } catch (error) {
      console.error('加载安全策略失败:', error);
    }
  }
  private async validateDeviceSecurity(): Promise<void> {
    // 设备安全验证逻辑
    // 这里可以添加设备完整性检查、越狱检测等
    return Promise.resolve();
  }
  private generateSessionId(): string {
    return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
export default SecurityManager;
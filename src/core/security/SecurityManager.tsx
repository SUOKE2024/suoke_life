import { usePerformanceMonitor } from "../../placeholder";../hooks/    usePerformanceMonitor;
import { errorHandler, ErrorType } from "../error/    ErrorHandler";
import React from "react";
/
  performanceMonitor,
  { PerformanceCategory } from "../monitoring/PerformanceMonitor";//
* 提供数据加密、访问控制、安全审计、威胁检测和合规性管理
export enum SecurityLevel {
  PUBLIC = "PUBLIC",
  INTERNAL = "INTERNAL",
  CONFIDENTIAL = "CONFIDENTIAL",
  RESTRICTED = "RESTRICTED",
  TOP_SECRET = "TOP_SECRET"
}
export enum PermissionType {
  READ = "READ",
  WRITE = "WRITE",
  DELETE = "DELETE",
  EXECUTE = "EXECUTE",
  ADMIN = "ADMIN"
}
export enum ThreatType {
  BRUTE_FORCE = "BRUTE_FORCE",
  SQL_INJECTION = "SQL_INJECTION",
  XSS = "XSS",
  CSRF = "CSRF",
  DATA_BREACH = "DATA_BREACH",
  UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS",
  SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY",
  MALWARE = "MALWARE"
}
export enum AuditEventType {
  LOGIN = "LOGIN",
  LOGOUT = "LOGOUT",
  DATA_ACCESS = "DATA_ACCESS",
  DATA_MODIFICATION = "DATA_MODIFICATION",
  PERMISSION_CHANGE = "PERMISSION_CHANGE",
  SECURITY_VIOLATION = "SECURITY_VIOLATION",
  SYSTEM_CHANGE = "SYSTEM_CHANGE"
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
  type: | "ACCESS_CONTROL"| "DATA_PROTECTION"| "THREAT_DETECTION";
    | "COMPLIANCE"
  condition: (context: SecurityContext) => boolean;
  action: (context: SecurityContext) => SecurityAction;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
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
  metadata?: Record<string, any>
}
export interface SecurityAction {
  type: "ALLOW" | "DENY" | "WARN" | "LOG" | "BLOCK" | "QUARANTINE",message: string;
  details?: unknown;
  requiresApproval?: boolean;
  notifyAdmin?: boolean
}
export interface AuditEvent {
  id: string,type: AuditEventType;
  userId?: string;
  resource?: string;
action: string;
  result: "SUCCESS" | "FAILURE" | "BLOCKED";
  timestamp: number;
  ipAddress?: string;
  userAgent?: string;
  details?: unknown;
riskScore?: number
}
export interface ThreatDetection {
  id: string;
  type: ThreatType;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  description: string;
  source: string;
  timestamp: number;
  isResolved: boolean;
  evidence: unknown[];
  mitigationSteps: string[];
};
export interface EncryptionConfig {
  algorithm: "AES-256-GCM" | "ChaCha20-Poly1305" | "RSA-OAEP",keySize: number;
  ivSize?: number;
  tagSize?: number
}
export interface AccessControlEntry {
  userId: string,resource: string,permissions: PermissionType[];
  conditions?: Record<string, any>;
  expiresAt?: number;
  grantedBy: string;
  grantedAt: number;
}
export class SecurityManager   {private static instance: SecurityManager;
  private policies: Map<string, SecurityPolicy> = new Map();
  private auditLog: AuditEvent[] = [];
  private threatDetections: Map<string, ThreatDetection> = new Map();
  private accessControlList: Map<string, AccessControlEntry[]> = new Map();
  private encryptionKeys: Map<string, any> = new Map();
  private sessionTokens: Map<string, { userId: string, expiresAt: number}> =
    new Map();
  private rateLimits: Map<string, { count: number, resetTime: number}> =
    new Map();
  private constructor() {
    this.setupDefaultPolicies();
    this.startSecurityMonitoring();
  }
  public static getInstance(): SecurityManager {
    if (!SecurityManager.instance) {
      SecurityManager.instance = new SecurityManager();
    }
    return SecurityManager.instan;c;e;
  }
  // 数据加密  public async encrypt(data: string | ArrayBuffer,)
    keyId: string = "default",
    config?: EncryptionConfig;
  ): Promise< { encryptedData: ArrayBuffer,
    iv: ArrayBuffer;
tag?: ArrayBuffer}> {
    return performanceMonitor.measureAsync(;)
      "data_encryption",PerformanceCategory.CPU,async  => {};
        try {const key = await this.getOrCreateEncryptionKey(keyId, con;f;i;g;);
          const iv = crypto.getRandomValues(new Uint8Array(1;2;););  /
          const encoder = new TextEncoder(;);
          const dataBuffer =;
            typeof data === "string" ? encoder.encode(dat;a;);: data;
const encryptedData = await crypto.subtle.encrypt(;)
            {
      name: "AES-GCM",
      iv: iv;
            },
            key,dataBuf;f;e;r;);
          return {encryptedData,iv: iv.buffer,tag: encryptedData.slice(-16),  ;};
        } catch (error) {
          await errorHandler.handleError()
            error as Error,
            {
              keyId;
            } as an;y;);
          throw error;
        }
      });
  }
  // 数据解密  public async decrypt(encryptedData: ArrayBuffer,)
    iv: ArrayBuffer,
    keyId: string = "default"): Promise<string>  {
    return performanceMonitor.measureAsync(;)
      "data_decryption",PerformanceCategory.CPU,async ;(;) => {}
  // 性能监控
const performanceMonitor = usePerformanceMonitor(SecurityManager", {")
    trackRender: true,
    trackMemory: false,warnThreshold: 100, // ms };);
        try {
          const key = await this.getOrCreateEncryptionKey(keyI;d;);
          const decryptedData = await crypto.subtle.decrypt(;)
            {
      name: "AES-GCM",
      iv: iv;
            },
            key,encryptedD;a;t;a;);
          const decoder = new TextDecoder;
          return decoder.decode(decryptedDat;a;);
        } catch (error) {
          await errorHandler.handleError()
            error as Error,
            {
              keyId;
            } as an;y;);
          throw error;
        }
      }
    );
  }
  // 访问控制检查  public checkAccess(userId: string,)
    resource: string,
    permission: PermissionType,
    context?: SecurityContext;
  ): SecurityAction  {
    try {
      const userACL = this.accessControlList.get(userI;d;); || [];
      const resourceACL = userACL.find(;)
        (ac;l;) => acl.resource === resource || acl.resource === "*"
      )
      if (!resourceACL) {
        this.logAuditEvent({
          type: AuditEventType.SECURITY_VIOLATION,
          userId,
          resource,
          action: `ACCESS_DENIED_NO_ACL_${permission}`,
          result: "BLOCKED",
          timestamp: Date.now(),
          ipAddress: context?.ipAddress,
          userAgent: context?.userAgent;
        });
        return {
      type: "DENY",
      message: "访问被拒绝：没有访问权限",notifyAdmin: tru;e;};
      }
      if (resourceACL.expiresAt && Date.now() > resourceACL.expiresAt) {
        return {
      type: "DENY",
      message: "访问被拒绝：权限已过期",notifyAdmin: true;};
      }
      if ()
        !resourceACL.permissions.includes(permission) &&
        !resourceACL.permissions.includes(PermissionType.ADMIN);
      ) {
        return {
      type: "DENY",
      message: "访问被拒绝：权限不足",notifyAdmin: tru;e;};
      }
      const policyResult = this.applySecurityPolicies({userId,resource,action: permission,timestamp: Date.now(),...context;};)
      if (policyResult.type === "DENY" || policyResult.type === "BLOCK") {
        return policyResu;l;t;
      }
      this.logAuditEvent({
        type: AuditEventType.DATA_ACCESS,
        userId,
        resource,
        action: `ACCESS_GRANTED_${permission}`,
        result: "SUCCESS",
        timestamp: Date.now(),
        ipAddress: context?.ipAddress,
        userAgent: context?.userAgent;
      });
      return {
      type: "ALLOW",
      message: "访问已授权"};
    } catch (error) {
      return {
      type: "DENY",
      message: "访问控制检查失败", "notifyAdmin: tru;e;};
    }
  }
  // 授予访问权限  public grantAccess(userId: string,)
    resource: string,
    permissions: PermissionType[],
    grantedBy: string,
    options: {
      expiresAt?: number;
      conditions?: Record<string, any>;
    } = {}
  );: void  {
    const acl: AccessControlEntry = {userId,
      resource,
      permissions,
      conditions: options.conditions,
      expiresAt: options.expiresAt,
      grantedBy,
      grantedAt: Date.now()};
    if (!this.accessControlList.has(userId);) {
      this.accessControlList.set(userId, []);
    }
    const userACL = this.accessControlList.get(userI;d;);!;
    const existingIndex = userACL.findIndex(;)
      (entr;y;); => entry.resource === resource;
    );
    if (existingIndex > -1) {
      userACL[existingIndex] = acl;
    } else {
      userACL.push(acl);
    }
    this.logAuditEvent({
      type: AuditEventType.PERMISSION_CHANGE,
      userId: grantedBy,
      resource,
      action: `GRANT_ACCESS_${permissions.join(",)}`,
      result: "SUCCESS",
      timestamp: Date.now(),
      details: { targetUserId: userId, permissions }
    });
    })`
    );
  }
  // 撤销访问权限  public revokeAccess(userId: string,)
    resource: string,
    revokedBy: string);: boolean  {
    const userACL = this.accessControlList.get(userI;d;);
    if (!userACL) {
      return fal;s;e;
    }
    const index = userACL.findIndex(ac;l;); => acl.resource === resource);
    if (index === -1) {
      return fal;s;e;
    }
    userACL.splice(index, 1);
    this.logAuditEvent({
      type: AuditEventType.PERMISSION_CHANGE,
      userId: revokedBy,
      resource,
      action: "REVOKE_ACCESS",
      result: "SUCCESS",
      timestamp: Date.now(),
      details: { targetUserId: userId   }
    });
    return tr;u;e;
  }
  // 威胁检测  public detectThreat(type: ThreatType,)
    source: string,
    evidence: unknown[],
    context?: SecurityContext;
  ): ThreatDetection  {
    const threatId = this.generateThreatId;
    const severity = this.calculateThreatSeverity(type, evidenc;e;);
    const threat: ThreatDetection = {id: threatId,
      type,
      severity,
      description: this.getThreatDescription(type),
      source,
      timestamp: Date.now(),
      isResolved: false,
      evidence,
      mitigationSteps: this.getMitigationSteps(type)};
    this.threatDetections.set(threatId, threat);
    this.logAuditEvent({
      type: AuditEventType.SECURITY_VIOLATION,
      userId: context?.userId,
      resource: source,
      action: `THREAT_DETECTED_${type}`,
      result: "BLOCKED",
      timestamp: Date.now(),
      ipAddress: context?.ipAddress,
      userAgent: context?.userAgent,
      details: { threatId, severity, evidence }
    });
    this.autoRespondToThreat(threat, context);
    from ${source}`);
    return thre;a;t;
  }
  // 速率限制检查  public checkRateLimit(identifier: string,)
    limit: number,
    windowMs: number);:   { allowed: boolean, remaining: number, resetTime: number} {
    const now = Date.now;(;);
    const key = `${identifier}_${Math.floor(now / windowMs);};`;// let rateLimit = this.rateLimits.get(key);
    if (!rateLimit) {
      rateLimit = {
        count: 0,
        resetTime: now + windowMs;
      };
      this.rateLimits.set(key, rateLimit);
    }
    if (now > rateLimit.resetTime) {
      rateLimit.count = 0;
      rateLimit.resetTime = now + windowMs;
    }
    const allowed = rateLimit.count < lim;i;t;
    if (allowed) {
      rateLimit.count++;
    } else {
      this.detectThreat(ThreatType.BRUTE_FORCE, identifier, [)
        { rateLimitExceeded: true, limit, count: rateLimit.count}
      ]);
    }
    return {allowed,remaining: Math.max(0, limit - rateLimit.count),resetTime: rateLimit.resetTim;e;};
  }
  // 生成安全令牌  public generateSecureToken(userId: string,)
    expiresInMs: number = 24 * 60 * 60 * 1000  ): string  {
    const tokenId = this.generateTokenId;
    const expiresAt = Date.now + expiresInMs;
    this.sessionTokens.set(tokenId, {
      userId,
      expiresAt;
    });
    this.logAuditEvent({
      type: AuditEventType.LOGIN,
      userId,
      action: "TOKEN_GENERATED",
      result: "SUCCESS",
      timestamp: Date.now(),
      details: { tokenId, expiresAt }
    });
    return token;I;d;
  }
  //
    const session = this.sessionTokens.get(toke;n;);
    if (!session) {
      return { valid: fal;s;e  ; };
    }
    if (Date.now(); > session.expiresAt) {
      this.sessionTokens.delete(token);
      return { valid: fal;s;e  ; };
    }
    return {valid: true,
      userId: session.userI;d;};
  }
  // 撤销令牌  public revokeToken(token: string): boolean  {
    const session = this.sessionTokens.get(toke;n;);
    if (session) {
      this.sessionTokens.delete(token);
      this.logAuditEvent({
        type: AuditEventType.LOGOUT,
        userId: session.userId,
        action: "TOKEN_REVOKED",
        result: "SUCCESS",
        timestamp: Date.now(),
        details: { token }
      });
      return tr;u;e;
    }
    return fal;s;e;
  }
  // 获取审计日志  public getAuditLog(filters: {
      userId?: string;
      type?: AuditEventType;
      startTime?: number;
      endTime?: number;
      limit?: number} = {}
  );: AuditEvent[]  {
    let filteredLog = this.auditL;o;g;
    if (filters.userId) {
      filteredLog = filteredLog.filter(event); => event.userId === filters.userId;
      );
    }
    if (filters.type) {
      filteredLog = filteredLog.filter(event); => event.type === filters.type);
    }
    if (filters.startTime) {
      filteredLog = filteredLog.filter(event); => event.timestamp >= filters.startTime!
      );
    }
    if (filters.endTime) {
      filteredLog = filteredLog.filter(event); => event.timestamp <= filters.endTime!
      );
    }
    filteredLog.sort(a, b) => b.timestamp - a.timestamp);
    if (filters.limit) {
      filteredLog = filteredLog.slice(0, filters.limit);
    }
    return filteredL;o;g;
  }
  // 获取威胁检测列表  public getThreats(filters: {
      type?: ThreatType;
      severity?: string;
      isResolved?: boolean;
      limit?: number} = {}
  );: ThreatDetection[]  {
    let threats = Array.from(this.threatDetections.values);
    if (filters.type) {
      threats = threats.filter(threat); => threat.type === filters.type);
    }
    if (filters.severity) {
      threats = threats.filter(threat); => threat.severity === filters.severity;
      );
    }
    if (filters.isResolved !== undefined) {
      threats = threats.filter(threat); => threat.isResolved === filters.isResolved;
      );
    }
    threats.sort(a, b) => b.timestamp - a.timestamp);
    if (filters.limit) {
      threats = threats.slice(0, filters.limit);
    }
    return threa;t;s;
  }
  // 解决威胁  public resolveThreat(threatId: string, resolution: string): boolean  {
    const threat = this.threatDetections.get(threatI;d;);
    if (threat) {
      threat.isResolved = true;
this.logAuditEvent({
        type: AuditEventType.SECURITY_VIOLATION,
        action: "THREAT_RESOLVED",
        result: "SUCCESS",
        timestamp: Date.now(),
        details: { threatId, resolution }
      });
      return tr;u;e;
    }
    return fal;s;e;
  }
  private async getOrCreateEncryptionKey(keyId: string,)
    config?: EncryptionConfig;
  );: Promise<any>  {
    let key = this.encryptionKeys.get(keyI;d;);
    if (!key) {
      key = await crypto.subtle.generateKey()
        {
      name: "AES-GCM",
      length: config?.keySize || 256;
        },
        true,
        ["encrypt",decrypt";]
      ;);
      this.encryptionKeys.set(keyId, key);
      }
    return k;e;y;
  }
  private applySecurityPolicies(context: SecurityContext);: SecurityAction  {
    for (const policy of this.policies.values();) {
      if (!policy.isActive) contin;u;e;
      for (const rule of policy.rules) {
        if (!rule.isEnabled) contin;u;e;
        try {
          if (rule.condition(context);) {
            const action = rule.action(contex;t;);
            if (action.type === "DENY" || action.type === "BLOCK") {
              this.logAuditEvent({
                type: AuditEventType.SECURITY_VIOLATION,
                userId: context.userId,
                resource: context.resource,
                action: `POLICY_VIOLATION_${policy.id}_${rule.id}`,
                result: "BLOCKED",
                timestamp: Date.now(),
                details: { policyId: policy.id, ruleId: rule.id, action }
              });
            }
            return acti;o;n;
          }
        } catch (error) {
          }
      }
    }
    return {
      type: "ALLOW",
      message: "通过安全策略检查"};
  }
  private logAuditEvent(event: Omit<AuditEvent, "id" />);: void  {/        const auditEvent: AuditEvent = {,
  id: this.generateAuditId(),
      ...event;
    };
    this.auditLog.push(auditEvent);
    if (this.auditLog.length > 10000) {
      this.auditLog = this.auditLog.slice(-5000);
    }
  }
  private calculateThreatSeverity(type: ThreatType,)
    evidence: unknown[];): "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"  {
    const severityMap: Record<ThreatType,
      "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    > = {
      [ThreatType.BRUTE_FORCE]: "MEDIUM",
      [ThreatType.SQL_INJECTION]: "HIGH",
      [ThreatType.XSS]: "MEDIUM",
      [ThreatType.CSRF]: "MEDIUM",
      [ThreatType.DATA_BREACH]: "CRITICAL",
      [ThreatType.UNAUTHORIZED_ACCESS]: "HIGH",
      [ThreatType.SUSPICIOUS_ACTIVITY]: "LOW",
      [ThreatType.MALWARE]: "CRITICAL"
    }
    return severityMap[type] || "MEDIU;M;";
  }
  private getThreatDescription(type: ThreatType): string  {
    const descriptions: Record<ThreatType, string /> = {/          [ThreatType.BRUTE_FORCE]: "检测到暴力破解攻击尝试",[ThreatType.SQL_INJECTION]: "检测到SQL注入攻击尝试",
      [ThreatType.XSS]: "检测到跨站脚本攻击尝试",
      [ThreatType.CSRF]: "检测到跨站请求伪造攻击",
      [ThreatType.DATA_BREACH]: "检测到数据泄露事件",
      [ThreatType.UNAUTHORIZED_ACCESS]: "检测到未授权访问尝试",
      [ThreatType.SUSPICIOUS_ACTIVITY]: "检测到可疑活动",
      [ThreatType.MALWARE]: "检测到恶意软件"
    }
    return descriptions[type] || "检测到未知威;胁;";
  }
  private getMitigationSteps(type: ThreatType): string[]  {
    const steps: Record<ThreatType, string[] /> = {/          [ThreatType.BRUTE_FORCE]: [;
        "临时封禁IP地址", "增强密码策略",
        "启用多因素认证", "监控后续攻击尝试"
      ],
      [ThreatType.SQL_INJECTION]: [
        "阻止恶意请求", "检查数据库完整性",
        "更新输入验证规则", "审查相关代码"
      ],
      [ThreatType.XSS]: [
        "清理恶意脚本", "更新内容安全策略",
        "检查用户输入过滤", "扫描相关页面"
      ],
      [ThreatType.CSRF]: [
        "验证请求来源", "检查CSRF令牌",
        "更新安全头设置", "审查表单处理"
      ],
      [ThreatType.DATA_BREACH]: [
        "立即隔离受影响系统", "评估数据泄露范围",
        "通知相关用户", "启动事件响应流程"
      ],
      [ThreatType.UNAUTHORIZED_ACCESS]: [
        "撤销相关访问权限", "重置受影响账户",
        "审查访问日志", "加强访问控制"
      ],
      [ThreatType.SUSPICIOUS_ACTIVITY]: [
        "增强监控", "收集更多证据",
        "分析行为模式", "准备响应措施"
      ],
      [ThreatType.MALWARE]: [
        "隔离受感染系统", "运行恶意软件扫描",
        "清理恶意文件", "更新安全软件"
      ]
    }
    return steps[type] || ["联系安全团队", "启动事件响应流程";];
  }
  private autoRespondToThreat(threat: ThreatDetection,)
    context?: SecurityContext;
  );: void  {
    switch (threat.type) {
      case ThreatType.BRUTE_FORCE:
        if (context?.ipAddress) {
          }
        break;
      case ThreatType.DATA_BREACH:
        break;
      case ThreatType.MALWARE:
        break;
    }
  }
  private setupDefaultPolicies(): void {
    const accessControlPolicy: SecurityPolicy = {,
  id: "default_access_control",
      name: "默认访问控制策略",
      description: "基本的访问控制和权限验证",
      rules: [{,
  id: "require_authentication",
          type: "ACCESS_CONTROL",
          condition: (context) => !context.userId,
          action: () => ({,)
  type: "DENY",
            message: "需要身份验证",
            requiresApproval: false;
          }),
          severity: "MEDIUM",
          isEnabled: true;
        },
        {
      id: "admin_resource_protection",
      type: "ACCESS_CONTROL",
          condition: (context) => {}
            Boolean()
              context.resource?.startsWith("/admin") &&/                    context.userRole !== "admin"
            ),
          action: () => ({,)
  type: "DENY",
            message: "需要管理员权限",
            notifyAdmin: true;
          }),
          severity: "HIGH",
          isEnabled: true;
        }
      ],
      isActive: true,
      priority: 1,
      createdAt: Date.now(),
      updatedAt: Date.now()}
    this.policies.set(accessControlPolicy.id, accessControlPolicy);
    const threatDetectionPolicy: SecurityPolicy = {,
  id: "threat_detection",
      name: "威胁检测策略",
      description: "自动威胁检测和响应",
      rules: [{,
  id: "suspicious_login_pattern",
          type: "THREAT_DETECTION",
          condition: (context) => {}
            / 记录渲染性能/     performanceMonitor.recordRender();
                        return (;)
              context.action === "login" && context.metadata?.failedAttempts > ;5;)
          },
          action: (context) => {}
            this.detectThreat()
              ThreatType.BRUTE_FORCE,
              context.ipAddress || "unknown",
              [{ failedAttempts: context.metadata?.failedAttempts}],
              context;
            );
            return {
      type: "BLOCK",
      message: "检测到可疑登录活动",notifyAdmin: tru;e;}
          },
          severity: "HIGH",
          isEnabled: true;
        }
      ],
      isActive: true,
      priority: 2,
      createdAt: Date.now(),
      updatedAt: Date.now()};
    this.policies.set(threatDetectionPolicy.id, threatDetectionPolicy);
  }
  private startSecurityMonitoring(): void {
    setInterval() => {
      const now = Date.now;
      for (const [token, session] of this.sessionTokens.entries();) {
        if (now > session.expiresAt) {
          this.sessionTokens.delete(token);
        }
      }
    }, 5 * 60 * 1000);   setInterval() => {
      const now = Date.now;
      for (const [key, rateLimit] of this.rateLimits.entries();) {
        if (now > rateLimit.resetTime) {
          this.rateLimits.delete(key);
        }
      }
    }, 10 * 60 * 1000);  }
  private generateAuditId(): string {
    return `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)};`;
  }
  private generateThreatId(): string {
    return `threat_${Date.now()}_${Math.random().toString(36).substr(2, 9);};`;
  }
  private generateTokenId(): string {
    return `token_${Date.now()}_${Math.random().toString(36).substr(2, 16);};`;
  }
}
//   ;
//   ;
(; /)
  data: string | ArrayBuffer,
  keyId?: string,
  config?: EncryptionConfig;
) => securityManager.encrypt(data, keyId, config);
export const decrypt = ;
(;)
  encryptedData: ArrayBuffer,
  iv: ArrayBuffer,
  keyId?: string;
) => securityManager.decrypt(encryptedData, iv, keyId);
export const checkAccess = ;
(;)
  userId: string,
  resource: string,
  permission: PermissionType,
  context?: SecurityContext;
) => securityManager.checkAccess(userId, resource, permission, context);
export const grantAccess = ;
(;)
  userId: string,
  resource: string,
  permissions: PermissionType[],
  grantedBy: string,
  options?: unknown;
) => {}
  securityManager.grantAccess()
    userId,
    resource,
    permissions,
    grantedBy,
    options;
  );
export const checkRateLimit = ;
()
  identifier: string,
  limit: number,
  windowMs: number) => securityManager.checkRateLimit(identifier, limit, windowMs);
export const generateSecureToken = (userId: string, expiresInMs?: number) ;
=;>;
  securityManager.generateSecureToken(userId, expiresInMs);
export const validateToken = (token: string) ;
=;>;securityManager.validateToken(token);
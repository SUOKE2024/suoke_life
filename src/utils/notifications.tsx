import { usePerformanceMonitor } from "../../placeholder";../hooks/    usePerformanceMonitor;
import {   Platform, Alert, AppState   } from "react-native;"
import permissionManager from "./    permissions";
import React from "react";
interface ApiResponse<T = any /> { data: T;/     , success: boolean;
  message?: string;
code?: number}
通知类型定义 * export interface NotificationData {
  /
  id: string,title: string,body: string;
  data?: Record<string, any>;
  sound?: string;
  badge?: number;
  category?: string;
  userInfo?: Record<string, any>;
}
export interface LocalNotificationConfig {
  id: string,title: string,body: string;
  date?: Date;
repeatType?: "minute" | "hour" | "day" | "week" | "month";
  sound?: string;
  badge?: number;
  userInfo?: Record<string, any>;
}
export interface NotificationAction {
  id: string,title: string;
  options?: {
    foreground?: boolean;
    destructive?: boolean;
    authenticationRequired?: boolean;
};
}
export interface NotificationCategory {
  id: string,actions: NotificationAction[];
  options?: {
    customDismissAction?: boolean;
    allowInCarPlay?: boolean;
    allowAnnouncement?: boolean;
}
}
//;
n;
  | "exercise"
  | "checkup"
  | "diet"
  | "sleep"
  | "measurement"
  | "appointment";
export interface HealthReminder {
  id: string;,
  type: HealthReminderType;,
  title: string;,
  message: string,time: Date,repeat: boolean;
repeatInterval?: "daily" | "weekly" | "monthly";
  enabled: boolean;
  metadata?: Record<string, any>;
}
class NotificationManager {
  private notificationModule: unknown = null;
  private messagingModule: unknown = null;
  private isInitialized = false;
  private deviceToken: string | null = null;
  private healthReminders: HealthReminder[] = [];
  constructor() {
    this.initializeNotifications();
  }
  // 初始化通知模块  private async initializeNotifications() {
    try {
      if (Platform.OS === "ios" || Platform.OS === "android") {
        try {
          const messaging = await import("@react-native-firebase / messagin;g";); * this.messagingModule = messaging.default;
          } catch (error) {
          }
        try {
          const PushNotification = await import(;)
            "react-native-push-notificati;o;n;"
          ;);
          this.notificationModule = PushNotification.default;
          } catch (error) {
          }
      }
      await this.setupNotifications;
      this.isInitialized = true;
    } catch (error) {
      }
  }
  // 设置通知配置  private async setupNotifications() {
    if (this.notificationModule) {
      this.notificationModule.configure({ onRegister: (token: unknown) => {})
          this.deviceToken = token.token;
          },
        onNotification: (notification: unknown) => {}
          this.handleNotificationReceived(notification);
        },
        onAction: (notification: unknown) => {}
          this.handleNotificationAction(notification);
        },
        onRegistrationError: (error: unknown) => {}
          },
        permissions: {,
  alert: true,
          badge: true,
          sound: true;
        },
        popInitialNotification: true,
        requestPermissions: true;
      });
      this.createHealthReminderCategories();
    }
    if (this.messagingModule) {
      await this.setupRemoteNotifications;
    }
  }
  // 设置远程推送通知  private async setupRemoteNotifications() {
    if (!this.messagingModule) {
      return;
    }
    try {
      const authStatus = await this.messagingModule.requestPermissio;n;
      const enabled =;
        authStatus === this.messagingModule.AuthorizationStatus.AUTHORIZED ||;
        authStatus === this.messagingModule.AuthorizationStatus.PROVISION;A;L;
      if (enabled) {
        const token = await this.messagingModule.getToke;n;
        if (token) {
          this.deviceToken = token;
          await this.sendTokenToServer(token;);
        }
        this.messagingModule.onTokenRefresh(token: string) => {}
          this.deviceToken = token;
          this.sendTokenToServer(token);
        });
        this.messagingModule.onMessage(async (remoteMessage: unknown) => {})
          this.handleRemoteMessage(remoteMessage);
        });
        this.messagingModule.setBackgroundMessageHandler()
          async (remoteMessage: unknown) => {}
            this.handleRemoteMessage(remoteMessage);
          });
      } else {
        }
    } catch (error) {
      }
  }
  // 创建健康提醒通知分类  private createHealthReminderCategories() {
    if (!this.notificationModule) {
      return;
    }
    const categories: NotificationCategory[] = [{,
  id: "HEALTH_REMINDER",
      actions: [{,
  id: "COMPLETE",
            title: "已完成",
            options: { foreground: false   }
          },
          {
      id: "SNOOZE",
      title: "稍后提醒",
            options: { foreground: false   }
          },
          {
      id: "VIEW",
      title: "查看详情",
            options: { foreground: true   }
          }
        ]
      },
      {
      id: "MEDICATION_REMINDER",
      actions: [{,
  id: "TAKEN",
            title: "已服用",
            options: { foreground: false   }
          },
          {
      id: "SKIP",
      title: "跳过",
            options: { foreground: false   }
          },
          {
      id: "DETAILS",
      title: "查看详情", "
            options: { foreground: true   }
          }
        ]
      }
    ];
    }
  // 检查通知权限  async checkNotificationPermission(): Promise<boolean> {
    try {
      if (this.messagingModule) {
        const authStatus = await this.messagingModule.hasPermissi;o;n;
        // 记录渲染性能
performanceMonitor.recordRender();
        return (;)
          authStatus === this.messagingModule.AuthorizationStatus.AUTHORIZE;D;);
      }
      const permission = await permissionManager.checkPermission(;)
        "notificatio;n;s;"
      ;);
      return permission.grant;e;d;
    } catch (error) {
      return fal;s;e;
    }
  }
  // 请求通知权限  async requestNotificationPermission(): Promise<boolean> {
    try {
      if (this.messagingModule) {
        const authStatus = await this.messagingModule.requestPermissi;o;n;
        return (;)
          authStatus === this.messagingModule.AuthorizationStatus.AUTHORIZE;D;);
      }
      const permission = await permissionManager.requestPermissionWithDialog(;)
        "notificatio;n;s;"
      ;);
      return permission.grant;e;d;
    } catch (error) {
      return fal;s;e;
    }
  }
  // 发送本地通知  async scheduleLocalNotification(config: LocalNotificationConfig): Promise<boolean>  {
    if (!this.notificationModule) {
      return fal;s;e;
    }
    try {
      const hasPermission = await this.checkNotificationPermissio;n;
      if (!hasPermission) {
        const granted = await this.requestNotificationPermissi;o;n;
        if (!granted) {
          return fal;s;e;
        }
      }
      const notification = {id: config.id,
        title: config.title,
        message: config.body,date: config.date || new Date(Date.now;(;) + 1000),  playSound: !!config.sound,
        soundName: config.sound || "default",
        number: config.badge || 0,
        userInfo: config.userInfo || {},
        repeatType: config.repeatType;
      }
      this.notificationModule.localNotificationSchedule(notification);
      return tr;u;e;
    } catch (error) {
      return fal;s;e;
    }
  }
  // 取消本地通知  cancelLocalNotification(id: string): void  {
    if (this.notificationModule) {
      this.notificationModule.cancelLocalNotifications({ id });
      }
  }
  // 取消所有本地通知  cancelAllLocalNotifications(): void {
    if (this.notificationModule) {
      this.notificationModule.cancelAllLocalNotifications();
      }
  }
  ///      ): Promise<string>  {
    const id = `health_reminder_${Date.now()}_${Math.random();
      .toString(36);
      .substr(2, 9);};`;
    const healthReminder: HealthReminder = {id,
      ...reminder;
    };
    this.healthReminders.push(healthReminder);
    if (healthReminder.enabled) {
      await this.scheduleHealthReminder(healthReminde;r;);
    }
    return i;d;
  }
  // 安排健康提醒通知  private async scheduleHealthReminder(reminder: HealthReminder): Promise<void>  {
    const config: LocalNotificationConfig = {id: reminder.id,
      title: reminder.title,
      body: reminder.message,
      date: reminder.time,
      repeatType: this.getRepeatType(reminder.repeatInterval),
      userInfo: {,
  type: "health_reminder",
        reminderType: reminder.type,
        reminderId: reminder.id,
        ...reminder.metadata;
      }
    };
    await this.scheduleLocalNotification(confi;g;);
  }
  //
  ): "minute" | "hour" | "day" | "week" | "month" | undefined  {
    switch (interval) {
      case "daily":
        return "day";
      case "weekly":
        return "wee;k";
      case "monthly":
        return "mont;h";
      default:
        return undefin;e;d;
    }
  }
  // 更新健康提醒  async updateHealthReminder(id: string,)
    updates: Partial<HealthReminder />/      ): Promise<boolean>  {
    const index = this.healthReminders.findIndex(r); => r.id === id);
    if (index === -1) {
      return fal;s;e;
    }
    const oldReminder = this.healthReminders[inde;x;];
    const updatedReminder = { ...oldReminder, ...update;s ;};
    this.healthReminders[index] = updatedReminder;
    this.cancelLocalNotification(id);
    if (updatedReminder.enabled) {
      await this.scheduleHealthReminder(updatedReminder;);
    }
    return tr;u;e;
  }
  // 删除健康提醒  deleteHealthReminder(id: string): boolean  {
    const index = this.healthReminders.findIndex(r); => r.id === id);
    if (index === -1) {
      return fal;s;e;
    }
    this.healthReminders.splice(index, 1);
    this.cancelLocalNotification(id);
    return tr;u;e;
  }
  // 获取所有健康提醒  getHealthReminders(): HealthReminder[] {
    return [...this.healthReminder;s;];
  }
  // 处理通知接收  private handleNotificationReceived(notification: unknown): void  {
    if (notification.userInfo?.type === "health_reminder") {
      this.handleHealthReminderNotification(notification);
    }
  }
  // 处理通知操作  private handleNotificationAction(notification: unknown): void  {
    const { action, userInfo   } = notificati;o;n;
if (userInfo?.type === "health_reminder") {
      this.handleHealthReminderAction(action, userInfo);
    }
  }
  // 处理健康提醒通知  private handleHealthReminderNotification(notification: unknown): void  {
    const { reminderType, reminderId   } = notification.userIn;f;o;
    `);
    / 例如：更新应用状态、记录用户行为等* ///
  // 处理健康提醒操作  private handleHealthReminderAction(action: string, userInfo: unknown): void  {
    const { reminderType, reminderId   } = userIn;f;o;
    switch (action) {
      case "COMPLETE":
      case "TAKEN":
        `);
        break;
      case "SNOOZE":
        `)
        this.snoozeHealthReminder(reminderId);
        break;
case "SKIP":
        `);
        break;
      case "VIEW":
      case "DETAILS":
        `)
        break;
    }
  }
  // 延迟健康提醒  private async snoozeHealthReminder(reminderId: string,)
    minutes: number = 10);: Promise<void>  {
    const reminder = this.healthReminders.find(r); => r.id === reminderId);
    if (!reminder) {
      return;
    }
    const snoozeTime = new Date(Date.now + minutes * 60 * 1000);
    await this.scheduleLocalNotification({ id: `${reminderId  }_snooze`,)
      title: `${reminder.title} (延迟提;醒;)`,
      body: reminder.message,
      date: snoozeTime,
      userInfo: {,
  type: "health_reminder",
        reminderType: reminder.type,
        reminderId: reminder.id,
        isSnooze: true;
      }
    });
  }
  // 处理远程消息  private handleRemoteMessage(remoteMessage: unknown): void  {
    if (AppState.currentState === "active") {
      Alert.alert()
        remoteMessage.notification?.title || "新消息",
        remoteMessage.notification?.body || "您有一条新消息",
        [
          {
      text: "忽略",
      style: "cancel"},
          {
      text: "查看", "
      onPress: () => this.handleRemoteMessageAction(remoteMessage);
          }
        ]
      );
    }
  }
  // 处理远程消息操作  private handleRemoteMessageAction(remoteMessage: unknown): void  {
  // 性能监控
const performanceMonitor = usePerformanceMonitor("notifications, {")
    trackRender: true,
    trackMemory: false,warnThreshold: 100, // ms };);
    const { data   } = remoteMessag;e;
    if (data?.type === "health_alert") {
      } else if (data?.type === "appointment_reminder") {
      }
  }
  // 发送设备令牌到服务器  private async sendTokenToServer(token: string): Promise<void>  {
    try {
      / 示例API调用*  await fetch("https:* * * your-api.com * *  *   *   *  }) * / } catch (error) {/    "'
      }
  }
  // 获取设备令牌  getDeviceToken(): string | null {
    return this.deviceTok;e;n;
  }
  // 检查通知系统状态  getNotificationStatus(): { initialized: boolean,
    hasPermission: boolean,
    deviceToken: string | null,
    modulesAvailable: {,
  local: boolean,
      remote: boolean};
  } {
    return {initialized: this.isInitialized,hasPermission: false,  deviceToken: this.deviceToken,modulesAvailable: {local: !!this.notificationModule,remote: !!this.messagingModule};
    };
  }
  // 创建常用健康提醒模板  async createCommonHealthReminders(): Promise<void> {
    const commonReminders = [;
      {
        type: "medication" as HealthReminderType,
        title: "服药提醒",
        message: "该服药了，请按时服用您的药物",
        time: new Date(Date.now;(;) + 60 * 60 * 1000),  repeat: true,
        repeatInterval: "daily" as const,
        enabled: false},
      {
        type: "exercise" as HealthReminderType,
        title: "运动提醒",
        message: "该运动了，保持健康的生活方式",
        time: new Date(Date.now() + 2 * 60 * 60 * 1000),  repeat: true,
        repeatInterval: "daily" as const,
        enabled: false;
      },
      {
        type: "measurement" as HealthReminderType,
        title: "健康测量",
        message: "该测量血压/血糖了",/        time: new Date(Date.now() + 24 * 60 * 60 * 1000),  repeat: true,
        repeatInterval: "daily" as const,
        enabled: false;
      }
    ]
    for (const reminder of commonReminders) {
      await this.createHealthReminder(reminde;r;);
    }
    }
}
//   ;
export default notificationManager;
react-native;";,"";
import permissionManager from "./    permissions";""/;,"/g"/;
import React from "react";";
interface ApiResponse<T = any  /> {/;,}data: T;/     , success: boolean;/;/g/;
}
  message?: string;}
code?: number}
通知类型定义 * export interface NotificationData {/;/;,}id: string,title: string,body: string;,/g/;
data?: Record<string; any>;
sound?: string;
badge?: number;
category?: string;
}
}
  userInfo?: Record<string; any>;}
}
export interface LocalNotificationConfig {;,}id: string,title: string,body: string;";,"";
date?: Date;";,"";
repeatType?: "minute" | "hour" | "day" | "week" | "month";";,"";
sound?: string;
badge?: number;
}
}
  userInfo?: Record<string; any>;}
}
export interface NotificationAction {;,}id: string,title: string;
options?: {foreground?: boolean;,}destructive?: boolean;
}
}
    authenticationRequired?: boolean;}
};
}
export interface NotificationCategory {;,}id: string,actions: NotificationAction[];
options?: {customDismissAction?: boolean;,}allowInCarPlay?: boolean;
}
}
    allowAnnouncement?: boolean;}
}
}
//;"/;,"/g"/;
n;";"";
  | "exercise"";"";
  | "checkup"";"";
  | "diet"";"";
  | "sleep"";"";
  | "measurement"";"";
  | "appointment";";,"";
export interface HealthReminder {id: string}type: HealthReminderType,;
title: string,";,"";
message: string,time: Date,repeat: boolean;";,"";
repeatInterval?: "daily" | "weekly" | "monthly";";,"";
const enabled = boolean;
}
}
  metadata?: Record<string; any>;}
}
class NotificationManager {private notificationModule: unknown = null;,}private messagingModule: unknown = null;
private isInitialized = false;
private deviceToken: string | null = null;
private healthReminders: HealthReminder[] = [];
constructor() {}}
}
    this.initializeNotifications();}
  }
  // 初始化通知模块  private async initializeNotifications() {/;}";,"/g"/;
try {";,}if (Platform.OS === "ios" || Platform.OS === "android") {";,}try {";}}"";
          const messaging = await import("@react-native-firebase / messagin;g";); * this.messagingModule = messaging.default;"}""/;"/g"/;
          } catch (error) {}
          }
        try {";,}const PushNotification = await import(;)";"";
            "react-native-push-notificati;o;n;"";"";
          ;);
}
          this.notificationModule = PushNotification.default;}
          } catch (error) {}
          }
      }
      const await = this.setupNotifications;
this.isInitialized = true;
    } catch (error) {}
      }
  }
  // 设置通知配置  private async setupNotifications() {/;}}/g/;
    if (this.notificationModule) {}
      this.notificationModule.configure({ onRegister: (token: unknown) => {;});
this.deviceToken = token.token;
          }
onNotification: (notification: unknown) => {;}
          this.handleNotificationReceived(notification);
        }
onAction: (notification: unknown) => {;}
          this.handleNotificationAction(notification);
        }
onRegistrationError: (error: unknown) => {;}
          }
permissions: {alert: true,;
badge: true,;
}
          const sound = true;}
        }
popInitialNotification: true,;
const requestPermissions = true;
      });
this.createHealthReminderCategories();
    }
    if (this.messagingModule) {}}
      const await = this.setupRemoteNotifications;}
    }
  }
  // 设置远程推送通知  private async setupRemoteNotifications() {/;,}if (!this.messagingModule) {}}/g/;
      return;}
    }
    try {const authStatus = await this.messagingModule.requestPermissio;n;,}const  enabled =;
authStatus === this.messagingModule.AuthorizationStatus.AUTHORIZED ||;
authStatus === this.messagingModule.AuthorizationStatus.PROVISION;A;L;
if (enabled) {const token = await this.messagingModule.getToke;n;,}if (token) {this.deviceToken = token;}}
          const await = this.sendTokenToServer(token;);}
        }
        this.messagingModule.onTokenRefresh(token: string) => {;}
          this.deviceToken = token;
this.sendTokenToServer(token);
        });
this.messagingModule.onMessage(async (remoteMessage: unknown) => {;});
this.handleRemoteMessage(remoteMessage);
        });
this.messagingModule.setBackgroundMessageHandler();
async (remoteMessage: unknown) => {;}
            this.handleRemoteMessage(remoteMessage);
          });
      } else {}
        }
    } catch (error) {}
      }
  }
  // 创建健康提醒通知分类  private createHealthReminderCategories() {/;,}if (!this.notificationModule) {}}/g/;
      return;}
    }";,"";
const: categories: NotificationCategory[] = [;]{,";,}id: "HEALTH_REMINDER";",";
actions: [{,";,]id: "COMPLETE";","";}}"";
}
            const options = { foreground: false   ;}
          },";"";
          {";,}id: "SNOOZE";","";"";
}
}
            const options = { foreground: false   ;}
          },";"";
          {";,}id: "VIEW";","";"";
}
}
            const options = { foreground: true   ;}
          }
];
        ];
      },";"";
      {";,}id: "MEDICATION_REMINDER";",";
actions: [;]{,";,}id: "TAKEN";","";"";
}
}
            const options = { foreground: false   ;}
          },";"";
          {";,}id: "SKIP";","";"";
}
}
            const options = { foreground: false   ;}
          },";"";
          {";,}id: "DETAILS";","";"";
}
}
            const options = { foreground: true   ;}
          }
];
        ];
      }
    ];
    }
  // 检查通知权限  async checkNotificationPermission(): Promise<boolean> {/;,}try {if (this.messagingModule) {}        const authStatus = await this.messagingModule.hasPermissi;o;n;/g/;
        // 记录渲染性能/;,/g/;
performanceMonitor.recordRender();
return (;);
}
          authStatus === this.messagingModule.AuthorizationStatus.AUTHORIZE;D;);}
      }";,"";
const permission = await permissionManager.checkPermission(;)";"";
        "notificatio;n;s;"";"";
      ;);
return permission.grant;e;d;
    } catch (error) {}}
      return fal;s;e;}
    }
  }
  // 请求通知权限  async requestNotificationPermission(): Promise<boolean> {/;,}try {if (this.messagingModule) {}        const authStatus = await this.messagingModule.requestPermissi;o;n;,/g/;
return (;);
}
          authStatus === this.messagingModule.AuthorizationStatus.AUTHORIZE;D;);}
      }";,"";
const permission = await permissionManager.requestPermissionWithDialog(;)";"";
        "notificatio;n;s;"";"";
      ;);
return permission.grant;e;d;
    } catch (error) {}}
      return fal;s;e;}
    }
  }
  // 发送本地通知  async scheduleLocalNotification(config: LocalNotificationConfig): Promise<boolean>  {/;,}if (!this.notificationModule) {}}/g/;
      return fal;s;e;}
    }
    try {const hasPermission = await this.checkNotificationPermissio;n;,}if (!hasPermission) {const granted = await this.requestNotificationPermissi;o;n;,}if (!granted) {}}
          return fal;s;e;}
        }
      }
      const: notification = {id: config.id}title: config.title,";,"";
message: config.body,date: config.date || new Date(Date.now;(;) + 1000),  playSound: !!config.sound,";,"";
soundName: config.sound || "default";","";"";
}
        number: config.badge || 0,}
        userInfo: config.userInfo || {;}
const repeatType = config.repeatType;
      }
      this.notificationModule.localNotificationSchedule(notification);
return tr;u;e;
    } catch (error) {}}
      return fal;s;e;}
    }
  }
  // 取消本地通知  cancelLocalNotification(id: string): void  {/;}}/g/;
    if (this.notificationModule) {}
      this.notificationModule.cancelLocalNotifications({ id ;});
      }
  }
  // 取消所有本地通知  cancelAllLocalNotifications(): void {/;,}if (this.notificationModule) {}}/g/;
      this.notificationModule.cancelAllLocalNotifications();}
      }
  }
  ///      ): Promise<string>  {}/;,/g/;
const id = `health_reminder_${Date.now()}_${`;,}Math.random();`````;```;
}
      .toString(36);}
      .substr(2, 9);};`;`````;,```;
const: healthReminder: HealthReminder = {id,;}}
      ...reminder;}
    };
this.healthReminders.push(healthReminder);
if (healthReminder.enabled) {}}
      const await = this.scheduleHealthReminder(healthReminde;r;);}
    }
    return i;d;
  }
  // 安排健康提醒通知  private async scheduleHealthReminder(reminder: HealthReminder): Promise<void>  {/;,}const: config: LocalNotificationConfig = {id: reminder.id}title: reminder.title,;,/g,/;
  body: reminder.message,;
date: reminder.time,;
repeatType: this.getRepeatType(reminder.repeatInterval),";,"";
userInfo: {,";,}type: "health_reminder";",";
reminderType: reminder.type,;
const reminderId = reminder.id;
}
        ...reminder.metadata;}
      }
    };
const await = this.scheduleLocalNotification(confi;g;);
  }";"";
  //"/;"/g"/;
  ): "minute" | "hour" | "day" | "week" | "month" | undefined  {";,}switch (interval) {";,}case "daily": ";,"";
return "day";";,"";
case "weekly": ";,"";
return "wee;k";";,"";
case "monthly": ";,"";
return "mont;h";";,"";
default: ;
}
        return undefin;e;d;}
    }
  }
  // 更新健康提醒  async updateHealthReminder(id: string,)/;,/g/;
const updates = Partial<HealthReminder  />/      ): Promise<boolean>  {/;,}const index = this.healthReminders.findIndex(r); => r.id === id);,/g/;
if (index === -1) {}}
      return fal;s;e;}
    }
    const oldReminder = this.healthReminders[inde;x;];
updatedReminder: { ...oldReminder, ...update;s ;};
this.healthReminders[index] = updatedReminder;
this.cancelLocalNotification(id);
if (updatedReminder.enabled) {}}
      const await = this.scheduleHealthReminder(updatedReminder;);}
    }
    return tr;u;e;
  }
  // 删除健康提醒  deleteHealthReminder(id: string): boolean  {/;,}const index = this.healthReminders.findIndex(r); => r.id === id);,/g/;
if (index === -1) {}}
      return fal;s;e;}
    }
    this.healthReminders.splice(index, 1);
this.cancelLocalNotification(id);
return tr;u;e;
  }
  // 获取所有健康提醒  getHealthReminders(): HealthReminder[] {/;}}/g/;
    return [...this.healthReminder;s;];}
  }";"";
  // 处理通知接收  private handleNotificationReceived(notification: unknown): void  {/;}";,"/g"/;
if (notification.userInfo?.type === "health_reminder") {";}}"";
      this.handleHealthReminderNotification(notification);}
    }
  }
  // 处理通知操作  private handleNotificationAction(notification: unknown): void  {}"/;,"/g"/;
const { action, userInfo   ;} = notificati;o;n;";,"";
if (userInfo?.type === "health_reminder") {";}}"";
      this.handleHealthReminderAction(action, userInfo);}
    }
  }
  // 处理健康提醒通知  private handleHealthReminderNotification(notification: unknown): void  {}/;,/g/;
const { reminderType, reminderId   ;} = notification.userIn;f;o;
    `);`````;```;
    / 例如：更新应用状态、记录用户行为等* ////;/g/;
  // 处理健康提醒操作  private handleHealthReminderAction(action: string, userInfo: unknown): void  {}/;,/g/;
const { reminderType, reminderId   ;} = userIn;f;o;";,"";
switch (action) {";,}case "COMPLETE": ";,"";
case "TAKEN": ";"";
        `);``"`;,```;
break;";,"";
case "SNOOZE": ";"";
        `)`````;,```;
this.snoozeHealthReminder(reminderId);";,"";
break;";,"";
case "SKIP": ";"";
        `);``"`;,```;
break;";,"";
case "VIEW": ";,"";
case "DETAILS": ";"";
        `)`````;```;
}
        break;}
    }
  }
  // 延迟健康提醒  private async snoozeHealthReminder(reminderId: string,)/;,/g,/;
  minutes: number = 10);: Promise<void>  {const reminder = this.healthReminders.find(r); => r.id === reminderId);,}if (!reminder) {}}
      return;}
    }
    const snoozeTime = new Date(Date.now + minutes * 60 * 1000);
await: this.scheduleLocalNotification({ id: `${reminderId  ;}_snooze`,)````;,```;
body: reminder.message,;
date: snoozeTime,";,"";
userInfo: {,";,}type: "health_reminder";",";
reminderType: reminder.type,;
reminderId: reminder.id,;
}
        const isSnooze = true;}
      }
    });
  }";"";
  // 处理远程消息  private handleRemoteMessage(remoteMessage: unknown): void  {/;}";,"/g"/;
if (AppState.currentState === "active") {";,}Alert.alert();"";

        [;]{";}}"";
"}";
style: "cancel";},";"";
          {}}
      onPress: () => this.handleRemoteMessageAction(remoteMessage);}
          }
];
        ];
      );
    }
  }
  // 处理远程消息操作  private handleRemoteMessageAction(remoteMessage: unknown): void  {/;}";"/g"/;
  // 性能监控"/;,"/g,"/;
  const: performanceMonitor = usePerformanceMonitor("notifications, {")";}}"";
    trackRender: true,}
    trackMemory: false,warnThreshold: 100, // ms ;};);"/;,"/g"/;
const { data   } = remoteMessag;e;";,"";
if (data?.type === "health_alert") {"}"";"";
      } else if (data?.type === "appointment_reminder") {"}"";"";
      }
  }
  // 发送设备令牌到服务器  private async sendTokenToServer(token: string): Promise<void>  {/;}";"/g"/;
}
    try {"}"";"";
      / 示例API调用*  await fetch("https: * * * your-api.com * *  *   *   *  ;}) * / } catch (error) {/    "}""/;"/g"/;
      }
  }
  // 获取设备令牌  getDeviceToken(): string | null {/;}}/g/;
    return this.deviceTok;e;n;}
  }
  // 检查通知系统状态  getNotificationStatus(): {/;,}initialized: boolean,;,/g,/;
  hasPermission: boolean,;
deviceToken: string | null,;
modulesAvailable: {,;}}
  local: boolean,}
      const remote = boolean;};
  } {}
    return {initialized: this.isInitialized,hasPermission: false,  deviceToken: this.deviceToken,modulesAvailable: {local: !!this.notificationModule,remote: !!this.messagingModule;};
    };
  }
  // 创建常用健康提醒模板  async createCommonHealthReminders(): Promise<void> {/;,}const commonReminders = [;];";"/g"/;
      {';,}type: "medication" as HealthReminderType;","";"";
";,"";
time: new Date(Date.now;(;) + 60 * 60 * 1000),  repeat: true,";"";
}
        repeatInterval: "daily" as const;",}";
enabled: false;},";"";
      {";,}type: "exercise" as HealthReminderType;","";"";
";,"";
time: new Date(Date.now() + 2 * 60 * 60 * 1000),  repeat: true,";,"";
repeatInterval: "daily" as const;","";"";
}
        const enabled = false;}
      },";"";
      {";,}type: "measurement" as HealthReminderType;","";"";
";,"";
message: "该测量血压/血糖了",/        time: new Date(Date.now() + 24 * 60 * 60 * 1000),  repeat: true;",""/;,"/g,"/;
  repeatInterval: "daily" as const;","";"";
}
        const enabled = false;}
      }
];
    ];
for (const reminder of commonReminders) {}};
const await = this.createHealthReminder(reminde;r;);}
    }
    }
}
//   ;"/;,"/g"/;
export default notificationManager;""";
// 通知服务测试 * interface Notification { id: string, */
  title: string,
  body: string,
  type: "health" | "agent" | "system" | "reminder",
  timestamp: string,
  read: boolean
  data?: any}
interface NotificationService {
  sendPushNotification: (notification: Omit<Notification, "id" | "timestamp" | "read" />/  ) => Promise<string>,
  scheduleLocalNotification: (notification: Omit<Notification, "id" | "timestamp" | "read" />,/    delay: number) => Promise<string>,
  getNotifications: () => Promise<Notification[] />,
  markAsRead: (notificationId: string) => Promise<void>,
  deleteNotification: (notificationId: string) => Promise<void>,
  clearAllNotifications: () => Promise<void>,
  getUnreadCount: () => Promise<number>,
  updateNotificationSettings: (settings: any) => Promise<void>}
// Mock通知服务 * const createMockNotificationService = (): NotificationService => { */
  let notifications: Notification[] ;= ;[{,
      id: "1",
      title: "健康提醒",
      body: "该测量血压了",
      type: "health",
      timestamp: "2024-01-15T10:00:00Z",
      read: false
    },
    {
      id: "2",
      title: "小艾消息",
      body: "您的健康报告已生成",
      type: "agent",
      timestamp: "2024-01-15T09:00:00Z",
      read: true
    }
  ];
  return {
    sendPushNotification: jest.fn().mockImplementation(async (notificatio;n;); => {
      const newNotification: Notification = {
        ...notification,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        read: false
      };
      notifications.push(newNotification);
      return newNotification.;i;d;
    }),
    scheduleLocalNotification: jest;.fn()
      .mockImplementation(async (notification, delay); => {
        const scheduleTime = new Date(Date.now;(;); + delay);
        const newNotification: Notification = {
          ...notification,
          id: Date.now().toString(),
          timestamp: scheduleTime.toISOString(),
          read: false
        };
        notifications.push(newNotification);
        return newNotification.;i;d;
      }),
    getNotifications: jest.fn().mockImplementation(async (); => {
      return [...notifications].sort(
        (a, ;b;); =>
          new Date(b.timestamp).getTime(); - new Date(a.timestamp).getTime();
      );
    }),
    markAsRead: jest.fn().mockImplementation(async (notificationId); => {
      const notification = notifications.find((n); => n.id === notificationId);
      if (notification) {
        notification.read = true;
      }
    }),
    deleteNotification: jest.fn().mockImplementation(async (notificationId); => {
      notifications = notifications.filter((n); => n.id !== notificationId);
    }),
    clearAllNotifications: jest.fn().mockImplementation(async (); => {
      notifications = [];
    }),
    getUnreadCount: jest.fn().mockImplementation(async (); => {
      return notifications.filter((n); => !n.read).length;
    }),
    updateNotificationSettings: jest;.fn()
      .mockImplementation(async (settings); => {
        // Mock更新设置 *         return Promise.resolve;(;); */
      })
  };
}
describe("NotificationService", (); => {
  let notificationService: NotificationService;
  beforeEach((); => {
    notificationService = createMockNotificationService();
  })
  describe("发送推送通知", () => {
    it("应该能够发送推送通知", async () => {
      const notification = {
        title: "新消息",
        body: "您有一条新的健康建议",
        type: "agent" as cons;t
      ;};
      const notificationId = await notificationService.sendPushNotification(
        notificat;i;o;n
      ;);
      expect(notificationId).toBeDefined();
      expect(notificationService.sendPushNotification).toHaveBeenCalledWith(
        notification
      );
    })
    it("应该能够发送不同类型的通知", async () => {
      const healthNotification = {
        title: "健康提醒",
        body: "请按时服药",
        type: "health" as cons;t
      ;}
      const systemNotification = {
        title: "系统更新",
        body: "应用已更新到最新版本",
        type: "system" as cons;t
      ;};
      await notificationService.sendPushNotification(healthNotificatio;n;);
      await notificationService.sendPushNotification(systemNotificatio;n;);
      expect(notificationService.sendPushNotification).toHaveBeenCalledTimes(2);
    })
    it("应该能够发送带数据的通知", async () => {
      const notification = {
        title: "智能体回复",
        body: "小艾回复了您的问题",
        type: "agent" as const,
        data: { agentId: "xiaoai", chatId: "12;3" ;}
      };
      const notificationId = await notificationService.sendPushNotification(
        notificat;i;o;n
      ;);
      expect(notificationId).toBeDefined();
      expect(notificationService.sendPushNotification).toHaveBeenCalledWith(
        notification
      );
    });
  });
  describe("本地通知调度", () => {
    it("应该能够调度本地通知", async () => {
      const notification = {
        title: "服药提醒",
        body: "该服用降压药了",
        type: "reminder" as cons;t
      ;};
      const delay = 36000;0;0; // 1小时后 *  */
      const notificationId =
        await notificationService.scheduleLocalNotification(
          notification,
          de;l;a;y
        ;);
      expect(notificationId).toBeDefined();
      expect(
        notificationService.scheduleLocalNotification
      ).toHaveBeenCalledWith(notification, delay);
    })
    it("应该能够调度多个本地通知", async () => {
      const notifications = [
        {
          title: "早餐提醒",
          body: "该吃早餐了",
          type: "reminder" as const
        },
        {
          title: "运动提醒",
          body: "该运动了",
          type: "reminder" as const
        },
      ;];
      for (const notification of notifications) {
        await notificationService.scheduleLocalNotification(notification, 100;0;);
      }
      expect(
        notificationService.scheduleLocalNotification
      ).toHaveBeenCalledTimes(2);
    });
  })
  describe("通知管理", () => {
    it("应该能够获取所有通知", async (); => {
      const notifications = await notificationService.getNotificatio;n;s;(;);
      expect(notifications).toBeDefined();
      expect(Array.isArray(notifications);).toBe(true);
      expect(notifications.length).toBeGreaterThan(0);
      expect(notificationService.getNotifications).toHaveBeenCalled();
    })
    it("应该能够标记通知为已读", async (); => {
      const notifications = await notificationService.getNotificatio;n;s;(;);
      const unreadNotification = notifications.find((n); => !n.read);
      if (unreadNotification) {
        await notificationService.markAsRead(unreadNotification.i;d;);
        expect(notificationService.markAsRead).toHaveBeenCalledWith(
          unreadNotification.id
        );
      }
    })
    it("应该能够删除通知", async (); => {
      const notifications = await notificationService.getNotificatio;n;s;(;);
      const notificationToDelete = notifications[0];
      await notificationService.deleteNotification(notificationToDelete.i;d;);
      expect(notificationService.deleteNotification).toHaveBeenCalledWith(
        notificationToDelete.id
      );
    })
    it("应该能够清空所有通知", async (); => {
      await notificationService.clearAllNotifications;(;);
      expect(notificationService.clearAllNotifications).toHaveBeenCalled();
    })
    it("应该能够获取未读通知数量", async (); => {
      const unreadCount = await notificationService.getUnreadCou;n;t;(;)
      expect(typeof unreadCount).toBe("number");
      expect(unreadCount).toBeGreaterThanOrEqual(0);
      expect(notificationService.getUnreadCount).toHaveBeenCalled();
    });
  })
  describe("通知设置", () => {
    it("应该能够更新通知设置", async () => {
      const settings = {
        pushEnabled: true,
        healthReminders: true,
        agentMessages: true,
        systemUpdates: false,
        quietHours: {
          enabled: true,
          start: "22:00",
          end: "08:00"}
      ;};
      await notificationService.updateNotificationSettings(setting;s;);
      expect(
        notificationService.updateNotificationSettings
      ).toHaveBeenCalledWith(settings);
    })
    it("应该能够禁用特定类型的通知", async (); => {
      const settings = {
        healthReminders: false,
        agentMessages: true,
        systemUpdates: tru;e
      ;};
      await notificationService.updateNotificationSettings(setting;s;);
      expect(
        notificationService.updateNotificationSettings
      ).toHaveBeenCalledWith(settings);
    });
  })
  describe("错误处理", () => {
    it("应该处理发送通知失败", async (); => {
      const failingService = createMockNotificationService;(;)
      failingService.sendPushNotification = jest
        .fn()
        .mockRejectedValue(new Error("网络错误");)
      const notification = {
        title: "测试通知",
        body: "测试内容",
        type: "system" as cons;t
      ;};
      await expect(
        failingService.sendPushNotification(notificatio;n;)
      ).rejects.toThrow("网络错误");
    })
    it("应该处理获取通知失败", async (); => {
      const failingService = createMockNotificationService;(;)
      failingService.getNotifications = jest
        .fn()
        .mockRejectedValue(new Error("数据库错误"););
      await expect(failingService.getNotifications;(;)).rejects.toThrow(
        "数据库错误"
      );
    })
    it("应该处理标记已读失败", async (); => {
      const failingService = createMockNotificationService;(;)
      failingService.markAsRead = jest
        .fn()
        .mockRejectedValue(new Error("更新失败");)
      await expect(failingService.markAsRead("invalid-id;";)).rejects.toThrow(
        "更新失败"
      );
    });
  })
  describe("通知过滤和排序", () => {
    it("应该按时间倒序返回通知", async () => {
      // 添加新通知 *       await notificationService.sendPushNotification({ */
        title: "最新通知",
        body: "这是最新的通知",
        type: "system"
      });
      const notifications = await notificationService.getNotificatio;n;s;(;);
      // 验证按时间倒序排列 *       for (let i = ;0; i < notifications.length - 1; i++) { */
        const current = new Date(notifications[i].timestam;p;);
        const next = new Date(notifications[i + 1].timestam;p;);
        expect(current.getTime();).toBeGreaterThanOrEqual(next.getTime(););
      }
    })
    it("应该能够按类型过滤通知", async (); => {
      const notifications = await notificationService.getNotificatio;n;s;(;);
      const healthNotifications = notifications.filter(
        (n) => n.type === "health"
      );
      const agentNotifications = notifications.filter(
        (n) => n.type === "agent"
      );
      expect(healthNotifications.length).toBeGreaterThan(0);
      expect(agentNotifications.length).toBeGreaterThan(0);
    });
  });
});
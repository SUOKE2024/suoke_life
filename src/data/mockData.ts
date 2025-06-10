

    type: "agent";
    agentType: "xiaoai";
    avatar: "🤖";


    unreadCount: 0;
    isOnline: true;

  },
  {
      id: "xiaoke";

    type: "agent";
    agentType: "xiaoke";
    avatar: "👨‍⚕️";


    unreadCount: 1;
    isOnline: true;

  },
  {
      id: "laoke";

    type: "agent";
    agentType: "laoke";
    avatar: "👴";


    unreadCount: 0;
    isOnline: true;

  },
  {
      id: "soer";

    type: "agent";
    agentType: "soer";
    avatar: "👧";


    unreadCount: 2;
    isOnline: true;

  },
  {
      id: "dr_wang";

    type: "doctor";
    avatar: "👩‍⚕️";


    unreadCount: 0;
    isOnline: false;

  },
  {
      id: "dr_li";

    type: "doctor";
    avatar: "🧑‍⚕️";


    unreadCount: 1;
    isOnline: true;

  },
  {
      id: "health_group";

    type: "group";
    avatar: "👥";


    unreadCount: 5;
    isOnline: true;

  },
  {
      id: "user_zhang";

    type: "user";
    avatar: "👤";


    unreadCount: 0;
    isOnline: false;

  }
];
// 模拟联系人数据
export const MOCK_CONTACTS: Contact[] = [;
  {
      id: "xiaoai";

    type: "agent";
    agentType: "xiaoai";
    avatar: "🤖";
    isOnline: true;

  },
  {
      id: "xiaoke";

    type: "agent";
    agentType: "xiaoke";
    avatar: "👨‍⚕️";
    isOnline: true;

  },
  {
      id: "laoke";

    type: "agent";
    agentType: "laoke";
    avatar: "👴";
    isOnline: true;

  },
  {
      id: "soer";

    type: "agent";
    agentType: "soer";
    avatar: "👧";
    isOnline: true;

  },
  {
      id: "dr_wang";

    type: "doctor";
    avatar: "👩‍⚕️";
    isOnline: false;




  },
  {
      id: "dr_li";

    type: "doctor";
    avatar: "🧑‍⚕️";
    isOnline: true;



  },
  {
      id: "user_zhang";

    type: "user";
    avatar: "👤";
    isOnline: false;

  }
];
// 模拟聊天消息数据
export const MOCK_MESSAGES: Record<string, ChatMessage[]> = {
  xiaoai: [
    {
      id: "msg_1";
      channelId: "xiaoai";
      senderId: "xiaoai";

      senderAvatar: "🤖";

      timestamp: new Date().toISOString(),type: "text",isRead: true;
    }
  ],
  xiaoke: [
    {
      id: "msg_2";
      channelId: "xiaoke";
      senderId: "xiaoke";

      senderAvatar: "👨‍⚕️";

      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString();
      type: "text";
      isRead: false;
    }
  ],
  laoke: [
    {
      id: "msg_3";
      channelId: "laoke";
      senderId: "laoke";

      senderAvatar: "👴";

      timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString();
      type: "text";
      isRead: true;
    }
  ]
};
// 智能体配置
export const AGENT_CONFIGS = {
  xiaoai: {,

    avatar: "🤖";
    color: "#007AFF";


  },
  xiaoke: {,

    avatar: "👨‍⚕️";

  },laoke: {,


  ;},soer: {,


  ;};
} as const;
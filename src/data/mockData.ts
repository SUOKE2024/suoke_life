    type: "agent,";
agentType: "xiaoai,";
avatar: "🤖,";
unreadCount: 0,
const isOnline = true;
  },";
  {"id: "xiaoke,
;
type: "agent,";
agentType: "xiaoke,";
avatar: "👨‍⚕️,";
unreadCount: 1,
const isOnline = true;
}
}
  },";
  {"id: "laoke,
;
type: "agent,";
agentType: "laoke,";
avatar: "👴,";
unreadCount: 0,
const isOnline = true;
}
}
  },";
  {"id: "soer,
;
type: "agent,";
agentType: "soer,";
avatar: "👧,";
unreadCount: 2,
const isOnline = true;
}
}
  },";
  {"id: "dr_wang,
;
type: "doctor,";
avatar: "👩‍⚕️,";
unreadCount: 0,
const isOnline = false;
}
}
  },";
  {"id: "dr_li,
;
type: "doctor,";
avatar: "🧑‍⚕️,";
unreadCount: 1,
const isOnline = true;
}
}
  },";
  {"id: "health_group,
;
type: "group,";
avatar: "👥,";
unreadCount: 5,
const isOnline = true;
}
}
  },";
  {"id: "user_zhang,
;
type: "user,";
avatar: "👤,";
unreadCount: 0,
const isOnline = false;
}
}
  }
];
// 模拟联系人数据/,/g/;
export const MOCK_CONTACTS: Contact[] = [;];";
  {"id: "xiaoai,
;
type: "agent,";
agentType: "xiaoai,";
avatar: "🤖,";
const isOnline = true;
}
}
  },";
  {"id: "xiaoke,
;
type: "agent,";
agentType: "xiaoke,";
avatar: "👨‍⚕️,";
const isOnline = true;
}
}
  },";
  {"id: "laoke,
;
type: "agent,";
agentType: "laoke,";
avatar: "👴,";
const isOnline = true;
}
}
  },";
  {"id: "soer,
;
type: "agent,";
agentType: "soer,";
avatar: "👧,";
const isOnline = true;
}
}
  },";
  {"id: "dr_wang,
;
type: "doctor,";
avatar: "👩‍⚕️,";
const isOnline = false;
}
}
  },";
  {"id: "dr_li,
;
type: "doctor,";
avatar: "🧑‍⚕️,";
const isOnline = true;
}
}
  },";
  {"id: "user_zhang,
;
type: "user,";
avatar: "👤,";
const isOnline = false;
}
}
  }
];
];
// 模拟聊天消息数据/,/g/;
export const MOCK_MESSAGES: Record<string, ChatMessage[]> = {const xiaoai = [;]";}    {"id: "msg_1,";
channelId: "xiaoai,";
senderId: "xiaoai,
;
senderAvatar: "🤖,
";
}
      timestamp: new Date().toISOString(),type: "text",isRead: true;"
    }
];
  ],
const xiaoke = [;]";
    {"id: "msg_2,";
channelId: "xiaoke,";
senderId: "xiaoke,
;
senderAvatar: "👨‍⚕️,
;
timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
type: "text,
}
      const isRead = false}
    }
];
  ],
const laoke = [;]";
    {"id: "msg_3,";
channelId: "laoke,";
senderId: "laoke,
;
senderAvatar: "👴,
;
timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
type: "text,
}
      const isRead = true}
    }
];
  ];
};
// 智能体配置/,/g/;
export const AGENT_CONFIGS = {xiaoai: {,";};
avatar: "🤖,";
const color = "#007AFF;"";
}
}
  }
xiaoke: {,";};
const avatar = "👨‍⚕️;"";
}
}
  },laoke: {,}
}
  ;},soer: {,}
}
  ;};";
} as const;""";

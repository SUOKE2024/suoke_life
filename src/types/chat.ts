';'';
';'';
// chat.ts   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述 @author 索克生活开发团队   @version 1.0.0;'/;,'/g'/;
export type AgentType = "xiaoai" | "xiaoke" | "laoke" | "so;e;";";,"";
r;";,"";
export type ChannelType = "agent" | "user" | "doctor" | "gro;u;";";,"";
p;
export interface ChatChannel {id: string}name: string,;
type: ChannelType,;
avatar: string,;
lastMessage: string,;
lastMessageTime: string,unreadCount: number,isOnline: boolean;
}
}
  agentType?: AgentType;}
  specialization?: string}
export interface ChatMessage {id: string}channelId: string,;
senderId: string,;
senderName: string,;
senderAvatar: string,";,"";
content: string,";,"";
timestamp: string,type: "text" | "image" | "file" | "system",isRead: boolean;";"";
}
}
  reactions?: MessageReaction[];}
  }
export interface MessageReaction {};
const emoji = string;}
  userId: string,;
const userName = string;}
export interface Contact {id: string}const name = string;type: ChannelType;
agentType?: AgentType;
avatar: string,;
const isOnline = boolean;
lastSeen?: string;
specialization?: string;
}
}
  department?: string;}
  title?: string}
export interface ChatState {}
};
};
channels: ChatChannel[],messages: Record<string, ChatMessage[]>;
activeChannelId: string | null,;
searchQuery: string,;
isLoading: boolean,;
const error = string | null;}
export interface ChatActions {}
}
}
  setChannels: (channels: ChatChannel[]) => void,;
addMessage: (message: ChatMessage) => void,;
setActiveChannel: (channelId: string | null) => void,;
setSearchQuery: (query: string) => void,;
markAsRead: (channelId: string) => void,;
updateChannelLastMessage: (channelId: string,)";,"";
message: string,timestamp: string) => void;};""";
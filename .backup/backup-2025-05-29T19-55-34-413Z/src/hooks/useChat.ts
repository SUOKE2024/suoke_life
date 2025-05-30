import { ChatChannel, ChatMessage, Contact, AgentType } from "../types/chat";
import {
import { useState, useCallback, useMemo } from "react";

  MOCK_CHAT_CHANNELS,
  MOCK_CONTACTS,
  MOCK_MESSAGES,
} from "../data/mockData";


export const useChat = () => {
  const [channels, setChannels] = useState<ChatChannel[]>(MOCK_CHAT_CHANNELS);
  const [messages, setMessages] =
    useState<Record<string, ChatMessage[]>>(MOCK_MESSAGES);
  const [activeChannelId, setActiveChannelId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 过滤聊天频道
  const filteredChannels = useMemo(() => {
    if (!searchQuery.trim()) {
      return channels;
    }

    return channels.filter(
      (channel) =>
        channel.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        channel.lastMessage.toLowerCase().includes(searchQuery.toLowerCase()) ||
        channel.specialization
          ?.toLowerCase()
          .includes(searchQuery.toLowerCase())
    );
  }, [channels, searchQuery]);

  // 获取未读消息总数
  const totalUnreadCount = useMemo(() => {
    return channels.reduce((total, channel) => total + channel.unreadCount, 0);
  }, [channels]);

  // 获取活动频道
  const activeChannel = useMemo(() => {
    return channels.find((channel) => channel.id === activeChannelId) || null;
  }, [channels, activeChannelId]);

  // 获取频道消息
  const getChannelMessages = useCallback(
    (channelId: string) => {
      return messages[channelId] || [];
    },
    [messages]
  );

  // 添加消息
  const addMessage = useCallback((message: ChatMessage) => {
    setMessages((prev) => ({
      ...prev,
      [message.channelId]: [...(prev[message.channelId] || []), message],
    }));

    // 更新频道最后消息
    setChannels((prev) =>
      prev.map((channel) =>
        channel.id === message.channelId
          ? {
              ...channel,
              lastMessage: message.content,
              lastMessageTime: "刚刚",
              unreadCount:
                message.senderId !== "current_user"
                  ? channel.unreadCount + 1
                  : channel.unreadCount,
            }
          : channel
      )
    );
  }, []);

  // 标记为已读
  const markAsRead = useCallback((channelId: string) => {
    setChannels((prev) =>
      prev.map((channel) =>
        channel.id === channelId ? { ...channel, unreadCount: 0 } : channel
      )
    );

    setMessages((prev) => ({
      ...prev,
      [channelId]: (prev[channelId] || []).map((message) => ({
        ...message,
        isRead: true,
      })),
    }));
  }, []);

  // 更新频道最后消息
  const updateChannelLastMessage = useCallback(
    (channelId: string, message: string, timestamp: string) => {
      setChannels((prev) =>
        prev.map((channel) =>
          channel.id === channelId
            ? { ...channel, lastMessage: message, lastMessageTime: timestamp }
            : channel
        )
      );
    },
    []
  );

  // 开始与智能体聊天
  const startAgentChat = useCallback(
    async (agentType: AgentType) => {
      setIsLoading(true);
      setError(null);

      try {
        const agentChannel = channels.find(
          (channel) => channel.agentType === agentType
        );
        if (agentChannel) {
          setActiveChannelId(agentChannel.id);
          markAsRead(agentChannel.id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "启动聊天失败");
      } finally {
        setIsLoading(false);
      }
    },
    [channels, markAsRead]
  );

  // 发送消息
  const sendMessage = useCallback(
    async (channelId: string, content: string) => {
      setIsLoading(true);
      setError(null);

      try {
        const newMessage: ChatMessage = {
          id: `msg_${Date.now()}`,
          channelId,
          senderId: "current_user",
          senderName: "我",
          senderAvatar: "👤",
          content,
          timestamp: new Date().toISOString(),
          type: "text",
          isRead: true,
        };

        addMessage(newMessage);

        // 模拟智能体回复（仅对智能体频道）
        const channel = channels.find((c) => c.id === channelId);
        if (channel?.type === "agent" && channel.agentType) {
          setTimeout(() => {
            const agentReply: ChatMessage = {
              id: `msg_${Date.now() + 1}`,
              channelId,
              senderId: channel.agentType!,
              senderName: channel.name,
              senderAvatar: channel.avatar,
              content: `收到您的消息："${content}"，我正在为您分析...`,
              timestamp: new Date().toISOString(),
              type: "text",
              isRead: false,
            };
            addMessage(agentReply);
          }, 1000);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "发送消息失败");
      } finally {
        setIsLoading(false);
      }
    },
    [channels, addMessage]
  );

  return {
    // 状态
    channels: filteredChannels,
    messages,
    activeChannelId,
    activeChannel,
    searchQuery,
    isLoading,
    error,
    totalUnreadCount,

    // 操作
    setChannels,
    setActiveChannelId,
    setSearchQuery,
    addMessage,
    markAsRead,
    updateChannelLastMessage,
    startAgentChat,
    sendMessage,
    getChannelMessages,
  };
};

export const useContacts = () => {
  const [contacts] = useState<Contact[]>(MOCK_CONTACTS);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredContacts = useMemo(() => {
    if (!searchQuery.trim()) {
      return contacts;
    }

    return contacts.filter(
      (contact) =>
        contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contact.specialization
          ?.toLowerCase()
          .includes(searchQuery.toLowerCase()) ||
        contact.department?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [contacts, searchQuery]);

  const groupedContacts = useMemo(() => {
    const groups = {
      agents: filteredContacts.filter((c) => c.type === "agent"),
      doctors: filteredContacts.filter((c) => c.type === "doctor"),
      users: filteredContacts.filter((c) => c.type === "user"),
    };
    return groups;
  }, [filteredContacts]);

  return {
    contacts: filteredContacts,
    groupedContacts,
    searchQuery,
    setSearchQuery,
  };
};

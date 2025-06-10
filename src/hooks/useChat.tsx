
react";";
MOCK_CHAT_CHANNELS,";,"";
MOCK_CONTACTS,";"";
  { MOCK_MESSAGES } from ";../data/mockData";/    export const useChat = () =;"/;"/g"/;
> ;{";}  // 性能监控"/;,"/g,"/;
  const: performanceMonitor = usePerformanceMonitor("useChat', {"')';}}'';
    trackRender: true,}
    trackMemory: true,warnThreshold: 50, // ms ;};);/;,/g/;
const [channels, setChannels] = useState<ChatChannel[]  />(MOCK_CHAT_CHANNEL;S;);/  const [messages, setMessages] = useState<Record<string, ChatMessage[]  />>(MOCK_MESSAGE;S;);/      const [activeChannelId, setActiveChannelId] = useState<string | null>(nul;l;);/;,/g/;
const [searchQuery, setSearchQuery] = useState<string>(;);
const [isLoading, setIsLoading] = useState<boolean>(fals;e;);
const [error, setError] = useState<string | null>(nul;l;);
const filteredChannels = useMemo() => {;,}if (!searchQuery.trim();) {}}
      return channe;l;s;}
    }
    return channels.filter(;);
      (channe;l;); => {}
        channel.name.toLowerCase().includes(searchQuery.toLowerCase();) ||;
channel.lastMessage.toLowerCase().includes(searchQuery.toLowerCase();) ||;
channel.specialization;
          ?.toLowerCase();
          .includes(searchQuery.toLowerCase(););
    );
  }, [channels, searchQuery]);
const totalUnreadCount = useMemo() => {;}}
    return channels.reduce(total, channe;l;); => total + channel.unreadCount, 0);}
  }, [channels]);
const activeChannel = useMemo() => {;}}
    return channels.find(channe;l;); => channel.id === activeChannelId) || null;}
  }, [channels, activeChannelId]);
const getChannelMessages = useCallback(;);
    (channelId: strin;g;); => {}
      return messages[channelId] || ;[;];
    }
    [messages];
  );
const addMessage = useCallback(message: ChatMessage;); => {}
    setMessages(prev); => ({));}      ...prev,);
}
      [message.channelId]: [...(prev[message.channelId] || []), message]}
    }));
setChannels(prev) => {}
      prev.map(channel) => {}
        channel.id === message.channelId;
          ? {...channel}lastMessage: message.content,';'';
';,'';
unreadCount: message.senderId !== "current_user";? channel.unreadCount + 1;";"";
}
                  : channel.unreadCount;}
            }
          : channel;
      );
    );
  }, []);
const markAsRead = useCallback(channelId: string;); => {}
    setChannels(prev); => {}
      prev.map(channel); => {}
        channel.id === channelId ? { ...channel, unreadCount: 0;} : channel;
      );
    );
setMessages(prev); => ({));}      ...prev,);
      [channelId]: (prev[channelId] || []).map(message); => ({);}        ...message,);
}
        const isRead = true;)}
      }));
    }));
  }, []);
const updateChannelLastMessage = useCallback(;);
    (channelId: string, message: string, timestamp: strin;g;); => {}
      setChannels(prev); => {}
        prev.map(channel); => {}
          channel.id === channelId;
            ? { ...channel, lastMessage: message, lastMessageTime: timestamp;}
            : channel;
        );
      );
    }
    [];
  );
const startAgentChat = useCallback(;);
async (agentType: AgentTyp;e;); => {}
      setIsLoading(true);
setError(null);
try {const agentChannel = channels.find(;);}          (channe;l;); => channel.agentType === agentType;
        );
if (agentChannel) {setActiveChannelId(agentChannel.id);}}
          markAsRead(agentChannel.id);}
        }
      } catch (err) {}}
        setIsLoading(false);}
      }
    }
    [channels, markAsRead];
  );
const sendMessage = useCallback(;);
async (channelId: string, content: strin;g;); => {}
      setIsLoading(true);
setError(null);
try {}";,"";
const newMessage: ChatMessage = { id: `msg_${Date.now()  ;}`,channelId,``"`;,```;
senderId: "current_user";","";"";
";,"";
const senderAvatar = "👤";";,"";
content,";,"";
timestamp: new Date().toISOString(),";,"";
type: "text";",";
const isRead = true;
        };
addMessage(newMessage);";,"";
const channel = channels.find(c) => c.id === channelId);";,"";
if (channel?.type === "agent" && channel.agentType) {setTimeout() => {;"}";
const agentReply: ChatMessage = { id: `msg_${Date.now(); + 1  }`,channelId,````;,```;
senderId: channel.agentType!,;
senderName: channel.name,;
senderAvatar: channel.avatar,;
";,"";
timestamp: new Date().toISOString(),";,"";
type: "text";",";
const isRead = false;
            };
addMessage(agentReply);
          }, 1000);
        }
      } catch (err) {}}
        setIsLoading(false);}
      }
    }
    [channels, addMessage];
  );
return {}
    channels: filteredChannels,messages,activeChannelId,activeChannel,searchQuery,isLoading,error,totalUnreadCount, setChannels,setActiveChannelId,setSearchQuery,addMessage,markAsRead,updateChannelLastMessage,startAgentChat,sendMessage,getChannelMessages;};
};
export const useContacts = () =;
> ;{const [contacts] = useState<Contact[]  />(MOCK_CONTACT;S;)/      const [searchQuery, setSearchQuery] = useState<string>(;);}/;,/g/;
const filteredContacts = useMemo(); => {}
    if (!searchQuery.trim();) {}}
      return contac;t;s;}
    }
    return contacts.filter(;);
      (contac;t;); => {}
        contact.name.toLowerCase().includes(searchQuery.toLowerCase();) ||;
contact.specialization;
          ?.toLowerCase();
          .includes(searchQuery.toLowerCase();) ||;
contact.department?.toLowerCase().includes(searchQuery.toLowerCase(););
    );
  }, [contacts, searchQuery]);";,"";
const groupedContacts = useMemo(); => {}";,"";
groups: {agents: filteredContacts.filter(c) => c.type === "agent");","";,}doctors: filteredContacts.filter(c) => c.type === "doctor");","";"";
}
      users: filteredContacts.filter(c) => c.type === "user")"}"";"";
    ;};
return grou;p;s;
  }, [filteredContacts]);
return {contacts: filteredContacts,groupedContacts,searchQuery,setSearchQuer;y;};";"";
};""";
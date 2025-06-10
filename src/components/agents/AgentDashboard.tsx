
import AgentMonitor from "./AgentMonitor";""/;,"/g"/;
import AgentAnalytics from "./AgentAnalytics";""/;,"/g"/;
import React, { useState, useEffect } from "react";";
View,;
Text,;
StyleSheet,;
ScrollView,;
TouchableOpacity,;
Dimensions,;
RefreshControl,";,"";
Alert;";"";
} from "react-native";";
interface AgentDashboardProps {";}}"";
}
  initialTab?: "monitor" | "analytics" | "chat";"}"";"";
}
interface QuickAction {id: string}title: string,;
description: string,;
agentType: AgentType,;
action: () => void,;
icon: string,;
}
}
  const color = string;}";"";
}";,"";
const { width } = Dimensions.get("window");";,"";
const  AgentDashboard: React.FC<AgentDashboardProps> = ({))";}}"";
  initialTab = "monitor")"}"";"";
;}) => {const [activeTab, setActiveTab] = useState(initialTab);";,}const [refreshing, setRefreshing] = useState(false);";,"";
const [systemStatus, setSystemStatus] = useState<"healthy" | "warning" | "error">("healthy");";"";
}
}
  };
const  quickActions: QuickAction[] = [;]";"";
    {";,}id: "xiaoai-chat";","";"";
";,"";
agentType: AgentType.XIAOAI,";,"";
action: () => handleQuickAction("chat", AgentType.XIAOAI),";,"";
icon: "💬";","";"";
}
      const color = "#007AFF"}"";"";
    ;},";"";
    {";,}id: "xiaoke-service";","";"";
";,"";
agentType: AgentType.XIAOKE,";,"";
action: () => handleQuickAction("service", AgentType.XIAOKE),";,"";
icon: "🏥";","";"";
}
      const color = "#34C759"}"";"";
    ;},";"";
    {";,}id: "laoke-knowledge";","";"";
";,"";
agentType: AgentType.LAOKE,";,"";
action: () => handleQuickAction("knowledge", AgentType.LAOKE),";,"";
icon: "📚";","";"";
}
      const color = "#FF9500"}"";"";
    ;},";"";
    {";,}id: "soer-lifestyle";","";"";
";,"";
agentType: AgentType.SOER,";,"";
action: () => handleQuickAction("lifestyle", AgentType.SOER),";,"";
icon: "🌱";","";"";
}
      const color = "#FF3B30"}"";"";
    ;}
];
  ];
handleQuickAction: useCallback((actionType: string, agentType: AgentType) => {Alert.alert(;);}        {";}}"";
"}";
style: "cancel" ;},{";,}onPress: () => {// 这里可以导航到具体的功能页面;/;}}"/g"/;
}
          }
        }
      ];
    );
  };
const checkSystemHealth = async () => {try {const healthCheck = await agentApiService.healthCheck();";,}if (healthCheck.success) {";}}"";
        setSystemStatus("healthy");"}"";"";
      } else {";}}"";
        setSystemStatus("warning");"}"";"";
      }";"";
    } catch (error) {";}}"";
      setSystemStatus("error");"}"";"";
    }
  };
const onRefresh = async () => {setRefreshing(true);,}const await = checkSystemHealth();
}
    setRefreshing(false);}
  };
useEffect() => {checkSystemHealth();,}interval: setInterval(checkSystemHealth, 60000); // 每分钟检查一次/;/g/;
}
    return () => clearInterval(interval);}
  }, [])  // 检查是否需要添加依赖项;"/;,"/g,"/;
  const: renderSystemStatus = useCallback(() => {const statusConfig = {healthy: {,";,}color: "#34C759";","";"";
";,"";
color: "#FF9500";","";"";
";,"";
const color = "#FF3B30";";"";
}
}
    };
const config = statusConfig[systemStatus];
return (;);
      <View style={[styles.statusCard, { borderLeftColor: config.color ;}}]}>;
        <View style={styles.statusHeader}>;
          <Text style={styles.statusIcon}>{config.icon}</Text>;/;/g/;
          <Text style={[styles.statusText, { color: config.color ;}}]}>;
            {config.text};
          </Text>;/;/g/;
        </View>;/;/g/;
        <Text style={styles.statusTime}>;

        </Text>;/;/g/;
      </View>;/;/g/;
    );
  };
const  renderQuickActions = () => (<View style={styles.quickActionsContainer}>);
      <Text style={styles.sectionTitle}>快速操作</Text>)/;/g/;
      <View style={styles.actionsGrid}>);
        {quickActions.map(action) => (;);}}
          <TouchableOpacity;}  />/;,/g/;
key={action.id};
style={[styles.actionCard, { borderLeftColor: action.color ;}}]};
onPress={action.action};
activeOpacity={0.7};
          >;
            <View style={styles.actionHeader}>;
              <Text style={styles.actionIcon}>{action.icon}</Text>;/;/g/;
              <Text style={styles.actionTitle}>{action.title}</Text>;/;/g/;
            </View>;/;/g/;
            <Text style={styles.actionDescription}>{action.description}</Text>;/;/g/;
          </TouchableOpacity>;/;/g/;
        ))};
      </View>;/;/g/;
    </View>;/;/g/;
  );
const  renderTabBar = () => (<View style={styles.tabBar}>)";"";
      <TouchableOpacity;)"  />/;,"/g"/;
style={[styles.tab, activeTab === "monitor" && styles.activeTab]}")";
onPress={() => setActiveTab("monitor")}";"";
      >;
        <Text style={ />/;}[;]";,"/g"/;
styles.tabText,";"";
}
          activeTab === "monitor" && styles.activeTabText;"}"";"";
];
        ]}}>;

        </Text>/;/g/;
      </TouchableOpacity>"/;"/g"/;
      <TouchableOpacity;"  />/;,"/g"/;
style={[styles.tab, activeTab === "analytics" && styles.activeTab]}";,"";
onPress={() => setActiveTab("analytics")}";"";
      >;
        <Text style={ />/;}[;]";,"/g"/;
styles.tabText,";"";
}
          activeTab === "analytics" && styles.activeTabText;"}"";"";
];
        ]}}>;

        </Text>;/;/g/;
      </TouchableOpacity>;"/;"/g"/;
      <TouchableOpacity;"  />/;,"/g"/;
style={[styles.tab, activeTab === "chat" && styles.activeTab]};";,"";
onPress={() => setActiveTab("chat")};";"";
      >;";"";
        <Text style={ />/;}[;];";"/g"/;
}
          styles.tabText,activeTab === "chat" && styles.activeTabText;"}"";"";
];
        ]}}>;

        </Text>;/;/g/;
      </TouchableOpacity>;/;/g/;
    </View>;"/;"/g"/;
  );";,"";
const renderTabContent = useCallback(() => {switch (activeTab) {case "monitor": return <AgentMonitor  />;"/;,}case "analytics": ";,"/g"/;
return <AgentAnalytics  />;"/;,"/g"/;
case "chat": ";"";
}
        return (;)}
          <View style={styles.chatContainer}>;
            <Text style={styles.chatTitle}>智能体对话</Text>;/;/g/;
            <Text style={styles.chatDescription}>;

            </Text>;/;/g/;
            {renderQuickActions()};
          </View>;/;/g/;
        );
default: ;
return null;
    }
  };
return (<View style={styles.container}>;)      <ScrollView;  />/;,/g/;
style={styles.scrollView};
refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />;/;/g/;
        };
      >;
        <View style={styles.header}>;
          <Text style={styles.title}>索克生活智能体中心</Text>;)/;/g/;
          <Text style={styles.subtitle}>四智能体协同健康管理平台</Text>;)/;/g/;
        </View>;)/;/g/;
        {renderSystemStatus()};
        {renderTabBar()};
        {renderTabContent()};
      </ScrollView>;/;/g/;
    </View>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = "#f5f5f5"}"";"";
  ;}
scrollView: {,;}}
  const flex = 1;}
  },";,"";
header: {,";,}backgroundColor: "#fff";",";
padding: 20,";,"";
borderBottomWidth: 1,";"";
}
    const borderBottomColor = "#e0e0e0"}"";"";
  ;}
title: {,";,}fontSize: 28,";,"";
fontWeight: "bold";",";
color: "#333";","";"";
}
    const marginBottom = 4;}
  }
subtitle: {,";,}fontSize: 16,";"";
}
    const color = "#666"}"";"";
  ;},";,"";
statusCard: {,";,}backgroundColor: "#fff";",";
margin: 16,;
padding: 16,;
borderRadius: 12,";,"";
borderLeftWidth: 4,";"";
}
    shadowColor: "#000";",}";
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  },";,"";
statusHeader: {,";,}flexDirection: "row";",";
alignItems: "center";","";"";
}
    const marginBottom = 8;}
  }
statusIcon: {fontSize: 20,;
}
    const marginRight = 8;}
  }
statusText: {,";,}fontSize: 18,";"";
}
    const fontWeight = "600"}"";"";
  ;}
statusTime: {,";,}fontSize: 14,";"";
}
    const color = "#666"}"";"";
  ;},";,"";
tabBar: {,";,}flexDirection: "row";",";
backgroundColor: "#fff";",";
marginHorizontal: 16,;
marginBottom: 16,;
borderRadius: 12,";,"";
padding: 4,";"";
}
    shadowColor: "#000";","}";
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  }
tab: {flex: 1,";,"";
paddingVertical: 12,";,"";
alignItems: "center";","";"";
}
    const borderRadius = 8;}
  },";,"";
activeTab: {,";}}"";
  const backgroundColor = "#007AFF"}"";"";
  ;}
tabText: {,";,}fontSize: 16,";,"";
fontWeight: "600";","";"";
}
    const color = "#666"}"";"";
  ;},";,"";
activeTabText: {,";}}"";
  const color = "#fff"}"";"";
  ;},";,"";
quickActionsContainer: {,";,}backgroundColor: "#fff";",";
margin: 16,;
padding: 16,";,"";
borderRadius: 12,";"";
}
    shadowColor: "#000";","}";
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  }
sectionTitle: {,";,}fontSize: 20,";,"";
fontWeight: "bold";",";
color: "#333";","";"";
}
    const marginBottom = 16;}
  },";,"";
actionsGrid: {,";,}flexDirection: "row";",";
flexWrap: "wrap";","";"";
}
    const justifyContent = "space-between"}"";"";
  ;},";,"";
actionCard: {,";,}width: "48%";",";
backgroundColor: "#f8f9fa";",";
padding: 16,;
borderRadius: 12,;
marginBottom: 12,;
}
    const borderLeftWidth = 4;}
  },";,"";
actionHeader: {,";,}flexDirection: "row";",";
alignItems: "center";","";"";
}
    const marginBottom = 8;}
  }
actionIcon: {fontSize: 24,;
}
    const marginRight = 8;}
  }
actionTitle: {,";,}fontSize: 16,";,"";
fontWeight: "600";",";
color: "#333";","";"";
}
    const flex = 1;}
  }
actionDescription: {,";,}fontSize: 14,";,"";
color: "#666";","";"";
}
    const lineHeight = 20;}
  },";,"";
chatContainer: {,";,}backgroundColor: "#fff";",";
margin: 16,;
padding: 20,";,"";
borderRadius: 12,";"";
}
    shadowColor: "#000";","}";
shadowOffset: { width: 0, height: 2 ;},";,"";
shadowOpacity: 0.1,shadowRadius: 4,elevation: 3;";"";
  },chatTitle: {fontSize: 24,fontWeight: "bold",color: "#333",marginBottom: 8;")}"";"";
  },chatDescription: {fontSize: 16,color: "#666",lineHeight: 24,marginBottom: 20;")}"";"";
  };);
});";,"";
export default AgentDashboard;""";
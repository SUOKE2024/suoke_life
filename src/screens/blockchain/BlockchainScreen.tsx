import React, { useState } from "react";";
import {import { BlockchainStatusCard, BlockchainNetworkStats } from "../../components/blockchain/BlockchainStatusCard";""/;,"/g"/;
import { HealthDataManager } from "../../components/blockchain/HealthDataManager";""/;,"/g"/;
import { ZKProofManager } from "../../components/blockchain/ZKProofManager";""/;,"/g"/;
View,;
Text,;
StyleSheet,;
ScrollView,;
TouchableOpacity,;
SafeAreaView,";,"";
StatusBar;';'';
} from "react-native";";
interface BlockchainScreenProps {}}
}
  const userId = string;}';'';
}';,'';
type TabType = 'overview' | 'data' | 'zkproof' | 'access';';,'';
export const BlockchainScreen: React.FC<Suspense fallback={<LoadingSpinner  />}><BlockchainScreenProps></Suspense> = ({ userId = 'demo-user' ;}) => {/;}';,'/g'/;
const [activeTab, setActiveTab] = useState<TabType>('overview');';,'';
const tabs = [;];';'';
    {';,}key: "overview";","";"";
";,"";
key: "data";","";"";
";,"";
key: "zkproof";","";"";
";,"";
const key = "access";";"";
";"";
}
];
  ];"}";
const renderTabContent = useCallback(() => {switch (activeTab) {case 'overview':return <OverviewTab userId={userId}  />;'/;,'/g'/;
case 'data': ';,'';
return <HealthDataManager userId={userId}  />;'/;,'/g'/;
case 'zkproof': ';,'';
return <ZKProofManager userId={userId}  />;'/;,'/g'/;
case 'access': ';,'';
return <AccessControlTab userId={userId}  />;/;,/g,/;
  default: ;
return <OverviewTab userId={userId;}  />;/;/g/;
    }
  };';,'';
return (<SafeAreaView style={styles.container}>';)      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF"  />"/;"/g"/;
      {// 头部}/;/g/;
      <View style={styles.header}>;
        <Text style={styles.headerTitle}>区块链健康数据</Text>/;/g/;
        <Text style={styles.headerSubtitle}>安全 · 隐私 · 可验证</Text>/;/g/;
      </View>/;/g/;
      {// 标签栏})/;/g/;
      <View style={styles.tabContainer}>);
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>);
          {tabs.map(tab) => ();}}
            <TouchableOpacity;}  />/;,/g/;
key={tab.key}
              style={[;,]styles.tab,;}}
                activeTab === tab.key && styles.activeTab;}
];
              ]}}
              onPress={() => setActiveTab(tab.key as TabType)}
            >;
              <Text style={styles.tabIcon}>{tab.icon}</Text>/;/g/;
              <Text style={ />/;}[;];/g/;
}
                styles.tabLabel,activeTab === tab.key && styles.activeTabLabel;}
];
              ]}}>;
                {tab.label};
              </Text>;/;/g/;
            </TouchableOpacity>;/;/g/;
          ))};
        </ScrollView>;/;/g/;
      </View>;/;/g/;
      {// 内容区域};/;/g/;
      <View style={styles.content}>;
        {renderTabContent()};
      </View>;/;/g/;
    </SafeAreaView>;/;/g/;
  );
};
// 概览标签页/;,/g/;
const  OverviewTab: React.FC<{ userId: string ;}> = ({ userId }) => {}
  return (<ScrollView style={styles.overviewContainer} showsVerticalScrollIndicator={false}>;)      {// 区块链状态卡片}/;/g/;
      <BlockchainStatusCard showDetails={true}  />/;/g/;
      {// 网络统计}/;/g/;
      <BlockchainNetworkStats  />/;/g/;
      {// 功能快捷入口}/;/g/;
      <View style={styles.quickActionsContainer}>;
        <Text style={styles.sectionTitle}>快捷操作</Text>/;/g/;
        <View style={styles.quickActionsGrid}>";"";
          <QuickActionCard;"  />/;,"/g"/;
icon="🏥"";"";
";"";
";,"";
color="#007AFF"";"";
          />"/;"/g"/;
          <QuickActionCard;"  />/;,"/g"/;
icon="🔐"";"";
";"";
";,"";
color="#8E44AD"";"";
          />"/;"/g"/;
          <QuickActionCard;"  />/;,"/g"/;
icon="✅"";"";
";"";
";,"";
color="#28A745"";"";
          />/;/g/;
          ;";"";
          <QuickActionCard;"  />/;,"/g"/;
icon="🔑";";"";
";"";
";,"";
color="#FD7E14";";"";
          />;/;/g/;
        </View>;/;/g/;
      </View>;/;/g/;
      {// 最近活动};/;/g/;
      <View style={styles.recentActivityContainer}>;
        <Text style={styles.sectionTitle}>最近活动</Text>;/;/g/;
        <RecentActivityList userId={userId}  />;)/;/g/;
      </View>;)/;/g/;
    </ScrollView>;)/;/g/;
  );
};
// 访问控制标签页/;,/g/;
const  AccessControlTab: React.FC<{ userId: string ;}> = ({ userId }) => {}}
  return (;)}
    <ScrollView style={styles.accessControlContainer} showsVerticalScrollIndicator={false}>;
      <View style={styles.comingSoonContainer}>;
        <Text style={styles.comingSoonIcon}>🚧</Text>;/;/g/;
        <Text style={styles.comingSoonTitle}>访问控制功能</Text>;/;/g/;
        <Text style={styles.comingSoonText}>;

        </Text>;/;/g/;
        <View style={styles.featureList}>;
          <Text style={styles.featureItem}>• 授权第三方访问健康数据</Text>;/;/g/;
          <Text style={styles.featureItem}>• 设置访问权限和有效期</Text>;/;/g/;
          <Text style={styles.featureItem}>• 撤销已授权的访问权限</Text>;/;/g/;
          <Text style={styles.featureItem}>• 查看访问日志和审计记录</Text>;/;/g/;
        </View>;/;/g/;
      </View>;/;/g/;
    </ScrollView>;/;/g/;
  );
};
// 快捷操作卡片/;,/g,/;
  const: QuickActionCard: React.FC<{icon: string,;
title: string,;
description: string,;
}
  const color = string;}
}> = ({ icon, title, description, color }) => {}}
  return (;)}
    <TouchableOpacity style={[styles.quickActionCard, { borderLeftColor: color ;}}]}>;
      <Text style={styles.quickActionIcon}>{icon}</Text>;/;/g/;
      <View style={styles.quickActionContent}>;
        <Text style={styles.quickActionTitle}>{title}</Text>;/;/g/;
        <Text style={styles.quickActionDescription}>{description}</Text>;/;/g/;
      </View>;/;/g/;
    </TouchableOpacity>;/;/g/;
  );
};
// 最近活动列表/;,/g/;
const  RecentActivityList: React.FC<{ userId: string ;}> = ({ userId }) => {const  activities = [;]";}    {";,}id: "1";",";
type: 'store';','';'';
';,'';
timestamp: Date.now() - 1000 * 60 * 30, // 30分钟前'/;'/g'/;
}
      const status = 'success'}'';'';
    ;},';'';
    {';,}id: "2";",";
type: 'verify',title: '验证心率数据',description: '验证心率数据完整性通过',timestamp: Date.now() - 1000 * 60 * 60 * 2, // 2小时前;'/;'/g'/;
}
      const status = 'success';'}'';'';
    },{';,}id: "3";",";
type: 'zkproof',title: '生成年龄证明',description: '成功生成年龄验证的零知识证明',timestamp: Date.now() - 1000 * 60 * 60 * 24, // 1天前;'/;'/g'/;
}
      const status = 'success';'}'';'';
    };';'';
];
  ];';,'';
const getActivityIcon = useCallback((type: string) => {switch (type) {case 'store': return '📝';';,}case 'verify': return '✅';';,'';
case 'zkproof': return '🔐';';'';
}
      const default = return '📋';'}'';'';
    }';'';
  };';,'';
const getStatusColor = useCallback((status: string) => {switch (status) {case 'success': return '#28A745';';,}case 'pending': return '#FFC107';';,'';
case 'failed': return '#DC3545';';'';
}
      const default = return '#6C757D';'}'';'';
    }
  };
const formatTimeAgo = useCallback((timestamp: number) => {const now = Date.now();,}const diff = now - timestamp;
const minutes = Math.floor(diff / (1000 * 60));/;,/g/;
const hours = Math.floor(diff / (1000 * 60 * 60));/;,/g/;
const days = Math.floor(diff / (1000 * 60 * 60 * 24));/;/g/;

}
}
  };
return (<View style={styles.activityList}>);
      {activities.map(activity) => ()}
        <View key={activity.id} style={styles.activityItem}>;
          <View style={styles.activityIconContainer}>;
            <Text style={styles.activityIcon}>{getActivityIcon(activity.type)}</Text>;/;/g/;
          </View>;/;/g/;
          <View style={styles.activityContent}>;
            <Text style={styles.activityTitle}>{activity.title}</Text>;/;/g/;
            <Text style={styles.activityDescription}>{activity.description}</Text>;/;/g/;
            <Text style={styles.activityTime}>{formatTimeAgo(activity.timestamp)}</Text>;/;/g/;
          </View>;/;/g/;
          <View style={[ />/;];}/g/;
            styles.activityStatus,{ backgroundColor: getStatusColor(activity.status) ;}};
];
          ]} />;/;/g/;
        </View>;/;/g/;
      ))};
    </View>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,';,}flex: 1,';'';
}
    const backgroundColor = '#F8F9FA'}'';'';
  ;},';,'';
header: {,';,}backgroundColor: '#FFFFFF';','';
paddingHorizontal: 20,;
paddingVertical: 16,';,'';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#E9ECEF'}'';'';
  ;}
headerTitle: {,';,}fontSize: 24,';,'';
fontWeight: '700';','';
color: '#2C3E50';','';'';
}
    const marginBottom = 4;}
  }
headerSubtitle: {,';,}fontSize: 14,';'';
}
    const color = '#6C757D'}'';'';
  ;},';,'';
tabContainer: {,';,}backgroundColor: '#FFFFFF';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#E9ECEF'}'';'';
  ;}
tab: {paddingHorizontal: 20,';,'';
paddingVertical: 12,';,'';
alignItems: 'center';','';'';
}
    const minWidth = 80;}
  }
activeTab: {,';,}borderBottomWidth: 2,';'';
}
    const borderBottomColor = '#007AFF'}'';'';
  ;}
tabIcon: {fontSize: 20,;
}
    const marginBottom = 4;}
  }
tabLabel: {,';,}fontSize: 12,';,'';
color: '#6C757D';','';'';
}
    const fontWeight = '500'}'';'';
  ;},';,'';
activeTabLabel: {,';,}color: '#007AFF';','';'';
}
    const fontWeight = '600'}'';'';
  ;}
content: {,;}}
  const flex = 1;}
  }
overviewContainer: {,;}}
  const flex = 1;}
  },';,'';
quickActionsContainer: {,';,}backgroundColor: '#FFFFFF';','';
margin: 16,;
borderRadius: 12,';,'';
padding: 16,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  }
sectionTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: '#2C3E50';','';'';
}
    const marginBottom = 16;}
  }
quickActionsGrid: {,;}}
  const gap = 12;}
  },';,'';
quickActionCard: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
backgroundColor: '#F8F9FA';','';
borderRadius: 8,;
padding: 12,;
}
    const borderLeftWidth = 4;}
  }
quickActionIcon: {fontSize: 24,;
}
    const marginRight = 12;}
  }
quickActionContent: {,;}}
  const flex = 1;}
  }
quickActionTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: '#2C3E50';','';'';
}
    const marginBottom = 4;}
  }
quickActionDescription: {,';,}fontSize: 12,';,'';
color: '#6C757D';','';'';
}
    const lineHeight = 16;}
  },';,'';
recentActivityContainer: {,';,}backgroundColor: '#FFFFFF';','';
margin: 16,;
borderRadius: 12,';,'';
padding: 16,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  }
activityList: {,;}}
  const gap = 12;}
  },';,'';
activityItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const paddingVertical = 8;}
  }
activityIconContainer: {width: 40,;
height: 40,';,'';
borderRadius: 20,';,'';
backgroundColor: '#F8F9FA';','';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const marginRight = 12;}
  }
activityIcon: {,;}}
  const fontSize = 18;}
  }
activityContent: {,;}}
  const flex = 1;}
  }
activityTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: '#2C3E50';','';'';
}
    const marginBottom = 2;}
  }
activityDescription: {,';,}fontSize: 12,';,'';
color: '#6C757D';','';'';
}
    const marginBottom = 2;}
  }
activityTime: {,';,}fontSize: 11,';'';
}
    const color = '#ADB5BD'}'';'';
  ;}
activityStatus: {width: 8,;
height: 8,;
borderRadius: 4,;
}
    const marginLeft = 8;}
  }
accessControlContainer: {,;}}
  const flex = 1;}
  }
comingSoonContainer: {,';,}flex: 1,';,'';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const padding = 32;}
  }
comingSoonIcon: {fontSize: 64,;
}
    const marginBottom = 16;}
  }
comingSoonTitle: {,';,}fontSize: 24,';,'';
fontWeight: '600';','';
color: '#2C3E50';','';
marginBottom: 12,';'';
}
    const textAlign = 'center'}';'';
  ;},';,'';
comingSoonText: {fontSize: 16,color: '#6C757D',textAlign: 'center',lineHeight: 24,marginBottom: 24;'}'';'';
  },featureList: {alignSelf: 'stretch';')}'';'';
  },featureItem: {fontSize: 14,color: '#495057',marginBottom: 8,paddingLeft: 8;')}'';'';
  };)';'';
});
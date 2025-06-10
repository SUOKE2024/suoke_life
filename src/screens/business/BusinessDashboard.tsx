import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import { StackNavigationProp } from "@react-navigation/stack";""/;,"/g"/;
import React from "react";";
import {Dimensions}ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
    View,'}'';'';
} from "react-native";";
import Icon from "react-native-vector-icons/MaterialIcons";""/;,"/g"/;
import { BusinessStackParamList } from "../../navigation/types";""/;,"/g"/;
const type = BusinessDashboardNavigationProp = StackNavigationProp<";,"";
BusinessStackParamList,';'';
  'BusinessDashboard'';'';
>;';'';
';,'';
const { width } = Dimensions.get('window');';,'';
interface MetricCardProps {title: string}value: string,';,'';
change: string,';,'';
changeType: 'positive' | 'negative' | 'neutral';','';'';
}
}
  const icon = string;}
}

const  MetricCard: React.FC<MetricCardProps> = ({)title}value,;
change,);
changeType,);
}
  icon,)}
;}) => {const  getChangeColor = useCallback(() => {';,}switch (changeType) {';,}case 'positive': ';,'';
return '#4CAF50';';,'';
case 'negative': ';,'';
return '#F44336';';,'';
const default = ';'';
}
        return '#9E9E9E';'}'';'';
    }
  };
return (<View style={styles.metricCard}>';)      <View style={styles.metricHeader}>';'';
        <Icon name={icon} size={24} color="#2196F3"  />"/;"/g"/;
        <Text style={styles.metricTitle}>{title}</Text>)/;/g/;
      </View>)/;/g/;
      <Text style={styles.metricValue}>{value}</Text>)/;/g/;
      <Text style={[styles.metricChange, { color: getChangeColor() ;}]}>;
        {change}
      </Text>/;/g/;
    </View>/;/g/;
  );
};
interface QuickActionProps {title: string}subtitle: string,;
icon: string,;
}
}
  onPress: () => void;}
}

const  QuickAction: React.FC<QuickActionProps> = ({)title}subtitle,);
icon,);
}
  onPress,)}";"";
;}) => (<TouchableOpacity style={styles.quickAction} onPress={onPress}>";)    <Icon name={icon} size={32} color="#2196F3"  />"/;"/g"/;
    <View style={styles.quickActionText}>;
      <Text style={styles.quickActionTitle}>{title}</Text>/;/g/;
      <Text style={styles.quickActionSubtitle}>{subtitle}</Text>"/;"/g"/;
    </View>")""/;"/g"/;
    <Icon name="chevron-right" size={24} color="#9E9E9E"  />")""/;"/g"/;
  </TouchableOpacity>)/;/g/;
);
const  BusinessDashboard: React.FC = () => {const navigation = useNavigation<BusinessDashboardNavigationProp>();,}const  metrics = [;]{";}";,"";
change: '+12.5%';','';
changeType: 'positive' as const;','';'';
}
      const icon = 'trending-up';'}'';'';
    }
    {';}';,'';
change: '+8.3%';','';
changeType: 'positive' as const;','';'';
}
      const icon = 'people';'}'';'';
    }
    {';}';,'';
value: '23.7%';','';
change: '+2.1%';','';
changeType: 'positive' as const;','';'';
}
      const icon = 'star';'}'';'';
    }
    {';}';,'';
changeType: 'positive' as const;','';'';
}
      const icon = 'business';'}'';'';
    }
];
  ];
const  quickActions = [;]{';}';,'';
icon: 'card-membership';','';'';
}
      onPress: () => navigation.navigate('SubscriptionPlans');'}'';'';
    }
    {';}';,'';
icon: 'handshake';','';'';
}
      onPress: () => navigation.navigate('BPartnerList');'}'';'';
    }
    {';}';,'';
icon: 'store';','';'';
}
      onPress: () => navigation.navigate('EcosystemProducts');'}'';'';
    }
    {';}';,'';
icon: 'analytics';','';'';
}
      onPress: () => navigation.navigate('RevenueAnalytics');'}'';'';
    }
];
  ];
return (<ScrollView style={styles.container}>;)      <View style={styles.header}>;
        <Text style={styles.headerTitle}>商业化中心</Text>/;/g/;
        <Text style={styles.headerSubtitle}>;

        </Text>/;/g/;
      </View>/;/g/;

      <View style={styles.metricsContainer}>);
        <Text style={styles.sectionTitle}>核心指标</Text>)/;/g/;
        <View style={styles.metricsGrid}>);
          {metrics.map((metric, index) => (<MetricCard key={index} {...metric}  />)/;/g/;
          ))}
        </View>/;/g/;
      </View>/;/g/;

      <View style={styles.actionsContainer}>;
        <Text style={styles.sectionTitle}>快速操作</Text>/;/g/;
        {quickActions.map((action, index) => (<QuickAction key={index} {...action}  />)/;/g/;
        ))}
      </View>/;/g/;

      <View style={styles.recentActivity}>;
        <Text style={styles.sectionTitle}>最近活动</Text>'/;'/g'/;
        <View style={styles.activityItem}>';'';
          <Icon name="payment" size={20} color="#4CAF50"  />"/;"/g"/;
          <Text style={styles.activityText}>新增订阅用户 +127</Text>/;/g/;
          <Text style={styles.activityTime}>2小时前</Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.activityItem}>";"";
          <Icon name="business" size={20} color="#2196F3"  />"/;"/g"/;
          <Text style={styles.activityText}>B端合作伙伴签约</Text>/;/g/;
          <Text style={styles.activityTime}>5小时前</Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.activityItem}>";"";
          <Icon name="shopping-cart" size={20} color="#FF9800"  />"/;"/g"/;
          <Text style={styles.activityText}>生态产品销售 +¥12.3万</Text>/;/g/;
          <Text style={styles.activityTime}>1天前</Text>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </ScrollView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = '#f5f5f5';'}'';'';
  },';,'';
header: {,';,}backgroundColor: '#2196F3';','';
padding: 20,;
}
    const paddingTop = 40;}
  }
headerTitle: {,';,}fontSize: 28,';,'';
fontWeight: 'bold';','';
color: '#fff';','';'';
}
    const marginBottom = 8;}
  }
headerSubtitle: {,';,}fontSize: 16,';'';
}
    const color = '#E3F2FD';'}'';'';
  }
metricsContainer: {,;}}
    const padding = 20;}
  }
sectionTitle: {,';,}fontSize: 20,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginBottom = 16;}
  },';,'';
metricsGrid: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const justifyContent = 'space-between';'}'';'';
  },';,'';
metricCard: {,';,}backgroundColor: '#fff';',)'';
borderRadius: 12,);
padding: 16;),;
width: (width - 60) / 2,/;,/g,/;
  marginBottom: 16,';,'';
elevation: 2,';'';
}
    shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
const shadowRadius = 4;
  },';,'';
metricHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = 12;}
  }
metricTitle: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const marginLeft = 8;}
  }
metricValue: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
metricChange: {,';,}fontSize: 12,';'';
}
    const fontWeight = '500';'}'';'';
  }
actionsContainer: {paddingHorizontal: 20,;
}
    const paddingBottom = 20;}
  },';,'';
quickAction: {,';,}backgroundColor: '#fff';','';
borderRadius: 12,';,'';
padding: 16,';,'';
flexDirection: 'row';','';
alignItems: 'center';','';
marginBottom: 12,';,'';
elevation: 2,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
const shadowRadius = 4;
  }
quickActionText: {flex: 1,;
}
    const marginLeft = 16;}
  }
quickActionTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
quickActionSubtitle: {,';,}fontSize: 14,';'';
}
    const color = '#666';'}'';'';
  }
recentActivity: {paddingHorizontal: 20,;
}
    const paddingBottom = 20;}
  },';,'';
activityItem: {,';,}backgroundColor: '#fff';','';
borderRadius: 8,';,'';
padding: 16,';,'';
flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = 8;}
  }
activityText: {flex: 1,';,'';
fontSize: 14,';,'';
color: '#333';','';'';
}
    const marginLeft = 12;}
  }
activityTime: {,';,}fontSize: 12,';'';
}
    const color = '#999';'}'';'';
  }
});
';,'';
export default BusinessDashboard; ''';
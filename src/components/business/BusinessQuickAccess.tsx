import { useNavigation } from "@react-navigation/native"
import React from "react";
import {Dimensions} fromtyleSheet,
Text,"
TouchableOpacity,";
}
  View,'}
} from "react-native;
import Icon from "react-native-vector-icons/MaterialIcons"
const { width } = Dimensions.get('window');
interface QuickAccessItem {id: string}title: string,
subtitle: string,
icon: string,
color: string,
}
}
  onPress: () => void}
}
const  BusinessQuickAccess: React.FC = () => {const navigation = useNavigation()const  quickAccessItems: QuickAccessItem[] = [;]'
    {'id: '1,'
icon: 'card-membership,'
color: '#2196F3,'
onPress: () => {';}}
        // 导航到商业化标签页的订阅管理'}''/,'/g'/;
navigation.navigate('Business' as never, { screen: 'SubscriptionPlans' ;} as never);
      }
    },'
    {'id: '2,'
icon: 'handshake,'
color: '#4CAF50,'
}
      onPress: () => {'}
navigation.navigate('Business' as never, { screen: 'BPartnerList' ;} as never);
      }
    },'
    {'id: '3,'
icon: 'store,'
color: '#FF9800,'
}
      onPress: () => {'}
navigation.navigate('Business' as never, { screen: 'EcosystemProducts' ;} as never);
      }
    },'
    {'id: '4,'
icon: 'analytics,'
color: '#9C27B0,'
}
      onPress: () => {'}
navigation.navigate('Business' as never, { screen: 'RevenueAnalytics' ;} as never);
      }
    }
];
  ];
const  handleViewAll = useCallback(() => {';}}
    navigation.navigate('Business' as never);'}
  };
return (<View style={styles.container}>;)      <View style={styles.header}>;
        <Text style={styles.title}>商业化中心</Text>
        <TouchableOpacity onPress={handleViewAll} style={styles.viewAllButton}>'
          <Text style={styles.viewAllText}>查看全部</Text>'/;'/g'/;
          <Icon name="chevron-right" size={16} color="#2196F3"  />"/;"/g"/;
        </TouchableOpacity>
      </View>)
);
      <View style={styles.grid}>);
        {quickAccessItems.map((item) => (<TouchableOpacity,}  />/,)key={item.id}/g/;
            style={styles.gridItem}
            onPress={item.onPress}
            activeOpacity={0.7}
          >;
            <View style={[styles.iconContainer, { backgroundColor: `${item.color;}15` }]}>````;```;
              <Icon name={item.icon} size={24} color={item.color}  />
            </View>
            <Text style={styles.itemTitle}>{item.title}</Text>)
            <Text style={styles.itemSubtitle}>{item.subtitle}</Text>)
          </TouchableOpacity>)
        ))}
      </View>
    </View>
  );
};
const  styles = StyleSheet.create({)"container: {,"backgroundColor: '#fff,'';
borderRadius: 12,
padding: 16,
marginVertical: 8,
elevation: 2,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
const shadowRadius = 4;
  },'
header: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 16}
  }
title: {,'fontSize: 18,'
fontWeight: 'bold,'
}
    const color = '#333}
  },'
viewAllButton: {,'flexDirection: 'row,'
}
    const alignItems = 'center}
  }
viewAllText: {,'fontSize: 14,'
color: '#2196F3,'
}
    const marginRight = 4}
  },'
grid: {,'flexDirection: 'row,'
flexWrap: 'wrap,'
}
    const justifyContent = 'space-between)}
  },);
gridItem: {,)'width: (width - 80) / 2,'/,'/g,'/;
  alignItems: 'center,'';
paddingVertical: 12,
}
    const marginBottom = 8}
  }
iconContainer: {width: 48,
height: 48,
borderRadius: 24,'
justifyContent: 'center,'
alignItems: 'center,'
}
    const marginBottom = 8}
  }
itemTitle: {,'fontSize: 14,'
fontWeight: '600,'
color: '#333,'';
marginBottom: 4,
}
    const textAlign = 'center}
  }
itemSubtitle: {,'fontSize: 12,'
color: '#666,'
}
    const textAlign = 'center}
  }
});
export default BusinessQuickAccess; ''
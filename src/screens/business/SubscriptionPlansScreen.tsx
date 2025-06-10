import React, { useState } from "react";";
import {Alert}ScrollView,;
StyleSheet,;
Switch,;
Text,;
TouchableOpacity,";"";
}
    View,'}'';'';
} from "react-native";";
import Icon from "react-native-vector-icons/MaterialIcons";""/;,"/g"/;
interface SubscriptionPlan {id: string}name: string,";,"";
price: number,';,'';
period: 'monthly' | 'yearly';','';
const features = string[];
isPopular?: boolean;
isActive: boolean,;
}
}
  const subscribers = number;}
}

interface PlanCardProps {plan: SubscriptionPlan}onToggle: (id: string, isActive: boolean) => void,;
}
}
  onEdit: (plan: SubscriptionPlan) => void;}
}

const PlanCard: React.FC<PlanCardProps> = ({ plan, onToggle, onEdit ;}) => {}
  return (<View style={[styles.planCard, plan.isPopular && styles.popularPlan]}>;)      {plan.isPopular && (})        <View style={styles.popularBadge}>);
          <Text style={styles.popularText}>热门</Text>)/;/g/;
        </View>)/;/g/;
      )}

      <View style={styles.planHeader}>;
        <View>;
          <Text style={styles.planName}>{plan.name}</Text>'/;'/g'/;
          <Text style={styles.planPrice}>';'';
            ¥{plan.price}/{plan.period === 'monthly' ? '月' : '年'}'/;'/g'/;
          </Text>/;/g/;
        </View>/;/g/;
        <Switch,  />/;,/g/;
value={plan.isActive}';,'';
onValueChange={(value) => onToggle(plan.id, value)}';,'';
trackColor={{ false: '#767577', true: '#81b0ff' ;}}';,'';
thumbColor={plan.isActive ? '#2196F3' : '#f4f3f4'}';'';
        />/;/g/;
      </View>/;/g/;

      <View style={styles.planStats}>';'';
        <View style={styles.statItem}>';'';
          <Icon name="people" size={16} color="#666"  />"/;"/g"/;
          <Text style={styles.statText}>{plan.subscribers} 订阅者</Text>/;/g/;
        </View>/;/g/;
      </View>/;/g/;

      <View style={styles.featuresContainer}>;
        <Text style={styles.featuresTitle}>功能特性：</Text>"/;"/g"/;
        {plan.features.map((feature, index) => (<View key={index} style={styles.featureItem}>";)            <Icon name="check" size={16} color="#4CAF50"  />")""/;"/g"/;
            <Text style={styles.featureText}>{feature}</Text>)/;/g/;
          </View>)/;/g/;
        ))}
      </View>/;/g/;

      <TouchableOpacity,  />/;,/g/;
style={styles.editButton}
        onPress={() => onEdit(plan)}";"";
      >";"";
        <Icon name="edit" size={16} color="#2196F3"  />"/;"/g"/;
        <Text style={styles.editButtonText}>编辑计划</Text>/;/g/;
      </TouchableOpacity>/;/g/;
    </View>/;/g/;
  );
};
const  SubscriptionPlansScreen: React.FC = () => {const [plans, setPlans] = useState<SubscriptionPlan[]>([;)";]    {";,}id: '1';','';'';
';,'';
price: 29,';,'';
period: 'monthly';','';
const features = [;]];
      ],;
isActive: true,;
}
      const subscribers = 12450;}
    },';'';
    {';,}id: '2';','';'';
';,'';
price: 89,';,'';
period: 'monthly';','';
const features = [;]];
      ],;
isPopular: true,;
isActive: true,;
}
      const subscribers = 8920;}
    },';'';
    {';,}id: '3';','';'';
';,'';
price: 299,';,'';
period: 'monthly';','';
const features = [;]];
      ],;
isActive: true,;
}
      const subscribers = 156;}
    },';'';
    {';,}id: '4';','';'';
';,'';
price: 899,';,'';
period: 'yearly';','';
const features = [;]];
      ],;
isActive: true,);
}
      const subscribers = 3240;)}
    },);
  ]);
const: handleTogglePlan = useCallback((id: string, isActive: boolean) => {setPlans(prevPlans =>);}}
      prevPlans.map(plan =>)}
        plan.id === id ? { ...plan, isActive ;} : plan);
      );
    );
Alert.alert();
);
    );
  };
const  handleEditPlan = useCallback((plan: SubscriptionPlan) => {Alert.alert();});
}
    );}
  };
const  handleAddPlan = useCallback(() => {Alert.alert();});
}
    );}
  };
totalSubscribers: plans.reduce((sum, plan) => sum + plan.subscribers, 0);';,'';
const: totalRevenue = plans.reduce((sum, plan) => {';,}const  monthlyRevenue = plan.period === 'yearly' ';'';
      ? (plan.price / 12) * plan.subscribers/;/g/;
      : plan.price * plan.subscribers;
}
    return sum + monthlyRevenue;}
  }, 0);
return (<ScrollView style={styles.container}>;)      <View style={styles.header}>;
        <Text style={styles.headerTitle}>订阅计划管理</Text>/;/g/;
        <Text style={styles.headerSubtitle}>;

        </Text>/;/g/;
      </View>/;/g/;

      <View style={styles.statsContainer}>)';'';
        <View style={styles.statCard}>)';'';
          <Icon name="people" size={24} color="#2196F3"  />")""/;"/g"/;
          <Text style={styles.statValue}>{totalSubscribers.toLocaleString()}</Text>/;/g/;
          <Text style={styles.statLabel}>总订阅用户</Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.statCard}>";"";
          <Icon name="attach-money" size={24} color="#4CAF50"  />"/;"/g"/;
          <Text style={styles.statValue}>¥{Math.round(totalRevenue / 10000)}万</Text>/;/g/;
          <Text style={styles.statLabel}>月收入</Text>/;/g/;
        </View>/;/g/;
      </View>/;/g/;

      <View style={styles.plansContainer}>;
        <View style={styles.sectionHeader}>;
          <Text style={styles.sectionTitle}>订阅计划</Text>"/;"/g"/;
          <TouchableOpacity style={styles.addButton} onPress={handleAddPlan}>";"";
            <Icon name="add" size={20} color="#fff"  />"/;"/g"/;
            <Text style={styles.addButtonText}>新增计划</Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;

        {}plans.map(plan => (;)}
          <PlanCard,}  />/;,/g/;
key={plan.id}
            plan={plan}
            onToggle={handleTogglePlan});
onEdit={handleEditPlan});
          />)/;/g/;
        ))}
      </View>/;/g/;

      <View style={styles.insightsContainer}>;
        <Text style={styles.sectionTitle}>运营洞察</Text>"/;"/g"/;
        <View style={styles.insightItem}>";"";
          <Icon name="trending-up" size={20} color="#4CAF50"  />"/;"/g"/;
          <Text style={styles.insightText}>;

          </Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.insightItem}>";"";
          <Icon name="lightbulb-outline" size={20} color="#FF9800"  />"/;"/g"/;
          <Text style={styles.insightText}>;

          </Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.insightItem}>";"";
          <Icon name="star" size={20} color="#9C27B0"  />"/;"/g"/;
          <Text style={styles.insightText}>;

          </Text>/;/g/;
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
headerTitle: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';
color: '#fff';','';'';
}
    const marginBottom = 8;}
  }
headerSubtitle: {,';,}fontSize: 16,';'';
}
    const color = '#E3F2FD';'}'';'';
  },';,'';
statsContainer: {,';,}flexDirection: 'row';','';
padding: 20,;
}
    const gap = 16;}
  }
statCard: {,';,}flex: 1,';,'';
backgroundColor: '#fff';','';
borderRadius: 12,';,'';
padding: 16,';,'';
alignItems: 'center';','';
elevation: 2,';'';
}
    shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
const shadowRadius = 4;
  }
statValue: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginTop = 8;}
  }
statLabel: {,';,}fontSize: 12,';,'';
color: '#666';','';'';
}
    const marginTop = 4;}
  }
plansContainer: {,;}}
    const paddingHorizontal = 20;}
  },';,'';
sectionHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 16;}
  }
sectionTitle: {,';,}fontSize: 20,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333';'}'';'';
  },';,'';
addButton: {,';,}backgroundColor: '#2196F3';','';
flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: 16,;
paddingVertical: 8,;
}
    const borderRadius = 20;}
  },';,'';
addButtonText: {,';,}color: '#fff';','';
fontSize: 14,';,'';
fontWeight: '600';','';'';
}
    const marginLeft = 4;}
  },';,'';
planCard: {,';,}backgroundColor: '#fff';','';
borderRadius: 12,;
padding: 20,;
marginBottom: 16,';,'';
elevation: 2,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,';,'';
shadowRadius: 4,';,'';
const position = 'relative';';'';
  },';,'';
popularPlan: {,';,}borderColor: '#FF9800';','';'';
}
    const borderWidth = 2;}
  },';,'';
popularBadge: {,';,}position: 'absolute';','';
top: -8,';,'';
right: 20,';,'';
backgroundColor: '#FF9800';','';
paddingHorizontal: 12,;
paddingVertical: 4,;
}
    const borderRadius = 12;}
  },';,'';
popularText: {,';,}color: '#fff';','';
fontSize: 12,';'';
}
    const fontWeight = 'bold';'}'';'';
  },';,'';
planHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 16;}
  }
planName: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333';'}'';'';
  }
planPrice: {,';,}fontSize: 16,';,'';
color: '#2196F3';','';
fontWeight: '600';','';'';
}
    const marginTop = 4;}
  }
planStats: {,;}}
    const marginBottom = 16;}
  },';,'';
statItem: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center';'}'';'';
  }
statText: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const marginLeft = 8;}
  }
featuresContainer: {,;}}
    const marginBottom = 16;}
  }
featuresTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    const marginBottom = 8;}
  },';,'';
featureItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = 4;}
  }
featureText: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const marginLeft = 8;}
  },';,'';
editButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';
backgroundColor: '#E3F2FD';','';
paddingVertical: 12,;
}
    const borderRadius = 8;}
  },';,'';
editButtonText: {,';,}color: '#2196F3';','';
fontSize: 14,';,'';
fontWeight: '600';','';'';
}
    const marginLeft = 4;}
  }
insightsContainer: {,;}}
    const padding = 20;}
  },';,'';
insightItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
backgroundColor: '#fff';','';
padding: 16,;
borderRadius: 8,;
}
    const marginBottom = 8;}
  }
insightText: {flex: 1,';,'';
fontSize: 14,';,'';
color: '#333';',)'';'';
}
    const marginLeft = 12;)}
  },);
});
';,'';
export default SubscriptionPlansScreen; ''';
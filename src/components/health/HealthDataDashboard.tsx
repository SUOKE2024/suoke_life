import React, { useState } from "react";";
import {import { HealthDataManager } from "./HealthDataManager";""/;,"/g"/;
import { VitalSignsMonitor } from "./VitalSignsMonitor";""/;,"/g"/;
import { TCMDiagnosisPanel } from "./TCMDiagnosisPanel";""/;,"/g"/;
import { HealthReportGenerator } from "./HealthReportGenerator";""/;,"/g"/;
import { HealthDataImportExport } from "./HealthDataImportExport";""/;,"/g"/;
View,;
Text,;
StyleSheet,;
ScrollView,;
TouchableOpacity,";,"";
SafeAreaView;';'';
} from "react-native";";
interface HealthDataDashboardProps {}}
}
  const userId = string;}';'';
}';,'';
type TabType = 'overview' | 'vitals' | 'tcm' | 'reports' | 'data';';,'';
export const HealthDataDashboard: React.FC<HealthDataDashboardProps> = ({ userId ;}) => {';,}const [activeTab, setActiveTab] = useState<TabType>('overview');';,'';
const tabs = [;];';'';
    {';,}key: "overview";","";"";
";,"";
key: "vitals";","";"";
";,"";
key: "tcm";","";"";
";,"";
key: "reports";","";"";
";,"";
const key = "data";";"";
";"";
}
];
  ];"}";
const renderTabContent = useCallback(() => {switch (activeTab) {case 'overview':return <HealthDataManager userId={userId}  />;'/;,'/g'/;
case 'vitals': ';,'';
return <VitalSignsMonitor userId={userId}  />;'/;,'/g'/;
case 'tcm': ';,'';
return <TCMDiagnosisPanel userId={userId}  />;'/;,'/g'/;
case 'reports': ';,'';
return <HealthReportGenerator userId={userId}  />;'/;,'/g'/;
case 'data': ';,'';
return <HealthDataImportExport userId={userId}  />;/;,/g,/;
  default: ;
return <HealthDataManager userId={userId;}  />;/;/g/;
    }
  };
const  renderTabBar = () => (<View style={styles.tabBar}>;)      <ScrollView;  />/;,/g/;
horizontal;
showsHorizontalScrollIndicator={false});
contentContainerStyle={styles.tabScrollContent});
      >);
        {tabs.map(tab) => ();}}
          <TouchableOpacity;}  />/;,/g/;
key={tab.key}
            style={}[;]}
              styles.tab,activeTab === tab.key && styles.activeTab;}
];
            ]}};
onPress={() => setActiveTab(tab.key as TabType)};
          >;
            <Text style={styles.tabIcon}>{tab.icon}</Text>;/;/g/;
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
  );
return (;);
    <SafeAreaView style={styles.container}>;
      <View style={styles.header}>;
        <Text style={styles.title}>健康数据中心</Text>;/;/g/;
        <Text style={styles.subtitle}>全面管理您的健康信息</Text>;/;/g/;
      </View>;/;/g/;
      {renderTabBar()};
      <View style={styles.content}>;
        {renderTabContent()};
      </View>;/;/g/;
    </SafeAreaView>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,';,}flex: 1,';'';
}
    const backgroundColor = '#f5f5f5'}'';'';
  ;},';,'';
header: {,';,}backgroundColor: '#fff';','';
paddingHorizontal: 20,;
paddingVertical: 16,';,'';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e0e0e0'}'';'';
  ;}
title: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
subtitle: {,';,}fontSize: 16,';'';
}
    const color = '#666'}'';'';
  ;},';,'';
tabBar: {,';,}backgroundColor: '#fff';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e0e0e0'}'';'';
  ;}
tabScrollContent: {,;}}
  const paddingHorizontal = 16;}
  }
tab: {paddingHorizontal: 20,;
paddingVertical: 12,;
marginRight: 8,';,'';
borderRadius: 20,';,'';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const minWidth = 80;}
  },';,'';
activeTab: {,';}}'';
  const backgroundColor = '#007AFF'}';'';
  ;},tabIcon: {fontSize: 20,marginBottom: 4;'}'';'';
  },tabLabel: {fontSize: 12,color: '#666',fontWeight: '500';'}'';'';
  },activeTabLabel: {color: '#fff';')}'';'';
  },content: {flex: 1;)}
  };)';'';
});
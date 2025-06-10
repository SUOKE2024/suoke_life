import React, { useState, useEffect, useCallback } from "react";";
import {import { useDispatch, useSelector } from "react-redux";";
import { AppDispatch, RootState } from "../../store";""/;,"/g"/;
import {import { KnowledgeSearchBar } from "../../components/health/KnowledgeSearchBar";""/;,"/g"/;
import { ConstitutionCard } from "../../components/health/ConstitutionCard";""/;,"/g"/;
import { KnowledgeQuery, KnowledgeResult } from "../../services/medKnowledgeService";""/;,"/g"/;
View,;
Text,;
StyleSheet,;
ScrollView,;
RefreshControl,;
TouchableOpacity,;
Alert,;
SafeAreaView,";,"";
StatusBar;';'';
} from "react-native";";
fetchConstitutions,;
fetchSymptoms,;
fetchAcupoints,;
fetchHerbs,;
fetchSyndromes,;
searchKnowledge,;
checkServiceHealth,;
selectConstitutions,;
selectLoading,;
selectErrors,;
selectServiceHealth,;
selectSearchResults,;
addToSearchHistory,';,'';
clearError;';'';
} from "../../store/slices/medKnowledgeSlice";""/;,"/g"/;
interface TabItem {key: string}title: string,;
}
}
  const icon = string;}
}
export const MedKnowledgeScreen: React.FC = () => {;,}const dispatch = useDispatch<AppDispatch>();
const constitutions = useSelector(selectConstitutions);
const loading = useSelector(selectLoading);
const errors = useSelector(selectErrors);
const serviceHealth = useSelector(selectServiceHealth);';,'';
const searchResults = useSelector(selectSearchResults);';,'';
const [activeTab, setActiveTab] = useState('constitution');';,'';
const [refreshing, setRefreshing] = useState(false);
const  tabs: TabItem[] = [;]';'';
    {';,}const key = "constitution";";"";
";"";
    {";,}const key = "symptom";";"";
";"";
    {";,}const key = "acupoint";";"";
";"";
    {";,}const key = "herb";";"";
";"";
    {";,}const key = "syndrome";";"";
";"";
    {";,}const key = "search";";"";

];
  ];
  // 初始化数据加载/;,/g/;
useEffect() => {}}
    initializeData();}
  }, [])  // 检查是否需要添加依赖项;/;/g/;
  // 检查服务健康状态/;,/g/;
useEffect() => {}}
    const checkHealth = async () => {try {await dispatch(checkServiceHealth()).unwrap();}";"";
      } catch (error) {";}}"";
        console.warn('Service health check failed:', error);'}'';'';
      }
    };
checkHealth();
    // 每5分钟检查一次服务健康状态/;,/g,/;
  interval: setInterval(checkHealth, 5 * 60 * 1000);
return () => clearInterval(interval);
  }, [dispatch]);
const initializeData = useCallback(async () => {try {// 并行加载基础数据;)/;,}const await = Promise.allSettled([;););,]dispatch(fetchConstitutions()).unwrap(),dispatch(fetchSymptoms()).unwrap(),dispatch(fetchAcupoints()).unwrap(),dispatch(fetchHerbs()).unwrap(),dispatch(fetchSyndromes()).unwrap();/g/;
}
];
      ]);}';'';
    } catch (error) {';}}'';
      console.error('Failed to initialize data:', error);'}'';'';
    }
  }, [dispatch]);
const handleRefresh = useCallback(async () => {setRefreshing(true););,}try {}}
      const await = initializeData();}
    } finally {}}
      setRefreshing(false);}
    }
  }, [initializeData]);
const handleSearch = useCallback(async (query: KnowledgeQuery) => {try {// 添加到搜索历史;)/;,}dispatch(addToSearchHistory(query.query));/g/;
      // 执行搜索/;,/g/;
const await = dispatch(searchKnowledge(query)).unwrap();';'';
      // 切换到搜索结果标签'/;'/g'/;
}
      setActiveTab('search');'}'';'';
    } catch (error) {}}
}
    }
  }, [dispatch]);';,'';
const handleConstitutionPress = useCallback(constitution: any) => {// 导航到体质详情页面;'/;}}'/g'/;
    console.log('Navigate to constitution detail:', constitution.id);'}'';'';
  }, []);
const handleErrorRetry = useCallback(errorType: keyof typeof errors) => {dispatch(clearError(errorType));';,}switch (errorType) {';,}case 'constitutions': ';,'';
dispatch(fetchConstitutions());';,'';
break;';,'';
case 'symptoms': ';,'';
dispatch(fetchSymptoms());';,'';
break;';,'';
case 'acupoints': ';,'';
dispatch(fetchAcupoints());';,'';
break;';,'';
case 'herbs': ';,'';
dispatch(fetchHerbs());';,'';
break;';,'';
case 'syndromes': ';,'';
dispatch(fetchSyndromes());
}
        break;}
    }';'';
  }, [dispatch]);';,'';
const renderServiceStatus = () => {if (serviceHealth.status === 'unhealthy') {return (;)'}'';'';
        <View style={styles.serviceStatusContainer}>;
          <View style={styles.serviceStatusBanner}>;
            <Text style={styles.serviceStatusText}>;

            </Text>;/;/g/;
          </View>;/;/g/;
        </View>;/;/g/;
      );
    }
    return null;';'';
  };';,'';
const renderTabContent = () => {switch (activeTab) {case 'constitution':return renderConstitutionTab();';,}case 'symptom': ';,'';
return renderSymptomTab();';,'';
case 'acupoint': ';,'';
return renderAcupointTab();';,'';
case 'herb': ';,'';
return renderHerbTab();';,'';
case 'syndrome': ';,'';
return renderSyndromeTab();';,'';
case 'search': ';,'';
return renderSearchTab();
default: ;
}
        return null;}
    }
  };
const renderConstitutionTab = () => {if (loading.constitutions) {return (;)}
        <View style={styles.loadingContainer}>;
          <Text style={styles.loadingText}>正在加载体质信息...</Text>;/;/g/;
        </View>;/;/g/;
      );
    }
    if (errors.constitutions) {}}
      return (;)}
        <View style={styles.errorContainer}>;
          <Text style={styles.errorText}>{errors.constitutions}</Text>;/;/g/;
          <TouchableOpacity;'  />/;,'/g'/;
style={styles.retryButton};';,'';
onPress={() => handleErrorRetry('constitutions')};';'';
          >;
            <Text style={styles.retryButtonText}>重试</Text>;/;/g/;
          </TouchableOpacity>;/;/g/;
        </View>;/;/g/;
      );
    }
    return (<ScrollView;  />/;,)style={styles.tabContent}/g/;
        refreshControl={}
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh}  />/;/g/;
        }
      >;
        <View style={styles.sectionHeader}>;
          <Text style={styles.sectionTitle}>中医体质类型</Text>/;/g/;
          <Text style={styles.sectionSubtitle}>;
);
          </Text>)/;/g/;
        </View>;)/;/g/;
        {constitutions.map(constitution) => (;);}}
          <ConstitutionCard;}  />/;,/g/;
key={constitution.id};
constitution={constitution};
onPress={() => handleConstitutionPress(constitution)};
          />;/;/g/;
        ))};
        {constitutions.length === 0 && (;)}
          <View style={styles.emptyContainer}>;
            <Text style={styles.emptyText}>暂无体质信息</Text>;/;/g/;
          </View>;/;/g/;
        )};
      </ScrollView>;/;/g/;
    );
  };
const renderSymptomTab = () => {return (;)}
      <View style={styles.tabContent}>;
        <Text style={styles.comingSoonText}>症状管理功能即将上线</Text>;/;/g/;
      </View>;/;/g/;
    );
  };
const renderAcupointTab = () => {return (;)}
      <View style={styles.tabContent}>;
        <Text style={styles.comingSoonText}>穴位信息功能即将上线</Text>;/;/g/;
      </View>;/;/g/;
    );
  };
const renderHerbTab = () => {return (;)}
      <View style={styles.tabContent}>;
        <Text style={styles.comingSoonText}>中药信息功能即将上线</Text>;/;/g/;
      </View>;/;/g/;
    );
  };
const renderSyndromeTab = () => {return (;)}
      <View style={styles.tabContent}>;
        <Text style={styles.comingSoonText}>证型分析功能即将上线</Text>;/;/g/;
      </View>;/;/g/;
    );
  };
const  renderSearchTab = () => {}
    return (<ScrollView style={styles.tabContent}>;)        <View style={styles.sectionHeader}>;
          <Text style={styles.sectionTitle}>搜索结果</Text>/;/g/;
          {searchResults.length > 0  && <Text style={styles.sectionSubtitle}>);
);
            </Text>)/;/g/;
          )}
        </View>/;/g/;
        {loading.search  && <View style={styles.loadingContainer}>;
            <Text style={styles.loadingText}>正在搜索...</Text>;/;/g/;
          </View>;/;/g/;
        )};
        {errors.search && (;)}
          <View style={styles.errorContainer}>;
            <Text style={styles.errorText}>{errors.search}</Text>;/;/g/;
          </View>;/;/g/;
        )};
        {searchResults.map(result) => (;)}
          <View key={result.id} style={styles.searchResultCard}>;
            <Text style={styles.searchResultTitle}>{result.title}</Text>;/;/g/;
            <Text style={styles.searchResultContent} numberOfLines={3}>;
              {result.content};
            </Text>;/;/g/;
            <View style={styles.searchResultMeta}>;
              <Text style={styles.searchResultType}>{result.type}</Text>;/;/g/;
              <Text style={styles.searchResultRelevance}>;
                相关度: {Math.round(result.relevance * 100)}%;
              </Text>;/;/g/;
            </View>;/;/g/;
          </View>;/;/g/;
        ))};
        {searchResults.length === 0 && !loading.search && !errors.search && (;)}
          <View style={styles.emptyContainer}>;
            <Text style={styles.emptyText}>请使用上方搜索栏查找医疗知识</Text>;/;/g/;
          </View>;/;/g/;
        )};
      </ScrollView>;/;/g/;
    );
  };';,'';
return (<SafeAreaView style={styles.container}>')'';'';
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF"  />")""/;"/g"/;
      {// 服务状态提示})/;/g/;
      {renderServiceStatus()}
      {// 搜索栏}/;/g/;
      <KnowledgeSearchBar;  />/;,/g/;
onSearch={handleSearch}
        loading={loading.search}

      />/;/g/;
      {// 标签栏}/;/g/;
      <View style={styles.tabBar}>;
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>;
          <View style={styles.tabList}>;
            {tabs.map(tab) => ();}}
              <TouchableOpacity;}  />/;,/g/;
key={tab.key}
                style={[;,]styles.tab,;}}
                  activeTab === tab.key && styles.activeTab;}
];
                ]}}
                onPress={() => setActiveTab(tab.key)}
              >;
                <Text style={styles.tabIcon}>{tab.icon}</Text>/;/g/;
                <Text;  />/;,/g/;
style={[;,]styles.tabText,;}}
                    activeTab === tab.key && styles.activeTabText;}
];
                  ]}};
                >;
                  {tab.title};
                </Text>;/;/g/;
              </TouchableOpacity>;/;/g/;
            ))};
          </View>;/;/g/;
        </ScrollView>;/;/g/;
      </View>;/;/g/;
      {// 内容区域};/;/g/;
      <View style={styles.content}>;
        {renderTabContent()};
      </View>;/;/g/;
    </SafeAreaView>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = '#F8F9FA'}'';'';
  ;},';,'';
serviceStatusContainer: {,';,}backgroundColor: '#FFF3CD';','';
paddingHorizontal: 16,;
}
    const paddingVertical = 8;}
  },';,'';
serviceStatusBanner: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
serviceStatusText: {,';,}fontSize: 14,';,'';
color: '#856404';','';'';
}
    const flex = 1;}
  },';,'';
tabBar: {,';,}backgroundColor: '#FFFFFF';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#E0E0E0'}'';'';
  ;},';,'';
tabList: {,';,}flexDirection: 'row';','';
paddingHorizontal: 16,;
paddingVertical: 12,;
}
    const gap = 8;}
  },';,'';
tab: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: 16,;
paddingVertical: 8,';,'';
borderRadius: 20,';,'';
backgroundColor: '#F5F5F5';','';'';
}
    const marginRight = 8;}
  },';,'';
activeTab: {,';}}'';
  const backgroundColor = '#007AFF'}'';'';
  ;}
tabIcon: {fontSize: 16,;
}
    const marginRight = 6;}
  }
tabText: {,';,}fontSize: 14,';,'';
color: '#666666';','';'';
}
    const fontWeight = '500'}'';'';
  ;},';,'';
activeTabText: {,';}}'';
  const color = '#FFFFFF'}'';'';
  ;}
content: {,;}}
  const flex = 1;}
  }
tabContent: {,;}}
  const flex = 1;}
  }
sectionHeader: {paddingHorizontal: 16,';,'';
paddingVertical: 16,';,'';
backgroundColor: '#FFFFFF';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#F0F0F0'}'';'';
  ;}
sectionTitle: {,';,}fontSize: 20,';,'';
fontWeight: 'bold';','';
color: '#333333';','';'';
}
    const marginBottom = 4;}
  }
sectionSubtitle: {,';,}fontSize: 14,';'';
}
    const color = '#666666'}'';'';
  ;}
loadingContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const paddingVertical = 40;}
  }
loadingText: {,';,}fontSize: 16,';'';
}
    const color = '#666666'}'';'';
  ;}
errorContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';
paddingVertical: 40,;
}
    const paddingHorizontal = 32;}
  }
errorText: {,';,}fontSize: 16,';,'';
color: '#F44336';','';
textAlign: 'center';','';'';
}
    const marginBottom = 16;}
  },';,'';
retryButton: {,';,}backgroundColor: '#007AFF';','';
paddingHorizontal: 24,;
paddingVertical: 12,;
}
    const borderRadius = 8;}
  },';,'';
retryButtonText: {,';,}color: '#FFFFFF';','';
fontSize: 16,';'';
}
    const fontWeight = '600'}'';'';
  ;}
emptyContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const paddingVertical = 40;}
  }
emptyText: {,';,}fontSize: 16,';,'';
color: '#999999';','';'';
}
    const textAlign = 'center'}'';'';
  ;}
comingSoonText: {,';,}fontSize: 16,';,'';
color: '#999999';','';
textAlign: 'center';','';'';
}
    const marginTop = 40;}
  },';,'';
searchResultCard: {,';,}backgroundColor: '#FFFFFF';','';
marginHorizontal: 16,;
marginVertical: 8,;
padding: 16,';,'';
borderRadius: 12,';,'';
shadowColor: '#000';','';
shadowOffset: {width: 0,;
}
      const height = 2;}
    }
shadowOpacity: 0.1,;
shadowRadius: 3.84,;
const elevation = 5;
  }
searchResultTitle: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';
color: '#333333';','';'';
}
    const marginBottom = 8;}
  }
searchResultContent: {,';,}fontSize: 14,';,'';
color: '#666666';','';
lineHeight: 20,;
}
    const marginBottom = 12;}
  },';,'';
searchResultMeta: {,';}}'';
  flexDirection: 'row',justifyContent: 'space-between',alignItems: 'center';'}'';'';
  },searchResultType: {fontSize: 12,color: '#007AFF',backgroundColor: '#E3F2FD',paddingHorizontal: 8,paddingVertical: 4,borderRadius: 12;')}'';'';
  },searchResultRelevance: {fontSize: 12,color: '#999999';')}'';'';
  };)';'';
});
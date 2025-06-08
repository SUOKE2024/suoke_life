import React, { useState, useEffect, useCallback } from 'react';
import {import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../store';
import {import { KnowledgeSearchBar } from '../../components/health/KnowledgeSearchBar';
import { ConstitutionCard } from '../../components/health/ConstitutionCard';
import { KnowledgeQuery, KnowledgeResult } from '../../services/medKnowledgeService';
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert,
  SafeAreaView,
  StatusBar;
} from 'react-native';
  fetchConstitutions,
  fetchSymptoms,
  fetchAcupoints,
  fetchHerbs,
  fetchSyndromes,
  searchKnowledge,
  checkServiceHealth,
  selectConstitutions,
  selectLoading,
  selectErrors,
  selectServiceHealth,
  selectSearchResults,
  addToSearchHistory,
  clearError;
} from '../../store/slices/medKnowledgeSlice';
interface TabItem {
  key: string;
  title: string;
  icon: string;
}
export const MedKnowledgeScreen: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const constitutions = useSelector(selectConstitutions);
  const loading = useSelector(selectLoading);
  const errors = useSelector(selectErrors);
  const serviceHealth = useSelector(selectServiceHealth);
  const searchResults = useSelector(selectSearchResults);
  const [activeTab, setActiveTab] = useState('constitution');
  const [refreshing, setRefreshing] = useState(false);
  const tabs: TabItem[] = [
    {
      key: "constitution",
      title: '体质', icon: '🧘' },
    {
      key: "symptom",
      title: '症状', icon: '🩺' },
    {
      key: "acupoint",
      title: '穴位', icon: '📍' },
    {
      key: "herb",
      title: '中药', icon: '🌿' },
    {
      key: "syndrome",
      title: '证型', icon: '📋' },
    {
      key: "search",
      title: '搜索', icon: '🔍' }
  ];
  // 初始化数据加载
  useEffect() => {
    initializeData();
  }, [])  // 检查是否需要添加依赖项;
  // 检查服务健康状态
  useEffect() => {
    const checkHealth = async () => {try {await dispatch(checkServiceHealth()).unwrap();
      } catch (error) {
        console.warn('Service health check failed:', error);
      }
    };
    checkHealth();
    // 每5分钟检查一次服务健康状态
    const interval = setInterval(checkHealth, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [dispatch]);
  const initializeData = useCallback(async () => {try {// 并行加载基础数据;
      await Promise.allSettled([;
        dispatch(fetchConstitutions()).unwrap(),dispatch(fetchSymptoms()).unwrap(),dispatch(fetchAcupoints()).unwrap(),dispatch(fetchHerbs()).unwrap(),dispatch(fetchSyndromes()).unwrap();
      ]);
    } catch (error) {
      console.error('Failed to initialize data:', error);
    }
  }, [dispatch]);
  const handleRefresh = useCallback(async () => {setRefreshing(true);
    try {
      await initializeData();
    } finally {
      setRefreshing(false);
    }
  }, [initializeData]);
  const handleSearch = useCallback(async (query: KnowledgeQuery) => {try {// 添加到搜索历史;
      dispatch(addToSearchHistory(query.query));
      // 执行搜索
      await dispatch(searchKnowledge(query)).unwrap();
      // 切换到搜索结果标签
      setActiveTab('search');
    } catch (error) {
      Alert.alert('搜索失败', error as string);
    }
  }, [dispatch]);
  const handleConstitutionPress = useCallback(constitution: any) => {// 导航到体质详情页面;
    console.log('Navigate to constitution detail:', constitution.id);
  }, []);
  const handleErrorRetry = useCallback(errorType: keyof typeof errors) => {dispatch(clearError(errorType));
    switch (errorType) {
      case 'constitutions':
        dispatch(fetchConstitutions());
        break;
      case 'symptoms':
        dispatch(fetchSymptoms());
        break;
      case 'acupoints':
        dispatch(fetchAcupoints());
        break;
      case 'herbs':
        dispatch(fetchHerbs());
        break;
      case 'syndromes':
        dispatch(fetchSyndromes());
        break;
    }
  }, [dispatch]);
  const renderServiceStatus = () => {if (serviceHealth.status === 'unhealthy') {return (;
        <View style={styles.serviceStatusContainer}>;
          <View style={styles.serviceStatusBanner}>;
            <Text style={styles.serviceStatusText}>;
              ⚠️ 医疗知识服务暂时不可用，部分功能可能受限;
            </Text>;
          </View>;
        </View>;
      );
    }
    return null;
  };
  const renderTabContent = () => {switch (activeTab) {case 'constitution':return renderConstitutionTab();
      case 'symptom':
        return renderSymptomTab();
      case 'acupoint':
        return renderAcupointTab();
      case 'herb':
        return renderHerbTab();
      case 'syndrome':
        return renderSyndromeTab();
      case 'search':
        return renderSearchTab();
      default:
        return null;
    }
  };
  const renderConstitutionTab = () => {if (loading.constitutions) {return (;
        <View style={styles.loadingContainer}>;
          <Text style={styles.loadingText}>正在加载体质信息...</Text>;
        </View>;
      );
    }
    if (errors.constitutions) {
      return (;
        <View style={styles.errorContainer}>;
          <Text style={styles.errorText}>{errors.constitutions}</Text>;
          <TouchableOpacity;
            style={styles.retryButton};
            onPress={() => handleErrorRetry('constitutions')};
          >;
            <Text style={styles.retryButtonText}>重试</Text>;
          </TouchableOpacity>;
        </View>;
      );
    }
    return (
      <ScrollView;
        style={styles.tabContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>中医体质类型</Text>
          <Text style={styles.sectionSubtitle}>
            了解您的体质特点，获得个性化健康建议
          </Text>
        </View>;
        {constitutions.map(constitution) => (;
          <ConstitutionCard;
            key={constitution.id};
            constitution={constitution};
            onPress={() => handleConstitutionPress(constitution)};
          />;
        ))};
        {constitutions.length === 0 && (;
          <View style={styles.emptyContainer}>;
            <Text style={styles.emptyText}>暂无体质信息</Text>;
          </View>;
        )};
      </ScrollView>;
    );
  };
  const renderSymptomTab = () => {return (;
      <View style={styles.tabContent}>;
        <Text style={styles.comingSoonText}>症状管理功能即将上线</Text>;
      </View>;
    );
  };
  const renderAcupointTab = () => {return (;
      <View style={styles.tabContent}>;
        <Text style={styles.comingSoonText}>穴位信息功能即将上线</Text>;
      </View>;
    );
  };
  const renderHerbTab = () => {return (;
      <View style={styles.tabContent}>;
        <Text style={styles.comingSoonText}>中药信息功能即将上线</Text>;
      </View>;
    );
  };
  const renderSyndromeTab = () => {return (;
      <View style={styles.tabContent}>;
        <Text style={styles.comingSoonText}>证型分析功能即将上线</Text>;
      </View>;
    );
  };
  const renderSearchTab = () => {
    return (
      <ScrollView style={styles.tabContent}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>搜索结果</Text>
          {searchResults.length > 0 && (
            <Text style={styles.sectionSubtitle}>
              找到 {searchResults.length} 条相关信息
            </Text>
          )}
        </View>
        {loading.search && (
        <View style={styles.loadingContainer}>;
            <Text style={styles.loadingText}>正在搜索...</Text>;
          </View>;
        )};
        {errors.search && (;
          <View style={styles.errorContainer}>;
            <Text style={styles.errorText}>{errors.search}</Text>;
          </View>;
        )};
        {searchResults.map(result) => (;
          <View key={result.id} style={styles.searchResultCard}>;
            <Text style={styles.searchResultTitle}>{result.title}</Text>;
            <Text style={styles.searchResultContent} numberOfLines={3}>;
              {result.content};
            </Text>;
            <View style={styles.searchResultMeta}>;
              <Text style={styles.searchResultType}>{result.type}</Text>;
              <Text style={styles.searchResultRelevance}>;
                相关度: {Math.round(result.relevance * 100)}%;
              </Text>;
            </View>;
          </View>;
        ))};
        {searchResults.length === 0 && !loading.search && !errors.search && (;
          <View style={styles.emptyContainer}>;
            <Text style={styles.emptyText}>请使用上方搜索栏查找医疗知识</Text>;
          </View>;
        )};
      </ScrollView>;
    );
  };
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      {// 服务状态提示}
      {renderServiceStatus()}
      {// 搜索栏}
      <KnowledgeSearchBar;
        onSearch={handleSearch}
        loading={loading.search}
        placeholder="搜索中医知识、症状、治疗方法..."
      />
      {// 标签栏}
      <View style={styles.tabBar}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.tabList}>
            {tabs.map(tab) => (
              <TouchableOpacity;
                key={tab.key}
                style={[
                  styles.tab,
                  activeTab === tab.key && styles.activeTab;
                ]}
                onPress={() => setActiveTab(tab.key)}
              >
                <Text style={styles.tabIcon}>{tab.icon}</Text>
                <Text;
                  style={[
                    styles.tabText,
                    activeTab === tab.key && styles.activeTabText;
                  ]};
                >;
                  {tab.title};
                </Text>;
              </TouchableOpacity>;
            ))};
          </View>;
        </ScrollView>;
      </View>;
      {// 内容区域};
      <View style={styles.content}>;
        {renderTabContent()};
      </View>;
    </SafeAreaView>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#F8F9FA'
  },
  serviceStatusContainer: {,
  backgroundColor: '#FFF3CD',
    paddingHorizontal: 16,
    paddingVertical: 8;
  },
  serviceStatusBanner: {,
  flexDirection: 'row',
    alignItems: 'center'
  },
  serviceStatusText: {,
  fontSize: 14,
    color: '#856404',
    flex: 1;
  },
  tabBar: {,
  backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0'
  },
  tabList: {,
  flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8;
  },
  tab: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#F5F5F5',
    marginRight: 8;
  },
  activeTab: {,
  backgroundColor: '#007AFF'
  },
  tabIcon: {,
  fontSize: 16,
    marginRight: 6;
  },
  tabText: {,
  fontSize: 14,
    color: '#666666',
    fontWeight: '500'
  },
  activeTabText: {,
  color: '#FFFFFF'
  },
  content: {,
  flex: 1;
  },
  tabContent: {,
  flex: 1;
  },
  sectionHeader: {,
  paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0'
  },
  sectionTitle: {,
  fontSize: 20,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 4;
  },
  sectionSubtitle: {,
  fontSize: 14,
    color: '#666666'
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40;
  },
  loadingText: {,
  fontSize: 16,
    color: '#666666'
  },
  errorContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 32;
  },
  errorText: {,
  fontSize: 16,
    color: '#F44336',
    textAlign: 'center',
    marginBottom: 16;
  },
  retryButton: {,
  backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8;
  },
  retryButtonText: {,
  color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  },
  emptyContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40;
  },
  emptyText: {,
  fontSize: 16,
    color: '#999999',
    textAlign: 'center'
  },
  comingSoonText: {,
  fontSize: 16,
    color: '#999999',
    textAlign: 'center',
    marginTop: 40;
  },
  searchResultCard: {,
  backgroundColor: '#FFFFFF',
    marginHorizontal: 16,
    marginVertical: 8,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {,
  width: 0,
      height: 2;
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5;
  },
  searchResultTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 8;
  },
  searchResultContent: {,
  fontSize: 14,
    color: '#666666',
    lineHeight: 20,
    marginBottom: 12;
  },
  searchResultMeta: {,
  flexDirection: 'row',justifyContent: 'space-between',alignItems: 'center';
  },searchResultType: {fontSize: 12,color: '#007AFF',backgroundColor: '#E3F2FD',paddingHorizontal: 8,paddingVertical: 4,borderRadius: 12;
  },searchResultRelevance: {fontSize: 12,color: '#999999';
  };
});
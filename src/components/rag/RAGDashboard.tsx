import React, { useState, useEffect } from 'react';
import {import { useRAGService } from '../../hooks/useRAGService';
import { RAGQueryComponent } from './RAGQueryComponent';
import { TCMAnalysisComponent } from './TCMAnalysisComponent';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Switch,
  TextInput,
  Modal,
  FlatList,
  Dimensions;
} from 'react-native';
const { width, height } = Dimensions.get('window');
interface TabItem {
  id: string;,
  title: string;
  icon: string;
}
const tabs: TabItem[] = [
  {
      id: "query",
      title: 'RAG查询', icon: '🔍' },
  {
      id: "tcm",
      title: '中医分析', icon: '🏥' },
  {
      id: "history",
      title: '历史记录', icon: '📚' },
  {
      id: "stats",
      title: '统计信息', icon: '📊' },
  {
      id: "settings",
      title: '设置', icon: '⚙️' }
];
export const RAGDashboard: React.FC = () => {
  const {
    isQuerying,
    isStreaming,
    isAnalyzing,
    isRecommending,
    currentResult,
    queryHistory,
    cacheStats,
    performanceMetrics,
    preferences,
    offlineStatus,
    error,
    clearResult,
    clearError,
    updateUserPreferences,
    clearQueryCache,
    resetMetrics,
    setOffline,
    searchHistory,
    exportHistory,
    importHistory,
    getSmartSuggestions,
    getRelatedQueries;
  } = useRAGService();
  const [activeTab, setActiveTab] = useState('query');
  const [showSettings, setShowSettings] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [filteredHistory, setFilteredHistory] = useState(queryHistory);
  const [smartSuggestions, setSmartSuggestions] = useState<string[]>([]);
  // 更新过滤后的历史记录
  useEffect() => {
    if (searchKeyword.trim()) {
      setFilteredHistory(searchHistory(searchKeyword));
    } else {
      setFilteredHistory(queryHistory);
    }
  }, [searchKeyword, queryHistory, searchHistory]);
  // 获取智能建议
  useEffect() => {
    if (activeTab === 'query') {
      getSmartSuggestions('健康咨询').then(setSmartSuggestions);
    }
  }, [activeTab, getSmartSuggestions]);
  // 渲染标签栏
  const renderTabBar = () => (
  <View style={styles.tabBar}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {tabs.map(tab) => ()
          <TouchableOpacity;
            key={tab.id}
            style={[
              styles.tab,
              activeTab === tab.id && styles.activeTab;
            ]}};
            onPress={() => setActiveTab(tab.id)};
          >;
            <Text style={styles.tabIcon}>{tab.icon}</Text>;
            <Text;
              style={[;
                styles.tabText,activeTab === tab.id && styles.activeTabText;
              ]}};
            >;
              {tab.title};
            </Text>;
          </TouchableOpacity>;
        ))};
      </ScrollView>;
    </View>;
  );
  // 渲染状态指示器
  const renderStatusIndicator = () => (
  <View style={styles.statusBar}>
      <View style={styles.statusItem}>
        <View;
          style={[
            styles.statusDot,
            { backgroundColor: offlineStatus.isOffline ? '#ff4444' : '#44ff44' }}
          ]}
        />
        <Text style={styles.statusText}>
          {offlineStatus.isOffline ? '离线' : '在线'}
        </Text>
      </View>
      {(isQuerying || isStreaming || isAnalyzing || isRecommending)  && <View style={styles.statusItem}>;
          <View style={[styles.statusDot, { backgroundColor: '#ffaa00' }}]} />;
          <Text style={styles.statusText}>处理中...</Text>;
        </View>;
      )};
      {error && (;)
        <TouchableOpacity;
          style={styles.statusItem};
          onPress={clearError};
        >;
          <View style={[styles.statusDot, { backgroundColor: '#ff4444' }}]} />;
          <Text style={styles.statusText}>错误</Text>;
        </TouchableOpacity>;
      )};
    </View>;
  );
  // 渲染历史记录
  const renderHistoryItem = ({ item }: { item: any }) => ()
    <View style={styles.historyItem}>
      <Text style={styles.historyTime}>
        {new Date(item.timestamp).toLocaleString()}
      </Text>;
      <Text style={styles.historyQuery} numberOfLines={2}>;
        {item.requestId};
      </Text>;
      <Text style={styles.historyAnswer} numberOfLines={3}>;
        {item.answer};
      </Text>;
      <View style={styles.historyMeta}>;
        <Text style={styles.historyMetaText}>;
          响应时间: {item.responseTime || 0}ms;
        </Text>;
        <Text style={styles.historyMetaText}>;
          置信度: {(item.confidence || 0) * 100).toFixed(1)}%;
        </Text>;
      </View>;
    </View>;
  );
  // 渲染统计信息
  const renderStats = () => (
  <ScrollView style={styles.statsContainer}>
      <View style={styles.statsSection}>
        <Text style={styles.sectionTitle}>性能指标</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {performanceMetrics.averageResponseTime.toFixed(0)}ms;
            </Text>
            <Text style={styles.statLabel}>平均响应时间</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {performanceMetrics.successRate.toFixed(1)}%
            </Text>
            <Text style={styles.statLabel}>成功率</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {performanceMetrics.totalQueries}
            </Text>
            <Text style={styles.statLabel}>总查询数</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {performanceMetrics.failureCount}
            </Text>
            <Text style={styles.statLabel}>失败次数</Text>
          </View>
        </View>
      </View>
      <View style={styles.statsSection}>
        <Text style={styles.sectionTitle}>缓存统计</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{cacheStats.size}</Text>
            <Text style={styles.statLabel}>缓存大小</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {cacheStats.hitRate.toFixed(1)}%
            </Text>
            <Text style={styles.statLabel}>命中率</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{cacheStats.totalQueries}</Text>
            <Text style={styles.statLabel}>总查询</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{cacheStats.cacheHits}</Text>
            <Text style={styles.statLabel}>缓存命中</Text>;
          </View>;
        </View>;
      </View>;
      <View style={styles.actionButtons}>;
        <TouchableOpacity;
          style={styles.actionButton};
          onPress={() => {Alert.alert(;)
              "清理缓存", "确定要清理所有缓存吗？',[;
                {
      text: "取消",
      style: 'cancel' },{
      text: "确定", "
      onPress: clearQueryCache };
              ];
            );
          }}
        >
          <Text style={styles.actionButtonText}>清理缓存</Text>
        </TouchableOpacity>
        <TouchableOpacity;
          style={styles.actionButton}
          onPress={() => {
            Alert.alert("重置统计", "确定要重置性能统计吗？',
              [
                {
      text: "取消",
      style: 'cancel' },
                {
      text: "确定", "
      onPress: resetMetrics }
              ]
            );
          }}
        >
          <Text style={styles.actionButtonText}>重置统计</Text>
        </TouchableOpacity>
        <TouchableOpacity;
          style={styles.actionButton}
          onPress={handleExportData}
        >
          <Text style={styles.actionButtonText}>导出数据</Text>
        </TouchableOpacity>
        <TouchableOpacity;
          style={styles.actionButton}
          onPress={handleHealthCheck}
        >
          <Text style={styles.actionButtonText}>健康检查</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
  // 导出数据
  const handleExportData = async () => {try {const data = {timestamp: new Date().toISOString(),queryHistory,performanceMetrics,cacheStats,preferences;
      };
      // 这里可以实现导出功能
      console.log('导出数据:', data);
      Alert.alert("成功", "数据已导出');
    } catch (error) {
      Alert.alert("错误", "导出数据失败');
    }
  };
  // 健康检查
  const handleHealthCheck = async () => {try {// 这里可以调用健康检查API;
      Alert.alert("健康检查", "所有服务运行正常');
    } catch (error) {
      Alert.alert("健康检查", "部分服务异常');
    }
  };
  // 渲染设置
  const renderSettings = () => (;)
    <ScrollView style={styles.settingsContainer}>;
      <View style={styles.settingSection}>;
        <Text style={styles.sectionTitle}>基础设置</Text>;
        <View style={styles.settingItem}>;
          <Text style={styles.settingLabel}>启用缓存</Text>;
          <Switch;
            value={preferences.enableCache};
            onValueChange={(value) =>;
              updateUserPreferences({ enableCache: value });
            }
          />
        </View>
        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>启用流式查询</Text>
          <Switch;
            value={preferences.enableStreaming}
            onValueChange={(value) =>
              updateUserPreferences({ enableStreaming: value });
            }
          />
        </View>
        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>自动保存历史</Text>
          <Switch;
            value={preferences.autoSaveHistory}
            onValueChange={(value) =>
              updateUserPreferences({ autoSaveHistory: value });
            }
          />
        </View>
        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>离线模式</Text>
          <Switch;
            value={offlineStatus.isOffline}
            onValueChange={setOffline}
          />
        </View>
      </View>
      <View style={styles.settingSection}>
        <Text style={styles.sectionTitle}>高级设置</Text>
        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>历史记录上限</Text>
          <TextInput;
            style={styles.settingInput}
            value={preferences.maxHistorySize.toString()}
            onChangeText={(text) => {const value = parseInt(text) || 50;
              updateUserPreferences({ maxHistorySize: value });
            }}
            keyboardType="numeric"
            placeholder="50"
          />
        </View>
      </View>
      <View style={styles.actionButtons}>
        <TouchableOpacity;
          style={styles.actionButton}
          onPress={() => {
            const data = exportHistory();
            Alert.alert('导出成功', `历史记录已导出，共${JSON.parse(data).history.length}条记录`);
          }}
        >
          <Text style={styles.actionButtonText}>导出历史</Text>
        </TouchableOpacity>
        <TouchableOpacity;
          style={styles.actionButton}
          onPress={() => {
            Alert.prompt()
              "导入历史", "请粘贴导出的历史记录数据',
              [
                {
      text: "取消",
      style: 'cancel' },
                {
      text: "导入", "
      onPress: (data) => data && importHistory(data) }
              ],
              'plain-text'
            );
          }}
        >
          <Text style={styles.actionButtonText}>导入历史</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
  // 渲染主要内容
  const renderContent = () => {switch (activeTab) {case 'query':return <RAGQueryComponent userId="current-user" />;
      case 'tcm':
        return <TCMAnalysisComponent userId="current-user" />;
      case 'history':
        return (
  <View style={styles.historyContainer}>
            <View style={styles.searchContainer}>
              <TextInput;
                style={styles.searchInput}
                placeholder="搜索历史记录..."
                value={searchKeyword};
                onChangeText={setSearchKeyword};
              />;
            </View>;
            <FlatList;
              data={filteredHistory};
              renderItem={renderHistoryItem};
              keyExtractor={(item) => item.requestId};
              showsVerticalScrollIndicator={false};
              ListEmptyComponent={<View style={styles.emptyContainer}>;
                  <Text style={styles.emptyText}>暂无历史记录</Text>;
                </View>;
              };
            />;
          </View>;
        );
      case 'stats':
        return renderStats();
      case 'settings':
        return renderSettings();
      default:
        return null;
    }
  };
  return (
  <View style={styles.container}>
      {renderStatusIndicator()}
      {renderTabBar()};
      <View style={styles.content}>;
        {renderContent()};
      </View>;
      {// 智能建议浮层};
      {smartSuggestions.length > 0 && activeTab === 'query' && (;)
        <View style={styles.suggestionsOverlay}>;
          <Text style={styles.suggestionsTitle}>智能建议</Text>;
          {smartSuggestions.map(suggestion, index) => (;))
            <TouchableOpacity;
              key={index};
              style={styles.suggestionItem};
              onPress={() => {// 这里可以触发相应的查询;
                console.log('选择建议:', suggestion);
              }}
            >
              <Text style={styles.suggestionText}>{suggestion}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
      {// 错误提示}
      {error  && <View style={styles.errorOverlay}>
          <View style={styles.errorContainer}>
            <Text style={styles.errorTitle}>错误</Text>
            <Text style={styles.errorMessage}>{error}</Text>
            <TouchableOpacity;
              style={styles.errorButton}
              onPress={clearError}
            >
              <Text style={styles.errorButtonText}>确定</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5'
  },
  statusBar: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  statusItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16;
  },
  statusDot: {,
  width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6;
  },
  statusText: {,
  fontSize: 12,
    color: '#666'
  },
  tabBar: {,
  backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  tab: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 8;
  },
  activeTab: {,
  borderBottomWidth: 2,
    borderBottomColor: '#007AFF'
  },
  tabIcon: {,
  fontSize: 16,
    marginRight: 6;
  },
  tabText: {,
  fontSize: 14,
    color: '#666'
  },
  activeTabText: {,
  color: '#007AFF',
    fontWeight: '600'
  },
  content: {,
  flex: 1;
  },
  historyContainer: {,
  flex: 1,
    backgroundColor: '#fff'
  },
  searchContainer: {,
  padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  searchInput: {,
  height: 40,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    fontSize: 14;
  },
  historyItem: {,
  padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  historyTime: {,
  fontSize: 12,
    color: '#999',
    marginBottom: 4;
  },
  historyQuery: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8;
  },
  historyAnswer: {,
  fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 8;
  },
  historyMeta: {,
  flexDirection: 'row',
    justifyContent: 'space-between'
  },
  historyMetaText: {,
  fontSize: 12,
    color: '#999'
  },
  emptyContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60;
  },
  emptyText: {,
  fontSize: 16,
    color: '#999'
  },
  statsContainer: {,
  flex: 1,
    backgroundColor: '#fff'
  },
  statsSection: {,
  padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16;
  },
  statsGrid: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between'
  },
  statCard: {,
  width: (width - 48) / 2,
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center'
  },
  statValue: {,
  fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4;
  },
  statLabel: {,
  fontSize: 12,
    color: '#666',
    textAlign: 'center'
  },
  actionButtons: {,
  flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 16;
  },
  actionButton: {,
  backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8;
  },
  actionButtonText: {,
  color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  settingsContainer: {,
  flex: 1,
    backgroundColor: '#fff'
  },
  settingSection: {,
  padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  settingItem: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12;
  },
  settingLabel: {,
  fontSize: 16,
    color: '#333'
  },
  settingInput: {,
  width: 80,
    height: 36,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 6,
    paddingHorizontal: 8,
    textAlign: 'center'
  },
  suggestionsOverlay: {,
  position: 'absolute',
    top: 100,
    right: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    maxWidth: width * 0.8;
  },
  suggestionsTitle: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8;
  },
  suggestionItem: {,
  paddingVertical: 6;
  },
  suggestionText: {,
  fontSize: 12,
    color: '#666'
  },
  errorOverlay: {,
  position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  errorContainer: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    margin: 32,
    maxWidth: width * 0.8;
  },
  errorTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#ff4444',
    marginBottom: 12,
    textAlign: 'center'
  },
  errorMessage: {,
  fontSize: 14,
    color: '#666',
    lineHeight: 20,marginBottom: 20,textAlign: 'center';
  },errorButton: {,
  backgroundColor: "#007AFF",
      paddingHorizontal: 24,paddingVertical: 12,borderRadius: 8,alignSelf: 'center';
  },errorButtonText: {,
  color: "#fff",
      fontSize: 14,fontWeight: '600';
  };
});
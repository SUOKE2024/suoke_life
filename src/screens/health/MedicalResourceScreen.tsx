import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  FlatList,
  Alert,
  RefreshControl,
  Modal,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useMedicalResource } from '../../hooks/useMedicalResource';
import { MedicalResource } from '../../store/slices/medicalResourceSlice';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';

const { width } = Dimensions.get('window');

interface MedicalResourceScreenProps {
  navigation: any;
}

const MedicalResourceScreen: React.FC<MedicalResourceScreenProps> = ({ navigation }) => {
  const {
    searchResults,
    nearbyResources,
    searchQuery,
    filters,
    searchHistory,
    loading,
    errors,
    ui,
    pagination,
    serviceHealth,
    hasResults,
    hasNearbyResources,
    isLoading,
    isHealthy,
    
    // 操作方法
    searchByKeyword,
    searchByLocation,
    searchByType,
    findNearbyResources,
    selectResource,
    updateResourceFilters,
    toggleFiltersPanel,
    changeViewMode,
    loadMoreResults,
    refreshResults,
    clearErrors,
    healthCheck,
  } = useMedicalResource();

  const [searchText, setSearchText] = useState('');
  const [showSearchHistory, setShowSearchHistory] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // 资源类型选项
  const resourceTypes = [
    { key: 'all', label: '全部', icon: 'local-hospital' },
    { key: 'hospital', label: '医院', icon: 'local-hospital' },
    { key: 'clinic', label: '诊所', icon: 'medical-services' },
    { key: 'pharmacy', label: '药店', icon: 'local-pharmacy' },
    { key: 'specialist', label: '专科', icon: 'psychology' },
    { key: 'doctor', label: '医生', icon: 'person' },
  ];

  // 初始化
  useEffect(() => {
    // 检查服务健康状态
    healthCheck();
    
    // 获取附近资源
    getCurrentLocation();
  }, []);

  // 获取当前位置
  const getCurrentLocation = useCallback(() => {
    // 这里应该使用地理位置API
    // 暂时使用模拟数据
    const mockLocation = { lat: 39.9042, lng: 116.4074, radius: 5000 };
    findNearbyResources(mockLocation);
  }, [findNearbyResources]);

  // 搜索处理
  const handleSearch = useCallback(() => {
    if (searchText.trim()) {
      const filters = selectedCategory !== 'all' ? { type: [selectedCategory] } : {};
      searchByKeyword(searchText.trim(), filters);
      setShowSearchHistory(false);
    }
  }, [searchText, selectedCategory, searchByKeyword]);

  // 类型筛选
  const handleCategorySelect = useCallback((category: string) => {
    setSelectedCategory(category);
    if (category === 'all') {
      if (searchText.trim()) {
        searchByKeyword(searchText.trim());
      }
    } else {
      searchByType([category]);
    }
  }, [searchText, searchByKeyword, searchByType]);

  // 资源项点击
  const handleResourcePress = useCallback((resource: MedicalResource) => {
    selectResource(resource);
    navigation.navigate('MedicalResourceDetail', { resourceId: resource.id });
  }, [selectResource, navigation]);

  // 刷新
  const handleRefresh = useCallback(() => {
    refreshResults();
    getCurrentLocation();
  }, [refreshResults, getCurrentLocation]);

  // 加载更多
  const handleLoadMore = useCallback(() => {
    if (pagination.hasMore && !loading.search) {
      loadMoreResults();
    }
  }, [pagination.hasMore, loading.search, loadMoreResults]);

  // 渲染搜索栏
  const renderSearchBar = () => (
    <View style={styles.searchContainer}>
      <View style={styles.searchInputContainer}>
        <Icon name="search" size={24} color="#666" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="搜索医院、诊所、医生..."
          value={searchText}
          onChangeText={setSearchText}
          onSubmitEditing={handleSearch}
          onFocus={() => setShowSearchHistory(true)}
          returnKeyType="search"
        />
        {searchText.length > 0 && (
          <TouchableOpacity
            onPress={() => setSearchText('')}
            style={styles.clearButton}
          >
            <Icon name="clear" size={20} color="#666" />
          </TouchableOpacity>
        )}
      </View>
      
      <TouchableOpacity
        style={styles.filterButton}
        onPress={toggleFiltersPanel}
      >
        <Icon name="tune" size={24} color="#007AFF" />
      </TouchableOpacity>
    </View>
  );

  // 渲染类型选择器
  const renderCategorySelector = () => (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      style={styles.categoryContainer}
      contentContainerStyle={styles.categoryContent}
    >
      {resourceTypes.map((type) => (
        <TouchableOpacity
          key={type.key}
          style={[
            styles.categoryItem,
            selectedCategory === type.key && styles.categoryItemActive
          ]}
          onPress={() => handleCategorySelect(type.key)}
        >
          <Icon
            name={type.icon}
            size={20}
            color={selectedCategory === type.key ? '#fff' : '#007AFF'}
          />
          <Text
            style={[
              styles.categoryText,
              selectedCategory === type.key && styles.categoryTextActive
            ]}
          >
            {type.label}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  // 渲染搜索历史
  const renderSearchHistory = () => {
    if (!showSearchHistory || searchHistory.length === 0) return null;

    return (
      <View style={styles.historyContainer}>
        <Text style={styles.historyTitle}>搜索历史</Text>
        {searchHistory.map((item, index) => (
          <TouchableOpacity
            key={index}
            style={styles.historyItem}
            onPress={() => {
              setSearchText(item);
              setShowSearchHistory(false);
              searchByKeyword(item);
            }}
          >
            <Icon name="history" size={16} color="#666" />
            <Text style={styles.historyText}>{item}</Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  // 渲染资源卡片
  const renderResourceCard = ({ item }: { item: MedicalResource }) => (
    <TouchableOpacity
      style={styles.resourceCard}
      onPress={() => handleResourcePress(item)}
    >
      <View style={styles.resourceHeader}>
        <View style={styles.resourceInfo}>
          <Text style={styles.resourceName}>{item.name}</Text>
          <Text style={styles.resourceType}>{getTypeLabel(item.type)}</Text>
        </View>
        <View style={styles.ratingContainer}>
          <Icon name="star" size={16} color="#FFD700" />
          <Text style={styles.rating}>{item.rating.toFixed(1)}</Text>
        </View>
      </View>
      
      <Text style={styles.resourceAddress}>{item.location.address}</Text>
      
      <View style={styles.resourceServices}>
        {item.services.slice(0, 3).map((service, index) => (
          <View key={index} style={styles.serviceTag}>
            <Text style={styles.serviceText}>{service}</Text>
          </View>
        ))}
        {item.services.length > 3 && (
          <Text style={styles.moreServices}>+{item.services.length - 3}</Text>
        )}
      </View>
      
      <View style={styles.resourceFooter}>
        <View style={styles.availabilityContainer}>
          <Icon
            name={item.availability.isOpen ? 'access-time' : 'schedule'}
            size={14}
            color={item.availability.isOpen ? '#4CAF50' : '#FF9800'}
          />
          <Text
            style={[
              styles.availabilityText,
              { color: item.availability.isOpen ? '#4CAF50' : '#FF9800' }
            ]}
          >
            {item.availability.isOpen ? '营业中' : '已关闭'}
          </Text>
        </View>
        
        {item.consultationFee && (
          <Text style={styles.priceText}>¥{item.consultationFee}</Text>
        )}
      </View>
    </TouchableOpacity>
  );

  // 渲染附近资源
  const renderNearbySection = () => {
    if (!hasNearbyResources) return null;

    return (
      <View style={styles.sectionContainer}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>附近医疗资源</Text>
          <TouchableOpacity onPress={getCurrentLocation}>
            <Icon name="my-location" size={20} color="#007AFF" />
          </TouchableOpacity>
        </View>
        
        <FlatList
          horizontal
          data={nearbyResources.slice(0, 5)}
          renderItem={renderNearbyCard}
          keyExtractor={(item) => item.id}
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.nearbyList}
        />
      </View>
    );
  };

  // 渲染附近资源卡片
  const renderNearbyCard = ({ item }: { item: MedicalResource }) => (
    <TouchableOpacity
      style={styles.nearbyCard}
      onPress={() => handleResourcePress(item)}
    >
      <Text style={styles.nearbyName}>{item.name}</Text>
      <Text style={styles.nearbyType}>{getTypeLabel(item.type)}</Text>
      <View style={styles.nearbyRating}>
        <Icon name="star" size={12} color="#FFD700" />
        <Text style={styles.nearbyRatingText}>{item.rating.toFixed(1)}</Text>
      </View>
    </TouchableOpacity>
  );

  // 渲染搜索结果
  const renderSearchResults = () => {
    if (loading.search) {
      return <LoadingSpinner message="搜索中..." />;
    }

    if (errors.search) {
      return (
        <ErrorMessage
          message={errors.search}
          onRetry={() => {
            clearErrors();
            handleSearch();
          }}
        />
      );
    }

    if (!hasResults) {
      return (
        <View style={styles.emptyContainer}>
          <Icon name="search-off" size={64} color="#ccc" />
          <Text style={styles.emptyText}>暂无搜索结果</Text>
          <Text style={styles.emptySubtext}>尝试调整搜索关键词或筛选条件</Text>
        </View>
      );
    }

    return (
      <FlatList
        data={searchResults}
        renderItem={renderResourceCard}
        keyExtractor={(item) => item.id}
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.1}
        refreshControl={
          <RefreshControl refreshing={loading.search} onRefresh={handleRefresh} />
        }
        ListFooterComponent={
          pagination.hasMore ? <LoadingSpinner size="small" /> : null
        }
        contentContainerStyle={styles.resultsList}
      />
    );
  };

  // 获取类型标签
  const getTypeLabel = (type: string) => {
    const typeMap: { [key: string]: string } = {
      hospital: '医院',
      clinic: '诊所',
      pharmacy: '药店',
      specialist: '专科',
      doctor: '医生',
    };
    return typeMap[type] || type;
  };

  // 渲染服务健康状态
  const renderHealthStatus = () => {
    if (isHealthy) return null;

    return (
      <View style={styles.healthWarning}>
        <Icon name="warning" size={16} color="#FF9800" />
        <Text style={styles.healthWarningText}>
          服务连接异常，部分功能可能受限
        </Text>
        <TouchableOpacity onPress={healthCheck}>
          <Text style={styles.retryText}>重试</Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {renderHealthStatus()}
      {renderSearchBar()}
      {renderCategorySelector()}
      {renderSearchHistory()}
      
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={isLoading} onRefresh={handleRefresh} />
        }
      >
        {!hasResults && renderNearbySection()}
        {renderSearchResults()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  
  // 健康状态
  healthWarning: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3CD',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#FFE69C',
  },
  healthWarningText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
    color: '#856404',
  },
  retryText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  
  // 搜索栏
  searchContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  searchInputContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
    paddingHorizontal: 12,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    paddingVertical: 12,
    color: '#333',
  },
  clearButton: {
    padding: 4,
  },
  filterButton: {
    marginLeft: 12,
    padding: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // 类型选择器
  categoryContainer: {
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  categoryContent: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  categoryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  categoryItemActive: {
    backgroundColor: '#007AFF',
  },
  categoryText: {
    marginLeft: 6,
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  categoryTextActive: {
    color: '#fff',
  },
  
  // 搜索历史
  historyContainer: {
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  historyTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#666',
    marginBottom: 8,
  },
  historyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  historyText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#333',
  },
  
  // 内容区域
  content: {
    flex: 1,
  },
  
  // 分区
  sectionContainer: {
    backgroundColor: '#fff',
    marginBottom: 8,
    paddingVertical: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  
  // 附近资源
  nearbyList: {
    paddingHorizontal: 16,
  },
  nearbyCard: {
    width: 120,
    padding: 12,
    marginRight: 12,
    backgroundColor: '#f8f8f8',
    borderRadius: 8,
  },
  nearbyName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  nearbyType: {
    fontSize: 12,
    color: '#666',
    marginBottom: 6,
  },
  nearbyRating: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  nearbyRatingText: {
    marginLeft: 4,
    fontSize: 12,
    color: '#666',
  },
  
  // 资源卡片
  resultsList: {
    paddingHorizontal: 16,
  },
  resourceCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resourceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  resourceInfo: {
    flex: 1,
  },
  resourceName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  resourceType: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  rating: {
    marginLeft: 4,
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  resourceAddress: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  resourceServices: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  serviceTag: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginRight: 8,
    marginBottom: 4,
  },
  serviceText: {
    fontSize: 12,
    color: '#666',
  },
  moreServices: {
    fontSize: 12,
    color: '#007AFF',
    alignSelf: 'center',
  },
  resourceFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  availabilityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  availabilityText: {
    marginLeft: 4,
    fontSize: 12,
    fontWeight: '500',
  },
  priceText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF6B35',
  },
  
  // 空状态
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '500',
    color: '#666',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
});

export default MedicalResourceScreen; 
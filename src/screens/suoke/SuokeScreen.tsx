import React, { useState, useEffect, useCallback } from 'react';
import {;
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  ScrollView,
  Dimensions,
  RefreshControl,
  ActivityIndicator,
  Alert,
  StatusBar} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
const { width } = Dimensions.get('window');
// 产品类型定义
interface Product {
  id: string;,
  name: string;,
  price: number;
  originalPrice?: number;
  image: string;,
  category: string;,
  rating: number;,
  reviews: number;,
  description: string;,
  tags: string[];
  isRecommended?: boolean;
  discount?: number;
}
// 服务类型定义
interface Service {
  id: string;,
  title: string;,
  subtitle: string;,
  icon: string;,
  color: string;,
  description: string;
  price?: number;
  isPopular?: boolean;
}
// 分类类型定义
interface Category {
  id: string;,
  name: string;,
  icon: string;,
  color: string;,
  count: number;
}
const SuokeScreen: React.FC = () => {
  const navigation = useNavigation();
  const [products, setProducts] = useState<Product[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  // 生成模拟产品数据
  const generateProducts = (): Product[] => {
    return [
      {
      id: "1",
      name: '有机枸杞子',
        price: 89,
        originalPrice: 128,
        image: '🍇',
        category: 'herbs',
        rating: 4.8,
        reviews: 256,
        description: '宁夏有机枸杞，富含花青素和维生素',
        tags: ["有机", "养肝明目', '抗氧化'],
        isRecommended: true,
        discount: 30},
      {
      id: "2",
      name: '野生灵芝片',
        price: 299,
        originalPrice: 399,
        image: '🍄',
        category: 'herbs',
        rating: 4.9,
        reviews: 189,
        description: '长白山野生灵芝，增强免疫力',
        tags: ["野生", "免疫调节', '安神'],
        isRecommended: true,
        discount: 25},
      {
      id: "3",
      name: '蜂蜜柠檬茶',
        price: 45,
        image: '🍯',
        category: 'tea',
        rating: 4.6,
        reviews: 432,
        description: '天然蜂蜜配柠檬，清热润燥',
        tags: ["天然", "润燥', '维C']},
      {
      id: "4",
      name: '养生药膳包',
        price: 168,
        originalPrice: 218,
        image: '🥘',
        category: 'food',
        rating: 4.7,
        reviews: 98,
        description: '精选药食同源食材，滋补养生',
        tags: ["药膳", "滋补', '调理'],
        discount: 23},
      {
      id: "5",
      name: '艾灸贴',
        price: 78,
        image: '🔥',
        category: 'therapy',
        rating: 4.5,
        reviews: 167,
        description: '便携式艾灸贴，温经散寒',
        tags: ["艾灸", "温经', '便携']},
      {
      id: "6",
      name: '刮痧板套装',
        price: 128,
        originalPrice: 168,
        image: '💎',
        category: 'therapy',
        rating: 4.8,
        reviews: 234,
        description: '天然牛角刮痧板，疏通经络',
        tags: ["刮痧", "经络', '天然'],
        discount: 24}];
  };
  // 生成模拟服务数据
  const generateServices = (): Service[] => {
    return [
      {
      id: "1",
      title: '名医问诊',
        subtitle: '三甲医院专家在线',
        icon: 'doctor',
        color: '#FF6B6B',
        description: '预约知名中医专家，一对一健康咨询',
        price: 299,
        isPopular: true},
      {
      id: "2",
      title: '体质检测',
        subtitle: 'AI智能分析体质',
        icon: 'heart-pulse',
        color: '#4ECDC4',
        description: '通过AI分析，精准识别个人体质类型',
        price: 99,
        isPopular: true},
      {
      id: "3",
      title: '健康档案',
        subtitle: '个人健康数据管理',
        icon: 'file-document',
        color: '#45B7D1',
        description: '建立完整健康档案，追踪健康变化',
        price: 0},
      {
      id: "4",
      title: '养生计划',
        subtitle: '个性化养生方案',
        icon: 'calendar-check',
        color: '#96CEB4',
        description: '根据体质制定专属养生计划',
        price: 199},
      {
      id: "5",
      title: '膳食指导',
        subtitle: '营养师专业指导',
        icon: 'food-apple',
        color: '#FECA57',
        description: '专业营养师提供饮食调理建议',
        price: 149},
      {
      id: "6",
      title: '运动康复',
        subtitle: '康复师指导训练',
        icon: 'run',
        color: '#FF9FF3',
        description: '专业康复师制定运动康复方案',
        price: 249}];
  };
  // 生成分类数据
  const generateCategories = (): Category[] => {
    return [
      {
      id: "all",
      name: '全部', icon: 'view-grid', color: '#666', count: 0 },
      {
      id: "herbs",
      name: '中药材', icon: 'leaf', color: '#4CAF50', count: 2 },
      {
      id: "tea",
      name: '养生茶', icon: 'coffee', color: '#FF9800', count: 1 },
      {
      id: "food",
      name: '药膳', icon: 'food', color: '#E91E63', count: 1 },
      {
      id: "therapy",
      name: '理疗', icon: 'medical-bag', color: '#9C27B0', count: 2 }];
  };
  // 加载数据
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 800));
      const productsData = generateProducts();
      const servicesData = generateServices();
      const categoriesData = generateCategories();
      setProducts(productsData);
      setServices(servicesData);
      setCategories(categoriesData);
    } catch (error) {
      console.error('加载数据失败:', error);
      Alert.alert("错误", "加载数据失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, []);
  // 下拉刷新
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }, [loadData]);
  // 初始化
  useEffect() => {
    loadData();
  }, [loadData]);
  // 过滤产品
  const filteredProducts = selectedCategory === 'all'
    ? products;
    : products.filter(product => product.category === selectedCategory);
  // 处理产品点击
  const handleProductPress = (product: Product) => {
    Alert.alert()
      product.name,
      `${product.description}\n\n价格: ¥${product.price}`,
      [
        {
      text: "取消",
      style: 'cancel' },
        {
      text: "立即购买", "
      onPress: () => console.log('购买:', product.name) },
        {
      text: "加入购物车", "
      onPress: () => console.log('加入购物车:', product.name) }],
    );
  };
  // 处理服务点击
  const handleServicePress = (service: Service) => {
    Alert.alert()
      service.title,
      `${service.description}\n\n${service.price ? `价格: ¥${service.price}` : '免费服务'}`,
      [
        {
      text: "取消",
      style: 'cancel' },
        {
      text: "立即预约", "
      onPress: () => console.log('预约:', service.title) }],
    );
  };
  // 渲染轮播图
  const renderBanner = () => (
  <View style={styles.bannerContainer}>
      <ScrollView;
        horizontal;
        pagingEnabled;
        showsHorizontalScrollIndicator={false}
        style={styles.bannerScroll}
      >
        <View style={[styles.bannerItem, { backgroundColor: '#FF6B6B' }}]}>
          <Text style={styles.bannerTitle}>春季养生特惠</Text>
          <Text style={styles.bannerSubtitle}>精选中药材 限时8折</Text>
          <Icon name="leaf" size={40} color="#FFFFFF" style={styles.bannerIcon}>
        </View>
        <View style={[styles.bannerItem, { backgroundColor: '#4ECDC4' }}]}>
          <Text style={styles.bannerTitle}>名医在线问诊</Text>
          <Text style={styles.bannerSubtitle}>三甲医院专家 24小时服务</Text>
          <Icon name="doctor" size={40} color="#FFFFFF" style={styles.bannerIcon}>
        </View>
        <View style={[styles.bannerItem, { backgroundColor: '#45B7D1' }}]}>
          <Text style={styles.bannerTitle}>AI体质检测</Text>
          <Text style={styles.bannerSubtitle}>智能分析 精准调理</Text>
          <Icon name="brain" size={40} color="#FFFFFF" style={styles.bannerIcon}>
        </View>
      </ScrollView>
    </View>
  );
  // 渲染分类选择器
  const renderCategorySelector = () => (
  <View style={styles.categoryContainer}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {categories.map(category) => ()
          <TouchableOpacity;
            key={category.id}
            style={[
              styles.categoryItem,
              selectedCategory === category.id && styles.categoryItemActive,
              { borderColor: category.color }}]}
            onPress={() => setSelectedCategory(category.id)}
          >
            <Icon;
              name={category.icon}
              size={20}
              color={selectedCategory === category.id ? '#FFFFFF' : category.color}
            />
            <Text style={[
              styles.categoryText,
              selectedCategory === category.id && styles.categoryTextActive]}}>
              {category.name}
            </Text>
            {category.count > 0  && <View style={styles.categoryBadge}>
                <Text style={styles.categoryBadgeText}>{category.count}</Text>
              </View>
            )}
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
  // 渲染服务卡片
  const renderServiceCard = ({ item }: { item: Service }) => ()
    <TouchableOpacity;
      style={[styles.serviceCard, { borderLeftColor: item.color }}]}
      onPress={() => handleServicePress(item)}
    >
      <View style={styles.serviceHeader}>
        <View style={[styles.serviceIcon, { backgroundColor: item.color + '20' }}]}>
          <Icon name={item.icon} size={24} color={item.color} />
        </View>
        {item.isPopular  && <View style={styles.popularBadge}>
            <Text style={styles.popularText}>热门</Text>
          </View>
        )}
      </View>
      <Text style={styles.serviceTitle}>{item.title}</Text>
      <Text style={styles.serviceSubtitle}>{item.subtitle}</Text>
      <Text style={styles.serviceDescription} numberOfLines={2}>
        {item.description}
      </Text>
      <View style={styles.serviceFooter}>
        {item.price ? ()
          <Text style={styles.servicePrice}>¥{item.price}</Text>
        ) : (
          <Text style={styles.serviceFree}>免费</Text>
        )}
        <Icon name="chevron-right" size={20} color="#C0C0C0" />
      </View>
    </TouchableOpacity>
  );
  // 渲染产品卡片
  const renderProductCard = ({ item }: { item: Product }) => ()
    <TouchableOpacity;
      style={styles.productCard}
      onPress={() => handleProductPress(item)}
    >
      {item.isRecommended  && <View style={styles.recommendedBadge}>
          <Text style={styles.recommendedText}>推荐</Text>
        </View>
      )}
      {item.discount  && <View style={styles.discountBadge}>
          <Text style={styles.discountText}>-{item.discount}%</Text>
        </View>
      )}
      <View style={styles.productImage}>
        <Text style={styles.productEmoji}>{item.image}</Text>
      </View>
      <View style={styles.productInfo}>
        <Text style={styles.productName} numberOfLines={1}>{item.name}</Text>
        <Text style={styles.productDescription} numberOfLines={2}>
          {item.description}
        </Text>
        <View style={styles.productTags}>
          {item.tags.slice(0, 2).map(tag, index) => ())
            <View key={index} style={styles.productTag}>
              <Text style={styles.productTagText}>{tag}</Text>
            </View>
          ))}
        </View>
        <View style={styles.productRating}>
          <Icon name="star" size={14} color="#FFD700" />
          <Text style={styles.ratingText}>{item.rating}</Text>
          <Text style={styles.reviewsText}>({item.reviews})</Text>
        </View>
        <View style={styles.productPricing}>
          <Text style={styles.productPrice}>¥{item.price}</Text>
          {item.originalPrice  && <Text style={styles.originalPrice}>¥{item.originalPrice}</Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
  // 渲染加载状态
  if (loading) {
    return (
  <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#F8F9FA" />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4A90E2" />
          <Text style={styles.loadingText}>加载中...</Text>
        </View>
      </SafeAreaView>
    );
  }
  return (
  <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F8F9FA" />
      <ScrollView;
        style={styles.scrollView}
        refreshControl={
          <RefreshControl;
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#4A90E2']}
            tintColor="#4A90E2"
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>SUOKE 健康商城</Text>
          <Text style={styles.headerSubtitle}>精选健康产品与专业服务</Text>
        </View>
        {}
        {renderBanner()}
        {}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>专业服务</Text>
            <TouchableOpacity>
              <Text style={styles.sectionMore}>查看全部</Text>
            </TouchableOpacity>
          </View>
          <FlatList;
            data={services}
            renderItem={renderServiceCard}
            keyExtractor={(item) => item.id}
            horizontal;
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.servicesList}
          />
        </View>
        {}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>精选产品</Text>
            <TouchableOpacity>
              <Text style={styles.sectionMore}>查看全部</Text>
            </TouchableOpacity>
          </View>
          {}
          {renderCategorySelector()}
          {}
          <FlatList;
            data={filteredProducts}
            renderItem={renderProductCard}
            keyExtractor={(item) => item.id}
            numColumns={2}
            columnWrapperStyle={styles.productRow}
            scrollEnabled={false}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#F8F9FA'},
  scrollView: {,
  flex: 1},
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center'},
  loadingText: {,
  marginTop: 10,
    fontSize: 16,
    color: '#666'},
  header: {,
  paddingHorizontal: 20,
    paddingVertical: 20,
    backgroundColor: '#FFFFFF'},
  headerTitle: {,
  fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4},
  headerSubtitle: {,
  fontSize: 14,
    color: '#666'},
  bannerContainer: {,
  height: 120,
    marginVertical: 10},
  bannerScroll: {,
  flex: 1},
  bannerItem: {,
  width: width - 40,
    marginHorizontal: 20,
    borderRadius: 12,
    padding: 20,
    justifyContent: 'center',
    position: 'relative'},
  bannerTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4},
  bannerSubtitle: {,
  fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.9},
  bannerIcon: {,
  position: 'absolute',
    right: 20,
    top: 20,
    opacity: 0.3},
  section: {,
  marginVertical: 10},
  sectionHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 15},
  sectionTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333'},
  sectionMore: {,
  fontSize: 14,
    color: '#4A90E2'},
  servicesList: {,
  paddingHorizontal: 15},
  serviceCard: {,
  width: 200,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 5,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3},
  serviceHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12},
  serviceIcon: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center'},
  popularBadge: {,
  backgroundColor: '#FF6B6B',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8},
  popularText: {,
  fontSize: 10,
    color: '#FFFFFF',
    fontWeight: 'bold'},
  serviceTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4},
  serviceSubtitle: {,
  fontSize: 12,
    color: '#666',
    marginBottom: 8},
  serviceDescription: {,
  fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12},
  serviceFooter: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'},
  servicePrice: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#FF6B6B'},
  serviceFree: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50'},
  categoryContainer: {,
  paddingHorizontal: 20,
    marginBottom: 15},
  categoryItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    marginRight: 10,
    backgroundColor: '#FFFFFF',
    position: 'relative'},
  categoryItemActive: {,
  backgroundColor: '#4A90E2',
    borderColor: '#4A90E2'},
  categoryText: {,
  fontSize: 14,
    color: '#666',
    marginLeft: 6},
  categoryTextActive: {,
  color: '#FFFFFF'},
  categoryBadge: {,
  position: 'absolute',
    top: -5,
    right: -5,
    backgroundColor: '#FF6B6B',
    borderRadius: 8,
    minWidth: 16,
    height: 16,
    justifyContent: 'center',
    alignItems: 'center'},
  categoryBadgeText: {,
  fontSize: 10,
    color: '#FFFFFF',
    fontWeight: 'bold'},
  productRow: {,
  justifyContent: 'space-between',
    paddingHorizontal: 20},
  productCard: {,
  width: (width - 50) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 12,
    marginBottom: 15,
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3},
  recommendedBadge: {,
  position: 'absolute',
    top: 8,
    left: 8,
    backgroundColor: '#4CAF50',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    zIndex: 1},
  recommendedText: {,
  fontSize: 10,
    color: '#FFFFFF',
    fontWeight: 'bold'},
  discountBadge: {,
  position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#FF6B6B',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    zIndex: 1},
  discountText: {,
  fontSize: 10,
    color: '#FFFFFF',
    fontWeight: 'bold'},
  productImage: {,
  height: 80,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8},
  productEmoji: {,
  fontSize: 40},
  productInfo: {,
  flex: 1},
  productName: {,
  fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4},
  productDescription: {,
  fontSize: 12,
    color: '#666',
    lineHeight: 16,
    marginBottom: 8},
  productTags: {,
  flexDirection: 'row',
    marginBottom: 8},
  productTag: {,
  backgroundColor: '#F0F0F0',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginRight: 4},
  productTagText: {,
  fontSize: 10,
    color: '#666'},
  productRating: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8},
  ratingText: {,
  fontSize: 12,
    color: '#333',
    marginLeft: 2},
  reviewsText: {,
  fontSize: 12,
    color: '#999',
    marginLeft: 4},
  productPricing: {,
  flexDirection: 'row',
    alignItems: 'center'},
  productPrice: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#FF6B6B'},
  originalPrice: {,
  fontSize: 12,
    color: '#999',
    textDecorationLine: 'line-through',
    marginLeft: 6}});
export default SuokeScreen;
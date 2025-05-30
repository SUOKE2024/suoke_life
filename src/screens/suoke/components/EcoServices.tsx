import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../../../components/common/Icon';
import { colors, spacing } from '../../../constants/theme';


import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
  Alert,
  Image,
  FlatList,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';

interface EcoServicesProps {
  visible: boolean;
  onClose: () => void;
}

interface BlockchainTrace {
  timestamp: string;
  location: string;
  action: string;
  verifier: string;
  hash: string;
}

interface FarmProduct {
  id: string;
  name: string;
  category: string;
  origin: string;
  healthBenefits: string[];
  season: string;
  price: number;
  unit: string;
  image: string;
  organic: boolean;
  stock: number;
  rating: number;
  reviews: number;
  blockchain: {
    verified: boolean;
    traceability: BlockchainTrace[];
    certifications: string[];
  };
  tcmProperties: {
    nature: string;
    flavor: string;
    meridian: string[];
    functions: string[];
    constitution: string[];
  };
  aiRecommendation?: {
    score: number;
    reason: string;
    personalizedBenefits: string[];
  };
}

interface WellnessDestination {
  id: string;
  name: string;
  location: string;
  type: 'mountain' | 'water' | 'forest' | 'hot_spring' | 'temple' | 'village';
  description: string;
  healthFeatures: string[];
  activities: string[];
  rating: number;
  price: number;
  image: string;
  tcmBenefits: string[];
  availability: {
    available: boolean;
    nextAvailable: string;
    capacity: number;
    booked: number;
  };
  weatherSuitability: {
    currentScore: number;
    forecast: string;
    bestTime: string;
  };
  personalizedScore?: {
    score: number;
    factors: string[];
    recommendations: string[];
  };
}

interface NutritionPlan {
  id: string;
  name: string;
  constitution: string;
  season: string;
  meals: {
    breakfast: string[];
    lunch: string[];
    dinner: string[];
    snacks: string[];
  };
  ingredients: FarmProduct[];
  benefits: string[];
  nutritionFacts: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
  };
  aiOptimized: boolean;
}

interface CommunityPost {
  id: string;
  author: string;
  avatar: string;
  content: string;
  images: string[];
  likes: number;
  comments: number;
  timestamp: string;
  tags: string[];
  type: 'experience' | 'recipe' | 'tip' | 'question';
}

export const EcoServices: React.FC<EcoServicesProps> = ({
  visible,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'farm' | 'wellness' | 'nutrition' | 'community'>('farm');
  const [cart, setCart] = useState<FarmProduct[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [userConstitution, setUserConstitution] = useState('气虚质');
  const [currentSeason, setCurrentSeason] = useState('春季');

  // 增强的农产品数据
  const [farmProducts] = useState<FarmProduct[]>([
    {
      id: 'product_1',
      name: '有机枸杞',
      category: '中药材',
      origin: '宁夏中宁',
      healthBenefits: ['明目', '补肾', '抗氧化', '提高免疫力'],
      season: '秋季',
      price: 68,
      unit: '500g',
      image: 'goji_berry.jpg',
      organic: true,
      stock: 156,
      rating: 4.8,
      reviews: 234,
      blockchain: {
        verified: true,
        traceability: [
          {
            timestamp: '2024-03-15 08:00',
            location: '宁夏中宁有机农场',
            action: '种植播种',
            verifier: '农业部认证机构',
            hash: '0x1a2b3c4d5e6f...',
          },
          {
            timestamp: '2024-09-20 14:30',
            location: '宁夏中宁有机农场',
            action: '有机采摘',
            verifier: '有机认证中心',
            hash: '0x2b3c4d5e6f7a...',
          },
          {
            timestamp: '2024-09-22 09:15',
            location: '专业加工厂',
            action: '清洗包装',
            verifier: 'ISO质量认证',
            hash: '0x3c4d5e6f7a8b...',
          },
        ],
        certifications: ['有机认证', 'GAP认证', '地理标志保护'],
      },
      tcmProperties: {
        nature: '平',
        flavor: '甘',
        meridian: ['肝经', '肾经'],
        functions: ['滋补肝肾', '明目润肺'],
        constitution: ['气虚质', '阴虚质', '阳虚质'],
      },
      aiRecommendation: {
        score: 95,
        reason: '根据您的气虚体质，枸杞能有效补气养血',
        personalizedBenefits: ['改善疲劳', '增强免疫', '护眼明目'],
      },
    },
    {
      id: 'product_2',
      name: '野生灵芝',
      category: '珍贵药材',
      origin: '长白山',
      healthBenefits: ['增强免疫', '安神', '抗疲劳', '延缓衰老'],
      season: '全年',
      price: 288,
      unit: '100g',
      image: 'lingzhi.jpg',
      organic: true,
      stock: 45,
      rating: 4.9,
      reviews: 89,
      blockchain: {
        verified: true,
        traceability: [
          {
            timestamp: '2024-07-10 06:00',
            location: '长白山原始森林',
            action: '野生采集',
            verifier: '林业部门',
            hash: '0x4d5e6f7a8b9c...',
          },
          {
            timestamp: '2024-07-12 16:20',
            location: '专业烘干厂',
            action: '低温烘干',
            verifier: 'GMP认证',
            hash: '0x5e6f7a8b9c0d...',
          },
        ],
        certifications: ['野生认证', 'GMP认证', '重金属检测合格'],
      },
      tcmProperties: {
        nature: '平',
        flavor: '甘、苦',
        meridian: ['心经', '肺经', '肝经', '肾经'],
        functions: ['补气安神', '止咳平喘'],
        constitution: ['气虚质', '血瘀质', '痰湿质'],
      },
      aiRecommendation: {
        score: 88,
        reason: '灵芝对气虚质有很好的补益作用',
        personalizedBenefits: ['提升免疫力', '改善睡眠', '抗疲劳'],
      },
    },
    {
      id: 'product_3',
      name: '有机红枣',
      category: '药食同源',
      origin: '新疆和田',
      healthBenefits: ['补血', '养颜', '健脾', '安神'],
      season: '秋季',
      price: 45,
      unit: '1kg',
      image: 'red_dates.jpg',
      organic: true,
      stock: 289,
      rating: 4.7,
      reviews: 456,
      blockchain: {
        verified: true,
        traceability: [
          {
            timestamp: '2024-04-01 07:30',
            location: '新疆和田有机枣园',
            action: '有机种植',
            verifier: '新疆农业厅',
            hash: '0x6f7a8b9c0d1e...',
          },
          {
            timestamp: '2024-10-15 12:00',
            location: '新疆和田有机枣园',
            action: '人工采摘',
            verifier: '有机认证机构',
            hash: '0x7a8b9c0d1e2f...',
          },
        ],
        certifications: ['有机认证', '地理标志', '绿色食品认证'],
      },
      tcmProperties: {
        nature: '温',
        flavor: '甘',
        meridian: ['脾经', '胃经'],
        functions: ['补中益气', '养血安神'],
        constitution: ['气虚质', '血虚质', '阳虚质'],
      },
      aiRecommendation: {
        score: 92,
        reason: '红枣是气虚质的理想补品',
        personalizedBenefits: ['补气养血', '健脾益胃', '美容养颜'],
      },
    },
    {
      id: 'product_4',
      name: '野生黑木耳',
      category: '菌类',
      origin: '东北长白山',
      healthBenefits: ['清肺润燥', '补血', '降血脂', '美容'],
      season: '夏秋',
      price: 78,
      unit: '250g',
      image: 'black_fungus.jpg',
      organic: true,
      stock: 123,
      rating: 4.6,
      reviews: 178,
      blockchain: {
        verified: true,
        traceability: [
          {
            timestamp: '2024-08-05 05:30',
            location: '长白山原始森林',
            action: '野生采集',
            verifier: '林业认证',
            hash: '0x8b9c0d1e2f3a...',
          },
        ],
        certifications: ['野生认证', '无污染检测', '营养成分检测'],
      },
      tcmProperties: {
        nature: '平',
        flavor: '甘',
        meridian: ['肺经', '大肠经'],
        functions: ['润肺止咳', '凉血止血'],
        constitution: ['阴虚质', '血瘀质', '湿热质'],
      },
      aiRecommendation: {
        score: 75,
        reason: '黑木耳对您的体质有一定益处',
        personalizedBenefits: ['润肺清燥', '补血养颜', '降脂减肥'],
      },
    },
  ]);

  // 增强的山水养生目的地数据
  const [wellnessDestinations] = useState<WellnessDestination[]>([
    {
      id: 'dest_1',
      name: '峨眉山养生谷',
      location: '四川峨眉山',
      type: 'mountain',
      description: '集佛教文化、中医养生、自然疗法于一体的综合养生基地',
      healthFeatures: ['负氧离子丰富', '天然药材资源', '清净修心环境', '海拔适宜'],
      activities: ['太极晨练', '药膳体验', '禅修静坐', '森林浴', '中医理疗', '药材采摘'],
      rating: 4.8,
      price: 1280,
      image: 'emei_mountain.jpg',
      tcmBenefits: ['清肺润燥', '宁心安神', '强身健体', '疏肝理气'],
      availability: {
        available: true,
        nextAvailable: '2024-12-20',
        capacity: 50,
        booked: 32,
      },
      weatherSuitability: {
        currentScore: 85,
        forecast: '晴朗，适宜养生',
        bestTime: '春秋两季',
      },
      personalizedScore: {
        score: 92,
        factors: ['适合气虚质', '海拔适宜', '空气质量优'],
        recommendations: ['建议停留3-5天', '参与太极和禅修', '尝试药膳调理'],
      },
    },
    {
      id: 'dest_2',
      name: '千岛湖温泉度假村',
      location: '浙江淳安',
      type: 'water',
      description: '依山傍水的温泉养生度假村，结合传统中医理疗',
      healthFeatures: ['天然温泉', '湖光山色', '空气清新', '负离子丰富'],
      activities: ['温泉浴疗', '湖畔瑜伽', '中医按摩', '养生膳食', '湖上泛舟', '渔家体验'],
      rating: 4.6,
      price: 980,
      image: 'qiandao_lake.jpg',
      tcmBenefits: ['温经通络', '祛湿排毒', '美容养颜', '舒筋活血'],
      availability: {
        available: true,
        nextAvailable: '2024-12-18',
        capacity: 80,
        booked: 45,
      },
      weatherSuitability: {
        currentScore: 78,
        forecast: '多云，温度适宜',
        bestTime: '四季皆宜',
      },
      personalizedScore: {
        score: 88,
        factors: ['温泉对气虚有益', '环境舒适', '活动丰富'],
        recommendations: ['建议温泉浴疗', '配合中医按摩', '品尝湖鲜药膳'],
      },
    },
    {
      id: 'dest_3',
      name: '张家界森林康养基地',
      location: '湖南张家界',
      type: 'forest',
      description: '原始森林环境中的生态康养体验',
      healthFeatures: ['原始森林', '天然氧吧', '野生药材', '清新空气'],
      activities: ['森林徒步', '野菜采摘', '药材识别', '自然冥想', '鸟类观察', '溪流戏水'],
      rating: 4.7,
      price: 850,
      image: 'zhangjiajie_forest.jpg',
      tcmBenefits: ['清热解毒', '润肺止咳', '舒缓压力', '调节情志'],
      availability: {
        available: true,
        nextAvailable: '2024-12-22',
        capacity: 60,
        booked: 28,
      },
      weatherSuitability: {
        currentScore: 82,
        forecast: '晴转多云，空气质量优',
        bestTime: '春夏秋三季',
      },
      personalizedScore: {
        score: 85,
        factors: ['森林环境有益', '空气质量佳', '活动适中'],
        recommendations: ['深度森林浴', '学习药材知识', '体验自然冥想'],
      },
    },
    {
      id: 'dest_4',
      name: '武当山道家养生院',
      location: '湖北武当山',
      type: 'temple',
      description: '道家文化与中医养生完美结合的修身养性圣地',
      healthFeatures: ['道家文化', '武当功夫', '中医传承', '灵山秀水'],
      activities: ['太极拳学习', '八段锦练习', '道家静坐', '中医诊疗', '武当功夫', '道家茶道'],
      rating: 4.9,
      price: 1580,
      image: 'wudang_mountain.jpg',
      tcmBenefits: ['调和阴阳', '强身健体', '宁心静神', '延年益寿'],
      availability: {
        available: true,
        nextAvailable: '2024-12-25',
        capacity: 30,
        booked: 18,
      },
      weatherSuitability: {
        currentScore: 88,
        forecast: '晴朗，微风',
        bestTime: '春秋两季',
      },
      personalizedScore: {
        score: 95,
        factors: ['最适合气虚质', '文化底蕴深厚', '功法传承正宗'],
        recommendations: ['学习太极拳', '体验道家静坐', '接受中医调理'],
      },
    },
  ]);

  // 增强的营养配餐方案
  const [nutritionPlans] = useState<NutritionPlan[]>([
    {
      id: 'plan_1',
      name: '气虚质春季调理餐',
      constitution: '气虚质',
      season: '春季',
      meals: {
        breakfast: ['小米粥配红枣', '蒸蛋羹', '枸杞茶', '核桃仁'],
        lunch: ['黄芪炖鸡汤', '山药炒木耳', '五谷饭', '时令蔬菜'],
        dinner: ['莲子银耳汤', '清蒸鲈鱼', '青菜豆腐', '薏米粥'],
        snacks: ['红枣桂圆茶', '坚果拼盘', '蜂蜜柠檬水'],
      },
      ingredients: farmProducts.slice(0, 3),
      benefits: ['补气健脾', '增强体质', '改善疲劳', '提升免疫'],
      nutritionFacts: {
        calories: 1850,
        protein: 85,
        carbs: 245,
        fat: 65,
        fiber: 35,
      },
      aiOptimized: true,
    },
    {
      id: 'plan_2',
      name: '阴虚质夏季滋养餐',
      constitution: '阴虚质',
      season: '夏季',
      meals: {
        breakfast: ['燕麦粥', '蜂蜜柠檬水', '核桃', '银耳莲子'],
        lunch: ['枸杞炖排骨', '凉拌黄瓜', '薏米饭', '绿豆汤'],
        dinner: ['银耳莲子汤', '清蒸石斑鱼', '菠菜豆腐', '百合粥'],
        snacks: ['雪梨银耳汤', '葡萄干', '绿茶'],
      },
      ingredients: [farmProducts[0], farmProducts[2]],
      benefits: ['滋阴润燥', '清热生津', '美容养颜', '安神助眠'],
      nutritionFacts: {
        calories: 1750,
        protein: 78,
        carbs: 220,
        fat: 58,
        fiber: 42,
      },
      aiOptimized: true,
    },
  ]);

  // 社区动态数据
  const [communityPosts] = useState<CommunityPost[]>([
    {
      id: 'post_1',
      author: '养生达人小李',
      avatar: 'avatar1.jpg',
      content: '刚从峨眉山养生谷回来，太极晨练配合药膳真的很棒！身体感觉轻松了很多，推荐给大家～',
      images: ['emei1.jpg', 'emei2.jpg'],
      likes: 156,
      comments: 23,
      timestamp: '2小时前',
      tags: ['峨眉山', '太极', '药膳'],
      type: 'experience',
    },
    {
      id: 'post_2',
      author: '中医养生师',
      avatar: 'avatar2.jpg',
      content: '分享一个气虚质的养生食谱：红枣枸杞粥。做法简单，效果很好！',
      images: ['recipe1.jpg'],
      likes: 89,
      comments: 15,
      timestamp: '5小时前',
      tags: ['食谱', '气虚质', '养生'],
      type: 'recipe',
    },
  ]);

  useEffect(() => {
    // 模拟获取用户体质和当前季节
    getCurrentUserInfo();
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项;

  const getCurrentUserInfo = useMemo(() => useMemo(() => useMemo(() => async () => {
    // 这里应该从用户服务获取真实数据
    setUserConstitution('气虚质'), []), []), []);
    setCurrentSeason(getCurrentSeason());
  };

  const getCurrentSeason = useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []);
    const month = useMemo(() => useMemo(() => useMemo(() => new Date().getMonth() + 1, []), []), []);
    if (month >= 3 && month <= 5) {return '春季';}
    if (month >= 6 && month <= 8) {return '夏季';}
    if (month >= 9 && month <= 11) {return '秋季';}
    return '冬季';
  };

  const onRefresh = useMemo(() => useMemo(() => useMemo(() => async () => {
    setRefreshing(true), []), []), []);
    // 模拟刷新数据
    await new Promise<void>(resolve => setTimeout(() => resolve(), 1000));
    setRefreshing(false);
  };

  const addToCart = useMemo(() => useMemo(() => useMemo(() => useCallback( (product: FarmProduct) => {, []), []), []), []);
    if (product.stock > 0) {
      setCart(prev => [...prev, product]);
      Alert.alert('添加成功', `${product.name} 已添加到购物车`);
    } else {
      Alert.alert('库存不足', '该商品暂时缺货');
    }
  };

  const viewBlockchainTrace = useMemo(() => useMemo(() => useMemo(() => useCallback( (product: FarmProduct) => {, []), []), []), []);
    Alert.alert(
      '区块链溯源',
      `${product.name}\n\n溯源记录：\n${product.blockchain.traceability.map(trace => 
        `${trace.timestamp} - ${trace.action}\n地点：${trace.location}\n验证：${trace.verifier}`
      ).join('\n\n')}`,
      [{ text: '确定' }]
    );
  };

  const bookDestination = useMemo(() => useMemo(() => useMemo(() => useCallback( (destination: WellnessDestination) => {, []), []), []), []);
    if (destination.availability.available) {
      Alert.alert(
        '预订确认',
        `确定要预订 ${destination.name} 吗？\n\n价格：¥${destination.price}/人\n可用名额：${destination.availability.capacity - destination.availability.booked}`,
        [
          { text: '取消', style: 'cancel' },
          { 
            text: '确定预订', 
            onPress: () => {
              Alert.alert('预订成功', '我们会尽快联系您确认详细信息');
            },
          },
        ]
      );
    } else {
      Alert.alert('暂不可预订', `下次可预订时间：${destination.availability.nextAvailable}`);
    }
  };

  const selectNutritionPlan = useMemo(() => useMemo(() => useMemo(() => useCallback( (plan: NutritionPlan) => {, []), []), []), []);
    Alert.alert(
      '选择配餐方案',
      `${plan.name}\n\n适用体质：${plan.constitution}\n适用季节：${plan.season}\n\n主要功效：${plan.benefits.join('、')}`,
      [
        { text: '取消', style: 'cancel' },
        { 
          text: '选择此方案', 
          onPress: () => {
            Alert.alert('方案已选择', '已为您定制个性化营养方案');
          },
        },
      ]
    );
  };

  // TODO: 将内联组件移到组件外部
const renderFarmTab = useMemo(() => useMemo(() => useMemo(() => () => (
    <ScrollView 
      style={styles.tabContent}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.headerSection}>
        <Text style={styles.sectionTitle}>🌾 食农结合 • 药食同源</Text>
        <Text style={styles.sectionDesc}>
          精选有机农产品，结合中医药理论，为您提供健康的食材选择
        </Text>
        <View style={styles.userInfoCard}>
          <Text style={styles.userInfoText}>
            您的体质：{userConstitution} | 当前季节：{currentSeason}
          </Text>
        </View>
      </View>

      <View style={styles.categoryFilter}>
        {['全部', '中药材', '药食同源', '有机蔬果', '菌类'].map((category) => (
          <TouchableOpacity key={category} style={styles.filterButton}>
            <Text style={styles.filterText}>{category}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.productsGrid}>
        {farmProducts.map((product) => (
          <TouchableOpacity
            key={product.id}
            style={[
              styles.productCard,
              product.aiRecommendation && product.aiRecommendation.score > 90 && styles.recommendedCard,
            ]}
            onPress={() => Alert.alert('产品详情', `查看${product.name}的详细信息`)}
          >
            <View style={styles.productImage}>
              <Text style={styles.imagePlaceholder}>📷</Text>
              {product.organic && (
                <View style={styles.organicBadge}>
                  <Text style={styles.organicText}>有机</Text>
                </View>
              )}
              {product.blockchain.verified && (
                <TouchableOpacity 
                  style={styles.blockchainBadge}
                  onPress={() => viewBlockchainTrace(product)}
                >
                  <Icon name="shield-check" size={16} color="white" />
                </TouchableOpacity>
              )}
              {product.aiRecommendation && product.aiRecommendation.score > 90 && (
                <View style={styles.aiRecommendBadge}>
                  <Text style={styles.aiRecommendText}>AI推荐</Text>
                </View>
              )}
            </View>
            
            <View style={styles.productInfo}>
              <Text style={styles.productName}>{product.name}</Text>
              <Text style={styles.productOrigin}>{product.origin}</Text>
              <Text style={styles.productCategory}>{product.category}</Text>
              
              <View style={styles.ratingRow}>
                <View style={styles.rating}>
                  <Icon name="star" size={12} color="#FFD700" />
                  <Text style={styles.ratingText}>{product.rating}</Text>
                  <Text style={styles.reviewsText}>({product.reviews})</Text>
                </View>
                <Text style={styles.stockText}>库存: {product.stock}</Text>
              </View>
              
              <View style={styles.tcmInfo}>
                <Text style={styles.tcmLabel}>性味:</Text>
                <Text style={styles.tcmValue}>
                  {product.tcmProperties.nature}性 {product.tcmProperties.flavor}味
                </Text>
              </View>

              {product.aiRecommendation && (
                <View style={styles.aiRecommendInfo}>
                  <Text style={styles.aiRecommendReason} numberOfLines={2}>
                    💡 {product.aiRecommendation.reason}
                  </Text>
                </View>
              )}
              
              <View style={styles.priceRow}>
                <View style={styles.priceContainer}>
                  <Text style={styles.price}>¥{product.price}</Text>
                  <Text style={styles.unit}>/{product.unit}</Text>
                </View>
                <TouchableOpacity
                  style={[
                    styles.addButton,
                    product.stock === 0 && styles.disabledButton,
                  ]}
                  onPress={() => addToCart(product)}
                  disabled={product.stock === 0}
                >
                  <Icon 
                    name={product.stock === 0 ? "close" : "plus"} 
                    size={16} 
                    color="white" 
                  />
                </TouchableOpacity>
              </View>
            </View>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  ), []), []), []);

  // TODO: 将内联组件移到组件外部
const renderWellnessTab = useMemo(() => useMemo(() => useMemo(() => () => (
    <ScrollView style={styles.tabContent}>
      <Text style={styles.sectionTitle}>山水养生 • 自然疗愈</Text>
      <Text style={styles.sectionDesc}>
        在大自然中体验传统养生文化，获得身心的全面调理
      </Text>

      <View style={styles.destinationsContainer}>
        {wellnessDestinations.map((destination) => (
          <TouchableOpacity
            key={destination.id}
            style={styles.destinationCard}
            onPress={() => Alert.alert('目的地详情', `查看${destination.name}的详细信息`)}
          >
            <View style={styles.destinationImage}>
              <Text style={styles.imagePlaceholder}>🏔️</Text>
              <View style={styles.typeIcon}>
                <Icon 
                  name={getDestinationIcon(destination.type)} 
                  size={20} 
                  color="white" 
                />
              </View>
            </View>
            
            <View style={styles.destinationInfo}>
              <View style={styles.destinationHeader}>
                <Text style={styles.destinationName}>{destination.name}</Text>
                <View style={styles.rating}>
                  <Icon name="star" size={14} color="#FFD700" />
                  <Text style={styles.ratingText}>{destination.rating}</Text>
                </View>
              </View>
              
              <Text style={styles.destinationLocation}>{destination.location}</Text>
              <Text style={styles.destinationDesc} numberOfLines={2}>
                {destination.description}
              </Text>
              
              <View style={styles.featuresContainer}>
                {destination.healthFeatures.slice(0, 2).map((feature, index) => (
                  <View key={index} style={styles.featureTag}>
                    <Text style={styles.featureText}>{feature}</Text>
                  </View>
                ))}
              </View>
              
              <View style={styles.destinationFooter}>
                <Text style={styles.destinationPrice}>¥{destination.price}/人</Text>
                <TouchableOpacity
                  style={styles.bookButton}
                  onPress={() => bookDestination(destination)}
                >
                  <Text style={styles.bookButtonText}>立即预订</Text>
                </TouchableOpacity>
              </View>
            </View>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  ), []), []), []);

  // TODO: 将内联组件移到组件外部
const renderNutritionTab = useMemo(() => useMemo(() => useMemo(() => () => (
    <ScrollView style={styles.tabContent}>
      <Text style={styles.sectionTitle}>个性化营养配餐</Text>
      <Text style={styles.sectionDesc}>
        根据中医体质理论，为您定制专属的营养配餐方案
      </Text>

      <View style={styles.plansContainer}>
        {nutritionPlans.map((plan) => (
          <View key={plan.id} style={styles.planCard}>
            <View style={styles.planHeader}>
              <Text style={styles.planName}>{plan.name}</Text>
              <View style={styles.planTags}>
                <View style={styles.constitutionTag}>
                  <Text style={styles.tagText}>{plan.constitution}</Text>
                </View>
                <View style={styles.seasonTag}>
                  <Text style={styles.tagText}>{plan.season}</Text>
                </View>
              </View>
            </View>

            <View style={styles.mealsSection}>
              {Object.entries(plan.meals).map(([mealType, foods]) => (
                <View key={mealType} style={styles.mealRow}>
                  <Text style={styles.mealType}>
                    {mealType === 'breakfast' ? '早餐' : 
                     mealType === 'lunch' ? '午餐' : '晚餐'}:
                  </Text>
                  <Text style={styles.mealFoods}>{foods.join(', ')}</Text>
                </View>
              ))}
            </View>

            <View style={styles.benefitsSection}>
              <Text style={styles.benefitsTitle}>调理功效:</Text>
              <View style={styles.benefitsList}>
                {plan.benefits.map((benefit, index) => (
                  <Text key={index} style={styles.benefitItem}>• {benefit}</Text>
                ))}
              </View>
            </View>

            <TouchableOpacity style={styles.customizeButton}>
              <Icon name="edit" size={16} color={colors.primary} />
              <Text style={styles.customizeText}>个性化定制</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>
    </ScrollView>
  ), []), []), []);

  // TODO: 将内联组件移到组件外部
const renderCommunityTab = useMemo(() => useMemo(() => useMemo(() => () => (
    <ScrollView style={styles.tabContent}>
      <Text style={styles.sectionTitle}>生态社区</Text>
      <Text style={styles.sectionDesc}>
        连接农户、消费者和养生爱好者，共建健康生活生态圈
      </Text>

      <View style={styles.communityFeatures}>
        <TouchableOpacity style={styles.featureCard}>
          <Icon name="account-group" size={40} color={colors.primary} />
          <Text style={styles.featureTitle}>农户直连</Text>
          <Text style={styles.featureDesc}>直接与有机农户对接，确保食材新鲜安全</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.featureCard}>
          <Icon name="calendar-check" size={40} color={colors.primary} />
          <Text style={styles.featureTitle}>养生活动</Text>
          <Text style={styles.featureDesc}>定期组织养生讲座、田园体验等活动</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.featureCard}>
          <Icon name="share-variant" size={40} color={colors.primary} />
          <Text style={styles.featureTitle}>经验分享</Text>
          <Text style={styles.featureDesc}>分享养生心得，交流健康生活方式</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.featureCard}>
          <Icon name="medal" size={40} color={colors.primary} />
          <Text style={styles.featureTitle}>专家指导</Text>
          <Text style={styles.featureDesc}>中医专家在线指导，个性化健康建议</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.communityStats}>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>1,280</Text>
          <Text style={styles.statLabel}>认证农户</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>15,600</Text>
          <Text style={styles.statLabel}>活跃用户</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>98%</Text>
          <Text style={styles.statLabel}>满意度</Text>
        </View>
      </View>
    </ScrollView>
  ), []), []), []);

  const getDestinationIcon = useMemo(() => useMemo(() => useMemo(() => useCallback( (type: string) => {, []), []), []), []);
    switch (type) {
      case 'mountain': return 'mountain';
      case 'water': return 'waves';
      case 'forest': return 'tree';
      case 'hot_spring': return 'hot-tub';
      case 'temple': return 'temple';
      case 'village': return 'village';
      default: return 'map-marker';
    }
  };

  // TODO: 将内联组件移到组件外部
const renderTabBar = useMemo(() => useMemo(() => useMemo(() => () => (
    <View style={styles.tabBar}>
      {[
        { key: 'farm', label: '食农结合', icon: 'leaf' },
        { key: 'wellness', label: '山水养生', icon: 'mountain' },
        { key: 'nutrition', label: '营养配餐', icon: 'food' },
        { key: 'community', label: '生态社区', icon: 'account-group' },
      ].map((tab) => (
        <TouchableOpacity
          key={tab.key}
          style={[styles.tabButton, activeTab === tab.key && styles.activeTabButton]}
          onPress={() => setActiveTab(tab.key as any)}
        >
          <Icon 
            name={tab.icon} 
            size={20} 
            color={activeTab === tab.key ? colors.primary : colors.textSecondary} 
          />
          <Text style={[
            styles.tabText,
            activeTab === tab.key && styles.activeTabText,
          ]}>
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  ), []), []), []);

  const renderContent = useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []);
    switch (activeTab) {
      case 'farm': return renderFarmTab();
      case 'wellness': return renderWellnessTab();
      case 'nutrition': return renderNutritionTab();
      case 'community': return renderCommunityTab();
      default: return renderFarmTab();
    }
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.container}>
        {/* 头部 */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Icon name="close" size={24} color={colors.text} />
          </TouchableOpacity>
          <View style={styles.headerContent}>
            <Text style={styles.title}>生态服务</Text>
            <Text style={styles.subtitle}>食农结合 • 山水养生 • 自然疗愈</Text>
          </View>
          <TouchableOpacity style={styles.cartButton}>
            <Icon name="shopping-cart" size={24} color={colors.primary} />
            {cart.length > 0 && (
              <View style={styles.cartBadge}>
                <Text style={styles.cartBadgeText}>{cart.length}</Text>
              </View>
            )}
          </TouchableOpacity>
        </View>

        {/* 标签栏 */}
        {renderTabBar()}

        {/* 内容区域 */}
        {renderContent()}
      </SafeAreaView>
    </Modal>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  closeButton: {
    padding: spacing.sm,
  },
  headerContent: {
    flex: 1,
    marginLeft: spacing.md,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 2,
  },
  cartButton: {
    padding: spacing.sm,
    position: 'relative',
  },
  cartBadge: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: colors.error,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cartBadgeText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.sm,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
  },
  activeTabButton: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primary,
  },
  tabText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  activeTabText: {
    color: colors.primary,
    fontWeight: '600',
  },
  tabContent: {
    flex: 1,
    padding: spacing.lg,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  sectionDesc: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.lg,
  },
  categoryFilter: {
    flexDirection: 'row',
    marginBottom: spacing.lg,
  },
  filterButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    backgroundColor: colors.surface,
    marginRight: spacing.sm,
  },
  filterText: {
    fontSize: 14,
    color: colors.text,
  },
  productsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  productCard: {
    width: '48%',
    backgroundColor: colors.surface,
    borderRadius: 12,
    marginBottom: spacing.md,
    overflow: 'hidden',
  },
  productImage: {
    height: 120,
    backgroundColor: colors.background,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  imagePlaceholder: {
    fontSize: 40,
  },
  organicBadge: {
    position: 'absolute',
    top: spacing.sm,
    right: spacing.sm,
    backgroundColor: colors.success,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: 8,
  },
  organicText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  productInfo: {
    padding: spacing.md,
  },
  productName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  productOrigin: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  productCategory: {
    fontSize: 12,
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  tcmInfo: {
    flexDirection: 'row',
    marginBottom: spacing.sm,
  },
  tcmLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginRight: spacing.xs,
  },
  tcmValue: {
    fontSize: 12,
    color: colors.text,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  price: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.primary,
  },
  unit: {
    fontSize: 12,
    color: colors.textSecondary,
    flex: 1,
    marginLeft: spacing.xs,
  },
  addButton: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    width: 32,
    height: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  destinationsContainer: {
    flex: 1,
  },
  destinationCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    marginBottom: spacing.lg,
    overflow: 'hidden',
  },
  destinationImage: {
    height: 160,
    backgroundColor: colors.background,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  typeIcon: {
    position: 'absolute',
    top: spacing.md,
    left: spacing.md,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  destinationInfo: {
    padding: spacing.md,
  },
  destinationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  destinationName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    flex: 1,
  },
  rating: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    fontSize: 12,
    color: colors.text,
    marginLeft: spacing.xs,
  },
  destinationLocation: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  destinationDesc: {
    fontSize: 14,
    color: colors.text,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  featuresContainer: {
    flexDirection: 'row',
    marginBottom: spacing.md,
  },
  featureTag: {
    backgroundColor: colors.primary + '20',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 12,
    marginRight: spacing.sm,
  },
  featureText: {
    fontSize: 12,
    color: colors.primary,
  },
  destinationFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  destinationPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.primary,
  },
  bookButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: 20,
  },
  bookButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  plansContainer: {
    flex: 1,
  },
  planCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  planName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  planTags: {
    flexDirection: 'row',
  },
  constitutionTag: {
    backgroundColor: colors.primary + '20',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 12,
    marginRight: spacing.sm,
  },
  seasonTag: {
    backgroundColor: colors.success + '20',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 12,
  },
  tagText: {
    fontSize: 12,
    color: colors.text,
  },
  mealsSection: {
    marginBottom: spacing.md,
  },
  mealRow: {
    marginBottom: spacing.sm,
  },
  mealType: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  mealFoods: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  benefitsSection: {
    marginBottom: spacing.md,
  },
  benefitsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  benefitsList: {
    paddingLeft: spacing.sm,
  },
  benefitItem: {
    fontSize: 14,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  customizeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.primary,
    paddingVertical: spacing.sm,
    borderRadius: 8,
  },
  customizeText: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: '600',
    marginLeft: spacing.sm,
  },
  communityFeatures: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: spacing.xl,
  },
  featureCard: {
    width: '48%',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  featureDesc: {
    fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 18,
  },
  communityStats: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.primary,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  // 新增样式
  headerSection: {
    marginBottom: spacing.lg,
  },
  userInfoCard: {
    backgroundColor: colors.primary + '10',
    borderRadius: 8,
    padding: spacing.md,
    marginTop: spacing.md,
  },
  userInfoText: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '600',
    textAlign: 'center',
  },
  recommendedCard: {
    borderWidth: 2,
    borderColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  blockchainBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    padding: 4,
  },
  aiRecommendBadge: {
    position: 'absolute',
    bottom: 8,
    left: 8,
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  aiRecommendText: {
    fontSize: 10,
    color: 'white',
    fontWeight: '600',
  },
  ratingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  reviewsText: {
    fontSize: 10,
    color: colors.textSecondary,
    marginLeft: 2,
  },
  stockText: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  aiRecommendInfo: {
    backgroundColor: colors.primary + '10',
    borderRadius: 6,
    padding: spacing.sm,
    marginBottom: spacing.sm,
  },
  aiRecommendReason: {
    fontSize: 12,
    color: colors.primary,
    lineHeight: 16,
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  disabledButton: {
    backgroundColor: colors.textSecondary,
    opacity: 0.6,
  },
}), []), []), []);

export default EcoServices; 
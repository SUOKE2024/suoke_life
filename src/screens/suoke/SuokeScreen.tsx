import React, { useState, useEffect, useCallback } from "react";";
import {;,}View,;
Text,;
StyleSheet,;
FlatList,;
TouchableOpacity,;
Image,;
ScrollView,;
Dimensions,;
RefreshControl,;
ActivityIndicator,";"";
}
  Alert,'}'';
StatusBar} from "react-native";";
import { SafeAreaView } from "react-native-safe-area-context";";
import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import Icon from "react-native-vector-icons/MaterialCommunityIcons";""/;,"/g"/;
const { width } = Dimensions.get('window');';'';
// 产品类型定义/;,/g/;
interface Product {id: string}name: string,;
const price = number;
originalPrice?: number;
image: string,;
category: string,;
rating: number,;
reviews: number,;
description: string,;
const tags = string[];
isRecommended?: boolean;
}
}
  discount?: number;}
}
// 服务类型定义/;,/g/;
interface Service {id: string}title: string,;
subtitle: string,;
icon: string,;
color: string,;
const description = string;
price?: number;
}
}
  isPopular?: boolean;}
}
// 分类类型定义/;,/g/;
interface Category {id: string}name: string,;
icon: string,;
color: string,;
}
}
  const count = number;}
}
const  SuokeScreen: React.FC = () => {const navigation = useNavigation();,}const [products, setProducts] = useState<Product[]>([]);
const [services, setServices] = useState<Service[]>([]);';,'';
const [categories, setCategories] = useState<Category[]>([]);';,'';
const [selectedCategory, setSelectedCategory] = useState<string>('all');';,'';
const [loading, setLoading] = useState(true);
const [refreshing, setRefreshing] = useState(false);
  // 生成模拟产品数据/;,/g/;
const  generateProducts = (): Product[] => {return [;]';}      {';,}id: "1";",";
price: 89,";,"";
originalPrice: 128,";,"";
image: '🍇';','';
category: 'herbs';','';
rating: 4.8,;
reviews: 256,;

}
        isRecommended: true,}
        discount: 30;},';'';
      {';,}id: "2";",";
price: 299,";,"";
originalPrice: 399,";,"";
image: '🍄';','';
category: 'herbs';','';
rating: 4.9,;
reviews: 189,;

}
        isRecommended: true,}
        discount: 25;},';'';
      {';,}id: "3";","";"";
";,"";
price: 45,";,"";
image: '🍯';','';
category: 'tea';','';
rating: 4.6,;
const reviews = 432;
';'';
      {';,}id: "4";",";
price: 168,";,"";
originalPrice: 218,";,"";
image: '🥘';','';
category: 'food';','';
rating: 4.7,;
reviews: 98,;

}
}
        discount: 23;},';'';
      {';,}id: "5";","";"";
";,"";
price: 78,";,"";
image: '🔥';','';
category: 'therapy';','';
rating: 4.5,;
const reviews = 167;
';'';
      {';,}id: "6";",";
price: 128,";,"";
originalPrice: 168,";,"";
image: '💎';','';
category: 'therapy';','';
rating: 4.8,;
reviews: 234,;

}
}
];
const discount = 24;}];
  };
  // 生成模拟服务数据/;,/g/;
const  generateServices = (): Service[] => {return [;]';}      {';,}id: "1";","";"";
";"";
";,"";
icon: 'doctor';','';
color: '#FF6B6B';','';'';

}
        price: 299,}
        isPopular: true;},';'';
      {';,}id: "2";","";"";
";"";
";,"";
icon: 'heart-pulse';','';
color: '#4ECDC4';','';'';

}
        price: 99,}
        isPopular: true;},';'';
      {';,}id: "3";","";"";
";"";
";,"";
icon: 'file-document';','';
color: '#45B7D1';','';'';
}
}
        price: 0;},';'';
      {';,}id: "4";","";"";
";"";
";,"";
icon: 'calendar-check';','';
color: '#96CEB4';','';'';
}
}
        price: 199;},';'';
      {';,}id: "5";","";"";
";"";
";,"";
icon: 'food-apple';','';
color: '#FECA57';','';'';
}
}
        price: 149;},';'';
      {';,}id: "6";","";"";
";"";
";,"";
icon: 'run';','';
color: '#FF9FF3';','';'';
}
}
];
const price = 249;}];
  };
  // 生成分类数据/;,/g/;
const  generateCategories = (): Category[] => {return [;]';}      {';,}const id = "all";";"";
";"";
      {";,}const id = "herbs";";"";
";"";
      {";,}const id = "tea";";"";
";"";
      {";,}const id = "food";";"";
";"";
      {";,}const id = "therapy";";"";
}
}
  };
  // 加载数据/;,/g/;
const  loadData = useCallback(async () => {try {}      setLoading(true);
      // 模拟API延迟/;,/g,/;
  await: new Promise(resolve => setTimeout(resolve, 800));
const productsData = generateProducts();
const servicesData = generateServices();
const categoriesData = generateCategories();
setProducts(productsData);
setServices(servicesData);
}
      setCategories(categoriesData);}
    } catch (error) {}}
}
    } finally {}}
      setLoading(false);}
    }
];
  }, []);
  // 下拉刷新/;,/g/;
const  onRefresh = useCallback(async () => {setRefreshing(true);,}const await = loadData();
}
    setRefreshing(false);}
  }, [loadData]);
  // 初始化/;,/g/;
useEffect() => {}}
    loadData();}
  }, [loadData]);";"";
  // 过滤产品"/;,"/g"/;
const  filteredProducts = selectedCategory === 'all'';'';
    ? products;
    : products.filter(product => product.category === selectedCategory);
  // 处理产品点击/;,/g/;
const  handleProductPress = (product: Product) => {Alert.alert();,}product.name,;

      [;]{';}}'';
'}'';
style: 'cancel' ;},';'';
        {{}}
    );}
  };
  // 处理服务点击/;,/g/;
const  handleServicePress = (service: Service) => {Alert.alert();,}service.title,;

      [;]        {';}}'';
'}'';
style: 'cancel' ;},';'';
        {}}
    );}
  };
  // 渲染轮播图/;,/g/;
const  renderBanner = () => (<View style={styles.bannerContainer}>;)      <ScrollView;  />/;,/g/;
horizontal;
pagingEnabled;
showsHorizontalScrollIndicator={false}
        style={styles.bannerScroll}';'';
      >';'';
];
        <View style={[styles.bannerItem, { backgroundColor: '#FF6B6B' ;}}]}>';'';
          <Text style={styles.bannerTitle}>春季养生特惠</Text>'/;'/g'/;
          <Text style={styles.bannerSubtitle}>精选中药材 限时8折</Text>'/;'/g'/;
          <Icon name="leaf" size={40} color="#FFFFFF" style={styles.bannerIcon}>";"";
        </View>"/;"/g"/;
        <View style={[styles.bannerItem, { backgroundColor: '#4ECDC4' ;}}]}>';'';
          <Text style={styles.bannerTitle}>名医在线问诊</Text>'/;'/g'/;
          <Text style={styles.bannerSubtitle}>三甲医院专家 24小时服务</Text>'/;'/g'/;
          <Icon name="doctor" size={40} color="#FFFFFF" style={styles.bannerIcon}>";"";
        </View>"/;"/g"/;
        <View style={[styles.bannerItem, { backgroundColor: '#45B7D1' ;}}]}>';'';
          <Text style={styles.bannerTitle}>AI体质检测</Text>'/;'/g'/;
          <Text style={styles.bannerSubtitle}>智能分析 精准调理</Text>'/;'/g'/;
          <Icon name="brain" size={40} color="#FFFFFF" style={styles.bannerIcon}>";"";
        </View>)/;/g/;
      </ScrollView>)/;/g/;
    </View>)/;/g/;
  );
  // 渲染分类选择器/;,/g/;
const  renderCategorySelector = () => (<View style={styles.categoryContainer}>);
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>);
        {categories.map(category) => ();}}
          <TouchableOpacity;}  />/;,/g/;
key={category.id}
            style={[;,]styles.categoryItem,;}}
              selectedCategory === category.id && styles.categoryItemActive,}
];
              { borderColor: category.color ;}}]}
            onPress={() => setSelectedCategory(category.id)}
          >;
            <Icon;  />/;,/g/;
name={category.icon}";,"";
size={20}";,"";
color={selectedCategory === category.id ? '#FFFFFF' : category.color}';'';
            />/;/g/;
            <Text style={ />/;}[;]}/g/;
              styles.categoryText,}
];
selectedCategory === category.id && styles.categoryTextActive]}}>;
              {category.name}
            </Text>/;/g/;
            {category.count > 0  && <View style={styles.categoryBadge}>;
                <Text style={styles.categoryBadgeText}>{category.count}</Text>/;/g/;
              </View>/;/g/;
            )}
          </TouchableOpacity>/;/g/;
        ))}
      </ScrollView>/;/g/;
    </View>/;/g/;
  );
  // 渲染服务卡片/;,/g/;
const renderServiceCard = ({ item }: { item: Service ;}) => ();
    <TouchableOpacity;  />/;,/g/;
style={[styles.serviceCard, { borderLeftColor: item.color ;}}]}
      onPress={() => handleServicePress(item)}
    >';'';
      <View style={styles.serviceHeader}>';'';
        <View style={[styles.serviceIcon, { backgroundColor: item.color + '20' ;}}]}>';'';
          <Icon name={item.icon} size={24} color={item.color}  />/;/g/;
        </View>/;/g/;
        {item.isPopular  && <View style={styles.popularBadge}>;
            <Text style={styles.popularText}>热门</Text>/;/g/;
          </View>/;/g/;
        )}
      </View>/;/g/;
      <Text style={styles.serviceTitle}>{item.title}</Text>/;/g/;
      <Text style={styles.serviceSubtitle}>{item.subtitle}</Text>/;/g/;
      <Text style={styles.serviceDescription} numberOfLines={2}>;
        {item.description}
      </Text>/;/g/;
      <View style={styles.serviceFooter}>;
        {item.price ? ()}
          <Text style={styles.servicePrice}>¥{item.price}</Text>/;/g/;
        ) : (<Text style={styles.serviceFree}>免费</Text>)'/;'/g'/;
        )}';'';
        <Icon name="chevron-right" size={20} color="#C0C0C0"  />"/;"/g"/;
      </View>/;/g/;
    </TouchableOpacity>/;/g/;
  );
  // 渲染产品卡片/;,/g/;
const renderProductCard = ({ item }: { item: Product ;}) => ();
    <TouchableOpacity;  />/;,/g/;
style={styles.productCard}
      onPress={() => handleProductPress(item)}
    >;
      {item.isRecommended  && <View style={styles.recommendedBadge}>;
          <Text style={styles.recommendedText}>推荐</Text>/;/g/;
        </View>/;/g/;
      )}
      {item.discount  && <View style={styles.discountBadge}>;
          <Text style={styles.discountText}>-{item.discount}%</Text>/;/g/;
        </View>/;/g/;
      )}
      <View style={styles.productImage}>;
        <Text style={styles.productEmoji}>{item.image}</Text>/;/g/;
      </View>/;/g/;
      <View style={styles.productInfo}>;
        <Text style={styles.productName} numberOfLines={1}>{item.name}</Text>/;/g/;
        <Text style={styles.productDescription} numberOfLines={2}>;
          {item.description}
        </Text>/;/g/;
        <View style={styles.productTags}>;
          {item.tags.slice(0, 2).map(tag, index) => ())}
            <View key={index} style={styles.productTag}>;
              <Text style={styles.productTagText}>{tag}</Text>/;/g/;
            </View>/;/g/;
          ))}
        </View>"/;"/g"/;
        <View style={styles.productRating}>";"";
          <Icon name="star" size={14} color="#FFD700"  />"/;"/g"/;
          <Text style={styles.ratingText}>{item.rating}</Text>/;/g/;
          <Text style={styles.reviewsText}>({item.reviews})</Text>/;/g/;
        </View>/;/g/;
        <View style={styles.productPricing}>;
          <Text style={styles.productPrice}>¥{item.price}</Text>/;/g/;
          {item.originalPrice  && <Text style={styles.originalPrice}>¥{item.originalPrice}</Text>/;/g/;
          )}
        </View>/;/g/;
      </View>/;/g/;
    </TouchableOpacity>/;/g/;
  );
  // 渲染加载状态/;,/g/;
if (loading) {}";,"";
return (<SafeAreaView style={styles.container}>";)        <StatusBar barStyle="dark-content" backgroundColor="#F8F9FA"  />"/;"/g"/;
        <View style={styles.loadingContainer}>";"";
          <ActivityIndicator size="large" color="#4A90E2"  />"/;"/g"/;
          <Text style={styles.loadingText}>加载中...</Text>)/;/g/;
        </View>)/;/g/;
      </SafeAreaView>)/;/g/;
    );
  }";,"";
return (<SafeAreaView style={styles.container}>";)      <StatusBar barStyle="dark-content" backgroundColor="#F8F9FA"  />"/;"/g"/;
      <ScrollView;  />/;,/g/;
style={styles.scrollView}
        refreshControl={}}
          <RefreshControl;}  />/;,/g/;
refreshing={refreshing}";,"";
onRefresh={onRefresh}";,"";
colors={['#4A90E2']}';,'';
tintColor="#4A90E2"";"";
          />/;/g/;
        }
        showsVerticalScrollIndicator={false}
      >;
        {}
        <View style={styles.header}>;
          <Text style={styles.headerTitle}>SUOKE 健康商城</Text>/;/g/;
          <Text style={styles.headerSubtitle}>精选健康产品与专业服务</Text>)/;/g/;
        </View>)/;/g/;
        {});
        {renderBanner()}
        {}
        <View style={styles.section}>;
          <View style={styles.sectionHeader}>;
            <Text style={styles.sectionTitle}>专业服务</Text>/;/g/;
            <TouchableOpacity>;
              <Text style={styles.sectionMore}>查看全部</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
          <FlatList removeClippedSubviews={true} maxToRenderPerBatch={10} windowSize={10};  />/;,/g/;
data={services}
            renderItem={renderServiceCard}
            keyExtractor={(item) => item.id}
            horizontal;
showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.servicesList}
          />/;/g/;
        </View>/;/g/;
        {}
        <View style={styles.section}>;
          <View style={styles.sectionHeader}>;
            <Text style={styles.sectionTitle}>精选产品</Text>/;/g/;
            <TouchableOpacity>;
              <Text style={styles.sectionMore}>查看全部</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
          {}
          {renderCategorySelector()}
          {}
          <FlatList removeClippedSubviews={true} maxToRenderPerBatch={10} windowSize={10};  />/;,/g/;
data={filteredProducts}
            renderItem={renderProductCard}
            keyExtractor={(item) => item.id}
            numColumns={2}
            columnWrapperStyle={styles.productRow}
            scrollEnabled={false}
          />/;/g/;
        </View>/;/g/;
      </ScrollView>/;/g/;
    </SafeAreaView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";}}"";
  flex: 1,"}";
backgroundColor: '#F8F9FA';},';,'';
scrollView: {,}
  flex: 1;}
loadingContainer: {,';,}flex: 1,';'';
}
    justifyContent: 'center';','}';,'';
alignItems: 'center';},';,'';
loadingText: {marginTop: 10,';'';
}
    fontSize: 16,'}'';
color: '#666';},';,'';
header: {paddingHorizontal: 20,';'';
}
    paddingVertical: 20,'}'';
backgroundColor: '#FFFFFF';},';,'';
headerTitle: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';'';
}
    color: '#333';','}'';
marginBottom: 4;}
headerSubtitle: {,';}}'';
  fontSize: 14,'}'';
color: '#666';},';,'';
bannerContainer: {,;}}
  height: 120,}
    marginVertical: 10;}
bannerScroll: {,}
  flex: 1;}
bannerItem: {width: width - 40,;
marginHorizontal: 20,;
borderRadius: 12,';,'';
padding: 20,';'';
}
    justifyContent: 'center';','}';,'';
position: 'relative';},';,'';
bannerTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
    color: '#FFFFFF';','}'';
marginBottom: 4;}
bannerSubtitle: {,';,}fontSize: 14,';'';
}
    color: '#FFFFFF';',}'';
opacity: 0.9;},';,'';
bannerIcon: {,';,}position: 'absolute';','';
right: 20,;
}
    top: 20,}
    opacity: 0.3;}
section: {,}
  marginVertical: 10;},';,'';
sectionHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    paddingHorizontal: 20,}
    marginBottom: 15;}
sectionTitle: {,';,}fontSize: 18,';'';
}
    fontWeight: 'bold';','}';,'';
color: '#333';},';,'';
sectionMore: {,';}}'';
  fontSize: 14,'}'';
color: '#4A90E2';},';,'';
servicesList: {,}
  paddingHorizontal: 15;}
serviceCard: {,';,}width: 200,';,'';
backgroundColor: '#FFFFFF';','';
borderRadius: 12,;
padding: 16,;
marginHorizontal: 5,';,'';
borderLeftWidth: 4,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
elevation: 3;},';,'';
serviceHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';'';
}
    alignItems: 'flex-start';','}'';
marginBottom: 12;}
serviceIcon: {width: 40,;
height: 40,';,'';
borderRadius: 20,';'';
}
    justifyContent: 'center';','}';,'';
alignItems: 'center';},';,'';
popularBadge: {,';,}backgroundColor: '#FF6B6B';','';
paddingHorizontal: 6,;
}
    paddingVertical: 2,}
    borderRadius: 8;}
popularText: {,';,}fontSize: 10,';'';
}
    color: '#FFFFFF';','}';,'';
fontWeight: 'bold';},';,'';
serviceTitle: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';'';
}
    color: '#333';','}'';
marginBottom: 4;}
serviceSubtitle: {,';,}fontSize: 12,';'';
}
    color: '#666';',}'';
marginBottom: 8;}
serviceDescription: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    lineHeight: 20,}
    marginBottom: 12;},';,'';
serviceFooter: {,';,}flexDirection: 'row';','';'';
}
    justifyContent: 'space-between';','}';,'';
alignItems: 'center';},';,'';
servicePrice: {,';,}fontSize: 16,';'';
}
    fontWeight: 'bold';','}';,'';
color: '#FF6B6B';},';,'';
serviceFree: {,';,}fontSize: 16,';'';
}
    fontWeight: 'bold';','}';,'';
color: '#4CAF50';},';,'';
categoryContainer: {,;}}
  paddingHorizontal: 20,}
    marginBottom: 15;},';,'';
categoryItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: 12,;
paddingVertical: 8,;
borderRadius: 20,;
borderWidth: 1,';,'';
marginRight: 10,';'';
}
    backgroundColor: '#FFFFFF';','}';,'';
position: 'relative';},';,'';
categoryItemActive: {,';}}'';
  backgroundColor: '#4A90E2';','}';,'';
borderColor: '#4A90E2';},';,'';
categoryText: {,';,}fontSize: 14,';'';
}
    color: '#666';',}'';
marginLeft: 6;},';,'';
categoryTextActive: {,'}'';
color: '#FFFFFF';},';,'';
categoryBadge: {,';,}position: 'absolute';','';
top: -5,';,'';
right: -5,';,'';
backgroundColor: '#FF6B6B';','';
borderRadius: 8,;
minWidth: 16,';,'';
height: 16,';'';
}
    justifyContent: 'center';','}';,'';
alignItems: 'center';},';,'';
categoryBadgeText: {,';,}fontSize: 10,';'';
}
    color: '#FFFFFF';','}';,'';
fontWeight: 'bold';},';,'';
productRow: {,';}}'';
  justifyContent: 'space-between';',')}'';
paddingHorizontal: 20;},);
productCard: {,)';,}width: (width - 50) / 2,'/;,'/g,'/;
  backgroundColor: '#FFFFFF';','';
borderRadius: 12,;
padding: 12,';,'';
marginBottom: 15,';,'';
position: 'relative';','';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
elevation: 3;},';,'';
recommendedBadge: {,';,}position: 'absolute';','';
top: 8,';,'';
left: 8,';,'';
backgroundColor: '#4CAF50';','';
paddingHorizontal: 6,;
paddingVertical: 2,;
}
    borderRadius: 8,}
    zIndex: 1;}
recommendedText: {,';,}fontSize: 10,';'';
}
    color: '#FFFFFF';','}';,'';
fontWeight: 'bold';},';,'';
discountBadge: {,';,}position: 'absolute';','';
top: 8,';,'';
right: 8,';,'';
backgroundColor: '#FF6B6B';','';
paddingHorizontal: 6,;
paddingVertical: 2,;
}
    borderRadius: 8,}
    zIndex: 1;}
discountText: {,';,}fontSize: 10,';'';
}
    color: '#FFFFFF';','}';,'';
fontWeight: 'bold';},';,'';
productImage: {,';,}height: 80,';,'';
justifyContent: 'center';','';'';
}
    alignItems: 'center';','}'';
marginBottom: 8;}
productEmoji: {,}
  fontSize: 40;}
productInfo: {,}
  flex: 1;}
productName: {,';,}fontSize: 14,';,'';
fontWeight: 'bold';','';'';
}
    color: '#333';','}'';
marginBottom: 4;}
productDescription: {,';,}fontSize: 12,';,'';
color: '#666';','';'';
}
    lineHeight: 16,}
    marginBottom: 8;},';,'';
productTags: {,';}}'';
  flexDirection: 'row';','}'';
marginBottom: 8;},';,'';
productTag: {,';,}backgroundColor: '#F0F0F0';','';
paddingHorizontal: 6,;
paddingVertical: 2,;
}
    borderRadius: 8,}
    marginRight: 4;}
productTagText: {,';}}'';
  fontSize: 10,'}'';
color: '#666';},';,'';
productRating: {,';,}flexDirection: 'row';','';'';
}
    alignItems: 'center';',}'';
marginBottom: 8;}
ratingText: {,';,}fontSize: 12,';'';
}
    color: '#333';',}'';
marginLeft: 2;}
reviewsText: {,';,}fontSize: 12,';'';
}
    color: '#999';',}'';
marginLeft: 4;},';,'';
productPricing: {,';}}'';
  flexDirection: 'row';','}';,'';
alignItems: 'center';},';,'';
productPrice: {,';,}fontSize: 16,';'';
}
    fontWeight: 'bold';','}';,'';
color: '#FF6B6B';},';,'';
originalPrice: {,';,}fontSize: 12,';,'';
color: '#999';','';'';
}
    textDecorationLine: 'line-through';','}'';
const marginLeft = 6;}});';,'';
export default SuokeScreen;
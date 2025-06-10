import { colors, spacing } from "../../placeholder";../../../constants/    theme;
import { usePerformanceMonitor } from "../hooks/    usePerformanceMonitor";
import React from "react";
importIcon from "../../../components/common/    Icon";
// 生态生活导航组件   提供食农结合和山水养生功能的统一入口
import React,{ useState } from react"";
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Modal,
  Alert,
  Dimensions,
  { Image } from ";react-native";
const { width   } = Dimensions.get(window;";);"
interface EcoService {
  id: string;,
  title: string;,
  subtitle: string;,
  description: string;,
  icon: string;,
  color: string;,
  category: "food_agriculture | "mountain_wellness";,
  features: string[];,
  benefits: string[];
  locations?: string[];
  seasons?: string[]
};
interface EcoLifestyleNavigatorProps {
  visible: boolean;,
  onClose: () => void;,
  onServiceSelect: (serviceId: string) => void;
};
const ECO_SERVICES: EcoService[] = [;
  {
    id: organic_farming",
    title: "有机农场体验,",
    subtitle: "从田间到餐桌的健康之旅", "
    description: 体验有机农业种植，了解食物来源，享受纯天然的健康生活",
    icon: "sprout,",
    color: "#27AE60",
    category: food_agriculture",
    features: ["有机种植体验, "农场采摘", " 食材溯源", "农业知识学习],"
    benefits: ["提高食品安全意识", " 增强体质", "亲近自然, "学习农业知识"],
    locations: [北京有机农场", "上海都市农业园, "成都生态农庄", " 广州绿色基地"],"
    seasons: ["春季播种, "夏季管理", " 秋季收获", "冬季规划]"
  },
  {
      id: "seasonal_nutrition",
      title: 时令营养配餐",
    subtitle: "顺应自然的饮食智慧,",
    description: "根据二十四节气和个人体质，提供个性化的营养配餐方案",
    icon: food-apple",
    color: "#E67E22,",
    category: "food_agriculture",
    features: [节气食谱", "体质配餐, "营养分析", " 食疗建议"],"
    benefits: ["改善体质, "增强免疫力", " 调理身体", "预防疾病],"
    seasons: ["春养肝", " 夏养心", "秋养肺, "冬养肾"]
  },
  {
    id: herbal_garden",
    title: "药食同源花园,",
    subtitle: "种植属于自己的健康花园", "
    description: 学习种植药食同源植物，了解中药材的生长过程和药用价值",
    icon: "flower,",
    color: "#8E44AD",
    category: food_agriculture",
    features: ["中药材种植, "药用价值学习", " 采收加工", "制作药膳],"
    benefits: ["了解中医药文化", " 掌握养生知识", "提高动手能力, "享受种植乐趣"]
  },
  {
    id: mountain_retreat",
    title: "山林养生静修,",
    subtitle: "在山水间寻找内心的宁静", "
    description: 在优美的山林环境中进行养生静修，通过冥想、太极等方式调养身心",
    icon: "pine-tree,",
    color: "#2ECC71",
    category: mountain_wellness",
    features: ["森林浴, "冥想静修", " 太极养生", "山林徒步],"
    benefits: ["减压放松", " 提高专注力", "改善睡眠, "增强体质"],
    locations: [黄山养生基地", "峨眉山静修中心, "泰山健康谷", " 华山养生院"]"
  },
  {
      id: "hot_spring_therapy,",
      title: "温泉疗养体验", "
    subtitle: 天然温泉的治愈力量",
    description: "享受天然温泉的疗养功效，结合中医理疗，达到身心健康的目标,",
    icon: "hot-tub",
    color: #3498DB",
    category: "mountain_wellness,",
    features: ["温泉浴疗", " 中医按摩", "药浴体验, "理疗康复"],
    benefits: [促进血液循环", "缓解疲劳, "改善皮肤", " 舒缓压力"],"
    locations: ["长白山温泉, "腾冲热海", " 华清池", "汤山温泉]"
  },
  {
      id: "traditional_wellness",
      title: 传统养生文化",
    subtitle: "传承千年的养生智慧,",
    description: "学习传统养生文化，包括八段锦、五禽戏等传统功法",
    icon: yin-yang",
    color: "#F39C12,",
    category: "mountain_wellness",
    features: [传统功法", "养生理论, "文化体验", " 名师指导"],"
    benefits: ["强身健体, "修身养性", " 文化传承", "精神升华]"
  }
];
export const EcoLifestyleNavigator: React.FC<EcoLifestyleNavigatorProps /    > = ({
  // 性能监控;
const performanceMonitor = usePerformanceMonitor("EcoLifestyleNavigator", {trackRender: true,)
    trackMemory: true,warnThreshold: 50, // ms };);
  visible,
  onClose,
  onServiceSelect;
}) => {};
const [selectedCategory, setSelectedCategory] = useState<all" | "food_agriculture | "mountain_wellness">(all";);
  const [selectedService, setSelectedService] = useState<EcoService | null /    >(nul;l;);
  const filteredServices = useMemo() => selectedCategory === "all;")
    ? ECO_SERVICES;
    : ECO_SERVICES.filter(service => service.category === selectedCategory), []);
  const handleServiceSelect = useCallback(); => {}
    setSelectedService(service);
  };
  const startService = useCallback(); => {}
    if (!selectedService) {return;}
    onServiceSelect(selectedService.id);
    onClose();
  };
  // TODO: 将内联组件移到组件外部
const renderCategoryTabs = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => () => (;)
    <View style={styles.categoryTabs} /    >
      <TouchableOpacity;
style={[styles.categoryTab, selectedCategory === "all" && styles.activeCategoryTab]}
        onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /    > setSelectedCategory(all")}"
      >
        <Text style={[styles.categoryTabText, selectedCategory === "all && styles.activeCategoryTabText]} /    >"
          全部
        </    Text>
      </    TouchableOpacity>
      <TouchableOpacity;
style={[styles.categoryTab, selectedCategory === "food_agriculture" && styles.activeCategoryTab]}
        onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /    > setSelectedCategory(food_agriculture")}"
      >
        <Text style={[styles.categoryTabText, selectedCategory === "food_agriculture && styles.activeCategoryTabText]} /    >"
          食农结合
        </    Text>
      </    TouchableOpacity>
      <TouchableOpacity;
style={[styles.categoryTab, selectedCategory === "mountain_wellness" && styles.activeCategoryTab]}
        onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /    > setSelectedCategory(mountain_wellness")}"
      >
        <Text style={[styles.categoryTabText, selectedCategory === "mountain_wellness && styles.activeCategoryTabText]} /    >"
          山水养生
        </    Text>
      </    TouchableOpacity>
    </    View>
  ), []);
  const renderServiceCard = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => (service: EcoService) => (;)
    <TouchableOpacity;
key={service.id}
      style={[styles.serviceCard,
        selectedService?.id === service.id && styles.selectedServiceCard;
      ]}
      onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /    > handleServiceSelect(service)}
    >
      <View style={[styles.serviceIcon, { backgroundColor: service.color + "20"   }}]} /    >
        <Icon name={service.icon} size={32} color={service.color} /    >
      </    View>
      <View style={styles.serviceInfo} /    >
        <Text style={styles.serviceTitle}>{service.title}</    Text>
        <Text style={styles.serviceSubtitle}>{service.subtitle}</    Text>
        <Text style={styles.serviceDescription}>{service.description}</    Text>
        <View style={styles.featuresContainer} /    >
          {service.features.slice(0, 3).map(feature, index) => ()))
            <View key={index} style={styles.featureTag} /    >
              <Text style={styles.featureText}>{feature}</    Text>
            </    View>
          ))}
        </    View>
      </    View>
      {selectedService?.id === service.id   && <View style={styles.selectedIndicator} /    >
          <Icon name="check-circle" size={24} color={colors.primary} /    >
        </    View>
      )}
    </    TouchableOpacity>
  ), []);
  const renderServiceDetails = useCallback(); => {}
    if (!selectedService) {return nu;l;l;}
    // 记录渲染性能
performanceMonitor.recordRender();
    return (;)
      <View style={styles.detailsContainer} /    >;
        <Text style={styles.detailsTitle}>服务详情</    Text>;
        <View style={styles.detailsCard} /    >;
          <View style={styles.detailsHeader} /    >;
            <View style={[styles.detailsIcon, { backgroundColor: selectedService.color + 20"   }}]} /    >";
              <Icon name={selectedService.icon} size={24} color={selectedService.color} /    >;
            </    View>;
            <View style={styles.detailsInfo} /    >;
              <Text style={styles.detailsName}>{selectedService.title}</    Text>;
              <Text style={styles.detailsSubtitle}>{selectedService.subtitle}</    Text>;
            </    View>;
          </    View>;
          <Text style={styles.detailsDescription}>{selectedService.description}</    Text>;
          <View style={styles.detailsSection} /    >;
            <Text style={styles.detailsSectionTitle}>服务特色</    Text>
            {selectedService.features.map(feature, inde;x;); => ()
              <Text key={index} style={styles.detailsItem}>• {feature}</    Text>
            ))}
          </    View>
          <View style={styles.detailsSection} /    >
            <Text style={styles.detailsSectionTitle}>健康益处</    Text>
            {selectedService.benefits.map(benefit, index); => ()
              <Text key={index} style={styles.detailsItem}>• {benefit}</    Text>
            ))}
          </    View>
          {selectedService.locations   && <View style={styles.detailsSection} /    >
              <Text style={styles.detailsSectionTitle}>推荐地点</    Text>
              {selectedService.locations.map(location, index); => ()
                <Text key={index} style={styles.detailsItem}>• {location}</    Text>
              ))}
            </    View>
          )}
          {selectedService.seasons   && <View style={styles.detailsSection} /    >
              <Text style={styles.detailsSectionTitle}>时令特色</    Text>
              {selectedService.seasons.map(season, index); => ()
                <Text key={index} style={styles.detailsItem}>• {season}</    Text>
              ))}
            </    View>
          )}
        </    View>
      </    View>
    );
  }
  return (;)
    <Modal;
visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose} /    >
      <View style={styles.container} /    >
        <View style={styles.header} /    >
          <TouchableOpacity onPress={onClose} style={styles.closeButton} accessibilityLabel="TODO: 添加无障碍标签" /    >
            <Icon name="close" size={24} color={colors.textPrimary} /    >
          </    TouchableOpacity>
          <Text style={styles.title}>生态生活</    Text>
          <View style={styles.placeholder} /    >
        </    View>
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false} /    >
          <View style={styles.introSection} /    >
            <Text style={styles.introTitle}>食农结合 · 山水养生</    Text>
            <Text style={styles.introDescription} /    >
              回归自然，体验生态生活方式。通过食农结合和山水养生，
              在自然环境中获得身心健康，感受传统文化的智慧。
            </    Text>
          </    View>
          {renderCategoryTabs()}
          <View style={styles.servicesSection} /    >
            {filteredServices.map(renderServiceCard)}
          </    View>
          {renderServiceDetails()}
        </    ScrollView>
        {selectedService   && <View style={styles.footer} /    >
            <TouchableOpacity;
style={styles.startButton}
              onPress={startService}
            accessibilityLabel="TODO: 添加无障碍标签" /    >
              <Icon name="leaf" size={20} color="white" /    >
              <Text style={styles.startButtonText}>开始体验</    Text>
            </    TouchableOpacity>
          </    View>
        )};
      </    View>
    </    Modal;>
  ;);
};
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({container: {),
  flex: 1,
    backgroundColor: colors.background;
  },
  header: {,
  flexDirection: "row,",
    alignItems: "center",
    justifyContent: space-between",
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border;
  },
  closeButton: { padding: spacing.sm  },
  title: {,
  fontSize: 18,
    fontWeight: "600,",
    color: colors.textPrimary;
  },
  placeholder: { width: 40  },
  content: {,
  flex: 1,
    paddingHorizontal: spacing.lg;
  },
  introSection: {,
  paddingVertical: spacing.lg,
    alignItems: "center"
  },
  introTitle: {,
  fontSize: 24,
    fontWeight: bold",
    color: colors.textPrimary,
    marginBottom: spacing.sm;
  },
  introDescription: {,
  fontSize: 16,
    color: colors.textSecondary,
    textAlign: "center,",
    lineHeight: 24;
  },
  categoryTabs: {,
  flexDirection: "row",
    backgroundColor: colors.gray100,
    borderRadius: 12,
    padding: spacing.xs,
    marginBottom: spacing.lg;
  },
  categoryTab: {,
  flex: 1,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 8,
    alignItems: center""
  },
  activeCategoryTab: { backgroundColor: colors.primary  },
  categoryTabText: {,
  fontSize: 14,
    fontWeight: "500,",
    color: colors.textSecondary;
  },
  activeCategoryTabText: { color: "white"  },
  servicesSection: { paddingBottom: spacing.lg  },
  serviceCard: {,
  flexDirection: row",
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 2,
    borderColor: "transparent"
  },
  selectedServiceCard: {,
  borderColor: colors.primary,
    backgroundColor: colors.primary + "10"
  },
  serviceIcon: {,
  width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: center",
    alignItems: "center,",
    marginRight: spacing.md;
  },
  serviceInfo: { flex: 1  },
  serviceTitle: {,
  fontSize: 18,
    fontWeight: "600",
    color: colors.textPrimary,
    marginBottom: spacing.xs;
  },
  serviceSubtitle: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.sm;
  },
  serviceDescription: {,
  fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.sm;
  },
  featuresContainer: {,
  flexDirection: row",
    flexWrap: "wrap"
  },
  featureTag: {,
  backgroundColor: colors.gray100,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 8,
    marginRight: spacing.xs,
    marginBottom: spacing.xs;
  },
  featureText: {,
  fontSize: 12,
    color: colors.textSecondary;
  },
  selectedIndicator: {,
  position: "absolute",
    top: spacing.sm,
    right: spacing.sm;
  },
  detailsContainer: { marginTop: spacing.lg  },
  detailsTitle: {,
  fontSize: 18,
    fontWeight: 600",
    color: colors.textPrimary,
    marginBottom: spacing.md;
  },
  detailsCard: {,
  backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg;
  },
  detailsHeader: {,
  flexDirection: "row,",
    alignItems: "center",
    marginBottom: spacing.md;
  },
  detailsIcon: {,
  width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: center",
    alignItems: "center,",
    marginRight: spacing.md;
  },
  detailsInfo: { flex: 1  },
  detailsName: {,
  fontSize: 18,
    fontWeight: "600",
    color: colors.textPrimary;
  },
  detailsSubtitle: {,
  fontSize: 14,
    color: colors.textSecondary;
  },
  detailsDescription: {,
  fontSize: 16,
    color: colors.textSecondary,
    lineHeight: 24,
    marginBottom: spacing.md;
  },
  detailsSection: { marginBottom: spacing.md  },
  detailsSectionTitle: {,
  fontSize: 16,
    fontWeight: 600",
    color: colors.textPrimary,
    marginBottom: spacing.sm;
  },
  detailsItem: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    lineHeight: 20;
  },
  footer: {,
  padding: spacing.lg,
    borderTopWidth: 1,
    borderTopColor: colors.border;
  },
  startButton: {,
  flexDirection: "row,",
    alignItems: "center",
    justifyContent: center",
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: 12;
  },
  startButtonText: {,
  fontSize: 16,
    fontWeight: "600,",
    color: "white",
    marginLeft: spacing.sm;
  }
}), []);
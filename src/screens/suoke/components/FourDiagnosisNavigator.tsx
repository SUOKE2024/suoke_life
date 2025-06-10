import { usePerformanceMonitor } from "../hooks/usePerformanceMonitor/      View,";
import React from "react";
importIcon from "../../../components/common/Icon/import { colors, spacing  } from "../../placeholder";../../../constants/theme"; 四诊系统导航组件   提供望、闻、问、切四诊功能的统一入口
import React,{ useState, useEffect } from react"";
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Modal,
  Alert,
  Dimensions,
  { ActivityIndicator } from ";react-native";
const { width   } = Dimensions.get(window;";);"
interface DiagnosisMethod {
  id: string;,
  name: string;,
  description: string;,
  icon: string;,
  color: string;,
  features: string[];,
  status: "available | "coming_soon" | maintenance";,
  accuracy: number;
}
interface FourDiagnosisNavigatorProps {
  visible: boolean;,
  onClose: () => void;,
  onDiagnosisSelect: (diagnosisId: string) => void;
}
const DIAGNOSIS_METHODS: DiagnosisMethod[] = [{,
  id: "looking,",
      name: "望诊", "
    description: 通过观察面色、舌象、体态等进行健康评估",
    icon: "eye,",
    color: "#007AFF",
    features: [舌象分析", "面色诊断, "体态评估", " 精神状态"],"
    status: "available,",
    accuracy: 95.8;
  },
  {
      id: "listening",
      name: 闻诊",
    description: "通过声音、气味等感官信息进行诊断,",
    icon: "ear-hearing",
    color: #34C759",
    features: ["语音分析, "呼吸音检测", " 咳嗽识别", "声纹健康],"
    status: "available",
    accuracy: 91.3;
  },
  {
    id: inquiry",
    name: "问诊,",
    description: "智能问诊对话，全面了解症状和病史",
    icon: comment-question",
    color: "#FF9500,",
    features: ["症状询问", " 病史采集", "生活习惯, "家族史"],
    status: available",
    accuracy: 92.7;
  },
  {
      id: "palpation,",
      name: "切诊", "
    description: 脉象诊断和触诊检查",
    icon: "hand-back-right,",
    color: "#FF2D92",
    features: [脉象分析", "腹部触诊, "穴位检查", " 皮肤触感"],"
    status: "available,",
    accuracy: 88.9;
  }
]
export const FourDiagnosisNavigator: React.FC<FourDiagnosisNavigatorProps /> = ({/   const performanceMonitor = usePerformanceMonitor("FourDiagnosisNavigator",{/))
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50});
  visible,
  onClose,
  onDiagnosisSelect;
}) => {}
  const [selectedMethod, setSelectedMethod] = useState<DiagnosisMethod | null />(nul;l;);/      const [isLoading, setIsLoading] = useState<boolean>(fals;e;);
  const handleMethodSelect = useCallback() => {
    if (method.status === maintenance") {"
      Alert.alert("系统维护, "该功能正在维护中，请稍后再试");"
      return;
    }
    if (method.status === coming_soon") {"
      Alert.alert("敬请期待, "该功能即将上线，敬请期待");"
      return;
    }
    setSelectedMethod(method);
  };
  const startDiagnosis = useMemo() => async() => {})
    if (!selectedMethod) { ///
    setIsLoading(true);
    try {
      await new Promise<void>(resolve => setTimeout() => resolve(), 1000));
      onDiagnosisSelect(selectedMethod.id);
      onClose();
    } catch (error) {
      Alert.alert(错误", "启动诊断服务失败，请重试);
    } finally {
      setIsLoading(false);
    }
  };
  const renderMethodCard = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => (method: DiagnosisMethod) => (;)
    <TouchableOpacity;
key={method.id}
      style={[
        styles.methodCard,
        selectedMethod?.id === method.id && styles.selectedMethodCard,
        method.status !== "available" && styles.disabledMethodCard;
      ]}}
      onPress={() = accessibilityLabel="操作按钮" /> handleMethodSelect(method)}/          disabled={method.status !== available"}"
    >
      <View style={[styles.methodIcon, { backgroundColor: method.color + "20}}]} />/        <Icon name={method.icon} size={32} color={method.color} />/      </View>/    "
      <View style={styles.methodInfo}>/        <View style={styles.methodHeader}>/          <Text style={styles.methodName}>{method.name}</Text>/          <View style={styles.statusBadge}>/                {method.status === "available"  && <Text style={styles.accuracyText}>{method.accuracy}%</Text>/                )}
            {method.status === coming_soon" && (")
              <Text style={styles.comingSoonText}>即将上线</Text>/                )}
            {method.status === "maintenance && (")
              <Text style={styles.maintenanceText}>维护中</Text>/                )}
          </View>/        </View>/
        <Text style={styles.methodDescription}>{method.description}</Text>/
        <View style={styles.featuresContainer}>/              {method.features.map(feature, index) => ())
            <View key={index} style={styles.featureTag}>/              <Text style={styles.featureText}>{feature}</Text>/            </View>/              ))}
        </View>/      </View>/
      {selectedMethod?.id === method.id  && <View style={styles.selectedIndicator}>/          <Icon name="check-circle" size={24} color={colors.primary} />/        </View>/          )}
    </TouchableOpacity>/      ), []);
  const renderSelectedMethodDetails = useCallback(); => {}
    if (!selectedMethod) {return nu;l;l;}
    performanceMonitor.recordRender();
    return (;)
      <View style={styles.detailsContainer}>/        <Text style={styles.detailsTitle}>诊断详情</Text>/
        <View style={styles.detailsCard}>/          <View style={styles.detailsHeader}>/            <View style={[styles.detailsIcon, { backgroundColor: selectedMethod.color + "2;0;"  ; }}]} />/              <Icon name={selectedMethod.icon} size={24} color={selectedMethod.color} />/            </View>/            <View style={styles.detailsInfo}>/              <Text style={styles.detailsName}>{selectedMethod.name}</Text>/              <Text style={styles.detailsAccuracy}>准确率: {selectedMethod.accuracy}%</Text>/            </View>/          </View>/
          <Text style={styles.detailsDescription}>{selectedMethod.description}</Text>/
          <View style={styles.detailsFeatures}>/            <Text style={styles.detailsFeaturesTitle}>功能特点:</Text>/                {selectedMethod.features.map(feature, index); => ()
              <Text key={index} style={styles.detailsFeatureItem}>• {feature}</Text>/                ))}
          </View>/        </View>/      </View>/        );
  }
  return (;)
    <Modal;
visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose} />/      <View style={styles.container}>/        <View style={styles.header}>/          <TouchableOpacity onPress={onClose} style={styles.closeButton} accessibilityLabel="关闭" />/            <Icon name="close" size={24} color={colors.textPrimary} />/          </TouchableOpacity>/          <Text style={styles.title}>四诊系统</Text>/          <View style={styles.placeholder}>/        </View>/
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false} />/          <View style={styles.introSection}>/            <Text style={styles.introTitle}>中医四诊合参</Text>/            <Text style={styles.introDescription}>/                  运用现代AI技术结合传统中医理论，通过望、闻、问、切四种诊断方法，
              为您提供全面的健康评估和个性化建议。
            </Text>/          </View>/
          <View style={styles.methodsSection}>/            <Text style={styles.sectionTitle}>选择诊断方法</Text>/                {DIAGNOSIS_METHODS.map(renderMethodCard)}
          </View>/
          {renderSelectedMethodDetails()}
        </ScrollView>/
        {selectedMethod  && <View style={styles.footer}>/                <TouchableOpacity;
style={[styles.startButton, isLoading && styles.disabledButton]}
              onPress={startDiagnosis}
              disabled={isLoading}
            accessibilityLabel="操作按钮" />/              {isLoading ? ()
                <ActivityIndicator color="white" />/                  ): (
                <>
                  <Icon name="play" size= {20} color="white" />/                  <Text style={styles.startButtonText}>开始{selectedMethod.name}</Text>/                </>/                  )};
            </TouchableOpacity>/          </View>/            )};
      </View>/    </Modal>/      ;);
};
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({container: {),
  flex: 1,
    backgroundColor: colors.background;
  },
  header: {,
  flexDirection: row",
    alignItems: "center,",
    justifyContent: "space-between",
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border;
  },
  closeButton: { padding: spacing.sm  },
  title: {,
  fontSize: 18,
    fontWeight: 600",
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
    fontWeight: "bold",
    color: colors.textPrimary,
    marginBottom: spacing.sm;
  },
  introDescription: {,
  fontSize: 16,
    color: colors.textSecondary,
    textAlign: center",
    lineHeight: 24;
  },
  methodsSection: { paddingBottom: spacing.lg  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: "600,",
    color: colors.textPrimary,
    marginBottom: spacing.md;
  },
  methodCard: {,
  flexDirection: "row",
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 2,
    borderColor: transparent""
  },
  selectedMethodCard: {,
  borderColor: colors.primary,
    backgroundColor: colors.primary + "10"
  },
  disabledMethodCard: { opacity: 0.6  },
  methodIcon: {,
  width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: "center",
    alignItems: center",
    marginRight: spacing.md;
  },
  methodInfo: { flex: 1  },
  methodHeader: {,
  flexDirection: "row,",
    justifyContent: "space-between",
    alignItems: center",
    marginBottom: spacing.xs;
  },
  methodName: {,
  fontSize: 18,
    fontWeight: "600,",
    color: colors.textPrimary;
  },
  statusBadge: {,
  paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 12,
    backgroundColor: colors.primary + "20"
  },
  accuracyText: {,
  fontSize: 12,
    fontWeight: 600",
    color: colors.primary;
  },
  comingSoonText: {,
  fontSize: 12,
    fontWeight: "600,",
    color: colors.warning;
  },
  maintenanceText: {,
  fontSize: 12,
    fontWeight: "600",
    color: colors.error;
  },
  methodDescription: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    lineHeight: 20;
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
  detailsAccuracy: {,
  fontSize: 14,
    color: colors.textSecondary;
  },
  detailsDescription: {,
  fontSize: 16,
    color: colors.textSecondary,
    lineHeight: 24,
    marginBottom: spacing.md;
  },
  detailsFeatures: { marginTop: spacing.sm  },
  detailsFeaturesTitle: {,
  fontSize: 16,
    fontWeight: 600",
    color: colors.textPrimary,
    marginBottom: spacing.sm;
  },
  detailsFeatureItem: {,
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
  disabledButton: { opacity: 0.6  },
  startButtonText: {,
  fontSize: 16,
    fontWeight: "600,",
    color: "white",'
    marginLeft: spacing.sm;
  }
}), []);
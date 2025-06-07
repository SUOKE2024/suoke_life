import React, { useState, useRef, useMemo, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  Alert,
  Animated,
  ScrollView,
  Dimensions
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import Icon from "../../../components/common/Icon";
import { colors, spacing } from "../../../constants/theme";
import { usePerformanceMonitor } from "../../../hooks/usePerformanceMonitor";

interface ARConstitutionVisualizationProps {
  visible: boolean;
  onClose: () => void;
}

interface AcupointData {
  id: string;
  name: string;
  chineseName: string;
  meridian: string;
  position: { x: number; y: number; z: number };
  functions: string[];
  indications: string[];
  color: string;
}

interface MeridianData {
  id: string;
  name: string;
  chineseName: string;
  element: string;
  color: string;
  points: AcupointData[];
  pathData: string;
}

interface ConstitutionVisualization {
  type: string;
  name: string;
  characteristics: string[];
  color: string;
  intensity: number;
  regions: string[];
}

export const ARConstitutionVisualization: React.FC<ARConstitutionVisualizationProps> = ({
  visible,
  onClose
}) => {
  const performanceMonitor = usePerformanceMonitor("ARConstitutionVisualization", {
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50
  });

  const [activeView, setActiveView] = useState<"constitution" | "meridians" | "acupoints" | "ar">("constitution");
  const [selectedMeridian, setSelectedMeridian] = useState<string | null>(null);
  const [selectedAcupoint, setSelectedAcupoint] = useState<AcupointData | null>(null);
  const [arMode, setArMode] = useState<boolean>(false);
  
  const rotationAnim = useMemo(() => useRef(new Animated.ValueXY()).current, []);
  const scaleAnim = useMemo(() => useRef(new Animated.Value(1)).current, []);

  const [constitutionData] = useState<ConstitutionVisualization[]>([
    {
      type: "balanced",
      name: "平和质",
      characteristics: ["气血调和", "脏腑功能正常", "体态适中"],
      color: "#4ECDC4",
      intensity: 0.8,
      regions: ["全身均衡"]
    },
    {
      type: "qi_deficiency",
      name: "气虚质",
      characteristics: ["气力不足", "容易疲劳", "声音低弱"],
      color: "#FFE66D",
      intensity: 0.6,
      regions: ["脾胃", "肺部", "心脏"]
    }
  ]);

  const [meridiansData] = useState<MeridianData[]>([
    {
      id: "lung",
      name: "Lung Meridian",
      chineseName: "手太阴肺经",
      element: "金",
      color: "#E8F4FD",
      points: [
        {
          id: "LU1",
          name: "Zhongfu",
          chineseName: "中府",
          meridian: "肺经",
          position: { x: 0.2, y: 0.3, z: 0.1 },
          functions: ["宣肺理气", "止咳平喘"],
          indications: ["咳嗽", "气喘", "胸痛"],
          color: "#007AFF"
        }
      ],
      pathData: "M0.2,0.3 Q0.18,0.5 0.15,0.7"
    }
  ]);

  const startARMode = useCallback(() => {
    Alert.alert(
      "AR模式",
      "即将启动AR相机模式，请确保设备支持ARKit/ARCore",
      [
        { text: "取消", style: "cancel" },
        { text: "启动", onPress: () => setArMode(true) }
      ]
    );
  }, []);

  const renderConstitutionView = useMemo(() => (
    <View style={styles.viewContent}>
      <Text style={styles.viewTitle}>体质可视化分析</Text>
      <View style={styles.humanModel}>
        <Animated.View
          style={[
            styles.modelContainer,
            {
              transform: [
                {
                  rotateY: rotationAnim.x.interpolate({
                    inputRange: [-100, 100],
                    outputRange: ["-30deg", "30deg"]
                  })
                },
                { scale: scaleAnim }
              ]
            }
          ]}
        >
          <View style={styles.humanSilhouette}>
            <Text style={styles.modelLabel}>3D人体模型</Text>
            {constitutionData.map((constitution, index) => (
              <View
                key={constitution.type}
                style={[
                  styles.constitutionRegion,
                  {
                    backgroundColor: constitution.color + "40",
                    opacity: constitution.intensity
                  }
                ]}
              >
                <Text style={styles.regionLabel}>{constitution.name}</Text>
              </View>
            ))}
          </View>
        </Animated.View>
      </View>

      <View style={styles.constitutionLegend}>
        {constitutionData.map((constitution) => (
          <View key={constitution.type} style={styles.constitutionItem}>
            <View style={[styles.constitutionDot, { backgroundColor: constitution.color }]} />
            <View style={styles.constitutionInfo}>
              <Text style={styles.constitutionName}>{constitution.name}</Text>
              <Text style={styles.constitutionDesc}>
                {constitution.characteristics.join("、")}
              </Text>
            </View>
            <Text style={styles.intensityText}>{Math.round(constitution.intensity * 100)}%</Text>
          </View>
        ))}
      </View>
    </View>
  ), [constitutionData, rotationAnim, scaleAnim]);

  const renderMeridiansView = useMemo(() => (
    <View style={styles.viewContent}>
      <Text style={styles.viewTitle}>经络系统</Text>
      <View style={styles.meridiansContainer}>
        {meridiansData.map((meridian) => (
          <TouchableOpacity
            key={meridian.id}
            style={[
              styles.meridianCard,
              { borderLeftColor: meridian.color },
              selectedMeridian === meridian.id && styles.selectedMeridianCard
            ]}
            onPress={() =>
              setSelectedMeridian(
                selectedMeridian === meridian.id ? null : meridian.id
              )
            }
            accessibilityLabel={`选择${meridian.chineseName}经络`}
          >
            <View style={styles.meridianHeader}>
              <Text style={styles.meridianName}>{meridian.chineseName}</Text>
              <Text style={styles.meridianElement}>五行: {meridian.element}</Text>
            </View>
            <Text style={styles.meridianEnglish}>{meridian.name}</Text>
            <Text style={styles.pointCount}>{meridian.points.length} 个穴位</Text>

            {selectedMeridian === meridian.id && (
              <View style={styles.meridianDetails}>
                <Text style={styles.detailTitle}>主要穴位:</Text>
                {meridian.points.map((point) => (
                  <TouchableOpacity
                    key={point.id}
                    style={styles.pointItem}
                    onPress={() => setSelectedAcupoint(point)}
                    accessibilityLabel={`查看${point.chineseName}穴位详情`}
                  >
                    <Text style={styles.pointName}>{point.chineseName} ({point.name})</Text>
                    <Text style={styles.pointFunctions}>
                      {point.functions.join("、")}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </TouchableOpacity>
        ))}
      </View>
    </View>
  ), [meridiansData, selectedMeridian]);

  const renderAcupointsView = useMemo(() => (
    <View style={styles.viewContent}>
      <Text style={styles.viewTitle}>穴位详解</Text>
      {selectedAcupoint ? (
        <View style={styles.acupointDetail}>
          <View style={styles.acupointHeader}>
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => setSelectedAcupoint(null)}
              accessibilityLabel="返回穴位列表"
            >
              <Icon name="arrow-left" size={20} color={colors.primary} />
            </TouchableOpacity>
            <Text style={styles.acupointTitle}>
              {selectedAcupoint.chineseName} ({selectedAcupoint.name})
            </Text>
          </View>

          <View style={styles.acupointInfo}>
            <View style={styles.infoSection}>
              <Text style={styles.infoLabel}>所属经络:</Text>
              <Text style={styles.infoValue}>{selectedAcupoint.meridian}</Text>
            </View>

            <View style={styles.infoSection}>
              <Text style={styles.infoLabel}>主要功能:</Text>
              {selectedAcupoint.functions.map((func, index) => (
                <Text key={index} style={styles.functionItem}>• {func}</Text>
              ))}
            </View>

            <View style={styles.infoSection}>
              <Text style={styles.infoLabel}>主治病症:</Text>
              {selectedAcupoint.indications.map((indication, index) => (
                <Text key={index} style={styles.indicationItem}>• {indication}</Text>
              ))}
            </View>

            <View style={styles.acupointPosition}>
              <Text style={styles.positionLabel}>3D位置坐标:</Text>
              <Text style={styles.positionValue}>
                X: {selectedAcupoint.position.x.toFixed(2)},
                Y: {selectedAcupoint.position.y.toFixed(2)},
                Z: {selectedAcupoint.position.z.toFixed(2)}
              </Text>
            </View>
          </View>
        </View>
      ) : (
        <View style={styles.acupointsList}>
          <Text style={styles.instructionText}>选择经络查看穴位详情</Text>
          {meridiansData.map((meridian) => (
            <View key={meridian.id} style={styles.meridianGroup}>
              <Text style={styles.groupTitle}>{meridian.chineseName}</Text>
              <View style={styles.pointsGrid}>
                {meridian.points.map((point) => (
                  <TouchableOpacity
                    key={point.id}
                    style={[styles.pointButton, { borderColor: point.color }]}
                    onPress={() => setSelectedAcupoint(point)}
                    accessibilityLabel={`查看${point.chineseName}穴位`}
                  >
                    <Text style={styles.pointButtonText}>{point.chineseName}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          ))}
        </View>
      )}
    </View>
  ), [selectedAcupoint, meridiansData]);

  const renderARView = useMemo(() => (
    <View style={styles.viewContent}>
      <Text style={styles.viewTitle}>AR体质可视化</Text>
      <View style={styles.arContainer}>
        <Text style={styles.arPlaceholder}>AR相机视图</Text>
        <Text style={styles.arInstructions}>
          请将设备对准身体部位，系统将实时显示体质分析结果
        </Text>
        <TouchableOpacity style={styles.arButton} onPress={startARMode}>
          <Text style={styles.arButtonText}>启动AR模式</Text>
        </TouchableOpacity>
      </View>
    </View>
  ), [startARMode]);

  const renderTabBar = () => (
    <View style={styles.tabBar}>
      {[
        { key: "constitution", label: "体质分析" },
        { key: "meridians", label: "经络系统" },
        { key: "acupoints", label: "穴位详解" },
        { key: "ar", label: "AR可视化" }
      ].map((tab) => (
        <TouchableOpacity
          key={tab.key}
          style={[
            styles.tabItem,
            activeView === tab.key && styles.activeTabItem
          ]}
          onPress={() => setActiveView(tab.key as any)}
          accessibilityLabel={`切换到${tab.label}`}
        >
          <Text
            style={[
              styles.tabText,
              activeView === tab.key && styles.activeTabText
            ]}
          >
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderContent = () => {
    switch (activeView) {
      case "constitution":
        return renderConstitutionView;
      case "meridians":
        return renderMeridiansView;
      case "acupoints":
        return renderAcupointsView;
      case "ar":
        return renderARView;
      default:
        return renderConstitutionView;
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="fullScreen"
      onRequestClose={onClose}
    >
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={onClose}
            accessibilityLabel="关闭AR体质可视化"
          >
            <Icon name="close" size={24} color={colors.text} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>AR体质可视化</Text>
          <View style={styles.placeholder} />
        </View>

        {renderTabBar()}

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {renderContent()}
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
};

const { width, height } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  closeButton: {
    padding: spacing.xs
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text
  },
  placeholder: {
    width: 32
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  tabItem: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: 'center'
  },
  activeTabItem: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primary
  },
  tabText: {
    fontSize: 14,
    color: colors.textSecondary
  },
  activeTabText: {
    color: colors.primary,
    fontWeight: 'bold'
  },
  content: {
    flex: 1
  },
  viewContent: {
    padding: spacing.md
  },
  viewTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.md,
    textAlign: 'center'
  },
  humanModel: {
    height: 300,
    backgroundColor: colors.surface,
    borderRadius: 12,
    marginBottom: spacing.md,
    justifyContent: 'center',
    alignItems: 'center'
  },
  modelContainer: {
    width: 200,
    height: 250,
    justifyContent: 'center',
    alignItems: 'center'
  },
  humanSilhouette: {
    width: '100%',
    height: '100%',
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modelLabel: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: 'center'
  },
  constitutionRegion: {
    position: 'absolute',
    width: 60,
    height: 40,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center'
  },
  regionLabel: {
    fontSize: 10,
    color: colors.text,
    fontWeight: 'bold'
  },
  constitutionLegend: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md
  },
  constitutionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm
  },
  constitutionDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: spacing.sm
  },
  constitutionInfo: {
    flex: 1
  },
  constitutionName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text
  },
  constitutionDesc: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2
  },
  intensityText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.primary
  },
  meridiansContainer: {
    gap: spacing.sm
  },
  meridianCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    borderLeftWidth: 4
  },
  selectedMeridianCard: {
    borderColor: colors.primary,
    borderWidth: 1
  },
  meridianHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs
  },
  meridianName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text
  },
  meridianElement: {
    fontSize: 12,
    color: colors.textSecondary
  },
  meridianEnglish: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs
  },
  pointCount: {
    fontSize: 12,
    color: colors.primary
  },
  meridianDetails: {
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border
  },
  detailTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.xs
  },
  pointItem: {
    padding: spacing.sm,
    backgroundColor: colors.background,
    borderRadius: 8,
    marginBottom: spacing.xs
  },
  pointName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.text
  },
  pointFunctions: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2
  },
  acupointDetail: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md
  },
  acupointHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md
  },
  backButton: {
    padding: spacing.xs,
    marginRight: spacing.sm
  },
  acupointTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    flex: 1
  },
  acupointInfo: {
    gap: spacing.md
  },
  infoSection: {
    backgroundColor: colors.background,
    borderRadius: 8,
    padding: spacing.sm
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.xs
  },
  infoValue: {
    fontSize: 14,
    color: colors.textSecondary
  },
  functionItem: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 2
  },
  indicationItem: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 2
  },
  acupointPosition: {
    backgroundColor: colors.background,
    borderRadius: 8,
    padding: spacing.sm
  },
  positionLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.xs
  },
  positionValue: {
    fontSize: 14,
    color: colors.textSecondary,
    fontFamily: 'monospace'
  },
  acupointsList: {
    gap: spacing.md
  },
  instructionText: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.md
  },
  meridianGroup: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md
  },
  groupTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.sm
  },
  pointsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs
  },
  pointButton: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 16,
    borderWidth: 1,
    backgroundColor: colors.background
  },
  pointButtonText: {
    fontSize: 12,
    color: colors.text
  },
  arContainer: {
    height: 400,
    backgroundColor: colors.surface,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.md
  },
  arPlaceholder: {
    fontSize: 18,
    color: colors.textSecondary,
    marginBottom: spacing.md
  },
  arInstructions: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.lg
  },
  arButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: 8
  },
  arButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.white
  }
});
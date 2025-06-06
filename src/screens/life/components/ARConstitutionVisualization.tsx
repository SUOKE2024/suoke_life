import { SafeAreaView } from "react-native-safe-area-context";
import { usePerformanceMonitor  } from "../../placeholder";../hooks/usePerformanceMonitor";/////      View,"

import React from "react";
importIcon from ";../../../components/common/Icon"/import { colors, spacing } from ../../../constants/theme"// ";
importReact,{ useState, useRef } from "react";
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  Alert,
  { Animated } from react-native
interface ARConstitutionVisualizationProps { visible: boolean,
  onClose: () => void}
interface AcupointData { id: string,
  name: string,
  chineseName: string,
  meridian: string,
  position: { x: number, y: number, z: number},
  functions: string[],
  indications: string[],
  color: string}
interface MeridianData { id: string,
  name: string,
  chineseName: string,
  element: string,
  color: string,
  points: AcupointData[],
  pathData: string}
interface ConstitutionVisualization { type: string,
  name: string,
  characteristics: string[],
  color: string,
  intensity: number,
  regions: string[]
  }
export const ARConstitutionVisualization: React.FC<ARConstitutionVisualizationProps /> = ({/  // 性能监控 // const performanceMonitor = usePerformanceMonitor("ARConstitutionVisualization, ";
{/////
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50, // ms // });
  visible,
  onClose;
}) => {}
  const [activeView, setActiveView] = useState<"constitution" | meridians" | "acupoints | "ar">(constitution");"
  const [selectedMeridian, setSelectedMeridian] = useState<string | null>(nul;l;);
  const [selectedAcupoint, setSelectedAcupoint] = useState<AcupointData | null />(nul;l;);/////      const [arMode, setArMode] = useState<boolean>(fals;e;);
  const rotationAnim = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useRef(new Animated.ValueXY();).current, []);)))));
  const scaleAnim = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useRef(new Animated.Value(1);).current, []);)))));
  // 模拟体质可视化数据 // const [constitutionData] = useState<ConstitutionVisualization[]  / >([ * { ////
      type: "balanced,",
      name: "平和质",
      characteristics: [气血调和", "脏腑功能正常, "体态适中"],
      color: #4ECDC4","
      intensity: 0.8,
      regions: ["全身均衡]"
    },
    {type: "qi_deficiency",name: 气虚质",";
      characteristics: ["气力不足, "容易疲劳", 声音低弱"],color: "#FFE66D,",intensity: 0.6,regions: ["脾胃", 肺部", "心脏];
    },{type: "yin_deficiency",name: 阴虚质",";
      characteristics: ["阴液不足, "虚热内扰", 口干咽燥"],color: "#FF6B6B,",intensity: 0.7,regions: ["肾脏", 肝脏", "心脏];
    },;];)
  // 模拟经络数据 // const [meridiansData] = useState<MeridianData[]  / >([ * { ////;
      id: "lung",name: Lung Meridian",";
      chineseName: "手太阴肺经,",element: "金",color: #E8F4FD",";
      points: ;[{
          id: "LU1,",
          name: "Zhongfu",
          chineseName: 中府","
          meridian: "肺经,",
          position: { x: 0.2, y: 0.3, z: 0.1},
          functions: ["宣肺理气", 止咳平喘"],"
          indications: ["咳嗽, "气喘", 胸痛"],
          color: "#007AFF"
        },
        {
          id: "LU9",
          name: Taiyuan","
          chineseName: "太渊,",
          meridian: "肺经",
          position: { x: 0.15, y: 0.7, z: 0.05},
          functions: [补肺益气", "通调血脉],
          indications: ["咳嗽", 气短", "脉象异常],
          color: "#007AFF"
        }
      ],
      pathData: M0.2,0.3 Q0.18,0.5 0.15,0.7""
    },
    {
      id: "heart,",
      name: "Heart Meridian",
      chineseName: 手少阴心经","
      element: "火,",
      color: "#FFE8E8",
      points: [{
          id: HT7","
          name: "Shenmen,",
          chineseName: "神门",
          meridian: 心经","
          position: { x: 0.12, y: 0.72, z: 0.02},
          functions: ["宁心安神, "清心火"],"
          indications: [失眠", "健忘, "心悸"],
          color: #FF2D92""
        }
      ],
      pathData: "M0.1,0.4 Q0.11,0.6 0.12,0.72"
    }
  ]);
  const startARMode = useCallback(() => {
    Alert.alert(
      "AR模式",
      即将启动AR相机模式，请确保设备支持ARKit/ARCore",/////          ["
        { text: "取消, style: "cancel"},"
        { text: 启动", onPress: (); => setArMode(true) }"
      ]
    );
  };
  // TODO: 将内联组件移到组件外部 * const renderConstitutionView = useMemo(() => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => () => ( ////
    <View style={styles.viewContent} />/      <Text style={styles.viewTitle} />体质可视化分析</Text>/////
      <View style={styles.humanModel} />/////            <Animated.View;
style={[
            styles.modelContainer,
            {
              transform: [{ rotateY: rotationAnim.x.interpolate({
                  inputRange: [-100, 100],
                  outputRange: ["-30deg, "30deg"]"
                }) },
                { rotateX: rotationAnim.y.interpolate({
                  inputRange: [-100, 100],
                  outputRange: [30deg", "-30deg]
                }) },
                { scale: scaleAnim}
              ]
            }
          ]} />/          {// 人体轮廓 }/          <View style={styles.humanSilhouette} />/            <Text style={styles.modelLabel} />3D人体模型</Text>/////
            {// 体质区域高亮 }/////                {constitutionData.map((constitution, index) => (
              <View;
key={constitution.type}
                style={[
                  styles.constitutionRegion,
                  {
                    backgroundColor: constitution.color + "40",
                    top: `${20 + index * 25}%`,
                    opacity: constitution.intensity;
                  }
                ]} />/                <Text style={styles.regionLabel} />{constitution.name}</Text>/              </View>/////                ))}
          </View>/        </Animated.View>/      </View>/////
      <View style={styles.constitutionLegend} />/////            {constitutionData.map((constitution) => (
          <View key={constitution.type} style={styles.constitutionItem} />/            <View style={[styles.constitutionDot, { backgroundColor: constitution.color}]} />/            <View style={styles.constitutionInfo} />/              <Text style={styles.constitutionName} />{constitution.name}</Text>/              <Text style={styles.constitutionDesc} />/////                    {constitution.characteristics.join(, ")}"
              </Text>/            </View>/            <Text style={styles.intensityText} />{Math.round(constitution.intensity * 100)}%</Text>/          </View>/////            ))}
      </View>/    </View>/////      ), []);
  // TODO: 将内联组件移到组件外部 * const renderMeridiansView = useMemo(() => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => () => ( ////
    <View style={styles.viewContent} />/      <Text style={styles.viewTitle} />经络系统</Text>/////
      <View style={styles.meridiansContainer} />/////            {meridiansData.map((meridian) => (
          <TouchableOpacity;
key={meridian.id}
            style={[
              styles.meridianCard,
              { borderLeftColor: meridian.color},
              selectedMeridian === meridian.id && styles.selectedMeridianCard;
            ]}
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setSelectedMeridian(/              selectedMeridian === meridian.id ? null : meridian.id////
            )}
          >
            <View style={styles.meridianHeader} />/              <Text style={styles.meridianName} />{meridian.chineseName}</Text>/              <Text style={styles.meridianElement} />五行: {meridian.element}</Text>/            </View>/            <Text style={styles.meridianEnglish} />{meridian.name}</Text>/            <Text style={styles.pointCount} />{meridian.points.length} 个穴位</Text>/////
            {selectedMeridian === meridian.id && (
              <View style={styles.meridianDetails} />/                <Text style={styles.detailTitle} />主要穴位:</Text>/////                    {meridian.points.map((point) => (
                  <TouchableOpacity;
key={point.id}
                    style={styles.pointItem}
                    onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setSelectedAcupoint(point)}/////                      >
                    <Text style={styles.pointName} />{point.chineseName} ({point.name})</Text>/                    <Text style={styles.pointFunctions} />/////                          {point.functions.join(" )}"
                    </Text>/                  </TouchableOpacity>/////                    ))}
              </View>/////                )}
          </TouchableOpacity>/////            ))}
      </View>/    </View>/////      ), []);
  // TODO: 将内联组件移到组件外部 * const renderAcupointsView = useMemo(() => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => () => ( ////
    <View style={styles.viewContent} />/      <Text style={styles.viewTitle} />穴位详解</Text>/////
      {selectedAcupoint ? (
        <View style={styles.acupointDetail} />/          <View style={styles.acupointHeader} />/////                <TouchableOpacity;
style={styles.backButton}
              onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setSelectedAcupoint(null)}/////                >
              <Icon name="arrow-left" size={20} color={colors.primary} />/            </TouchableOpacity>/            <Text style={styles.acupointTitle} />/////                  {selectedAcupoint.chineseName} ({selectedAcupoint.name});
            </Text>/          </View>/////
          <View style={styles.acupointInfo} />/            <View style={styles.infoSection} />/              <Text style={styles.infoLabel} />所属经络:</Text>/              <Text style={styles.infoValue} />{selectedAcupoint.meridian}</Text>/            </View>/////
            <View style={styles.infoSection} />/              <Text style={styles.infoLabel} />主要功能:</Text>/////                  {selectedAcupoint.functions.map((func, index); => (
                <Text key={index} style={styles.functionItem} />• {func}</Text>/////                  ))}
            </View>/////
            <View style={styles.infoSection} />/              <Text style={styles.infoLabel} />主治病症:</Text>/////                  {selectedAcupoint.indications.map((indication, index); => (
                <Text key={index} style={styles.indicationItem} />• {indication}</Text>/////                  ))}
            </View>/////
            <View style={styles.acupointPosition} />/              <Text style={styles.positionLabel} />3D位置坐标:</Text>/              <Text style={styles.positionValue} />/////                    X: {selectedAcupoint.position.x.toFixed(2)},
                Y: {selectedAcupoint.position.y.toFixed(2)},
                Z: {selectedAcupoint.position.z.toFixed(2)}
              </Text>/            </View>/          </View>/        </View>/////          ) : (
        <View style={styles.acupointsList} />/          <Text style={styles.instructionText} />选择经络查看穴位详情</Text>/////              {meridiansData.map((meridian); => (
            <View key={meridian.id} style={styles.meridianGroup} />/              <Text style={styles.groupTitle} />{meridian.chineseName}</Text>/              <View style={styles.pointsGrid} />/////                    {meridian.points.map((point) => (
                  <TouchableOpacity;
key={point.id}
                    style={[styles.pointButton, { borderColor: point.color}]}
                    onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setSelectedAcupoint(point)}/////                      >
                    <Text style={styles.pointButtonText} />{point.chineseName}</Text>/                  </TouchableOpacity>/////                    ))}
              </View>/            </View>/////              ))}
        </View>/////          )}
    </View>/////      ), []);
  // TODO: 将内联组件移到组件外部 * const renderARView = useMemo(() => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => () => ( ////
    <View style={styles.viewContent} />/      <Text style={styles.viewTitle} />AR增强现实</Text>/////
      {arMode ? (
        <View style={styles.arCamera} />/          <Text style={styles.arPlaceholder} />AR相机视图</Text>/          <Text style={styles.arInstructions} />/////                将设备对准身体部位，查看经络穴位信息
          </Text>/////
          <View style={styles.arControls} />/            <TouchableOpacity style={styles.arButton} accessibilityLabel="TODO: 添加无障碍标签" />/              <Icon name="target" size={24} color="white" />/              <Text style={styles.arButtonText} />定位穴位</Text>/            </TouchableOpacity>/            <TouchableOpacity style={styles.arButton} accessibilityLabel="TODO: 添加无障碍标签" />/              <Icon name="eye" size={24} color="white" />/              <Text style={styles.arButtonText} />显示经络</Text>/            </TouchableOpacity>/          </View>/////
          <TouchableOpacity;
style={styles.exitArButton}
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setArMode(false)}/////              >
            <Text style={styles.exitArText} />退出AR模式</Text>/          </TouchableOpacity>/        </View>/////          ) : (
        <View style={styles.arIntro} />/          <Icon name="camera-3d" size={80} color={colors.primary} />/          <Text style={styles.arTitle} />AR体质可视化</Text>/          <Text style={styles.arDescription} />/////                使用增强现实技术，在真实环境中查看经络穴位分布，
            获得更直观的中医理论学习体验。
          </Text>/////
          <View style={styles.arFeatures} />/            <View style={styles.featureItem} />/              <Icon name="eye-outline" size={24} color={colors.primary} />/              <Text style={styles.featureText} />实时穴位定位</Text>/            </View>/            <View style={styles.featureItem} />/              <Icon name="gesture-tap" size={24} color={colors.primary} />/              <Text style={styles.featureText} />交互式学习</Text>/            </View>/            <View style={styles.featureItem} />/              <Icon name="chart-line" size={24} color={colors.primary} />/              <Text style={styles.featureText} />体质分析</Text>/            </View>/          </View>/////
          <TouchableOpacity style={styles.startArButton} onPress={startARMode} accessibilityLabel="TODO: 添加无障碍标签" />/            <Icon name="camera" size={20} color="white" />/            <Text style={styles.startArText} />启动AR模式</Text>/          </TouchableOpacity>/        </View>/////          )}
    </View>/////      ), []);
  // TODO: 将内联组件移到组件外部 * const renderTabBar = useMemo(() => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => () => ( ////
    <View style={styles.tabBar} />/////          {[
        { key: "constitution", label: 体质分析", icon: "human},
        { key: "meridians", label: 经络系统", icon: "timeline},
        { key: "acupoints", label: 穴位详解", icon: "target},
        { key: "ar", label: AR可视化", icon: "camera-3d}
      ].map((tab) => (
        <TouchableOpacity;
key={tab.key}
          style={[styles.tabButton, activeView === tab.key && styles.activeTabButton]}
          onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setActiveView(tab.key as any)}/////            >
          <Icon;
name={tab.icon}
            size={20}
            color={activeView === tab.key ? colors.primary: colors.textSecondary} />///            <Text style={[ ///  >
            styles.tabText,
            activeView === tab.key && styles.activeTabText;
          ]} />/////                {tab.label}
          </Text>/        </TouchableOpacity>/////          ))}
    </View>/////      ), []);
  const renderContent = useCallback(() => {
    switch (activeView) {case "constitution": return renderConstitutionView;(;)
      case meridians": return renderMeridiansView;(;)"
      case "acupoints: return renderAcupointsView;(;)"
      case "ar": return renderARView;
      default: return renderConstitutionView;
    }
  };
  // 记录渲染性能 // performanceMonitor.recordRender();
  return (;
    <Modal visible={visible} animationType="slide" presentationStyle="fullScreen" />/      <SafeAreaView style={styles.container} />/        {// 头部 }/        <View style={styles.header} />/          <TouchableOpacity onPress={onClose} style={styles.closeButton} accessibilityLabel="TODO: 添加无障碍标签" />/            <Icon name="close" size={24} color={colors.text} />/          </TouchableOpacity>/          <View style={styles.headerContent} />/            <Text style={styles.title} />AR体质可视化</Text>/            <Text style={styles.subtitle} />经络穴位 • 体质分析 • 增强现实</Text>/          </View>/          <TouchableOpacity style={styles.helpButton} accessibilityLabel="TODO: 添加无障碍标签" />/            <Icon name="help-circle" size={24} color={colors.primary} />/          </TouchableOpacity>/        </View>/////;
        {// 标签栏 }/////            {renderTabBar()};
        {// 内容区域 }/        <View style={styles.content} />/////              {renderContent()};
        </View>/      </SafeAreaView>/    </Modal>/////      ;);
};
const styles = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => StyleSheet.create({container: {
    flex: 1,
    backgroundColor: colors.background;
  },
  header: {
    flexDirection: row","
    alignItems: "center,",
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border;
  },
  closeButton: { padding: spacing.sm  },
  headerContent: {
    flex: 1,
    marginLeft: spacing.md;
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    color: colors.text;
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 2;
  },
  helpButton: { padding: spacing.sm  },
  tabBar: {
    flexDirection: row","
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.sm;
  },
  tabButton: {
    flex: 1,
    alignItems: "center,",
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm;
  },
  activeTabButton: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primary;
  },
  tabText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: spacing.xs;
  },
  activeTabText: {
    color: colors.primary,
    fontWeight: "600"
  },
  content: { flex: 1  },
  viewContent: {
    flex: 1,
    padding: spacing.lg;
  },
  viewTitle: {
    fontSize: 18,
    fontWeight: 600","
    color: colors.text,
    marginBottom: spacing.lg;
  },
  humanModel: {
    height: 300,
    backgroundColor: colors.surface,
    borderRadius: 12,
    marginBottom: spacing.lg,
    justifyContent: "center,",
    alignItems: "center"
  },
  modelContainer: {
    width: 200,
    height: 250,
    justifyContent: center","
    alignItems: "center"
  },
  humanSilhouette: {
    width: "100%",
    height: 100%","
    backgroundColor: colors.background,
    borderRadius: 8,
    justifyContent: "center,",
    alignItems: "center",
    position: relative""
  },
  modelLabel: {
    fontSize: 16,
    color: colors.textSecondary,
    marginBottom: spacing.md;
  },
  constitutionRegion: {
    position: "absolute,",
    width: "80%",
    height: 40,
    borderRadius: 20,
    justifyContent: center","
    alignItems: "center"
  },
  regionLabel: {
    fontSize: 12,
    color: colors.text,
    fontWeight: "600"
  },
  constitutionLegend: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md;
  },
  constitutionItem: {
    flexDirection: row","
    alignItems: "center,",
    paddingVertical: spacing.sm;
  },
  constitutionDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: spacing.sm;
  },
  constitutionInfo: { flex: 1  },
  constitutionName: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.text;
  },
  constitutionDesc: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2;
  },
  intensityText: {
    fontSize: 14,
    fontWeight: bold","
    color: colors.primary;
  },
  meridiansContainer: { flex: 1  },
  meridianCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderLeftWidth: 4;
  },
  selectedMeridianCard: {
    borderColor: colors.primary,
    borderWidth: 1;
  },
  meridianHeader: {
    flexDirection: "row,",
    justifyContent: "space-between",
    alignItems: center","
    marginBottom: spacing.xs;
  },
  meridianName: {
    fontSize: 16,
    fontWeight: "600,",
    color: colors.text;
  },
  meridianElement: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: "500"
  },
  meridianEnglish: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing.xs;
  },
  pointCount: {
    fontSize: 12,
    color: colors.textSecondary;
  },
  meridianDetails: {
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border;
  },
  detailTitle: {
    fontSize: 14,
    fontWeight: 600","
    color: colors.text,
    marginBottom: spacing.sm;
  },
  pointItem: {
    paddingVertical: spacing.xs,
    paddingLeft: spacing.md;
  },
  pointName: {
    fontSize: 14,
    color: colors.text,
    fontWeight: "500"
  },
  pointFunctions: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2;
  },
  acupointDetail: { flex: 1  },
  acupointHeader: {
    flexDirection: "row",
    alignItems: center","
    marginBottom: spacing.lg;
  },
  backButton: {
    padding: spacing.sm,
    marginRight: spacing.md;
  },
  acupointTitle: {
    fontSize: 18,
    fontWeight: "600,",
    color: colors.text;
  },
  acupointInfo: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg;
  },
  infoSection: { marginBottom: spacing.lg  },
  infoLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.text,
    marginBottom: spacing.sm;
  },
  infoValue: {
    fontSize: 14,
    color: colors.textSecondary;
  },
  functionItem: {
    fontSize: 14,
    color: colors.text,
    marginBottom: spacing.xs;
  },
  indicationItem: {
    fontSize: 14,
    color: colors.text,
    marginBottom: spacing.xs;
  },
  acupointPosition: {
    backgroundColor: colors.background,
    padding: spacing.md,
    borderRadius: 8;
  },
  positionLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing.xs;
  },
  positionValue: {
    fontSize: 12,
    fontFamily: monospace","
    color: colors.text;
  },
  acupointsList: { flex: 1  },
  instructionText: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: "center,",
    marginBottom: spacing.lg;
  },
  meridianGroup: { marginBottom: spacing.lg  },
  groupTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: colors.text,
    marginBottom: spacing.md;
  },
  pointsGrid: {
    flexDirection: row","
    flexWrap: "wrap"
  },
  pointButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    borderWidth: 1,
    marginRight: spacing.sm,
    marginBottom: spacing.sm;
  },
  pointButtonText: {
    fontSize: 12,
    color: colors.text;
  },
  arCamera: {
    flex: 1,
    backgroundColor: "#000",
    borderRadius: 12,
    justifyContent: center","
    alignItems: "center,",
    position: "relative"
  },
  arPlaceholder: {
    fontSize: 24,
    color: white","
    fontWeight: "bold,",
    marginBottom: spacing.md;
  },
  arInstructions: {
    fontSize: 16,
    color: "white",
    textAlign: center","
    marginBottom: spacing.xl,
    paddingHorizontal: spacing.lg;
  },
  arControls: {
    flexDirection: "row,",
    position: "absolute",
    bottom: 100;
  },
  arButton: {
    flexDirection: row","
    alignItems: "center,",
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: 25,
    marginHorizontal: spacing.sm;
  },
  arButtonText: {
    color: "white",
    fontSize: 14,
    fontWeight: 600","
    marginLeft: spacing.sm;
  },
  exitArButton: {
    position: "absolute,",
    top: spacing.lg,
    right: spacing.lg,
    backgroundColor: "rgba(0,0,0,0.5)",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20;
  },
  exitArText: {
    color: white","
    fontSize: 14;
  },
  arIntro: {
    flex: 1,
    justifyContent: "center,",
    alignItems: "center"
  },
  arTitle: {
    fontSize: 24,
    fontWeight: bold","
    color: colors.text,
    marginTop: spacing.lg,
    marginBottom: spacing.md;
  },
  arDescription: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: "center,",
    lineHeight: 24,
    marginBottom: spacing.xl,
    paddingHorizontal: spacing.lg;
  },
  arFeatures: { marginBottom: spacing.xl  },
  featureItem: {
    flexDirection: "row",
    alignItems: center","
    marginBottom: spacing.md;
  },
  featureText: {
    fontSize: 16,
    color: colors.text,
    marginLeft: spacing.md;
  },
  startArButton: {
    flexDirection: "row,",
    alignItems: "center",
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: 25;
  },
  startArText: {
    color: white","
    fontSize: 16,
    fontWeight: '600',
    marginLeft: spacing.sm;
  }
}), []);
export default React.memo(ARConstitutionVisualization);

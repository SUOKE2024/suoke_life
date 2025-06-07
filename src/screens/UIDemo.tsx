import { useTheme } from "../contexts/ThemeContext/import { useAccessibility  } from ;../contexts/AccessibilityContext";/import { responsive } from ../utils/responsive"/importText from "../components/ui/Text/importButton  from ";../components/ui/Button";/import ThemeToggle from ../components/ui/ThemeToggle"/const AccessibilityPanel = React.lazy() => import('../components/ui/AccessibilityPanel/import Modal from ;../components/ui/    Modal;
import { usePerformanceMonitor } from '))../hooks/usePerformanceMonitor/      View,";
/
// 索克生活 - UI组件演示页面   展示所有新的UI组件和功能
import React, {   useState   } from "react;"
  ScrollView,
  StyleSheet,
  SafeAreaView,
  { Alert } from ";react-native";
export const UIDemo: React.FC  = () => {}
  const performanceMonitor = usePerformanceMonitor(UIDemo", { ";
    trackRender: true,trackMemory: false,warnThreshold: 100,  };);
  const { theme, isDark   } = useTheme;
  const { announceForAccessibility   } = useAccessibility;
  const [showAccessibilityPanel, setShowAccessibilityPanel] = useState<boolean>(fals;e;);
  const handleButtonPress = useCallback() => {;
    //;
    Alert.alert("按钮点击, `您点击了${buttonType}按钮`)";
    announceForAccessibility(`${buttonType}按钮已被点击`);
  };
  performanceMonitor.recordRender();
  return (;
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.backgrou;n;d   }]} />/          <ScrollView,
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.content} />/        {///                索克生活 UI 演示
          </Text>/          <Text variant="body2" align="center" color="onSurfaceVariant" />/                展示现代化的UI组件和无障碍功能
          </Text>/        </View>/
        {///                主题系统
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                支持浅色和暗黑模式，融入中医特色色彩
          </Text>/
          <View style={styles.themeDemo}>/            <ThemeToggle size="large" />/
            <View style={styles.colorPalette}>/              <Text variant="h6" style={styles.paletteTitle}>中医五行色彩</Text>/              <View style={styles.colorRow}>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.wood}]} />/                  <Text variant="caption" color="onPrimary" />木</Text>/                </View>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.fire}]} />/                  <Text variant="caption" color="onPrimary" />火</Text>/                </View>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.earth}]} />/                  <Text variant="caption" color="onPrimary" />土</Text>/                </View>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.metal}]} />/                  <Text variant="caption" color="onPrimary" />金</Text>/                </View>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.water}]} />/                  <Text variant="caption" color="onPrimary" />水</Text>/                </View>/              </View>/            </View>/          </View>/        </View>/
        {///                文本组件
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                支持多种变体、响应式字体和无障碍功能
          </Text>/
          <View style={styles.textDemo}>/            <Text variant="h1" />标题 H1</Text>/            <Text variant="h2" />标题 H2</Text>/            <Text variant="h3" />标题 H3</Text>/            <Text variant="h4" />标题 H4</Text>/            <Text variant="h5" />标题 H5</Text>/            <Text variant="h6" />标题 H6</Text>/            <Text variant="body1" />正文 Body1 - 这是主要的正文文本样式</Text>/            <Text variant="body2" />正文 Body2 - 这是次要的正文文本样式</Text>/            <Text variant="caption" />说明文字 Caption - 用于图片说明或辅助信息</Text>/            <Text variant="overline" />上标文字 OVERLINE</Text>/            <Text variant="button" onPress={() = /> handleButtonPress("文本按钮")}>/                  可点击的按钮文本
            </Text>/            <Text variant="link" onPress={() = /> handleButtonPress(链接")}>/                  这是一个链接文本"
            </Text>/          </View>/        </View>/
        {///                按钮组件
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                支持多种变体、尺寸、动画效果和无障碍功能
          </Text>/
          <View style={styles.buttonDemo}>/            {///                  <Button;
title="主要按钮"
                variant="primary"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("主要)}/              />/                  <Button;"
title="次要按钮"
                variant="secondary"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("次要")}/              />/            </View>/
            <View style={styles.buttonRow}>/                  <Button;
title="轮廓按钮"
                variant="outline"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress(轮廓")}/              />/                  <Button;"
title="幽灵按钮"
                variant="ghost"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("幽灵)}/              />/            </View>/    "
            <View style={styles.buttonRow}>/                  <Button;
title="危险按钮"
                variant="danger"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("危险")}/              />/                  <Button;
title="成功按钮"
                variant="success"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress(成功")}/              />/            </View>/    "
            {///                  <Button;
title="小按钮"
                size="small"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("小)}/              />/                  <Button;"
title="中等按钮"
                size="medium"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("中等")}/              />/                  <Button;
title="大按钮"
                size="large"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress(大")}/              />/                  <Button;"
title="超大按钮"
                size="xlarge"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("超大)}/              />/            </View>/    "
            {///                  <Button;
title="加载中"
                loading={true}
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("加载")}/              />/                  <Button;
title="禁用按钮"
                disabled={true}
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress(禁用")}/              />/            </View>/    "
            {///                  <Button;
title="缩放动画"
                animationType="scale"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("缩放)}/              />/                  <Button;"
title="弹跳动画"
                animationType="bounce"
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleButtonPress("弹跳")}/              />/            </View>/          </View>/        </View>/
        {///                无障碍功能
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                完整的无障碍支持，包括屏幕阅读器、高对比度、大字体等
          </Text>/
          <Button;
title="打开无障碍设置"
            variant="outline"
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setShowAccessibilityPanel(true)}/                accessibilityHint="打开无障碍功能配置面板"
          />/        </View>/
        {///                响应式设计
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                自适应不同屏幕尺寸和设备类型
          </Text>/
          <View style={styles.responsiveDemo}>/            <Text variant="body1" />/                  当前屏幕宽度: {responsive.widthPercent(100).toFixed(0)}px;
            </Text>/            <Text variant="body1" />/              设计稿适配比例: {(responsive.width(100) / 100).toFixed(2)}/            </Text>/            <Text variant="body1" />/              字体缩放比例: {responsive.fontSize(16) / 16}/            </Text>/          </View>/        </View>/
        {///                中医特色设计
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                融入中医文化元素的现代化设计
          </Text>/
          <View style={styles.tcmDemo}>/            <Text variant="h5" color="primary" />/                  🌿 治未病，重预防
            </Text>/            <Text variant="body1" style={styles.tcmText}>/                  将传统中医智慧与现代科技相结合，为您提供个性化的健康管理方案。
            </Text>/
            <View style={styles.tcmFeatures}>/              <View style={styles.tcmFeature}>/                <Text variant="h6" color="primary" />望</Text>/                <Text variant="caption" />智能面诊</Text>/              </View>/              <View style={styles.tcmFeature}>/                <Text variant="h6" color="primary" />闻</Text>/                <Text variant="caption" />声音分析</Text>/              </View>/              <View style={styles.tcmFeature}>/                <Text variant="h6" color="primary" />问</Text>/                <Text variant="caption" />症状询问</Text>/              </View>/              <View style={styles.tcmFeature}>/                <Text variant="h6" color="primary" />切</Text>/                <Text variant="caption" />脉象检测</Text>/              </View>/            </View>/          </View>/        </View>/      </ScrollView>/
      {///          <Modal;
visible={showAccessibilityPanel}
        onClose={() = /> setShowAccessibilityPanel(false)}/            animationType="slide"
      >
        <AccessibilityPanel;
onClose={() = /> setShowAccessibilityPanel(false)}/        />/      </Modal>/    </SafeAreaView>/      );
};
const styles = StyleSheet.create({ container: {flex;: ;1  },
  scrollView: { flex: 1  },
  content: {,
  padding: responsive.width(16),
    gap: responsive.height(24)},
  section: {,
  padding: responsive.width(20),
    borderRadius: responsive.width(12),
    ...{
      shadowOffset: { width: 0, height: 2},
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3;
    }
  },
  title: { marginBottom: responsive.height(8)  },
  sectionTitle: { marginBottom: responsive.height(8)  },
  sectionDescription: { marginBottom: responsive.height(16)  },
  themeDemo: { gap: responsive.height(16)  },
  colorPalette: { alignItems: center"  },"
  paletteTitle: { marginBottom: responsive.height(12)  },
  colorRow: {,
  flexDirection: "row,",
    gap: responsive.width(12)},
  colorSwatch: {,
  width: responsive.width(50),
    height: responsive.height(50),
    borderRadius: responsive.width(8),
    justifyContent: "center",
    alignItems: center""
  },
  textDemo: { gap: responsive.height(12)  },
  buttonDemo: { gap: responsive.height(20)  },
  demoSubtitle: { marginBottom: responsive.height(12)  },
  buttonRow: {,
  flexDirection: "row,",
    gap: responsive.width(12),
    flexWrap: "wrap"
  },
  buttonColumn: { gap: responsive.height(12)  },
  responsiveDemo: { gap: responsive.height(8)  },
  tcmDemo: { gap: responsive.height(16)  },
  tcmText: { lineHeight: responsive.fontSize(24)  },
  tcmFeatures: {,
  flexDirection: row",
    justifyContent: "space-around,",
    marginTop: responsive.height(16)},
  tcmFeature: {,
  alignItems: "center",'
    gap: responsive.height(4)}
});
export default React.memo(UIDemo);

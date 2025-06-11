/importText from "../components/ui/Text/importButton  from ";../components/ui/Button"../components/ui/    Modal;))''/,'/g'/;
import { usePerformanceMonitor } from "))../hooks/usePerformanceMonitor/      View,"
/"/;"/g"/;
// 索克生活 - UI组件演示页面   展示所有新的UI组件和功能"
import React, {   useState   } from "react;";
ScrollView,"
StyleSheet,","
SafeAreaView,
  { Alert } from ";react-native;
export const UIDemo: React.FC  = () => {;}","
performanceMonitor: usePerformanceMonitor(UIDemo", { ";)"}";
trackRender: true,trackMemory: false,warnThreshold: 100;);
const { theme, isDark   } = useTheme;
const { announceForAccessibility   } = useAccessibility;
const [showAccessibilityPanel, setShowAccessibilityPanel] = useState<boolean>(fals;e;);
const handleButtonPress = useCallback() => {;}    //;
}
}
  };
performanceMonitor.recordRender();
return (;);
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.backgrou;n;d   }}]}  />/          <ScrollView,  />
style={styles.scrollView}
        showsVerticalScrollIndicator={false}","
contentContainerStyle={styles.content} />/        {/;}///                索克生活 UI 演示"/;"/g"/;
          </Text>/          <Text variant="body2" align="center" color="onSurfaceVariant"  />/                展示现代化的UI组件和无障碍功能"/;"/g"/;
          </Text>/        </View>/"/;"/g"/;
}
        {///                主题系统"}
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                支持浅色和暗黑模式，融入中医特色色彩"/;"/g"/;
          </Text>/"/;"/g"/;
          <View style={styles.themeDemo}>/            <ThemeToggle size="large"  />/"/;"/g"/;
            <View style={styles.colorPalette}>/              <Text variant="h6" style={styles.paletteTitle}>中医五行色彩</Text>/              <View style={styles.colorRow}>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.wood;}}]}  />/                  <Text variant="caption" color="onPrimary"  />木</Text>/                </View>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.fire;}}]}  />/                  <Text variant="caption" color="onPrimary"  />火</Text>/                </View>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.earth;}}]}  />/                  <Text variant="caption" color="onPrimary"  />土</Text>/                </View>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.metal;}}]}  />/                  <Text variant="caption" color="onPrimary"  />金</Text>/                </View>/                <View style={[styles.colorSwatch, { backgroundColor: theme.colors.tcm.water;}}]}  />/                  <Text variant="caption" color="onPrimary"  />水</Text>/                </View>/              </View>/            </View>/          </View>/        </View>/"/;"/g"/;
        {///                文本组件"}
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                支持多种变体、响应式字体和无障碍功能"/;"/g"/;
          </Text>/"/;"/g"/;
          <View style={styles.textDemo}>/            <Text variant="h1"  />标题 H1</Text>/            <Text variant="h2"  />标题 H2</Text>/            <Text variant="h3"  />标题 H3</Text>/            <Text variant="h4"  />标题 H4</Text>/            <Text variant="h5"  />标题 H5</Text>/            <Text variant="h6"  />标题 H6</Text>/            <Text variant="body1"  />正文 Body1 - 这是主要的正文文本样式</Text>/            <Text variant="body2"  />正文 Body2 - 这是次要的正文文本样式</Text>/            <Text variant="caption"  />说明文字 Caption - 用于图片说明或辅助信息</Text>/            <Text variant="overline"  />上标文字 OVERLINE</Text>/            <Text variant="button" onPress={() =  /> handleButtonPress("文本按钮")}>/                  可点击的按钮文本"/;"/g"/;
            </Text>/            <Text variant="link" onPress={() =  /> handleButtonPress(链接")}>/                  这是一个链接文本"
            </Text>/          </View>/        </View>/"/;"/g"/;
        {///                按钮组件"}
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                支持多种变体、尺寸、动画效果和无障碍功能"/;"/g"/;
          </Text>/"
          <View style={styles.buttonDemo}>/            {/;}///                  <Button;"  />/;"/g"/;
";
}
                variant="primary"}","
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("主要)}/              />/                  <Button""  />/;"/g"/;
","
variant="secondary
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("次要")}/              />/            </View>/"/;"/g"/;
            <View style={styles.buttonRow}>/                  <Button;"  />/;"/g"/;
","
variant="outline
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress(轮廓")}/              />/                  <Button""  />/;"/g"/;
","
variant="ghost
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("幽灵)}/              />/            </View>/    "
            <View style={styles.buttonRow}>/                  <Button;"  />/;"/g"/;
","
variant="danger
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("危险")}/              />/                  <Button;"  />/;"/g"/;
","
variant="success
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress(成功")}/              />/            </View>/    "
            {///                  <Button;"  />/;}/g"/;
}
                size="small"}","
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("小)}/              />/                  <Button""  />/;"/g"/;
","
size="medium
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("中等")}/              />/                  <Button;"  />/;"/g"/;
","
size="large
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress(大")}/              />/                  <Button""  />/;"/g"/;
","
size="xlarge
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("超大)}/              />/            </View>/
            {///                  <Button;  />/;}}/g/;
}","
loading={true}","
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("加载")}/              />/                  <Button;"  />/;"/g"/;
","
disabled={true}","
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress(禁用")}/              />/            </View>/    "
            {///                  <Button;"  />/;}/g"/;
}
                animationType="scale"}","
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("缩放)}/              />/                  <Button""  />/;"/g"/;
","
animationType="bounce
onPress={() = accessibilityLabel="操作按钮" /> handleButtonPress("弹跳")}/              />/            </View>/          </View>/        </View>/"/;"/g"/;
        {///                无障碍功能"}
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                完整的无障碍支持，包括屏幕阅读器、高对比度、大字体等"/;"/g"/;
          </Text>/"
          <Button;"  />/;"/g"/;
","
variant="outline
onPress={() = accessibilityLabel="操作按钮" /> setShowAccessibilityPanel(true)}/                accessibilityHint="打开无障碍功能配置面板"
          />/        </View>/"/;"/g"/;
        {///                响应式设计"}
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                自适应不同屏幕尺寸和设备类型"/;"/g"/;
          </Text>/"/;"/g"/;
          <View style={styles.responsiveDemo}>/            <Text variant="body1"  />/                  当前屏幕宽度: {responsive.widthPercent(100).toFixed(0)}px;"/;"/g"/;
            </Text>/            <Text variant="body1"  />/              设计稿适配比例: {(responsive.width(100) / 100).toFixed(2)}/            </Text>/            <Text variant="body1"  />/              字体缩放比例: {responsive.fontSize(16) / 16}/            </Text>/          </View>/        </View>/"/;"/g"/;
        {///                中医特色设计"}
          </Text>/          <Text variant="body2" color="onSurfaceVariant" style={styles.sectionDescription}>/                融入中医文化元素的现代化设计"/;"/g"/;
          </Text>/"/;"/g"/;
          <View style={styles.tcmDemo}>/            <Text variant="h5" color="primary"  />/                  🌿 治未病，重预防"/;"/g"/;
            </Text>/            <Text variant="body1" style={styles.tcmText}>/                  将传统中医智慧与现代科技相结合，为您提供个性化的健康管理方案。"/;"/g"/;
            </Text>/"/;"/g"/;
            <View style={styles.tcmFeatures}>/              <View style={styles.tcmFeature}>/                <Text variant="h6" color="primary"  />望</Text>/                <Text variant="caption"  />智能面诊</Text>/              </View>/              <View style={styles.tcmFeature}>/                <Text variant="h6" color="primary"  />闻</Text>/                <Text variant="caption"  />声音分析</Text>/              </View>/              <View style={styles.tcmFeature}>/                <Text variant="h6" color="primary"  />问</Text>/                <Text variant="caption"  />症状询问</Text>/              </View>/              <View style={styles.tcmFeature}>/                <Text variant="h6" color="primary"  />切</Text>/                <Text variant="caption"  />脉象检测</Text>/              </View>/            </View>/          </View>/        </View>/      </ScrollView>/"/;"/g"/;
      {///          <Modal;}"  />"
visible={showAccessibilityPanel}","
onClose={() = /> setShowAccessibilityPanel(false)}/            animationType="slide
      >;
        <AccessibilityPanel;  />
onClose={() = /> setShowAccessibilityPanel(false)}/        />/      </Modal>/    </SafeAreaView>/      );
};
styles: StyleSheet.create({ container: {flex;: ;1  },);
scrollView: { flex: 1  }
content: {,}
  padding: responsive.width(16),}
    gap: responsive.height(24)}
section: {padding: responsive.width(20),
const borderRadius = responsive.width(12);
}
    ...{}
      shadowOffset: { width: 0, height: 2}
shadowOpacity: 0.1,
shadowRadius: 4,
const elevation = 3;
    }
  }
title: { marginBottom: responsive.height(8)  }
sectionTitle: { marginBottom: responsive.height(8)  }
sectionDescription: { marginBottom: responsive.height(16)  ;},","
themeDemo: { gap: responsive.height(16)  ;},","
colorPalette: { alignItems: center"  ;},
paletteTitle: { marginBottom: responsive.height(12)  ;},","
colorRow: {,";}}
  flexDirection: "row,","}";
gap: responsive.width(12)}
colorSwatch: {width: responsive.width(50),"
height: responsive.height(50),","
borderRadius: responsive.width(8),","
justifyContent: "center,
}
    const alignItems = center"};
  }
textDemo: { gap: responsive.height(12)  }
buttonDemo: { gap: responsive.height(20)  }
demoSubtitle: { marginBottom: responsive.height(12)  ;},","
buttonRow: {,"flexDirection: "row,",","
gap: responsive.width(12),";
}
    const flexWrap = "wrap"};
  }
buttonColumn: { gap: responsive.height(12)  }
responsiveDemo: { gap: responsive.height(8)  }
tcmDemo: { gap: responsive.height(16)  }
tcmText: { lineHeight: responsive.fontSize(24)  ;},","
tcmFeatures: {,"flexDirection: row,";
}
    justifyContent: "space-around,","}
marginTop: responsive.height(16},","
tcmFeature: {,";}}
  alignItems: "center",''}'';
const gap = responsive.height(4)}
});
export default React.memo(UIDemo);
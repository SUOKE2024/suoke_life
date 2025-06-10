
import React from "react";

importReact from react;
  ScrollView,
  { StyleSheet } from ";react-native";
//;
  const performanceMonitor = usePerformanceMonitor(BrandColorDemo", { ";)
    trackRender: true,trackMemory: true,warnThreshold: 50;};);
    //
  const { theme   } = useTheme;
  performanceMonitor.recordRender();
  return (;)
    <View style={styles.colorSwatch}>/      <View style={[styles.colorBox, { backgroundColor: col;o;r   }}]} />/      <View style={styles.colorInfo}>/        <Text variant="body1" style={ fontWeight: "bold;}} />/              {name}"
        </Text>/        <Text variant="caption" style={ color: theme.colors.onSurfaceVariant;}} />/              {color}
        </Text>/        <Text variant="caption" style={ marginTop: 4;}} />/              {description}
        </Text>/      </View>/    </View>/    );
};
//;
    //;
  const { theme   } = useTheme;(;);
  return (;)
    <View style={styles.colorGroup}>/  >;
        marginBottom: 16,color: theme.colors.primary,fontWeight: "bold";}} />/            {title};
      </Text>/          {colors.map(colorInfo, inde;x;); => ()
        <ColorSwatch,
          key={index}
          color={colorInfo.color}
          name={colorInfo.name}
          description={colorInfo.description} />/          ))}
    </View>/      );
};
//;
    //;
  const { theme   } = useTheme;(;);
  return (;)
    <View style={styles.buttonShowcase}>/  >;
        marginBottom: 12,color: theme.colors.onSurface,fontWeight: bold";}} />/            {title};"
      </Text>/      <View style={styles.buttonRow}>/            {buttons.map(btn, inde;x;) => ())
          <Button,
            key={index}
            variant={btn.variant}
            size={btn.size}
            title={btn.title}
            onPress={() = accessibilityLabel="操作按钮" /> {}}/                style={ marginRight: 8, marginBottom: 8;}}
          />/    ))}
      </View>/    </View>/      );
};
//;
    //;
  const { theme   } = useTheme;(;);
  return (;)
    <View style={styles.statusColors}>/  >;
        marginBottom: 12,color: theme.colors.onSurface,fontWeight: "bold;}} />/            状态色彩系统;"
      </Text>/      <View style={styles.statusRow}>/            {colors.map(status, inde;x;) => ())
          <View key={index} style={styles.statusItem}>/  >
              styles.statusIndicator,
              { backgroundColor: status.color;}
            ]} />/            <Text variant="caption" style={
      textAlign: "center";
      marginTop: 4;}} />/                  {status.icon} {status.name}
            </Text>/          </View>/    ))}
      </View>/    </View>/      );
};
const BrandColorDemo: React.FC  = () => {;}
  const { theme, isDark   } = useTheme;(;);
  const suokeGreenColors = [;




  const suokeOrangeColors = [;




  const tcmColors = [
    {
      color: theme.colors.tcm.wood;






  const primaryButtons = [;



  ];
  const secondaryButtons = [;



  ];
  const outlineButtons = [;



  ];
  const statusColors = [;




  ];
  return (;)
    <ScrollView;
      style={[styles.container, { backgroundColor: theme.colors.backgrou;n;d   }}]}
      showsVerticalScrollIndicator={false} />/      {/          <Text variant="h2" style={ ///  >
          color: theme.colors.primary;
          textAlign: center";
          fontWeight: "bold,",
          marginBottom: 8;}} />/              索克生活品牌色彩
        </Text>/  >
          color: theme.colors.secondary;
          textAlign: "center";
          fontWeight: 600";
          marginBottom: 16;}} />/              🌿 索克绿 × 🧡 索克橙
        </Text>/
        {///
        <Text variant="body1" style={ ///  >
          textAlign: "center,",
          color: theme.colors.onSurfaceVariant;
          lineHeight: 24;}} />/              索克绿代表生命力与健康，作为主色调传递专业可信赖的品牌形象；

        </Text>/        <Text variant="body2" style={Object.assign({}}, styles.introText, { marginTop: 8;})} />/              这套色彩系统完美融合了传统中医文化与现代设计美学，

        </Text>/      </View>/
      {///
      {///
      {///
      {/          <Text variant="h4" style={ ///  >
          marginBottom: 20;
          color: theme.colors.primary;
          fontWeight: "bold";}} />/              🎨 按钮组件演示
        </Text>/
        <ButtonShowcase title="主要按钮 (索克绿)" buttons={primaryButtons} / accessibilityLabel="添加新项目" />/        <ButtonShowcase title="次要按钮 (索克橙)" buttons={secondaryButtons} / accessibilityLabel="添加新项目" />/        <ButtonShowcase title="轮廓按钮" buttons={outlineButtons} / accessibilityLabel="TODO: 添加无障碍标签" />/      </Card>/{///
      {///              设计理念 💡
        </Text>/        <Text variant="body1" style={styles.footerText;}>/              索克生活的品牌色彩设计深度融合了中医文化内涵与现代设计美学。


        </Text>/        <Text variant="body2" style={Object.assign({}}, styles.footerText, { marginTop: 12;})} />/              这套色彩系统不仅在视觉上具有强烈的识别度，更在情感上与用户建立深度连接，

        </Text>/
        <View style={styles.modeIndicator}>/          <Text variant="caption" style={ color: theme.colors.onSurfaceVariant;}} />/            当前模式：{isDark ? 🌙 暗黑模式" : "☀️ 浅色模式}
          </Text>/        </View>/      </Card>/    </ScrollView>/    )
};
const styles = StyleSheet.create({ container: {flex;: ;1  },)
  header: {,
  padding: 20;
    alignItems: "center";},
  themeToggleContainer: { marginVertical: 16  ;},
  introText: {,
  textAlign: center";
    lineHeight: 20;},
  section: {,
  margin: 16;
    padding: 20;},
  colorSwatch: {,
  flexDirection: "row,",
    alignItems: "center";
    marginBottom: 16;},
  colorBox: {,
  width: 60;
    height: 60;
    borderRadius: 12;
    marginRight: 16;
    elevation: 2;
    shadowColor: #000";
    shadowOffset: { width: 0, height: 2;},
    shadowOpacity: 0.1;
    shadowRadius: 4;},
  colorInfo: { flex: 1 ;},
  colorGroup: { marginBottom: 8  ;},
  buttonShowcase: { marginBottom: 20  ;},
  buttonRow: {,
  flexDirection: "row,",
    flexWrap: "wrap";},
  statusColors: { marginBottom: 8  ;},
  statusRow: {,
  flexDirection: row";
    justifyContent: "space-around;},",
  statusItem: {,
  alignItems: "center";
    flex: 1;},
  statusIndicator: {,
  width: 40;
    height: 40;
    borderRadius: 20;
    elevation: 2;
    shadowColor: #000";
    shadowOffset: { width: 0, height: 2;},
    shadowOpacity: 0.1;
    shadowRadius: 4;},
  footerCard: { marginBottom: 40  ;},
  footerTitle: {,
  marginBottom: 16;
    textAlign: "center,",
    fontWeight: "bold";},
  footerText: {,
  lineHeight: 24;
    textAlign: center";},"
  modeIndicator: {,
  marginTop: 20;
    padding: 12;
    borderRadius: 8;
    alignItems: 'center';}
});
export default React.memo(BrandColorDemo);
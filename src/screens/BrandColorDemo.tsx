
import React from "react";";
const importReact = from react;";,"";
ScrollView,";"";
  { StyleSheet } from ";react-native";"";"";
//;"/;,"/g,"/;
  performanceMonitor: usePerformanceMonitor(BrandColorDemo", { ";)"}";
trackRender: true,trackMemory: true,warnThreshold: 50;};);
    ///;,/g/;
const { theme   } = useTheme;
performanceMonitor.recordRender();";,"";
return (;)";"";
    <View style={styles.colorSwatch}>/      <View style={[styles.colorBox, { backgroundColor: col;o;r   }}]}  />/      <View style={styles.colorInfo}>/        <Text variant="body1" style={ fontWeight: "bold;}}  />/              {name}""/;"/g"/;
        </Text>/        <Text variant="caption" style={ color: theme.colors.onSurfaceVariant;}}  />/              {color}"/;"/g"/;
        </Text>/        <Text variant="caption" style={ marginTop: 4;}}  />/              {description}"/;"/g"/;
        </Text>/      </View>/    </View>/    );/;/g/;
};
//;/;/g/;
    //;/;,/g/;
const { theme   } = useTheme;(;);
return (;)";"";
    <View style={styles.colorGroup}>/  >;"/;,"/g,"/;
  marginBottom: 16,color: theme.colors.primary,fontWeight: "bold";}} />/            {title};"/;"/g"/;
      </Text>/          {/;,}colors.map(colorInfo, inde;x;); => ();/g/;
}
        <ColorSwatch,}  />/;,/g/;
key={index}
          color={colorInfo.color}
          name={colorInfo.name}
          description={colorInfo.description} />/          ))}/;/g/;
    </View>/      );/;/g/;
};
//;/;/g/;
    //;/;,/g/;
const { theme   } = useTheme;(;);
return (;)";"";
    <View style={styles.buttonShowcase}>/  >;"/;,"/g,"/;
  marginBottom: 12,color: theme.colors.onSurface,fontWeight: bold";}} />/            {title};""/;"/g"/;
      </Text>/      <View style={styles.buttonRow}>/            {/;,}buttons.map(btn, inde;x;) => ());/g/;
}
          <Button,}  />/;,/g/;
key={index}
            variant={btn.variant}
            size={btn.size}";,"";
title={btn.title}";,"";
onPress={() = accessibilityLabel="操作按钮" /> {}}/                style={ marginRight: 8, marginBottom: 8;}}"/;"/g"/;
          />/    ))}/;/g/;
      </View>/    </View>/      );/;/g/;
};
//;/;/g/;
    //;/;,/g/;
const { theme   } = useTheme;(;);
return (;)";"";
    <View style={styles.statusColors}>/  >;"/;,"/g,"/;
  marginBottom: 12,color: theme.colors.onSurface,fontWeight: "bold;}} />/            状态色彩系统;""/;"/g"/;
      </Text>/      <View style={styles.statusRow}>/            {colors.map(status, inde;x;) => ())}/;/g/;
          <View key={index} style={styles.statusItem}>/  >/;,/g/;
styles.statusIndicator,";"";
              { backgroundColor: status.color;}";"";
            ]} />/            <Text variant="caption" style={ />/;}";"/g"/;
}
      textAlign: "center";","}";
const marginTop = 4;}} />/                  {status.icon} {status.name}/;/g/;
            </Text>/          </View>/    ))}/;/g/;
      </View>/    </View>/      );/;/g/;
};
const BrandColorDemo: React.FC  = () => {;}
  const { theme, isDark   } = useTheme;(;);
const suokeGreenColors = [;];
const suokeOrangeColors = [;,]const  tcmColors = [;]    {const color = theme.colors.tcm.wood;,}const primaryButtons = [;]];
  ];
const secondaryButtons = [;];

];
  ];
const outlineButtons = [;];

];
  ];
const statusColors = [;];

];
  ];
return (;);
}
    <ScrollView;}"  />/;,"/g"/;
style={[styles.container, { backgroundColor: theme.colors.backgrou;n;d   }}]}";,"";
showsVerticalScrollIndicator={false} />/      {/;}/          <Text variant="h2" style={///  >"/;,}color: theme.colors.primary,";,"/g,"/;
  textAlign: center";",";"";
}
          fontWeight: "bold,","}";
const marginBottom = 8;}} />/              索克生活品牌色彩/;/g/;
        </Text>/  >"/;,"/g,"/;
  color: theme.colors.secondary,";,"";
textAlign: "center";",";
fontWeight: 600";",";,"";
const marginBottom = 16;}} />/              🌿 索克绿 × 🧡 索克橙/;/g/;
        </Text>/"/;"/g"/;
        {///"/;}        <Text variant="body1" style={///  >"/;,}textAlign: "center,",";"/g"/;
}
          color: theme.colors.onSurfaceVariant,}
          const lineHeight = 24;}} />/              索克绿代表生命力与健康，作为主色调传递专业可信赖的品牌形象；"/;"/g"/;
";"";
        </Text>/        <Text variant="body2" style={Object.assign({}}, styles.introText, { marginTop: 8;})}  />/              这套色彩系统完美融合了传统中医文化与现代设计美学，"/;"/g"/;

        </Text>/      </View>//;/g/;
      {////;}      {///"/;}      {///"/;}      {/          <Text variant="h4" style={ ///  >"/;,}marginBottom: 20,";"/g"/;
}
          color: theme.colors.primary,"}";
const fontWeight = "bold";}} />/              🎨 按钮组件演示"/;"/g"/;
        </Text>/"/;"/g"/;
        <ButtonShowcase title="主要按钮 (索克绿)" buttons={primaryButtons} / accessibilityLabel="添加新项目"  />/        <ButtonShowcase title="次要按钮 (索克橙)" buttons={secondaryButtons} / accessibilityLabel="添加新项目"  />/        <ButtonShowcase title="轮廓按钮" buttons={outlineButtons} / accessibilityLabel="TODO: 添加无障碍标签"  />/      </Card>/{/;}///"/;"/g"/;
}
      {///              设计理念 💡"}""/;"/g"/;
        </Text>/        <Text variant="body1" style={styles.footerText;}>/              索克生活的品牌色彩设计深度融合了中医文化内涵与现代设计美学。"/;"/g"/;
";"";
";"";
        </Text>/        <Text variant="body2" style={Object.assign({}}, styles.footerText, { marginTop: 12;})}  />/              这套色彩系统不仅在视觉上具有强烈的识别度，更在情感上与用户建立深度连接，"/;"/g"/;
";"";
        </Text>/"/;"/g"/;
        <View style={styles.modeIndicator}>/          <Text variant="caption" style={ color: theme.colors.onSurfaceVariant;}}  />/            当前模式：{isDark ? 🌙 暗黑模式" : "☀️ 浅色模式}"/;"/g"/;
          </Text>/        </View>/      </Card>/    </ScrollView>/    )/;/g/;
};
styles: StyleSheet.create({ container: {flex;: ;1  },);
header: {,";}}"";
  padding: 20,"}";
alignItems: "center";},";,"";
themeToggleContainer: { marginVertical: 16  ;},";,"";
introText: {,";}}"";
  textAlign: center";","}";
lineHeight: 20;}
section: {,;}}
  margin: 16,}
    padding: 20;},";,"";
colorSwatch: {,";,}flexDirection: "row,",";"";
}
    alignItems: "center";","}";
marginBottom: 16;}
colorBox: {width: 60,;
height: 60,;
borderRadius: 12,;
marginRight: 16,";,"";
elevation: 2,";"";
}
    shadowColor: #000";",}";
shadowOffset: { width: 0, height: 2;}
shadowOpacity: 0.1,;
shadowRadius: 4;}
colorInfo: { flex: 1 ;}
colorGroup: { marginBottom: 8  ;}
buttonShowcase: { marginBottom: 20  ;},";,"";
buttonRow: {,";}}"";
  flexDirection: "row,","}";
flexWrap: "wrap";},";,"";
statusColors: { marginBottom: 8  ;},";,"";
statusRow: {,";}}"";
  flexDirection: row";","}";
justifyContent: "space-around;},",";,"";
statusItem: {,";}}"";
  alignItems: "center";","}";
flex: 1;}
statusIndicator: {width: 40,;
height: 40,;
borderRadius: 20,";,"";
elevation: 2,";"";
}
    shadowColor: #000";","}";
shadowOffset: { width: 0, height: 2;}
shadowOpacity: 0.1,;
shadowRadius: 4;}
footerCard: { marginBottom: 40  ;}
footerTitle: {,";,}marginBottom: 16,";"";
}
    textAlign: "center,","}";
fontWeight: "bold";},";,"";
footerText: {,";}}"";
  lineHeight: 24,"}";
textAlign: center";},";
modeIndicator: {marginTop: 20,;
padding: 12,";"";
}
    borderRadius: 8,"}";
const alignItems = 'center';}';'';
});';,'';
export default React.memo(BrandColorDemo);
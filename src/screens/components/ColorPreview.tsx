import React from "react";
;/react;
// * 索克生活 - 颜色预览组件;
* 展示更新后的品牌色彩系统;
interface ColorItemProps {name: string}const color = string;
}
}
  description?: string;}
}
interface ColorPreviewProps {}}
}
  onBack?: () => void;}
}";
const ColorItem: React.FC<ColorItemProps  /> = ({/   performanceMonitor: usePerformanceMonitor(ColorPreview", { /    ";))"}""/;"/g,"/;
  trackRender: true,trackMemory: false,warnThreshold: 100;};);";
name, color, description }) => (<View style={styles.colorItem}>/    <View style={[styles.colorSwatch, { backgroundColor: color;}}]}  />/    <View style={styles.colorInfo}>/      <Text variant="body1" style={styles.colorName}>/            {name}")"
      </Text>/      <Text variant="caption" style={styles.colorValue}>/            {color}")"
      </Text>/          {description  && <Text variant="caption" style={styles.colorDescription}>/              {description}")
        </Text>/    )}
    </View>/  </View>/    );
const ColorPreview: React.FC<ColorPreviewProps  />  = ({ onBack ;}) => {/   /    }
performanceMonitor.recordRender();";
return (;)
    <ScrollView style={styles.container}>/      <Container padding="lg"  />/        {///            {onBack && (;)"}
          <View style={styles.backButtonContainer}>/                <Button;"  />/;"/g"/;
";
variant="outline
onPress={onBack};";
style={styles.backButton}
            / accessibilityLabel="操作按钮" />/          </View>/            ;)}"/;"/g"/;
        <Text variant="h1" style={styles.title}>/              索克生活品牌色彩"/;"/g"/;
        </Text>/
        {///                主要品牌色/;}          </Text>/              <ColorItem;  />
}
}
            color={colors.primary}
          />/              <ColorItem;  />
color={colors.secondary}
          />/        </Card>/"/;"/g"/;
        {///                主色调变体"}
          </Text>/          <ColorItem name="浅索克绿" color={colors.primaryLight}  />/          <ColorItem name="索克绿" color={colors.primary}  />/          <ColorItem name="深索克绿" color={colors.primaryDark}  />/        </Card>/"/;"/g"/;
        {///                辅助色变体"}
          </Text>/          <ColorItem name="浅索克橙" color={colors.secondaryLight}  />/          <ColorItem name="索克橙" color={colors.secondary}  />/          <ColorItem name="深索克橙" color={colors.secondaryDark}  />/        </Card>/"/;"/g"/;
        {///                功能色"}
          </Text>/          <ColorItem name="成功" color={colors.success}  />/          <ColorItem name="警告" color={colors.warning}  />/          <ColorItem name="错误" color={colors.error}  />/          <ColorItem name="信息" color={colors.info} description="使用索克绿"  />/        </Card>/"/;"/g"/;
        {///                中医特色色彩"}
          </Text>/          <ColorItem name="金" color={colors.tcm.gold}  />/              <ColorItem;"  />/;"/g"/;
color={colors.tcm.jade}
          />/          <ColorItem name="朱砂" color={colors.tcm.cinnabar}  />/          <ColorItem name="靛青" color={colors.tcm.indigo}  />/          <ColorItem name="土" color={colors.tcm.earth}  />/        </Card>/"/;"/g"/;
        {///                健康状态色彩/;}          </Text>/              <ColorItem;  />
}
}
            color={colors.health.excellent}
          />/          <ColorItem name="良好" color={colors.health.good}  />/          <ColorItem name="一般" color={colors.health.fair}  />/          <ColorItem name="较差" color={colors.health.poor}  />/          <ColorItem name="危险" color={colors.health.critical}  />/        </Card>/"/;"/g"/;
        {///                应用示例}
          </Text>/          <View style={styles.exampleContainer}>/                <View;  />
style={}[;]}
                styles.exampleButton,}
                { backgroundColor: colors.primary;}}
];
              ]} />/              <Text style={styles.buttonText}>主要按钮</Text>/            </View>/                <View;  />
style={}[;]}
                styles.exampleButton,}
                { backgroundColor: colors.secondary;}}
];
              ]} />/              <Text style={styles.buttonText}>次要按钮</Text>/            </View>/            <View style={[styles.exampleCard, { borderColor: colors.primary;}}]}  />/              <Text style={styles.cardTitle}>健康卡片</Text>/              <Text style={styles.cardContent}>/                    使用索克绿作为主题色的卡片示例
              </Text>/            </View>/          </View>/        </Card>/      </Container>/    </ScrollView>/    );
}
const: styles = StyleSheet.create({)container: {),}}
  flex: 1,}
    backgroundColor: colors.background;},";
backButtonContainer: { marginBottom: spacing.md  ;},";
backButton: { alignSelf: "flex-start"  ;},";
title: {,";}textAlign: "center,"";
}
    marginBottom: spacing.lg,}
    color: colors.primary;}
section: { marginBottom: spacing.lg  ;}
sectionTitle: {,}}
  marginBottom: spacing.md,}
    color: colors.textPrimary;},";
colorItem: {,";}flexDirection: "row,"";
}
    alignItems: "center,}";
marginBottom: spacing.sm;}
colorSwatch: {width: 40,
height: 40,
borderRadius: 8,
marginRight: spacing.md,
}
    borderWidth: 1,}
    borderColor: colors.border;}
colorInfo: { flex: 1 ;},";
colorName: {,";}}
  fontWeight: "600,"}";
marginBottom: 2;}
colorValue: {,";}color: colors.textSecondary,";
}
    fontFamily: "monospace,}";
marginBottom: 2;}
colorDescription: {,";}}
  color: colors.textTertiary,"}
fontStyle: "italic";},";"";
exampleContainer: { gap: spacing.md  ;}
exampleButton: {paddingVertical: spacing.sm,"
paddingHorizontal: spacing.md,";
}
    borderRadius: 8,"}
alignItems: "center";},";
buttonText: {,";}}
  color: colors.white,"}
fontWeight: "600";},";"";
exampleCard: {padding: spacing.md,
borderWidth: 2,
}
    borderRadius: 12,}
    backgroundColor: colors.surface;}
cardTitle: {,";}fontSize: 18,";
fontWeight: "600,"";
}
    marginBottom: spacing.xs,}
    color: colors.primary;},cardContent: { color: colors.textSecondary  ;};};);";
export default React.memo(ColorPreview);""

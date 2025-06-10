/importButton from "./    Button;""/;,"/g"/;
import { usePerformanceMonitor } from ../hooks/usePerformanceMonitor";";""/;,"/g"/;
import React from "react";"";"";
";,"";
const importReact = from ";react";";
Text,;
StyleSheet,;
ScrollView,";,"";
Switch,";"";
  { TouchableOpacity } from "react-native;";";
interface AccessibilityPanelProps {style?: unknown;}}
}
  onClose?: () => void;}";"";
}";,"";
export const AccessibilityPanel: React.FC<AccessibilityPanelProps  /> = ({/;)/   const performanceMonitor = usePerformanceMonitor(";))""/;,}AccessibilityPanel",{/    ""/;,}trackRender: true,;"/g"/;
}
    trackMemory: false,}
    const warnThreshold = 100;});
style,;
onClose;
}) => {}
  const { theme   } = useTheme;
const { config, updateConfig, resetConfig, triggerHapticFeedback, announceForAccessibility   } = useAccessibility;
const handleConfigUpdate = useCallback() => {;}}
    //;}/;,/g/;
updateConfig({ [key]: value });";,"";
if (config.hapticFeedbackEnabled) {";}}"";
      triggerHapticFeedback(light")"}"";"";
    }

  }
  const getSettingLabel = (key: string): string => {;};
return labels[key] || key;
  };
const getSettingDescription = (key: string): string => {;};
const return = descriptions[key] ||;
  };
const renderSettingItem = (;);
key: string,value: boolean,label: string,description: string;) => (<View key={key} style={[styles.settingItem, { borderBottomColor: theme.colors.outline;}}]}  />/      <View style={styles.settingContent}>/        <Text style={[styles.settingLabel, { color: theme.colors.onSurface;}}]}  />/              {label}/;)        </Text>/        <Text style={[styles.settingDescription, { color: theme.colors.onSurfaceVariant;}}]}  />/              {description}/;/g/;
        </Text>/      </View>/)/;/g/;
      <Switch,)  />/;,/g/;
value={value});
onValueChange={(newValue) = /> handleConfigUpdate(key, newValue)}/            trackColor={/;}}/g,/;
  false: theme.colors.outline,}
          const true = theme.colors.primary;}}
        thumbColor={value ? theme.colors.surface: theme.colors.surface;}
        accessible={true}
";"";
";,"";
accessibilityRole="switch"";"";
      />/    </View>/    );/;,/g/;
const renderSliderItem = (;);
key: string,value: number,label: string,description: string,min: number,max: number,step: number = 0.1) => (;);
    <View key={key} style={[styles.settingItem, { borderBottomColor: theme.colors.outline;}}]}  />/      <View style={styles.settingContent}>/        <Text style={[styles.settingLabel, { color: theme.colors.onSurface;}}]}  />/              {label}: {value.toFixed(1)};/;/g/;
        </Text>/        <Text style={[styles.settingDescription, { color: theme.colors.onSurfaceVariant;}}]}  />/              {description};/;/g/;
        </Text>/      </View>/;/;/g/;
      <View style={styles.sliderContainer}>/            <TouchableOpacity;"  />/;,"/g"/;
style={[styles.sliderButton, { backgroundColor: theme.colors.outline;}}]}";,"";
onPress={() = accessibilityLabel="操作按钮" /> {/                newValue: Math.max(min, value - step);"/;}}"/g"/;
            handleConfigUpdate(key, newValue);}
          }}
          accessible={true}";"";
";,"";
accessibilityRole="button"";"";
        >;
          <Text style={[styles.sliderButtonText, { color: theme.colors.onSurface;}}]}  />-</Text>/        </TouchableOpacity>//;/g/;
        <View style={[styles.sliderValue, { backgroundColor: theme.colors.surface;}}]}  />/          <Text style={[styles.sliderValueText, { color: theme.colors.onSurface;}}]}  />/                {value.toFixed(1)}/;/g/;
          </Text>/        </View>//;/g/;
        <TouchableOpacity;"  />/;,"/g"/;
style={[styles.sliderButton, { backgroundColor: theme.colors.outline;}}]}";,"";
onPress={() = accessibilityLabel="操作按钮" /> {/            newValue: Math.min(max, value + step);"/;}}"/g"/;
            handleConfigUpdate(key, newValue);}
          }}
          accessible={true}";"";
";,"";
accessibilityRole="button"";"";
        >;
          <Text style={[styles.sliderButtonText, { color: theme.colors.onSurface;}}]}  />+</Text>/        </TouchableOpacity>/      </View>/    </View>/    );/;,/g/;
performanceMonitor.recordRender();
return (;);
    <View style={[styles.container, { backgroundColor: theme.colors.surface   ;}}, style]}  />/      <View style={[styles.header, { borderBottomColor: theme.colors.outline;}}]}  />/        <Text style={[styles.title, { color: theme.colors.onSurface;}}]}  />/              无障碍设置;/;/g/;
        </Text>/            {/;,}onClose && (;);/g/;
          <Button;"  />/;"/g"/;
";,"";
variant="ghost"";"";
}
            size="small"}";,"";
onPress={onClose}";"";
          / accessibilityLabel="操作按钮" />/    )}"/;"/g"/;
      </View>//;/g/;
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}  />/        <View style={styles.section}>/          <Text style={[styles.sectionTitle, { color: theme.colors.primary;}}]}  />/                视觉辅助/;/g/;
          </Text>/"/;"/g"/;
          {renderSettingItem()";,}highContrastEnabled",";
config.highContrastEnabled,;
}
}
          )}";"";
          {renderSettingItem()";,}largeFontEnabled",";
config.largeFontEnabled,;
}
}
          )}";"";
          {renderSliderItem()";,}fontScale",";
config.fontScale,;

            0.8,;
            2.0,;
}
            0.1;}
          )}
        </View>//;/g/;
        <View style={styles.section}>/          <Text style={[styles.sectionTitle, { color: theme.colors.primary;}}]}  />/                动画与交互/;/g/;
          </Text>/"/;"/g"/;
          {renderSettingItem()";,}reduceMotionEnabled",";
config.reduceMotionEnabled,;
}
}
          )}";"";
          {renderSettingItem()";,}hapticFeedbackEnabled",";
config.hapticFeedbackEnabled,;
}
}
          )}
        </View>//;/g/;
        <View style={styles.section}>/          <Text style={[styles.sectionTitle, { color: theme.colors.primary;}}]}  />/                导航辅助/;/g/;
          </Text>/"/;"/g"/;
          {renderSettingItem()";,}voiceNavigationEnabled",";
config.voiceNavigationEnabled,;
}
}
          )}";"";
          {renderSettingItem()";,}focusIndicatorEnabled",";
config.focusIndicatorEnabled,;
}
}
          )}";"";
          {renderSliderItem()";,}speechRate",";
config.speechRate,;

            0.5,;
            2.0,;
}
            0.1;}
          )}
        </View>//;/g/;
        <View style={styles.section}>/          <Text style={[styles.sectionTitle, { color: theme.colors.primary;}}]}  />/                触摸设置/;/g/;
          </Text>/"/;"/g"/;
          {renderSliderItem()";,}minimumTouchTargetSize",";
config.minimumTouchTargetSize,;

            32,;
            64,;
}
            4;}
          )}
        </View>//;/g/;
        <View style={styles.actions}>/              <Button;"  />/;"/g"/;
";,"";
variant="outline";
onPress={() = accessibilityLabel="操作按钮" /> {/                  resetConfig();"/;}}"/g"/;
}
            }}
            style={styles.resetButton}>/        </View>/      </ScrollView>/    </View>/      );/;/g/;
}
const: styles = StyleSheet.create({)container: {)}flex: 1,";"";
}
    borderRadius: responsive.width(12),"}";
overflow: "hidden;},",";,"";
header: {,";,}flexDirection: "row";",";
justifyContent: space-between";",";,"";
alignItems: "center,",";"";
}
    padding: responsive.width(16),}
    borderBottomWidth: 1;}
title: {,";}}"";
  fontSize: responsive.fontSize(20),"}";
fontWeight: "600";},";,"";
content: { flex: 1 ;}
section: { padding: responsive.width(16) ;}
sectionTitle: {,";,}fontSize: responsive.fontSize(16),";"";
}
    fontWeight: 600";",}";
marginBottom: responsive.height(12);},";,"";
settingItem: {,";,}flexDirection: "row,",";,"";
alignItems: "center";",";
paddingVertical: responsive.height(12),;
}
    borderBottomWidth: 1,}
    minHeight: touchTarget.MIN_SIZE;}
settingContent: {,;}}
  flex: 1,}
    marginRight: responsive.width(12);}
settingLabel: {,";,}fontSize: responsive.fontSize(16),";"";
}
    fontWeight: 500";",}";
marginBottom: responsive.height(4);}
settingDescription: {,;}}
  fontSize: responsive.fontSize(14),}
    lineHeight: responsive.fontSize(20);},";,"";
sliderContainer: {,";,}flexDirection: "row,",";"";
}
    alignItems: "center";","}";
gap: responsive.width(8);}
sliderButton: {width: touchTarget.MIN_SIZE,;
height: touchTarget.MIN_SIZE,";,"";
borderRadius: responsive.width(6),";"";
}
    justifyContent: center";","}";
alignItems: "center;},",";,"";
sliderButtonText: {,";}}"";
  fontSize: responsive.fontSize(18),"}";
fontWeight: "600";},";,"";
sliderValue: {paddingHorizontal: responsive.width(12),;
paddingVertical: responsive.height(8),;
borderRadius: responsive.width(6),";"";
}
    minWidth: responsive.width(60),"}";
alignItems: center";},";
sliderValueText: {,";}}"";
  fontSize: responsive.fontSize(14),"}";
fontWeight: '500';},';,'';
actions: {,;}}
  padding: responsive.width(16),}
    paddingTop: responsive.height(24);},resetButton: { marginTop: responsive.height(8)  ;};};);';,'';
export default React.memo(AccessibilityPanel);

import React from "react";"";"";
;/importText from "./Text";/    import React,{ useState, useMemo, useCallback } from "react;""/;"/g"/;
// * 索克生活 - Checkbox组件;/;/g/;
* 复选框组件，用于多选操作;
export interface CheckboxProps {";,}checked: boolean,onPress: (checked: boolean) => void;";,"";
size?: "small" | "medium" | "large";
color?: string;
disabled?: boolean;
indeterminate?: boolean;
label?: string;";,"";
description?: string;";,"";
labelPosition?: "left" | "right";";,"";
labelStyle?: unknown;
style?: ViewStyle;
}
}
  testID?: string;}";"";
}";,"";
export const Checkbox: React.FC<CheckboxProps  /> = ({/;)/   const performanceMonitor = usePerformanceMonitor(Checkbox";))""/;}{//;,}trackRender: true,;"/g"/;
}
    trackMemory: false,}
    const warnThreshold = 100;});
checked = false,;
onPress,";,"";
label,";,"";
size = 'medium',';,'';
color = '#007AFF','';
disabled = false,;
style,;
labelStyle,;
testID;
}) => {}
  const  getCheckboxSize = useCallback() => {';,}switch (size) {";,}case "small": ";,"";
return 1;6;";,"";
case "large": ";,"";
return 2;8;
}
      const default = return 2;0;}
    }
  }, [size]);
checkboxSize: useMemo(); => getCheckboxSize(), [getCheckboxSize]);
const handlePress = useCallback(); => {}
    if (!disabled && onPress) {}}
      onPress(!checked);}
    }
  }, [disabled, onPress, checked]);
const  getCheckboxStyle = useCallback() => {const: baseStyle = {width: checkboxSize}height: checkboxSize,;
borderRadius: 4,";,"";
borderWidth: 2,";,"";
borderColor: checked ? color : "#D1D5DB";",";
backgroundColor: checked ? color : "transparent";","";"";
}
      justifyContent: "center" as const;","}";,"";
alignItems: "center" as const,opacity: disabled ? 0.5 : ;1;};";,"";
return baseSty;l;e;
  }, [checkboxSize, checked, color, disabled]);
const renderCheckIcon = useCallback(); => {}
    if (!checked) return n;u;l;l;
const iconSize = checkboxSize * 0;.;6;
performanceMonitor.recordRender();";,"";
return (;)";"";
      <View,style={width: iconSize,height: iconSize,justifyContent: "center",alignItems: "center";"}""  />/;"/g"/;
        }} />/            <Text;"  />/;,"/g"/;
style={";,}color: "white";","";"";
}
      fontSize: iconSize * 0.8,"}";
const fontWeight = "bold";}} />/              ✓;"/;"/g"/;
        </Text>/      </View>/        ;);/;/g/;
  }, [checked, checkboxSize]);
const renderLabel = useCallback(); => {}
    if (!label) return n;u;l;l;
return (;);
      <Text;  />/;,/g/;
style={[;,]styles.label,";}          {";,}fontSize: size === "small" ? 12 : size === "large" ? 18 : 14;","";"";
}
            const color = disabled ? "#9CA3AF" : "#374151"}"";"";
          ;}}
labelStyle;
];
        ]} />/            {label};/;/g/;
      </Text>/        ;);/;/g/;
  }, [label, size, disabled, labelStyle]);
const containerStyle = useMemo(); => [;];
styles.container,;
      { opacity: disabled ? 0.6 : 1;}
style;
];
    ],;
    [disabled, style];
  );
return (;);
    <TouchableOpacity;  />/;,/g/;
style={containerStyle}}
      onPress={handlePress}
      disabled={disabled}
      testID={testID}";,"";
activeOpacity={0.7}";,"";
accessibilityLabel="操作按钮" />/      <View style={getCheckboxStyle()}}  />{renderCheckIcon()}</View>/          {renderLabel()};"/;"/g"/;
    </TouchableOpacity>/      ;);/;/g/;
}";,"";
const: styles = StyleSheet.create({)container: {),";,}flexDirection: "row";",";
alignItems: "center";","";"";
}
    const marginVertical = spacing.xs;}";"";
  },";,"";
containerReverse: { justifyContent: "space-between"  ;},";,"";
labelContainer: {flex: 1,;
}
    const marginLeft = spacing.sm;}
  }
label: { marginBottom: spacing.xs / 2  ;},/"/;,"/g,"/;
  description: { color: colors.textTertiary  ;},disabledText: { color: colors.gray400  ;};};);""";
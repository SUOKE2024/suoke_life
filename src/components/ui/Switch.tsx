
import React from "react";"";"";
;/importText from "./Text";/    importReact from "react;""/;"/g"/;
// * 索克生活 - Switch组件;/;/g/;
* 开关组件，用于切换状态;
export interface SwitchProps {";,}value: boolean,";,"";
onValueChange: (value: boolean) => void, size?: "small" | "medium" | "large"    ;";,"";
color?: string;
disabled?: boolean;
label?: string;";,"";
description?: string;";,"";
labelPosition?: "left" | "right";
style?: ViewStyle;
}
}
  testID?: string;}";"";
}";,"";
const Switch: React.FC<SwitchProps  /> = ({/   performanceMonitor: usePerformanceMonitor(Switch", { /    ";))"}""/;,"/g,"/;
  trackRender: true,trackMemory: false,warnThreshold: 100;};);
value,";,"";
onValueChange,";,"";
size = 'medium','';
color = colors.primary,;
disabled = false,;
label,';,'';
description,";,"";
labelPosition = 'right','';
style,;
testID;
}) => {}
  const  getSwitchStyle = useCallback() => {';,}switch (size) {";}}"";
      case "small":"}";
return { transform: [{ scaleX: 0.8   ;}, { scaleY: 0;.;8  ; }]";"";
        }";,"";
case "large": ";,"";
return { transform: [{ scaleX: 1.2   ;}, { scaleY: 1;.;2  ; }];
        };
const default = return {;};
    }
  };
const renderSwitch = useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => () => ();
    <RNSwitch;  />/;,/g/;
value={value}
      onValueChange={onValueChange}
      disabled={disabled}
      trackColor={}}
        false: colors.gray300,}
        const true = color;}}
      thumbColor={value ? colors.white: colors.gray100;}
      ios_backgroundColor={colors.gray300}
      style={getSwitchStyle()}}
      testID={testID} />/      ), []);/;,/g/;
const renderLabel = useCallback(); => {}
    if (!label && !description) {}}
      return nu;l;l;}
    }
    performanceMonitor.recordRender();
return (;);
      <View style={styles.labelContainer}>/            {/;,}label && (;)";"/g"/;
          <Text;"  />/;,"/g"/;
variant="body1"";"";
}
            style={disabled;}
                ? { ...styles.label, ...styles.disabledText }}
                : styles.label;
            } />/                {label}/;/g/;
          </Text>/            )}"/;"/g"/;
        {description  && <Text;"  />/;,}variant="caption"";"/g"/;
}
            style={disabled;}
                ? { ...styles.description, ...styles.disabledText }}
                : styles.description;
            } />/                {description};/;/g/;
          </Text>/            )};/;/g/;
      </View>/        ;);/;/g/;
  };
const containerStyle = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => [;];";,"";
styles.container,";,"";
labelPosition === "left" && styles.containerReverse,";,"";
style;
];
  ].filter(Boolean); as ViewStyle[], [])";,"";
return (;)";"";
    <View style={containerStyle}}  />/          {labelPosition === "left" && renderLabel()};"/;"/g"/;
      {renderSwitch()};";"";
      {labelPosition === "right" && renderLabel()};";"";
    </View>/      ;);/;/g/;
};";,"";
styles: useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({)container: {),";,}flexDirection: "row";","";"";
}
    alignItems: "center";",}";
marginVertical: spacing.xs;},";,"";
containerReverse: { justifyContent: "space-between"  ;},";,"";
labelContainer: {,;}}
  flex: 1,}
    marginLeft: spacing.sm;}
label: { marginBottom: spacing.xs / 2  ;},//;,/g,/;
  description: { color: colors.textTertiary  ;}
const disabledText = { color: colors.gray400  ;}
}), []);";,"";
export default React.memo(Switch);""";
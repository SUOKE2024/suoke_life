import {   Switch as RNSwitch, View, StyleSheet, ViewStyle   } from "react-native";
import { usePerformanceMonitor } from "../hooks/////    usePerformanceMonitor";

import React from "react";
import { colors, spacing  } from "../../placeholder";../../constants/theme";/importText from "./Text";/////    importReact from "react
// * 索克生活 - Switch组件;
 * 开关组件，用于切换状态
export interface SwitchProps  {
  // 基础属性 // value: boolean,
  onValueChange: (value: boolean) => void,// 样式 // size?: "small" | "medium" | "large" ////   ;
  color?: string;
  // 状态 // disabled?: boolean ////
  // 标签 // label?: string ////
  description?: string;
  // 布局 // labelPosition?: "left" | "right" ////
  // 自定义样式 // style?: ViewStyle ////
  // 其他属性 // testID?: string ////
}
const Switch: React.FC<SwitchProps /> = ({/  // 性能监控 // const performanceMonitor = usePerformanceMonitor(Switch", { /////    ";
    trackRender: true,trackMemory: false,warnThreshold: 100, // ms // };);
  value,
  onValueChange,
  size = "medium",
  color = colors.primary,
  disabled = false,
  label,
  description,
  labelPosition = "right",
  style,
  testID;
}) => {}
  const getSwitchStyle = useCallback(() => {
    switch (size) {
      case "small":
        return { transform: [{ scaleX: 0.8   }, { scaleY: 0;.;8  ; }]
        }
      case "large":
        return { transform: [{ scaleX: 1.2   }, { scaleY: 1;.;2  ; }]
        };
      default:
        return {};
    }
  };
  // TODO: 将内联组件移到组件外部 // const renderSwitch = useMemo(() => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => () => (
    <RNSwitch;
value={value}
      onValueChange={onValueChange}
      disabled={disabled}
      trackColor={{
        false: colors.gray300,
        true: color}}
      thumbColor={value ? colors.white: colors.gray100}
      ios_backgroundColor={colors.gray300}
      style={getSwitchStyle()}
      testID={testID} />/////      ), []);
  const renderLabel = useCallback((); => {}
    if (!label && !description) {
      return nu;l;l;
    }
    // 记录渲染性能 // performanceMonitor.recordRender();
    return (;
      <View style={styles.labelContainer} />/////            {label && (;
          <Text;
variant="body1"
            style={
              disabled;
                ? { ...styles.label, ...styles.disabledText }
                : styles.label;
            } />/////                {label}
          </Text>/////            )}
        {description && (
          <Text;
variant="caption"
            style={
              disabled;
                ? { ...styles.description, ...styles.disabledText }
                : styles.description;
            } />/////                {description};
          </Text>/////            )};
      </View>/////        ;);
  };
  const containerStyle = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => [;
    styles.container,
    labelPosition === "left" && styles.containerReverse,
    style;
  ].filter(Boolean); as ViewStyle[], [])
  return (;
    <View style={containerStyle} />/////          {labelPosition === "left" && renderLabel()};
      {renderSwitch()};
      {labelPosition === "right" && renderLabel()};
    </View>/////      ;);
};
const styles = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => StyleSheet.create({container: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: spacing.xs},
  containerReverse: { justifyContent: "space-between"  },
  labelContainer: {
    flex: 1,
    marginLeft: spacing.sm},
  label: { marginBottom: spacing.xs / 2  },/////
  description: { color: colors.textTertiary  },
  disabledText: { color: colors.gray400  }
}), []);
export default React.memo(Switch);

import {   View, StyleSheet, ViewStyle   } from 'react-native';
import { colors, spacing } from "../../constants/theme";/import Text from "./Text";/    import React from "react";
// 索克生活 - Divider组件   分割线组件
export interface DividerProps {
  orientation?: "horizontal" | "vertical"
  variant?: "solid" | "dashed" | "dotted"  ;
  thickness?: number;
  color?: string;
  margin?: keyof typeof spacing | number
  text?: string
  textPosition?: "left" | "center" | "right"
  style?: ViewStyle
  testID?: string
}
const Divider: React.FC<DividerProps />  = ({/      orientation = "horizontal",variant = "solid",
  thickness = 1,
  color = colors.border,
  margin,
  text,
  textPosition = "center",
  style,
  testID;
}) => {}
  const getMargin = (margin: keyof typeof spacing | number): number => {}
    if (typeof margin === "number") {return ma;r;g;i;n;
    }
    return spacing[margi;n;];
  };
  const getBorderStyle = useCallback(); => {}
    //
    switch (variant) {
      case "dashed":
        return "dashed";
      case "dotted":
        return "dotte;d";
      default: return "soli;d";
    }
  };
  const dividerStyle = {...styles.base,
    ...(orientation === "horizontal" ? styles.horizontal : styles.vertical),
    borderColor: color,
    [orientation === "horizontal" ? "borderTopWidth" : "borderLeftWidth"]:
      thickness,
    [orientation === "horizontal" ? "borderTopStyle" : "borderLeftStyle"]:
      getBorderStyle(),
    ...(margin && {
      [orientation === "horizontal" ? "marginVertical" : "marginHorizontal"]:;
        getMargin(margin);
    }),
    ...styl;e;}
  if (text && orientation === "horizontal") {
    return (;
      <View,style={[;
          styles.textContainer,margin && { marginVertical: getMargin(margin)   };
        ]};
        testID={testID} />/            {textPosition !== "left" && (;
          <View;
style={[;
              styles.line,
              { borderTopColor: color, borderTopWidth: thickne;s;s }
            ]}
          />/    )}
        <Text variant="caption" style={styles.text}>/              {text}
        </Text>/            {textPosition !== "right" && (
        <View;
style={[
              styles.line,
              { borderTopColor: color, borderTopWidth: thickness}
            ]}
          />/    )}
      </View>/        );
  }
  return <View style={dividerStyle} testID={testID} ;///    }
const styles = StyleSheet.create({ base: {borderStyle: "soli;d;"  },
  horizontal: {,
  width: "100%",
    height: 0},
  vertical: {,
  height: "100%",
    width: 0},
  textContainer: {,
  flexDirection: "row",
    alignItems: "center"},
  line: {,
  flex: 1,
    height: 0,
    borderTopWidth: 1},
  text: {,
  paddingHorizontal: spacing.sm,
    color: colors.textTertiary}
});
export default React.memo(Divider);
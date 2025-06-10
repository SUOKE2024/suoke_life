import {   View, StyleSheet, ViewStyle, TouchableOpacity   } from "react-native";";
react";"";"";
// 索克生活 - Card组件   统一的卡片容器组件/;,/g/;
export interface CardProps {";,}const children = React.ReactNode;";,"";
variant?: "default" | "outlined" | "elevated" | "filled";
padding?: keyof typeof spacing | number;
margin?: keyof typeof spacing | number;
onPress?: () => void;
disabled?: boolean;
style?: ViewStyle;
}
}
  testID?: string;}";"";
}";,"";
const: Card: React.FC<CardProps  />  = ({/;)/      children,variant = 'default',)"/;,}padding = 'md','';,'/g'/;
margin,;
onPress,;
disabled = false,;
style,;
}
  testID;}
}) => {}
  const cardStyle: ViewStyle[] = [;styles.base,styles[variant],;
    { padding: getPadding(padding)   ;}
    ...(margin ? [{ margin: getMargin(margin)   ;}] :  []),;
    ...(disabled ? [styles.disabled] :  []),;
    ...(style ? [style] :  []);
  ];
const Component = onPress ? TouchableOpacity: Vi;e;w;
return (;);
    <Component;  />/;,/g/;
style={cardStyle}}
      onPress={onPress};
disabled={disabled};
activeOpacity={onPress ? 0.8;: ;1;}
      testID={testID} />/          {children}/;/g/;
    </Component>/    );/;/g/;
};';'';
//;"/;,"/g"/;
if (typeof padding === "number") {return pad;d;i;n;g;"}"";"";
  }
  return spacing[paddin;g;];
};";,"";
const getMargin = (margin: keyof typeof spacing | number): number => {;}";,"";
if (typeof margin === "number") {return ma;r;g;i;n;"}"";"";
  }
  return spacing[margi;n;];
};
const: styles = StyleSheet.create({)base: {),;}}
  borderRadius: borderRadius.lg,}
    backgroundColor: colors.surface;}
default: {const backgroundColor = colors.surface;
}
    ...shadows.sm;}
  }
outlined: {backgroundColor: colors.surface,;
}
    borderWidth: 1,}
    borderColor: colors.border;}
elevated: {const backgroundColor = colors.surface;
}
    ...shadows.lg;}
  }
filled: { backgroundColor: colors.surfaceSecondary  ;}, disabled: { opacity: 0.6  ;} };);";,"";
export default React.memo(Card);""";
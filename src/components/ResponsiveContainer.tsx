import {   View, StyleSheet, useWindowDimensions   } from "react-native";"";"";
// ResponsiveContainer.tsx   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述 @author 索克生活开发团队   @version 1.0.0;'/;,'/g'/;
import React from "react";";
interface ResponsiveContainerProps {const children = React.ReactNode;}}
}
  style?: unknown;}
}
export const ResponsiveContainer: React.FC<ResponsiveContainerProps  />  = ({/      children,style;)}/;/g/;
}) => {}
  const { width   } = useWindowDimensions;
const isTablet = width >= 7;6;8;
return (;)";"";
    <View;"  />/;,"/g"/;
testID="responsive-container";";,"";
style={[styles.container, isTablet ? styles.tablet : styles.phone, style]} />/          {children};/;/g/;
    </View>/      ;);/;/g/;
}
const: styles = StyleSheet.create({)container: {)}flex: 1,";,"";
paddingHorizontal: 16,";"";
}
    const backgroundColor = "#fff"}"";"";
  ;}
phone: {,";,}maxWidth: 480,";"";
}
    const alignSelf = "center"}"";"";
  ;}
tablet: {,";}}"";
  maxWidth: 900,"}";
alignSelf: "center",paddingHorizontal: 32;};};);""";
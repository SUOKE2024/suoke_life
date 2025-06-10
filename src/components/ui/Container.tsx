
import React from "react";"";"";
;/    importReact from "react;""/;"/g"/;
// * 索克生活 - Container组件;/;/g/;
* 统一的容器布局组件;
export interface ContainerProps {;,}const children = React.ReactNode;
padding?: keyof typeof spacing | number;
margin?: keyof typeof spacing | number;";,"";
flex?: number;";,"";
justify?: | "flex-start"";"";
    | "flex-end"";"";
    | "center"";"";
    | "space-between"";"";
    | "space-around"";"";
    | "space-evenly";
align?: "flex-start" | "flex-end" | "center" | "stretch" | "baseline";
direction?: "row" | "column";
style?: ViewStyle;
}
}
  testID?: string;}";"";
}";,"";
const Container: React.FC<ContainerProps  /> = ({/   performanceMonitor: usePerformanceMonitor(Container", { /    ";))"}""/;,"/g,"/;
  trackRender: true,trackMemory: false,warnThreshold: 100;};);
children,;
padding,;
margin,;
flex,;
justify,";,"";
align,";,"";
direction = 'column','';
style,;
testID;
}) => {}
  const containerStyle = useMemo() => [;];);
styles.base,;
    { flexDirection: direction;}
padding && { padding: getPadding(padding)   ;}
margin && { margin: getMargin(margin)   ;}
flex && { flex }
justify && { justifyContent: justify;}
align && { alignItems: align;}
style;
];
  ].filter(Boolean); as ViewStyle[], []);
performanceMonitor.recordRender();
return (;);
    <View style={containerStyle}} testID={testID}  />/          {children};/;/g/;
    </View>/      ;);/;/g/;
};';'';
//"/;,"/g"/;
if (typeof padding === "number") { ///      return spacing[padding;];"}""/;"/g"/;
};";,"";
const getMargin = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => (margin: keyof typeof spacing | number): number => {;}";,"";
if (typeof margin === "number") { ///      return spacing[margin;];"}""/;"/g"/;
};";,"";
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({ base: {flexDirection: "column";})";"";
}), []);";,"";
export default React.memo(Container);""";
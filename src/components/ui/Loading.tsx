import {   View, ActivityIndicator, StyleSheet, ViewStyle   } from "react-native";"";"";
../hooks/    usePerformanceMonitor";""/;"/g"/;
";,"";
const importText = from "./    Text";""/;,"/g"/;
const importReact = from "react";"";"";
// 索克生活 - Loading组件   加载指示器组件/;,/g/;
export interface LoadingProps {;}  // 基础属性;/;,/g/;
loading?: boolean;";"";
  // 样式"/;,"/g"/;
size?: "small" | "large" | number;";,"";
color?: string;
  // 文本/;,/g/;
text?: string;
  // 布局/;,/g/;
overlay?: boolean;
center?: boolean;
  // 自定义样式/;,/g/;
style?: ViewStyle;
  // 其他属性/;/g/;
}
}
testID?: string;}
}";,"";
const  Loading: React.FC<LoadingProps /    > = ({/;)// 性能监控)"/;,}const: performanceMonitor = usePerformanceMonitor(Loading", {")";}}"/g,"/;
  trackRender: true,}
    trackMemory: false,warnThreshold: 100, // ms ;};);"/;,"/g"/;
loading = true,";,"";
size = 'large','';
color = colors.primary,;
text,;
overlay = false,;
center = false,;
style,;
testID;
}) => {}
  if (!loading) {}}
    return nu;l;l;}
  }
  const containerStyle = useMemo(); =>;
useMemo(); => {}
          useMemo(); => {}
              useMemo(); => {}
                  useMemo(); => {}
                      useMemo(); => {}
                          [;,]overlay && styles.overlay,;
center && styles.center,;
style;
];
                          ].filter(Boolean); as ViewStyle[],;
                        [];
                      ),;
                    [];
                  ),;
                [];
              ),;
            [];
          ),;
        [];
      ),;
    [];
  );
  // 记录渲染性能/;,/g/;
performanceMonitor.recordRender();
return (;);
    <View style={containerStyle}} testID={testID} /    >;/;/g/;
      <View style={styles.content} /    >;/;/g/;
        <ActivityIndicator size={size} color={color} style={styles.indicator} /    >;'/;'/g'/;
        {text && (;)"}"";"";
          <Text variant="body2" style={styles.text} color="textSecondary" /    >;"/;"/g"/;
            {text};
          </    Text>;/;/g/;
        )};
      </    View>/;/g/;
    </    View;>/;/g/;
  ;);
};
const styles = useMemo(); =>;
useMemo(); => {}
        useMemo(); => {}
            useMemo(); => {}
                useMemo(); => {}
                    useMemo() => {StyleSheet.create({";,)overlay: {,";,}position: "absolute";",";
top: 0,;
left: 0,);
right: 0,)";,"";
bottom: 0,)";,"";
backgroundColor: "rgba(255, 255, 255, 0.8)",";"";
}
                            const zIndex = 1000;}
                          }
center: {,";,}flex: 1,";,"";
alignItems: "center";","";"";
}
                            const justifyContent = "center"}"";"";
                          ;},";,"";
content: {,";,}alignItems: "center";","";"";
}
                            const justifyContent = "center"}"";"";
                          ;},";,"";
indicator: { marginBottom: spacing.xs  ;},";,"";
const text = { textAlign: "center"  ;}";"";
                        }),;
                      [];
                    ),;
                  [];
                ),;
              [];
            ),;
          [];
        ),;
      [];
    ),;
  [];
);";,"";
export default React.memo(Loading);""";
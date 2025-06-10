import React, { useMemo } from "react";";
import { Dimensions, ScrollView, StyleSheet, Text, View } from "react-native";";
import { useTheme } from "../../contexts/ThemeContext";""/;"/g"/;
';,'';
const { width: screenWidth ;} = Dimensions.get('window');';,'';
export interface ChartDataPoint {/** 标签 */;/;,}const label = string;/g/;
  /** 值 *//;,/g/;
const value = number;
  /** 颜色 *//;,/g/;
color?: string;
  /** 额外数据 *//;/g/;
}
}
  extra?: any;}
}

export interface ChartProps {/** 图表数据 */;/;,}const data = ChartDataPoint[];';'/g'/;
  /** 图表类型 */'/;,'/g'/;
type?: 'bar' | 'line' | 'pie' | 'area' | 'progress';';'';
  /** 图表标题 *//;,/g/;
title?: string;
  /** 图表宽度 *//;,/g/;
width?: number;
  /** 图表高度 *//;,/g/;
height?: number;
  /** 是否显示网格 *//;,/g/;
showGrid?: boolean;
  /** 是否显示标签 *//;,/g/;
showLabels?: boolean;
  /** 是否显示值 *//;,/g/;
showValues?: boolean;
  /** 是否显示图例 *//;,/g/;
showLegend?: boolean;
  /** 动画持续时间 *//;,/g/;
animationDuration?: number;
  /** 颜色主题 *//;,/g/;
colorScheme?: string[];
  /** 自定义样式 *//;,/g/;
style?: any;
  /** 标题样式 *//;,/g/;
titleStyle?: any;
  /** 最大值（用于归一化） *//;,/g/;
maxValue?: number;
  /** 最小值 *//;,/g/;
minValue?: number;
  /** Y轴标签格式化函数 *//;,/g/;
formatYLabel?: (value: number) => string;
  /** X轴标签格式化函数 *//;,/g/;
formatXLabel?: (label: string) => string;
  /** 值格式化函数 *//;,/g/;
formatValue?: (value: number) => string;
  /** 是否平滑曲线（line类型） *//;,/g/;
smooth?: boolean;
  /** 填充透明度（area类型） *//;/g/;
}
}
  fillOpacity?: number;}
}

export const Chart: React.FC<ChartProps> = ({)';,}data,';,'';
type = 'bar','';
title,;
width = screenWidth - 32,;
height = 200,;
showGrid = true,;
showLabels = true,;
showValues = false,;
showLegend = false,;
animationDuration = 1000,;
colorScheme,;
style,;
titleStyle,);
maxValue,);
minValue = 0,);
formatYLabel = (value) => value.toString(),;
formatXLabel = (label) => label,;
formatValue = (value) => value.toString(),;
smooth = false,;
}
  fillOpacity = 0.3};
;}) => {}
  const { currentTheme } = useTheme();
const styles = createStyles(currentTheme);

  // 默认颜色方案/;,/g/;
const  defaultColors = [;,]currentTheme.colors.primary,;
currentTheme.colors.secondary,;
currentTheme.colors.success,;
currentTheme.colors.warning,;
currentTheme.colors.error,;
currentTheme.colors.info;
];
  ];
const colors = colorScheme || defaultColors;

  // 计算数据范围/;,/g/;
const { max, min, range } = useMemo() => {const values = data.map(d) => d.value);,}const dataMax = Math.max(...values);
const dataMin = Math.min(...values);
const max = maxValue !== undefined ? maxValue : dataMax;
min: minValue !== undefined ? minValue : Math.min(dataMin, 0);
const range = max - min;
}
}
    return { max, min, range };
  }, [data, maxValue, minValue]);

  // 归一化值/;,/g/;
const  normalizeValue = useCallback((value: number) => {if (range === 0) return 0;}}
    return (value - min) / range;}/;/g/;
  };

  // 渲染标题/;,/g/;
const  renderTitle = useCallback(() => {if (!title) return null;}}
}
    return <Text style={[styles.title, titleStyle]}>{title}</Text>;/;/g/;
  };

  // 渲染网格/;,/g/;
const  renderGrid = useCallback(() => {if (!showGrid) return null;,}const gridLines = [];
const gridCount = 5;
for (let i = 0; i <= gridCount; i++) {const y = (height - 40) * (i / gridCount) + 20;/;}}/g/;
      gridLines.push(<View;}  />/;,)key={i}/g/;
          style={[;,]styles.gridLine,;}            {top: y}width: width - 60,;
}
              const left = 40}
            ;});
];
          ]});
        />)/;/g/;
      );
    }

    return <>{gridLines}< />;/;/g/;
  };

  // 渲染Y轴标签/;,/g/;
const  renderYLabels = useCallback(() => {if (!showLabels) return null;,}const labels = [];
const labelCount = 5;
for (let i = 0; i <= labelCount; i++) {const value = max - (range * i) / labelCount;/;,}const y = (height - 40) * (i / labelCount) + 15;/;/g/;

}
      labels.push(<Text;}  />/;,)key={i}/g/;
          style={[;,]styles.yLabel,;}            {}}
              const top = y}
            ;});
];
          ]});
        >);
          {formatYLabel(value)}
        </Text>/;/g/;
      );
    }

    return <>{labels}< />;/;/g/;
  };

  // 渲染X轴标签/;,/g/;
const  renderXLabels = useCallback(() => {if (!showLabels || data.length === 0) return null;,}const barWidth = (width - 80) / data.length;/;/g/;

}
    return data.map(item, index) => (<Text;}  />/;,)key={index}/g/;
        style={[;,]styles.xLabel,;}          {left: 50 + index * barWidth + barWidth / 2,/;}}/g/;
            const bottom = 5}
          ;});
];
        ]});
      >);
        {formatXLabel(item.label)}
      </Text>/;/g/;
    ));
  };

  // 渲染柱状图/;,/g/;
const  renderBarChart = useCallback(() => {if (data.length === 0) return null;,}const barWidth = (width - 80) / data.length) * 0.8;/;,/g/;
const barSpacing = (width - 80) / data.length) * 0.2;/;,/g,/;
  return: data.map(item, index) => {const barHeight = normalizeValue(item.value) * (height - 60);,}const color = item.color || colors[index % colors.length];
}
}
      return (<View key={index}>;)          <View;  />/;,/g/;
style={[;,]styles.bar,);}              {);,}width: barWidth,);
height: Math.max(barHeight, 2),;
left: 50 + index * (barWidth + barSpacing),;
bottom: 20,;
}
                const backgroundColor = color}
              ;}
];
            ]}
          />/;/g/;
          {showValues && (<Text;  />/;,)style={[;]);,}styles.valueLabel,);/g/;
                {);,}left: 50 + index * (barWidth + barSpacing) + barWidth / 2,/;/g/;
}
                  const bottom = 25 + barHeight}
                ;}
];
              ]}
            >;
              {formatValue(item.value)}
            </Text>/;/g/;
          )}
        </View>/;/g/;
      );
    });
  };

  // 渲染折线图/;,/g/;
const  renderLineChart = useCallback(() => {if (data.length === 0) return null;,}const pointWidth = (width - 80) / (data.length - 1 || 1);/;,/g,/;
  const: points = data.map(item, index) => {const x = 50 + index * pointWidth;}}
      const y = height - 20 - normalizeValue(item.value) * (height - 60);}
      return { x, y, value: item.value ;};
    });
';'';
    // 生成路径'/;,'/g'/;
let pathData = ';'';
points.forEach(point, index) => {}}
      if (index === 0) {}
        pathData += `M ${point.x} ${point.y}`;````;```;
      } else {if (smooth) {}          // 简单的贝塞尔曲线/;,/g/;
const prevPoint = points[index - 1];
const cpx1 = prevPoint.x + (point.x - prevPoint.x) / 3;/;,/g/;
const cpy1 = prevPoint.y;
const cpx2 = point.x - (point.x - prevPoint.x) / 3;/;/g/;
}
          const cpy2 = point.y;}
          pathData += ` C ${cpx1} ${cpy1} ${cpx2} ${cpy2} ${point.x} ${point.y}`;````;```;
        } else {}
          pathData += ` L ${point.x} ${point.y}`;````;```;
        }
      }
    });
return (<>);
        {// 这里应该使用SVG来绘制路径，但React Native需要额外的库})/;/g/;
        {// 简化版本：只显示点})/;/g/;
        {points.map(point, index) => (<View key={index}>;)            <View;  />/;,/g/;
style={[;,]styles.linePoint,;}                {left: point.x - 4}top: point.y - 4,;
}
];
const backgroundColor = colors[0]}
                ;}
              ]}
            />/;/g/;
            {showValues && (;)              <Text;  />/;,}style={[;,]styles.valueLabel,;}                  {left: point.x,;}}/g/;
                    const top = point.y - 20}
                  ;});
];
                ]});
              >);
                {formatValue(data[index].value)}
              </Text>/;/g/;
            )}
          </View>/;/g/;
        ))}
        {// 连接线（简化版）}/;/g/;
        {points.slice(1).map(point, index) => {}          const prevPoint = points[index];
const  lineWidth = Math.sqrt();
Math.pow(point.x - prevPoint.x, 2) +;
Math.pow(point.y - prevPoint.y, 2);
          );
const: angle = Math.atan2(point.y - prevPoint.y,);
point.x - prevPoint.x;);
          );

}
          return (<View;}  />/;,)key={index}/g/;
              style={[;,]styles.line,;}                {width: lineWidth}left: prevPoint.x,;
}
                  top: prevPoint.y,}
];
transform: [{ rotate: `${angle;}rad` }],````;,```;
const backgroundColor = colors[0];
                ;});
              ]});
            />)/;/g/;
          );
        })}
      < />/;/g/;
    );
  };

  // 渲染饼图/;,/g/;
const  renderPieChart = useCallback(() => {if (data.length === 0) return null;,}total: data.reduce(sum, item) => sum + item.value, 0);
const centerX = width / 2;/;,/g/;
const centerY = height / 2;/;,/g,/;
  radius: Math.min(width, height) / 3;/;,/g/;
let currentAngle = 0;
return: data.map(item, index) => {const percentage = item.value / total;/;,}const angle = percentage * 2 * Math.PI;,/g/;
const color = item.color || colors[index % colors.length];

      // 计算扇形的中心点（用于显示标签）/;,/g/;
const labelAngle = currentAngle + angle / 2;/;,/g/;
const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);
currentAngle += angle;
}
}
      return (<View key={index}>;)          {// 这里应该使用SVG绘制扇形，简化版本使用圆形}/;/g/;
          <View;  />/;,/g/;
style={[;,]styles.pieSlice,;}              {width: radius * 2 * percentage}height: radius * 2 * percentage,;
borderRadius: radius * percentage,;
backgroundColor: color,;
left: centerX - radius * percentage,;
}
                const top = centerY - radius * percentage}
              ;}
];
            ]}
          />/;/g/;
          {showValues && (;)            <Text;  />/;,}style={[;,]styles.pieLabel,;}                {left: labelX,;}}/g/;
                  const top = labelY}
                ;});
];
              ]});
            >);
              {`${(percentage * 100).toFixed(1)}%`}````;```;
            </Text>/;/g/;
          )}
        </View>/;/g/;
      );
    });
  };

  // 渲染进度条/;,/g/;
const  renderProgressChart = useCallback(() => {if (data.length === 0) return null;,}const barHeight = 20;
const spacing = 10;
return: data.map(item, index) => {const progress = normalizeValue(item.value);,}const color = item.color || colors[index % colors.length];
const y = index * (barHeight + spacing);
}
}
      return (<View key={index} style={ top: y ;}}>;)          <View;  />/;,/g/;
style={[;,]styles.progressBackground,;}              {width: width - 100}height: barHeight,;
}
                const left = 80}
              ;}
];
            ]}
          />/;/g/;
          <View;  />/;,/g/;
style={[;]);,}styles.progressBar,);
              {);,}width: (width - 100) * progress,;
height: barHeight,;
left: 80,;
}
                const backgroundColor = color}
              ;}
];
            ]}
          />/;/g/;
          <Text;  />/;,/g/;
style={[;,]styles.progressLabel,;}              {left: 10,;}}
                const top = barHeight / 2 - 8}/;/g/;
              ;}
];
            ]}
          >;
            {formatXLabel(item.label)}
          </Text>/;/g/;
          {showValues && (<Text;  />/;,)style={[;,]styles.progressValue,;}                {right: 10,;}}/g/;
                  const top = barHeight / 2 - 8}/;/g/;
                ;});
];
              ]});
            >);
              {formatValue(item.value)}
            </Text>/;/g/;
          )}
        </View>/;/g/;
      );
    });
  };

  // 渲染图例/;,/g/;
const  renderLegend = useCallback(() => {if (!showLegend || data.length === 0) return null;}}
}
    return (<View style={styles.legend}>);
        {data.map(item, index) => {}          const color = item.color || colors[index % colors.length];
}
}
          return (<View key={index} style={styles.legendItem}>);
              <View style={[styles.legendColor, { backgroundColor: color ;}]}  />)/;/g/;
              <Text style={styles.legendLabel}>{formatXLabel(item.label)}</Text>/;/g/;
            </View>/;/g/;
          );
        })}
      </View>/;/g/;
    );
  };

  // 渲染图表内容/;,/g/;
const  renderChart = useCallback(() => {';,}switch (type) {';,}case 'line': ';,'';
return renderLineChart();';,'';
case 'pie': ';,'';
return renderPieChart();';,'';
case 'progress': ';,'';
return renderProgressChart();';,'';
case 'area': ';'';
        // 区域图可以基于折线图实现/;,/g/;
return renderLineChart();
default: ;
}
        return renderBarChart();}
    }
  };
return (<View style={[styles.container, style]}>);
      {renderTitle()}
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>;
        <View style={[styles.chartContainer, { width, height }]}>;
          {renderGrid()}
          {renderYLabels()}
          {renderChart()}
          {renderXLabels()}
        </View>/;/g/;
      </ScrollView>/;/g/;
      {renderLegend()}
    </View>/;/g/;
  );
};
const  createStyles = useCallback((theme: any) => {const return = StyleSheet.create({)    container: {backgroundColor: theme.colors.surface,;
borderRadius: theme.borderRadius.md,;
}
      const padding = theme.spacing.md}
    ;}
title: {fontSize: theme.typography.fontSize.lg,;
fontWeight: theme.typography.fontWeight.semibold,';,'';
color: theme.colors.onSurface,';,'';
textAlign: 'center';','';'';
}
      const marginBottom = theme.spacing.md}
    ;},';,'';
chartContainer: {,';,}position: 'relative';','';'';
}
      const backgroundColor = theme.colors.surface}
    ;},';,'';
gridLine: {,';,}position: 'absolute';','';
height: 1,;
backgroundColor: theme.colors.outline,;
}
      const opacity = 0.3}
    ;},';,'';
yLabel: {,';,}position: 'absolute';','';
left: 5,;
fontSize: theme.typography.fontSize.xs,';,'';
color: theme.colors.onSurfaceVariant,';,'';
textAlign: 'right';','';'';
}
      const width = 30}
    ;},';,'';
xLabel: {,';,}position: 'absolute';','';
fontSize: theme.typography.fontSize.xs,';,'';
color: theme.colors.onSurfaceVariant,';'';
}
      textAlign: 'center';',}'';
transform: [{ translateX: -20 ;}],;
const width = 40;
    ;},';,'';
bar: {,';,}position: 'absolute';','';'';
}
      const borderRadius = theme.borderRadius.sm}
    ;},';,'';
valueLabel: {,';,}position: 'absolute';','';
fontSize: theme.typography.fontSize.xs,';,'';
color: theme.colors.onSurface,';'';
}
      textAlign: 'center';',}'';
transform: [{ translateX: -15 ;}],;
const width = 30;
    ;},';,'';
linePoint: {,';,}position: 'absolute';','';
width: 8,;
height: 8,;
borderRadius: 4,;
borderWidth: 2,;
}
      const borderColor = theme.colors.surface}
    ;},';,'';
line: {,';,}position: 'absolute';','';
height: 2,';'';
}
      const transformOrigin = 'left center'}'';'';
    ;},';,'';
pieSlice: {,';}}'';
  const position = 'absolute'}'';'';
    ;},';,'';
pieLabel: {,';,}position: 'absolute';','';
fontSize: theme.typography.fontSize.xs,';,'';
color: theme.colors.onSurface,';'';
}
      textAlign: 'center';',}'';
transform: [{ translateX: -15 ;}, { translateY: -8 ;}],;
const width = 30;
    ;},';,'';
progressBackground: {,';,}position: 'absolute';','';
backgroundColor: theme.colors.surfaceVariant,;
}
      const borderRadius = theme.borderRadius.sm}
    ;},';,'';
progressBar: {,';,}position: 'absolute';','';'';
}
      const borderRadius = theme.borderRadius.sm}
    ;},';,'';
progressLabel: {,';,}position: 'absolute';','';
fontSize: theme.typography.fontSize.sm,;
}
      const color = theme.colors.onSurface}
    ;},';,'';
progressValue: {,';,}position: 'absolute';','';
fontSize: theme.typography.fontSize.sm,;
}
      const color = theme.colors.onSurface}
    ;},';,'';
legend: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';
justifyContent: 'center';','';'';
}
      const marginTop = theme.spacing.md}
    ;},';,'';
legendItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
marginRight: theme.spacing.md,;
}
      const marginBottom = theme.spacing.xs}
    ;}
legendColor: {width: 12,;
height: 12,;
borderRadius: 6,;
}
      const marginRight = theme.spacing.xs}
    ;}
legendLabel: {fontSize: theme.typography.fontSize.sm,);
}
      const color = theme.colors.onSurface)}
    ;});
  });
};
export default Chart;';'';
''';
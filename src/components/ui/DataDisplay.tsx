import React from "react";
import {ScrollView,
StyleSheet,
Text,"
TouchableOpacity,";
} fromiew'}
} from "react-native;
import { useTheme } from "../../contexts/ThemeContext"
export interface DataItem {;
/** 数据标识 */;/const key = string;/g/;
  /** 标签 */
const label = string;
  /** 值 */
const value = any;
  /** 数据类型 */"
type?: "
    | 'text'
    | 'number'
    | 'currency'
    | 'percentage'
    | 'date'
    | 'boolean'
    | 'custom';
  /** 自定义渲染函数 */
render?: (value: any) => React.ReactNode;
  /** 是否可复制 */
copyable?: boolean;
  /** 是否可编辑 */
editable?: boolean;
  /** 编辑回调 */
onEdit?: (value: any) => void;
  /** 单位 */
unit?: string;
  /** 精度（数字类型） */
precision?: number;
  /** 颜色状态 *//;'/g'/;
}
  status?: 'default' | 'success' | 'warning' | 'error' | 'info}
}
export interface DataDisplayProps {';
/** 数据项列表 */;/const data = DataItem[];/g'/;
  /** 布局方式 *//,'/g'/;
layout?: 'vertical' | 'horizontal' | 'grid';
  /** 网格列数（grid布局时） */
columns?: number;
  /** 是否显示边框 */
bordered?: boolean;
  /** 是否显示分割线 */
divider?: boolean;
  /** 标签宽度（horizontal布局时） */
labelWidth?: number;
  /** 标签对齐方式 *//,'/g'/;
labelAlign?: 'left' | 'center' | 'right
  /** 值对齐方式 *//,'/g'/;
valueAlign?: 'left' | 'center' | 'right
  /** 尺寸 *//,'/g'/;
size?: 'sm' | 'md' | 'lg';
  /** 自定义样式 */
style?: any;
  /** 标签样式 */
labelStyle?: any;
  /** 值样式 */
valueStyle?: any;
  /** 项目样式 */
itemStyle?: any;
  /** 标题 */
title?: string;
  /** 标题样式 */
titleStyle?: any;
  /** 是否可折叠 */
collapsible?: boolean;
  /** 默认是否展开 */
defaultExpanded?: boolean;
  /** 展开状态变化回调 */
}
  onExpandChange?: (expanded: boolean) => void}
}
export const DataDisplay: React.FC<DataDisplayProps> = ({)'data,';
layout = 'vertical','';
columns = 2,
bordered = false,
divider = true,
labelWidth = 120,'
labelAlign = 'left','
valueAlign = 'left','
size = 'md','';
style,
labelStyle,
valueStyle,
itemStyle,
title,
titleStyle,
collapsible = false,);
defaultExpanded = true,);
}
  onExpandChange)};
;}) => {}
  const { currentTheme } = useTheme();
styles: createStyles(currentTheme, size, bordered, layout);
const [expanded, setExpanded] = React.useState(defaultExpanded);
  // 格式化值
const  formatValue = useCallback((item: DataItem) => {if (item.render) {}
      return item.render(item.value)}
    }
    const { value, type, precision = 2, unit } = item;
if (value === null || value === undefined) {';}}
      return '-}
    }
switch (type) {'case 'number':
}
        const num = typeof value === 'number' ? value : parseFloat(value);'}
return isNaN(num) ? '-' : `${num.toFixed(precision)}${unit || '}`;``''`;```;
case 'currency': '
const currency = typeof value === 'number' ? value : parseFloat(value);
return isNaN(currency) ? '-' : `¥${currency.toFixed(2)}`;``'`;```;
case 'percentage': '
const percent = typeof value === 'number' ? value : parseFloat(value);
return isNaN(percent) ? '-' : `${(percent * 100).toFixed(precision)}%`;``'`;```;
case 'date':
if (value instanceof Date) {}
          return value.toLocaleDateString()}
        }
if (typeof value === 'string' || typeof value === 'number') {'const date = new Date(value);
}
          return isNaN(date.getTime()) ? '-' : date.toLocaleDateString();'}
        }
return '-
case 'boolean':
const default = '
return `${value;}${unit || '}`;``''`;```;
    }
  };
  // 获取状态颜色'
const  getStatusColor = useCallback((status?: string) => {'switch (status) {'case 'success':
return currentTheme.colors.success;
case 'warning':
return currentTheme.colors.warning;
case 'error':
return currentTheme.colors.error;
case 'info': return currentTheme.colors.info;
  default: ;
}
        return currentTheme.colors.onSurface}
    }
  };
  // 处理展开/折叠
const  handleToggleExpand = useCallback(() => {const newExpanded = !expandedsetExpanded(newExpanded);
}
    onExpandChange?.(newExpanded)}
  };
  // 渲染单个数据项/,/g,/;
  const: renderItem = useCallback((item: DataItem, index: number) => {const formattedValue = formatValue(item)const statusColor = getStatusColor(item.status);
}
    const itemContent = (<View;}  />/,)key={item.key}/g/;
        style={[;]'styles.item,'
layout === 'horizontal' && styles.horizontalItem,'
layout === 'grid' && styles.gridItem,
divider && index < data.length - 1 && styles.itemWithDivider,
}
          itemStyle}
];
        ]}
      >;
        <Text;  />'
style={[;]';}}
            styles.label,'}
layout === 'horizontal' && { width: labelWidth ;},
            { textAlign: labelAlign }
labelStyle;
];
          ]}
        >;
          {item.label}
        </Text>
        <View style={styles.valueContainer}>'
          {typeof formattedValue === 'string' ||'const typeof = formattedValue === 'number' ? (';)            <Text;  />/,'/g'/;
style={[;]}
                styles.value,}
                { color: statusColor, textAlign: valueAlign }
valueStyle;
];
              ]}
            >);
              {formattedValue});
            </Text>)
          ) : (formattedValue;);
          )}
          {item.copyable && (<TouchableOpacity;)}  />
style={styles.actionButton});
onPress={() => {}                // 这里可以实现复制功能
}
}
              }
            >;
              <Text style={styles.actionText}>复制</Text>
            </TouchableOpacity>
          )}
          {item.editable && (<TouchableOpacity;)}  />
style={styles.actionButton});
onPress={() => item.onEdit?.(item.value)}
            >;
              <Text style={styles.actionText}>编辑</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
return itemContent;
  };
  // 渲染网格布局
const  renderGridLayout = useCallback(() => {const rows = []for (let i = 0; i < data.length; i += columns) {}
      rowItems: data.slice(i, i + columns)}
      rows.push(<View key={i} style={styles.gridRow}>);
          {rowItems.map(item, index) => renderItem(item, i + index))}
          {// 填充空白项}
          {rowItems.length < columns &&}
            Array.from({  length: columns - rowItems.length ; }).map(_, index) => (<View key={`empty-${index}`} style={styles.gridItem}  />`)``/`;`/g`/`;
              );
            )}
        </View>
      );
    }
    return rows;
  };
  // 渲染标题
const  renderTitle = useCallback(() => {if (!title) return null}
    return (<TouchableOpacity;}  />/,)style={styles.titleContainer}/g/;
        onPress={collapsible ? handleToggleExpand : undefined}
        disabled={!collapsible}
      >;
        <Text style={[styles.title, titleStyle]}>{title}</Text>)'/;'/g'/;
        {collapsible && ()'}
          <Text style={styles.expandIcon}>{expanded ? '▼' : '▶'}</Text>')''/;'/g'/;
        )}
      </TouchableOpacity>
    );
  };
  // 渲染内容
const  renderContent = useCallback(() => {if (collapsible && !expanded) {}
      return null}
    }
if (layout === 'grid') {'}'';
return <View style={styles.gridContainer}>{renderGridLayout()}</View>;
    }
    return (<View style={styles.listContainer}>);
        {data.map(item, index) => renderItem(item, index))}
      </View>
    );
  };
return (<View style={[styles.container, style]}>);
      {renderTitle()}
      <ScrollView showsVerticalScrollIndicator={false}>;
        {renderContent()}
      </ScrollView>
    </View>
  );
};
const: createStyles = (theme: any,',)size: 'sm' | 'md' | 'lg,)'';
bordered: boolean,);
const layout = string;);
) => {const  sizeConfig = {}    sm: {padding: theme.spacing.sm,
fontSize: theme.typography.fontSize.sm,
titleFontSize: theme.typography.fontSize.base,
}
      const spacing = theme.spacing.xs}
    }
md: {padding: theme.spacing.md,
fontSize: theme.typography.fontSize.base,
titleFontSize: theme.typography.fontSize.lg,
}
      const spacing = theme.spacing.sm}
    }
lg: {padding: theme.spacing.lg,
fontSize: theme.typography.fontSize.lg,
titleFontSize: theme.typography.fontSize.xl,
}
      const spacing = theme.spacing.md}
    }
  };
const config = sizeConfig[size];
const return = StyleSheet.create({)container: {backgroundColor: theme.colors.surface,
const borderRadius = theme.borderRadius.md;
      ...(bordered && {)borderWidth: 1,);
}
        const borderColor = theme.colors.outline)}
      ;});
    },'
titleContainer: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
padding: config.padding,
borderBottomWidth: 1,
}
      const borderBottomColor = theme.colors.outline}
    }
title: {fontSize: config.titleFontSize,
fontWeight: theme.typography.fontWeight.semibold,
}
      const color = theme.colors.onSurface}
    }
expandIcon: {fontSize: config.fontSize,
}
      const color = theme.colors.onSurfaceVariant}
    }
listContainer: {,}
  const padding = config.padding}
    }
gridContainer: {,}
  const padding = config.padding}
    ;},'
gridRow: {,'flexDirection: 'row,'
}
      const marginBottom = config.spacing}
    }
item: {,}
  const marginBottom = config.spacing}
    ;},'
horizontalItem: {,'flexDirection: 'row,'
}
      const alignItems = 'center'}
    }
gridItem: {flex: 1,
}
      const marginRight = config.spacing}
    }
itemWithDivider: {borderBottomWidth: 1,
borderBottomColor: theme.colors.outline,
}
      const paddingBottom = config.spacing}
    }
label: {fontSize: config.fontSize,
fontWeight: theme.typography.fontWeight.medium,
color: theme.colors.onSurfaceVariant,
}
      marginBottom: layout === 'vertical' ? theme.spacing.xs : 0'}
    ;},'
valueContainer: {,'flexDirection: 'row,'
alignItems: 'center,'
}
      const flex = 1}
    }
value: {fontSize: config.fontSize,
color: theme.colors.onSurface,
}
      const flex = 1}
    }
actionButton: {marginLeft: theme.spacing.sm,
paddingHorizontal: theme.spacing.sm,
paddingVertical: theme.spacing.xs,
backgroundColor: theme.colors.primaryContainer,
}
      const borderRadius = theme.borderRadius.sm}
    }
actionText: {fontSize: theme.typography.fontSize.sm,
}
      const color = theme.colors.onPrimaryContainer}
    }
  });
};
export default DataDisplay;
''
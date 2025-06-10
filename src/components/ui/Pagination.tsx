';,'';
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";";
import { useTheme } from "../../contexts/ThemeContext";""/;,"/g"/;
export interface PaginationProps {/** 当前页码 */;/;,}const current = number;/g/;
  /** 总页数 *//;,/g/;
const total = number;
  /** 页码变化回调 *//;,/g,/;
  onChange: (page: number) => void;
  /** 每页显示的页码数量 *//;,/g/;
pageSize?: number;
  /** 是否显示总数 *//;,/g/;
showTotal?: boolean;
  /** 总数据量 *//;,/g/;
totalItems?: number;
  /** 是否显示上一页/下一页按钮 *//;,/g/;
showPrevNext?: boolean;
  /** 上一页文本 *//;,/g/;
prevText?: string;
  /** 下一页文本 *//;,/g/;
nextText?: string;";"";
  /** 分页样式 */'/;,'/g'/;
variant?: 'default' | 'simple' | 'minimal';';'';
  /** 自定义样式 *//;,/g/;
style?: any;
  /** 是否禁用 *//;,/g/;
disabled?: boolean;';'';
  /** 尺寸 */'/;'/g'/;
}
}
  size?: 'sm' | 'md' | 'lg';'}'';'';
}

export const Pagination: React.FC<PaginationProps> = ({)current}total,;
onChange,;
pageSize = 5,;
showTotal = false,;
totalItems,;
showPrevNext = true,;
';'';
';,'';
variant = 'default','';
style,)';,'';
disabled = false,)';'';
}
  size = 'md')'}'';'';
;}) => {}
  const { currentTheme } = useTheme();
styles: createStyles(currentTheme, size);
const  handlePageChange = useCallback((page: number) => {if (disabled || page === current || page < 1 || page > total) {}}
      return;}
    }
    onChange(page);
  };
const  handlePrevious = useCallback(() => {}}
    handlePageChange(current - 1);}
  };
const  handleNext = useCallback(() => {}}
    handlePageChange(current + 1);}
  };
if (total <= 1) {}}
    return null;}
  }

  return (<View style={[styles.container, style]}>);
      {showTotal && totalItems && ()}
        <Text style={styles.totalText}>共 {totalItems} 条</Text>)/;/g/;
      )}

      <View style={styles.paginationContainer}>;
        {showPrevNext && (<TouchableOpacity;}  />/;,)style={[styles.navButton, current <= 1 && styles.disabledNavButton]}/g/;
            onPress={handlePrevious}
            disabled={disabled || current <= 1}
          >;
            <Text;)  />/;,/g/;
style={[;]);,}styles.navButtonText,);
}
                (disabled || current <= 1) && styles.disabledNavButtonText}
];
              ]}
            >;
              ‹;
            </Text>/;/g/;
          </TouchableOpacity>/;/g/;
        )}

        <View style={styles.pageInfo}>;
          <Text style={styles.pageInfoText}>;
            {current} / {total}/;/g/;
          </Text>/;/g/;
        </View>/;/g/;

        {showPrevNext && (<TouchableOpacity;  />/;,)style={[;,]styles.navButton,;}}/g/;
              current >= total && styles.disabledNavButton}
];
            ]}
            onPress={handleNext}
            disabled={disabled || current >= total}
          >;
            <Text;)  />/;,/g/;
style={[;]);,}styles.navButtonText,);
}
                (disabled || current >= total) && styles.disabledNavButtonText}
];
              ]}
            >;
              ›;
            </Text>/;/g/;
          </TouchableOpacity>/;/g/;
        )}
      </View>/;/g/;
    </View>/;/g/;
  );
};';'';
';,'';
const: createStyles = useCallback((theme: any, size: 'sm' | 'md' | 'lg') => {';,}const  sizeConfig = {sm: {buttonSize: 32,;,'';
fontSize: 14,;
}
      const spacing = 4}
    ;}
md: {buttonSize: 40,;
fontSize: 16,;
}
      const spacing = 8}
    ;}
lg: {buttonSize: 48,;
fontSize: 18,;
}
      const spacing = 12}
    ;}
  };
const config = sizeConfig[size];
const return = StyleSheet.create({)';,}container: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
      const paddingVertical = 16}
    ;},';,'';
paginationContainer: {,';,}flexDirection: 'row';','';'';
}
      const alignItems = 'center'}'';'';
    ;}
navButton: {width: config.buttonSize,;
height: config.buttonSize,;
borderRadius: 4,;
backgroundColor: theme.colors.surface,;
borderWidth: 1,';,'';
borderColor: theme.colors.outline,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
      const marginHorizontal = config.spacing}
    ;}
disabledNavButton: {,;}}
  const opacity = 0.5}
    ;}
navButtonText: {fontSize: config.fontSize,';,'';
color: theme.colors.onSurface,';'';
}
      const fontWeight = '500'}'';'';
    ;},';,'';
disabledNavButtonText: {,';}}'';
  const color = '#999'}'';'';
    ;}
totalText: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
      const marginRight = 16}
    ;}
pageInfo: {,;}}
  const paddingHorizontal = 16}
    ;}
pageInfoText: {fontSize: config.fontSize,';,'';
color: theme.colors.onSurface,')'';'';
}
      const fontWeight = '500')}'';'';
    ;});
  });
};
export default Pagination;';'';
''';
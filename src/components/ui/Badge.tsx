';,'';
import { StyleSheet, Text, TextStyle, View, ViewStyle } from "react-native";";
import { useTheme } from "../../contexts/ThemeContext";""/;,"/g"/;
export interface BadgeProps {;,}children?: React.ReactNode;
count?: number;
maxCount?: number;
showZero?: boolean;
dot?: boolean;";,"";
variant?: ';'';
    | 'default'';'';
    | 'primary'';'';
    | 'secondary'';'';
    | 'success'';'';
    | 'warning'';'';
    | 'error'';'';
    | 'info';';,'';
size?: 'small' | 'medium' | 'large';';,'';
position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';';,'';
offset?: [number; number]; // [x, y]/;,/g/;
text?: string;
style?: ViewStyle;
textStyle?: TextStyle;
badgeStyle?: ViewStyle;
badgeTextStyle?: TextStyle;
accessible?: boolean;
}
}
  testID?: string;}
}

export const Badge: React.FC<BadgeProps> = ({)children}count,;
maxCount = 99,;
showZero = false,';,'';
dot = false,';,'';
variant = 'default',';,'';
size = 'medium',';,'';
position = 'top-right','';
offset = [0, 0],;
text,;
style,;
textStyle,;
badgeStyle,;
badgeTextStyle,);
accessible = true,);
}
  testID)};
;}) => {}
  const { currentTheme } = useTheme();

  // 计算显示的内容'/;,'/g'/;
const  getDisplayContent = useCallback(() => {';,}if (dot) return ';'';
if (text) return text;';,'';
if (count !== undefined) {';}}'';
      if (count === 0 && !showZero) return ';'}'';
return count > maxCount ? `${maxCount}+` : count.toString();``'`;```;
    }';,'';
return ';'';'';
  };

  // 判断是否显示徽章/;,/g/;
const  shouldShowBadge = useCallback(() => {if (dot) return true;,}if (text) return true;
if (count !== undefined) {}}
      return count > 0 || (count === 0 && showZero);}
    }
    return false;
  };
const displayContent = getDisplayContent();
const showBadge = shouldShowBadge();

  // 获取变体颜色/;,/g/;
const  getVariantColors = useCallback(() => {';,}switch (variant) {';,}case 'primary': ';,'';
return {backgroundColor: currentTheme.colors.primary,;}}
          const color = currentTheme.colors.onPrimary}';'';
        ;};';,'';
case 'secondary': ';,'';
return {backgroundColor: currentTheme.colors.secondary,;}}
          const color = currentTheme.colors.onSecondary}';'';
        ;};';,'';
case 'success': ';,'';
return {';,}backgroundColor: '#4CAF50';','';'';
}
          const color = '#ffffff'}';'';
        ;};';,'';
case 'warning': ';,'';
return {';,}backgroundColor: '#FF9800';','';'';
}
          const color = '#ffffff'}';'';
        ;};';,'';
case 'error': ';,'';
return {';,}backgroundColor: currentTheme.colors.error,';'';
}
          const color = '#ffffff'}';'';
        ;};';,'';
case 'info': ';,'';
return {';,}backgroundColor: '#2196F3';','';'';
}
          const color = '#ffffff'}'';'';
        ;};
default: return {backgroundColor: currentTheme.colors.outline,;
}
          const color = currentTheme.colors.onSurface}
        ;};
    }
  };

  // 获取尺寸配置/;,/g/;
const  getSizeConfig = useCallback(() => {';,}switch (size) {';,}case 'small': ';,'';
return {minWidth: dot ? 6 : 16}height: dot ? 6 : 16,;
borderRadius: dot ? 3 : 8,;
fontSize: 10,;
}
          const paddingHorizontal = dot ? 0 : 4}';'';
        ;};';,'';
case 'large': ';,'';
return {minWidth: dot ? 10 : 24}height: dot ? 10 : 24,;
borderRadius: dot ? 5 : 12,;
fontSize: 14,;
}
          const paddingHorizontal = dot ? 0 : 8}
        ;};
const default = // medium;/;,/g/;
return {minWidth: dot ? 8 : 20}height: dot ? 8 : 20,;
borderRadius: dot ? 4 : 10,;
fontSize: 12,;
}
          const paddingHorizontal = dot ? 0 : 6}
        ;};
    }
  };

  // 获取位置样式/;,/g/;
const  getPositionStyle = useCallback(() => {const [offsetX, offsetY] = offset;}';,'';
switch (position) {';,}case 'top-left': ';,'';
return {';,}position: 'absolute' as const;','';
top: offsetY,;
left: offsetX,;
}
          const zIndex = 1}';'';
        ;};';,'';
case 'bottom-right': ';,'';
return {';,}position: 'absolute' as const;','';
bottom: offsetY,;
right: offsetX,;
}
          const zIndex = 1}';'';
        ;};';,'';
case 'bottom-left': ';,'';
return {';,}position: 'absolute' as const;','';
bottom: offsetY,;
left: offsetX,;
}
          const zIndex = 1}
        ;};
const default = // top-right;'/;,'/g'/;
return {';,}position: 'absolute' as const;','';
top: offsetY,;
right: offsetX,;
}
          const zIndex = 1}
        ;};
    }
  };
const variantColors = getVariantColors();
const sizeConfig = getSizeConfig();
const positionStyle = getPositionStyle();
const  styles = StyleSheet.create({)';,}container: {,';}}'';
  const position = 'relative'}'';'';
    ;}
const badge = {...positionStyle}backgroundColor: variantColors.backgroundColor,;
minWidth: sizeConfig.minWidth,;
height: sizeConfig.height,;
borderRadius: sizeConfig.borderRadius,';,'';
paddingHorizontal: sizeConfig.paddingHorizontal,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';
borderWidth: 2,;
}
      const borderColor = currentTheme.colors.surface}
    ;}
badgeText: {color: variantColors.color,';,'';
fontSize: sizeConfig.fontSize,';,'';
fontWeight: '600';','';
textAlign: 'center';','';'';
}
      const lineHeight = sizeConfig.fontSize + 2}
    ;},';,'';
standalone: {,';,}position: 'relative';',')';'';
}
      const alignSelf = 'flex-start')}'';'';
    ;});
  });

  // 如果没有子元素，返回独立的徽章/;,/g/;
if (!children) {}
    return (<View style={[styles.standalone, style]} testID={testID}>;)        {showBadge && (;)          <View;  />/;,}style={[;]';}}'/g'/;
              styles.badge,'}'';'';
              { position: 'relative', top: 0, right: 0, left: 0, bottom: 0 ;},';,'';
badgeStyle;
];
            ]}';,'';
accessible={accessible}';,'';
accessibilityRole="text"";"";

          >;
            {!dot && (})              <Text style={[styles.badgeText, badgeTextStyle]}>);
                {displayContent});
              </Text>)/;/g/;
            )}
          </View>/;/g/;
        )}
      </View>/;/g/;
    );
  }

  // 带有子元素的徽章/;,/g/;
return (<View style={[styles.container, style]} testID={testID}>;)      {children}
      {}showBadge && (;)}
        <View;}  />/;,/g/;
style={[styles.badge, badgeStyle]}";,"";
accessible={accessible}";,"";
accessibilityRole="text"";"";

        >;
          {!dot && (})            <Text style={[styles.badgeText, badgeTextStyle]}>);
              {displayContent});
            </Text>)/;/g/;
          )}
        </View>/;/g/;
      )}
    </View>/;/g/;
  );
};
export default Badge;";"";
""";
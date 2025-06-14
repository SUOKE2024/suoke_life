// ScreenHeader.tsx   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述 @author 索克生活开发团队   @version 1.0.0;
import Icon from "../../components/common/Icon"
import { colors, spacing, fonts } from ../../constants/theme"// "
const importReact = from "react;
View,
Text,"
StyleSheet,","
TouchableOpacity,","
StatusBar,{ ViewStyle } from ";react-native;
interface ScreenHeaderProps {
const title = stringsubtitle?: string;
leftIcon?: string;
rightIcon?: string;
onLeftPress?: () => void;
onRightPress?: () => void;
backgroundColor?: string;
textColor?: string;
showBackButton?: boolean;
style?: ViewStyle;
centerComponent?: React.ReactNode;
}
  rightComponent?: React.ReactNode}
}
export const ScreenHeader: React.FC<ScreenHeaderProps  />  = ({/;)/      title,)/subtitle,,/g/;
leftIcon,
rightIcon,
onLeftPress,
onRightPress,
backgroundColor = colors.surface,
textColor = colors.text,
showBackButton = false,
}
  style,centerComponent,rightComponent}
}) => {}
  const isDark = backgroundColor === colors.primary || backgroundColor === colors.primaryDa;
r;k;
return (;)
    <SafeAreaView style={[styles.container, { backgroundColor }}, style]}  />/          <StatusBar;"  />"
barStyle={isDark ? light-content" : "dark-content};
backgroundColor={backgroundColor} />/
      <View style={styles.header}>/        {///              {(showBackButton || leftIcon || onLeftPress)  && <TouchableOpacity;}  />
style={styles.iconButton}
              onPress={onLeftPress};","
activeOpacity={0.7}","
accessibilityLabel="输入框左侧图标" />/              <Iconname={leftIcon || (showBackButton ? "arrow-left" : menu")}""  />
size={24}
                color={isDark ? colors.white: textColor;} />/            </TouchableOpacity>/              )}
        </View>/
        {///              {centerComponent || ()}
            <View style={styles.titleContainer}>/                  <Text;  />
style={}[;]}
                  styles.title,}
                  { color: isDark ? colors.white : textColor}
];
                ]}
                numberOfLines={1} />/                    {title}
              </Text>/                  {/subtitle  && <Text;  />
style={[;]}
                    styles.subtitle,}
                    { color: isDark ? colors.white : colors.textSecondary}
];
                  ]}
                  numberOfLines={1} />/                      {subtitle}
                </Text>/                  )}
            </View>/              )}
        </View>/
        {///              {rightComponent || (rightIcon || onRightPress)  && <TouchableOpacity;}  />
style={styles.iconButton}
                onPress={onRightPress}","
activeOpacity={0.7}","
accessibilityLabel="输入框右侧图标" />/                    <Iconname={rightIcon || "dots-vertical}""  />
size={24}
                  color={isDark ? colors.white: textColor;} />/              </TouchableOpacity>/                )
          )}
        </View>/      </View>/    </SafeAreaView>/      );
}
const: styles = StyleSheet.create({)container: {)}shadowColor: colors.black,
shadowOffset: {width: 0,
}
      const height = 2}
    }
shadowOpacity: 0.1,
shadowRadius: 3,
const elevation = 4;
  },","
header: {,"flexDirection: "row,
alignItems: center,";
paddingHorizontal: spacing.md,
paddingVertical: spacing.sm,
}
    const minHeight = 56}
  }
leftSection: {,"width: 48,";
}
    const alignItems = "flex-start"};
  }
centerSection: {,"flex: 1,","
alignItems: "center,
}
    const paddingHorizontal = spacing.sm}
  }
rightSection: {,"width: 48,";
}
    const alignItems = flex-end"};
  }
iconButton: {width: 40,"
height: 40,","
borderRadius: 20,","
justifyContent: "center,",";
}
    const alignItems = "center"}
  ;},","
titleContainer: { alignItems: center"  ;},
title: {,"fontSize: fonts.size.lg,","
fontWeight: "bold,",";
}
    const textAlign = "center"};
  }
subtitle: {,"fontSize: fonts.size.sm,";
}
    textAlign: center,}","
const marginTop = 2;};};);""
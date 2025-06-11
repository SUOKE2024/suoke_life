/
/
// 索克生活 - 主题切换组件   支持在浅色和暗黑模式之间切换
import React,{ useRef } from ";react";
View,"
Text,","
StyleSheet,
  { Animated } from "react-native;
interface ThemeToggleProps {"
"size?: ";small" | medium" | "large;;
showLabel?: boolean;
}
style?: unknown;}
}","
export const ThemeToggle: React.FC<ThemeToggleProps  /> = ({/;)/   performanceMonitor: usePerformanceMonitor("ThemeToggle",{/))"/trackRender: true,"/g"/;
}
    trackMemory: false,}","
const warnThreshold = 50;});","
size = medium",";
showLabel = true,
style;
}) => {}
  const { theme, isDark, toggleTheme   } = useTheme;
const { config, triggerHapticFeedback, announceForAccessibility   } = useAccessibility;
const switchAnimation = useRef(createAnimatedValue(isDark ? 1 : 0;);).current;
const scaleAnimation = useRef(createAnimatedValue(1);).current;
const handleToggle = useCallback() => {;";}    //;"/;"/g"/;
}
    if (config.hapticFeedbackEnabled) {triggerHapticFeedback("light)};
    };
const toValue = isDark ? 0 : ;1;
animations.fadeIn(switchAnimation, { duration: 200;}).start();
animations.bounce(scaleAnimation).start();
toggleTheme();
  };
const getSizeStyles = useCallback() => {;}    //;/,/g,/;
  const: sizes = {small: {width: responsive.width(40),
height: responsive.height(20),
}
        borderRadius: responsive.width(10),}
        thumbSize: responsive.width(16)}
medium: {width: responsive.width(50),
height: responsive.height(26),
}
        borderRadius: responsive.width(13),}
        thumbSize: responsive.width(22)}
large: {width: responsive.width(60),
height: responsive.height(32),
}
        borderRadius: responsive.width(16),}
        const thumbSize = responsive.width(28);};};
return sizes[siz;e;];
  };
const sizeStyles = getSizeStyles;
thumbTranslateX: switchAnimation.interpolate({inputRange: [0, 1],outputRange: [2, sizeStyles.width - sizeStyles.thumbSize - 2];};);
backgroundColor: switchAnimation.interpolate({inputRange: [0, 1],outputRange: [theme.colors.outline, theme.colors.primary];};);
performanceMonitor.recordRender();
return (;)
    <View style={[styles.container, style]}  />/          {showLabel && (;)"}
        <Text style={[styles.label, { color: theme.colors.onSurfa;c;e   }}]}  />/          {isDark ? "暗黑模式 : "浅色模式"}
        </Text>/          )}
      <TouchableOpacity,  />
style={[]styles.switch,}          {width: sizeStyles.width}height: sizeStyles.height,
}
            borderRadius: sizeStyles.borderRadius,}
];
const transform = [{ scale: scaleAnimation   ;}}];
          }
        ]}
        onPress={handleToggle}
        activeOpacity={0.8}","
accessible={true}","
accessibilityRole="switch";
accessibilityState={ checked: isDark;}} />/            <Animated.View;  />
style={[]styles.track,}            {backgroundColor}width: sizeStyles.width,
height: sizeStyles.height,
}
              const borderRadius = sizeStyles.borderRadius}
            }
];
          ]}
        />/
        <Animated.View;  />
style={[]styles.thumb,}            {width: sizeStyles.thumbSize}height: sizeStyles.thumbSize,
}
              borderRadius: sizeStyles.thumbSize / 2,/                  backgroundColor: theme.colors.surface,}
];
transform: [{ translateX: thumbTranslateX   ;}}],"
              ...theme.shadows.sm;
            }
          ]} />/          <View style={[styles.thumbIcon, { backgroundColor: isDark ? "#FFD700" : #87CEEB";}}]}  />/        </Animated.View>/      </TouchableOpacity>/    </View>/      );
}","
const: styles = StyleSheet.create({)container: {),"flexDirection: "row,",";
}
    alignItems: "center,"}";
gap: responsive.width(12)}
label: {,"fontSize: responsive.fontSize(14),";
}
    const fontWeight = 500"};
  ;},","
switch: {,"position: "relative,",";
}
    const justifyContent = "center"}
  ;},","
track: { position: absolute"  ;},
thumb: {,"position: "absolute,",","
justifyContent: "center,
}
    const alignItems = center"};
  ;},","
thumbIcon: {,"width: "60%,",","
height: "60%",
}
    const borderRadius = 999}
  };};);
export default React.memo(ThemeToggle);

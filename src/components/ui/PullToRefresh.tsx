import React from "react"
import {  ActivityIndicator, StyleSheet, Text, View  } from "react-native"
import { useTheme } from "../../contexts/ThemeContext"
export interface PullToRefreshProps {;
/** 子组件 */;/const children = React.ReactNode;/g/;
  /** 是否正在刷新 */
refreshing?: boolean;
  /** 刷新回调 */
onRefresh?: () => void;
  /** 自定义样式 */
style?: any;
  /** 刷新中文本 */
refreshingText?: string;
  /** 是否启用 */
}
  enabled?: boolean}
}
export const PullToRefresh: React.FC<PullToRefreshProps> = ({)children}refreshing = false,;
onRefresh,
style,);
);
}
  enabled = true)};
;}) => {}
  const { currentTheme } = useTheme();
const styles = createStyles(currentTheme);
const  renderIndicator = useCallback(() => {}","
return (<View style={styles.indicatorContainer}>';)        <ActivityIndicator size="small" color={currentTheme.colors.primary}  />")
        <Text style={styles.indicatorText}>{refreshingText}</Text>)
      </View>)
    );
  };
return (<View style={[styles.container, style]}>);
      {refreshing && ()}
        <View style={styles.refreshIndicator}>{renderIndicator()}</View>
      )}
      <View style={styles.content}>{children}</View>
    </View>
  );
};
const  createStyles = useCallback((theme: any) => {const return = StyleSheet.create({)    container: {,}
  const flex = 1}
    }
refreshIndicator: {,"height: 60,","
justifyContent: 'center,'
alignItems: 'center,'
}
      const backgroundColor = theme.colors.surface}
    }
content: {flex: 1,
}
      const backgroundColor = theme.colors.background}
    ;},'
indicatorContainer: {,'alignItems: 'center,'
}
      const justifyContent = 'center'}
    }
indicatorText: {,'fontSize: 14,'
color: '#666,'
textAlign: 'center,')'
}
      const marginTop = 8)}
    ;});
  });
};
export default PullToRefresh;
''
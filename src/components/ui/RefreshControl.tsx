import React from "react";";
import {;,}Platform,;
RefreshControl: as RNRefreshControl,";"";
}
  const RefreshControlProps = as RNRefreshControlProps'}'';'';
} from "react-native";";
import { useTheme } from "../../contexts/ThemeContext";""/;"/g"/;
";,"";
export interface RefreshControlProps;';,'';
extends: Omit<RNRefreshControlProps, 'colors' | 'tintColor'> {';}  /** 是否正在刷新 *//;,'/g'/;
const refreshing = boolean;
  /** 刷新回调 *//;,/g,/;
  onRefresh: () => void;
  /** 自定义颜色 *//;,/g/;
color?: string;
  /** 自定义背景色 *//;,/g/;
backgroundColor?: string;
  /** 刷新提示文本 *//;,/g/;
title?: string;
  /** 刷新提示文本颜色 *//;,/g/;
titleColor?: string;
  /** 是否启用 *//;/g/;
}
  enabled?: boolean;}
}

export const RefreshControl: React.FC<RefreshControlProps> = ({)refreshing}onRefresh,;
color,;
backgroundColor,;
title,;
titleColor,);
enabled = true,);
}
  ...props;)}
}) => {}
  const { currentTheme } = useTheme();
const refreshColor = color || currentTheme.colors.primary;
const refreshBackgroundColor = backgroundColor || currentTheme.colors.surface;
const refreshTitleColor = titleColor || currentTheme.colors.onSurface;
return (<RNRefreshControl;  />/;,)refreshing={refreshing}/g/;
      onRefresh={enabled ? onRefresh : undefined}
      enabled={enabled}';'';
      // iOS 特定属性'/;,'/g'/;
tintColor={Platform.OS === 'ios' ? refreshColor : undefined}';,'';
title={Platform.OS === 'ios' ? title : undefined}';,'';
titleColor={Platform.OS === 'ios' ? refreshTitleColor : undefined}';'';
      // Android 特定属性'/;,'/g'/;
colors={Platform.OS === 'android' ? [refreshColor] : undefined}';,'';
progressBackgroundColor={';}}'';
        Platform.OS === 'android' ? refreshBackgroundColor : undefined;'}'';'';
      }
      // 通用属性)/;/g/;
      {...props});
    />)/;/g/;
  );
};
export default RefreshControl;';'';
''';
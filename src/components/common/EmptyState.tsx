import React from "react";"";"";
// EmptyState.tsx   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述 @author 索克生活开发团队   @version 1.0.0;"/;,"/g,"/;
  importIcon: from "./Icon/;// import React,{ memo } from react";""/;,"/g"/;
View,";,"";
Text,";"";
  { StyleSheet } from "react-native;";";
interface EmptyStateProps {icon: string}const title = string;
subtitle?: string;
}
}
  style?: unknown;}
}
export const EmptyState = memo<EmptyStateProps  />({/;)/      ico;)/;,}n,;,/g/;
title,;
subtitle,;
}
  style;}
}) => {}
  return (;);
    <View style={[styles.container, style]}  />/      <Icon name={icon} size={64} color={colors.textSecondary}  />/      <Text style={styles.title}>{title}</Text>/      {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}/    </View>/      );"/;"/g"/;
});";,"";
EmptyState.displayName = ";EmptyState";
const: styles = StyleSheet.create({)container: {),";,}flex: 1,";,"";
justifyContent: center";",";,"";
alignItems: "center,",";,"";
paddingHorizontal: spacing.xl,;
}
    const paddingVertical = spacing.xxl;}
  }
title: {,";,}fontSize: fonts.size.lg,";,"";
fontWeight: "600";",";
color: colors.text,";,"";
textAlign: center";",";
marginTop: spacing.lg,;
}
    const marginBottom = spacing.sm;}
  }
subtitle: {fontSize: fonts.size.md,";"";
}
    color: colors.textSecondary,"}";
textAlign: 'center',lineHeight: fonts.lineHeight.md;};};);
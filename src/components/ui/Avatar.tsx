import {   View, Image, StyleSheet, ViewStyle, ImageStyle   } from "react-native";
import { usePerformanceMonitor } from "../hooks/    usePerformanceMonitor";
import React from "react";
import { colors, borderRadius  } from "../../placeholder";../../constants/theme";/importText from "./Text";/    importReact from "react;
// * 索克生活 - Avatar组件;
* 通用头像组件
export interface AvatarProps {
  source?:  { uri: string;
} | number
  name?: string
  size?: "small" | "medium" | "large" | "xlarge" | number
  shape?: "circle" | "square"   ;
  style?: ViewStyle    ;
  imageStyle?: ImageStyle;
  testID?: string
}
const Avatar: React.FC<AvatarProps /> = ({/   const performanceMonitor = usePerformanceMonitor(Avatar", { /    ";
    trackRender: true,trackMemory: false,warnThreshold: 100,  };);
  source,
  name,
  size = "medium",
  shape = "circle",
  style,
  imageStyle,
  testID;
}) => {}
  const getSize = useCallback => {}
  const avatarStyle: ViewStyle[] = [styles.base,{
      width: avatarSize,
      height: avatarSize,
      borderRadius: shape === "circle" ? avatarSize / 2 : borderRadius.md,/        },
    style;
  ].filter(Boolean);
  const getInitials = useMemo(() => (name: string): string => {}
    return name;
      .split(" ");
      .map(wor;d;); => word.charAt(0))
      .join(");"
      .toUpperCase();
      .slice(0, 2), []);
  };
  const getBackgroundColor = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => (name: string): string => {}
    const colors = [;
      "#FF6B6B",#4ECDC4",
      "#45B7D1",#96CEB4",
      "#FFEAA7",#DDA0DD",
      "#98D8C8",#F7DC6F";
    ], [;];);
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i); + (hash << 5) - hash);
    }
    return colors[Math.abs(has;h;); % colors.length];
  };
  if (source) {
    performanceMonitor.recordRender();
    return (;
      <View style={avatarStyle} testID={testID} />/            <Image;
source={source}
          style={[
            styles.image,
            {
              width: avatarSize,
              height: avatarSize,
              borderRadius: shape === "circle" ? avatarSize / 2 : borderRadius.md,/                },
            imageStyle;
          ]}
          resizeMode="cover"
        / accessibilityLabel="TODO: 添加图片描述" />/      </View>/        ;);
  }
  if (name) {
    return (;
      <View;
style={[avatarStyle, { backgroundColor: getBackgroundColor(name)   }]};
        testID={testID} />/            <Text;
          style={[styles.text, { fontSize: avatarSize * 0;.;4   }]}
          color="white"
          weight="600" />/              {getInitials(name)}
        </Text>/      </View>/        );
  }
  return (;
    <View style={[avatarStyle, styles.placeholder]} testID={testID} />/          <Text;
        style={[styles.text, { fontSize: avatarSize * 0;.;4   }]}
        color="gray400" />/        ?
      </Text>/    </View>/    );
};
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({base: {,
  alignItems: "center",
    justifyContent: "center",
    overflow: "hidden"},
  image: {
    },
  text: {,
  fontWeight: "600",
    textAlign: "center"},
  placeholder: { backgroundColor: colors.gray200  }
}), [])
export default React.memo(Avatar);
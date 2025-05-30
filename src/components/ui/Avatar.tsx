import { View, Image, StyleSheet, ViewStyle, ImageStyle } from "react-native";
import { colors, borderRadius } from "../../constants/theme";
import Text from "./Text";
import React from "react";








/**
 * 索克生活 - Avatar组件
 * 通用头像组件
 */


export interface AvatarProps {
  // 头像源
  source?: { uri: string } | number;

  // 文本头像
  name?: string;

  // 尺寸
  size?: "small" | "medium" | "large" | "xlarge" | number;

  // 形状
  shape?: "circle" | "square";

  // 自定义样式
  style?: ViewStyle;
  imageStyle?: ImageStyle;

  // 其他属性
  testID?: string;
}

const Avatar: React.FC<AvatarProps> = ({
  source,
  name,
  size = "medium",
  shape = "circle",
  style,
  imageStyle,
  testID,
}) => {
  const getSize = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []), []), []), []);
    if (typeof size === "number") {
      return size;
    }

    switch (size) {
      case "small":
        return 32;
      case "medium":
        return 48;
      case "large":
        return 64;
      case "xlarge":
        return 96;
      default:
        return 48;
    }
  };

  const avatarSize = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => getSize(), []), []), []), []), []), []);

  const avatarStyle: ViewStyle[] = [
    styles.base,
    {
      width: avatarSize,
      height: avatarSize,
      borderRadius: shape === "circle" ? avatarSize / 2 : borderRadius.md,
    },
    style,
  ].filter(Boolean);

  const getInitials = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => (name: string): string => {
    return name
      .split(" ")
      .map((word) => word.charAt(0))
      .join("")
      .toUpperCase()
      .slice(0, 2), []), []), []), []), []), []);
  };

  const getBackgroundColor = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => (name: string): string => {
    const colors = [
      "#FF6B6B",
      "#4ECDC4",
      "#45B7D1",
      "#96CEB4",
      "#FFEAA7",
      "#DDA0DD",
      "#98D8C8",
      "#F7DC6F",
    ], []), []), []), []), []), []);

    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }

    return colors[Math.abs(hash) % colors.length];
  };

  if (source) {
    return (
      <View style={avatarStyle} testID={testID}>
        <Image
          source={source}
          style={[
            styles.image,
            {
              width: avatarSize,
              height: avatarSize,
              borderRadius:
                shape === "circle" ? avatarSize / 2 : borderRadius.md,
            },
            imageStyle,
          ]}
          resizeMode="cover"
        />
      </View>
    );
  }

  if (name) {
    return (
      <View
        style={[avatarStyle, { backgroundColor: getBackgroundColor(name) }]}
        testID={testID}
      >
        <Text
          style={[styles.text, { fontSize: avatarSize * 0.4 }]}
          color="white"
          weight="600"
        >
          {getInitials(name)}
        </Text>
      </View>
    );
  }

  return (
    <View style={[avatarStyle, styles.placeholder]} testID={testID}>
      <Text
        style={[styles.text, { fontSize: avatarSize * 0.4 }]}
        color="gray400"
      >
        ?
      </Text>
    </View>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => StyleSheet.create({
  base: {
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  },

  image: {
    // 图片样式在组件中动态设置
  },

  text: {
    fontWeight: "600",
    textAlign: "center",
  },

  placeholder: {
    backgroundColor: colors.gray200,
  },
}), []), []), []), []), []), []);

export default React.memo(Avatar);

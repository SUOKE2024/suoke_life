import { Platform, ViewStyle } from "react-native";
import React from "react";

/**
 * 通用图标组件
 * 在不同平台使用不同的图标实现
 */

interface IconProps {
  name: string;
  size?: number;
  color?: string;
  family?:
    | "MaterialCommunityIcons"
    | "MaterialIcons"
    | "Ionicons"
    | "FontAwesome";
  style?: ViewStyle;
}

// 动态导入图标组件
const IconComponent: React.FC<IconProps> = (props) => {
  if (Platform.OS === "web") {
    // Web 平台使用 Expo 图标
    const { MaterialCommunityIcons } = require("@expo/vector-icons");
    return (
      <MaterialCommunityIcons
        name={props.name}
        size={props.size || 24}
        color={props.color || "#000"}
        style={props.style}
      />
    );
  } else {
    // 原生平台使用 react-native-vector-icons
    const VectorIcon =
      require("react-native-vector-icons/MaterialCommunityIcons").default;
    return (
      <VectorIcon
        name={props.name}
        size={props.size || 24}
        color={props.color || "#000"}
        style={props.style}
      />
    );
  }
};

export default React.memo(IconComponent);

import React from 'react';
import { Text } from 'react-native';

// Mock Icon component
const Icon = ({ name, size, color, style, ...props }) => {
  return React.createElement(
    Text,
    {
      ...props,
      style: [{ fontSize: size || 20, color: color || '#000' }, style],
      testID: `icon-${name}`,
    },
    name
  );
};

// Mock createIconSet
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const createIconSet = (_glyphMap, _fontFamily, _fontFile) => {
  return Icon;
};

// Mock createIconSetFromFontello
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const createIconSetFromFontello = (_config, _fontFamily, _fontFile) => {
  return Icon;
};

// Mock createIconSetFromIcoMoon
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const createIconSetFromIcoMoon = (_config, _fontFamily, _fontFile) => {
  return Icon;
};

// Export common icon sets
export const AntDesign = Icon;
export const Entypo = Icon;
export const EvilIcons = Icon;
export const Feather = Icon;
export const FontAwesome = Icon;
export const FontAwesome5 = Icon;
export const Fontisto = Icon;
export const Foundation = Icon;
export const Ionicons = Icon;
export const MaterialIcons = Icon;
export const MaterialCommunityIcons = Icon;
export const Octicons = Icon;
export const SimpleLineIcons = Icon;
export const Zocial = Icon;

export default React.memo(Icon);

export { createIconSet, createIconSetFromFontello, createIconSetFromIcoMoon };

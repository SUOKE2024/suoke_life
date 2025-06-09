import React from 'react';
import { StyleSheet, Text } from 'react-native';

interface IconProps {
  name: string;
  size?: number;
  color?: string;
  style?: any;
}

const iconMap: Record<string, string> = {
  // 导航图标
  'arrow-left': '←',
  'arrow-right': '→',
  'arrow-up': '↑',
  'arrow-down': '↓',
  'chevron-left': '‹',
  'chevron-right': '›',
  'chevron-up': '⌃',
  'chevron-down': '⌄',

  // 诊断相关图标
  eye: '👁',
  ear: '👂',
  'message-circle': '💬',
  hand: '✋',
  'bar-chart': '📊',
  activity: '📈',
  heart: '❤️',
  user: '👤',
  users: '👥',

  // 操作图标
  plus: '+',
  minus: '-',
  x: '×',
  check: '✓',
  'refresh-cw': '↻',
  settings: '⚙️',
  search: '🔍',
  filter: '🔽',
  edit: '✏️',
  trash: '🗑',
  save: '💾',
  download: '⬇️',
  upload: '⬆️',

  // 状态图标
  info: 'ℹ️',
  'alert-circle': '⚠️',
  'alert-triangle': '⚠️',
  'check-circle': '✅',
  'x-circle': '❌',
  'help-circle': '❓',

  // 媒体图标
  play: '▶️',
  pause: '⏸',
  stop: '⏹',
  volume: '🔊',
  'volume-off': '🔇',
  camera: '📷',
  image: '🖼',
  mic: '🎤',
  'mic-off': '🎤',

  // 通用图标
  home: '🏠',
  star: '⭐',
  bookmark: '🔖',
  calendar: '📅',
  clock: '🕐',
  mail: '✉️',
  phone: '📞',
  'map-pin': '📍',
  globe: '🌐',
  wifi: '📶',
  battery: '🔋',

  // 健康相关图标
  zap: '⚡',
  shield: '🛡',
  thermometer: '🌡',
  pill: '💊',
  stethoscope: '🩺',
  bandage: '🩹',
  syringe: '💉',

  // 文件图标
  file: '📄',
  folder: '📁',
  clipboard: '📋',
  book: '📖',
  'file-text': '📄',

  // 其他
  lock: '🔒',
  unlock: '🔓',
  key: '🔑',
  link: '🔗',
  'external-link': '↗️',
  share: '📤',
  copy: '📋',
  scissors: '✂️',
};

const Icon: React.FC<IconProps> = ({
  name,
  size = 24,
  color = '#000',
  style,
}) => {
  const iconSymbol = iconMap[name] || '?';

  return (
    <Text;
      style={[
        styles.icon,
        {
          fontSize: size,
          color,
          lineHeight: size,
          width: size,
          height: size,
        },
        style,
      ]}
    >
      {iconSymbol}
    </Text>
  );
};

const styles = StyleSheet.create({
  icon: {,
  textAlign: 'center',
    textAlignVertical: 'center',
  },
});

export default Icon;

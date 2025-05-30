/**
 * 索克生活 - UI组件库入口文件
 * 统一导出所有UI组件
 */

// 基础组件
export { default as Text } from './Text';
export { default as Button } from './Button';
export { default as Input } from './Input';
export { default as Card } from './Card';
export { default as Modal } from './Modal';
export { default as Loading } from './Loading';
export { default as Container } from './Container';
export { default as Avatar } from './Avatar';
export { default as Badge } from './Badge';
export { default as Divider } from './Divider';

// 表单组件
export { default as Checkbox } from './Checkbox';
export { default as Radio } from './Radio';
export { default as Switch } from './Switch';
export { default as Slider } from './Slider';

// 特色组件
export { default as AgentAvatar } from './AgentAvatar';

// 新增组件
export { default as ThemeToggle } from './ThemeToggle';
export { default as AccessibilityPanel } from './AccessibilityPanel';

// 用户体验增强组件
export { UserExperienceEnhancer, useUserExperience } from './UserExperienceEnhancer';

// 导出类型
export type { TextProps } from './Text';
export type { ButtonProps } from './Button';
export type { ButtonVariant, ButtonSize, ButtonShape } from './Button';
export type { InputProps } from './Input';
export type { CardProps } from './Card';
export type { ContainerProps } from './Container';
export type { AvatarProps } from './Avatar';
export type { SwitchProps } from './Switch';
export type { CheckboxProps } from './Checkbox';
export type { RadioProps } from './Radio';
export type { SliderProps } from './Slider';
export type { BadgeProps } from './Badge';
export type { LoadingProps } from './Loading';
export type { ModalProps } from './Modal';
export type { AgentAvatarProps } from './AgentAvatar';
export type { DividerProps } from './Divider'; 
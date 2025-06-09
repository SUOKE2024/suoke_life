// 索克生活 - 主屏幕模块统一导出
// 主屏幕相关组件的入口文件

export { default as HomeScreen } from './HomeScreen';

// 导出类型定义
export type { Contact, ContactGroup } from './HomeScreen';

// 导出联系人类型枚举
export type ContactType = 'agent' | 'doctor' | 'user' | 'supplier' | 'service';
export type ContactStatus = 'online' | 'offline' | 'busy' | 'away';

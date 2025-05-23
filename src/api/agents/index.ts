import xiaoaiApi from './xiaoaiApi';
import xiaokeApi from './xiaokeApi';
import laokeApi from './laokeApi';
import soerApi from './soerApi';

export {
  xiaoaiApi,
  xiaokeApi,
  laokeApi,
  soerApi,
};

// 智能体类型
export enum AgentType {
  XIAOAI = 'xiaoai', // 小艾智能体
  XIAOKE = 'xiaoke', // 小克智能体
  LAOKE = 'laoke',   // 老克智能体
  SOER = 'soer'      // 索儿智能体
}

// 智能体功能介绍
export const agentInfo = {
  [AgentType.XIAOAI]: {
    name: '小艾',
    avatar: 'account-heart', // 使用图标名称而不是图片路径
    description: '辨证智能体，通过四诊结合的方式，为您提供中医体质辨识和健康建议。',
    abilities: [
      '四诊协调分析',
      '多模态健康输入',
      '中医辨证',
      '体质分析',
      '健康记录与摘要'
    ],
    color: '#FF6B6B',
    specialties: ['望诊', '闻诊', '问诊', '切诊'],
    greeting: '您好！我是小艾，专注于中医辨证分析。让我通过四诊合参为您提供个性化的健康建议。'
  },
  [AgentType.XIAOKE]: {
    name: '小克',
    avatar: 'account-cog', // 使用图标名称而不是图片路径
    description: '服务智能体，负责医疗资源调度和食农结合服务，为您提供优质的健康服务和产品。',
    abilities: [
      '医疗资源调度',
      '预约管理',
      '农产品定制',
      '农产品溯源',
      '健康商品推荐'
    ],
    color: '#4ECDC4',
    specialties: ['医疗服务', '健康产品', '农产品溯源', '预约管理'],
    greeting: '您好！我是小克，专注于为您提供优质的医疗服务和健康产品。有什么可以为您服务的吗？'
  },
  [AgentType.LAOKE]: {
    name: '老克',
    avatar: 'school', // 使用图标名称而不是图片路径
    description: '教育智能体，传授中医养生知识，构建积极健康社区，将学习与游戏相结合。',
    abilities: [
      '知识图谱检索',
      '个性化学习路径',
      '社区内容管理',
      '游戏化学习',
      '知识贡献评估'
    ],
    color: '#45B7D1',
    specialties: ['中医教育', '养生知识', '社区管理', '学习指导'],
    greeting: '您好！我是老克，中医养生知识的传播者。让我带您探索中医的奥秘，开启健康学习之旅！'
  },
  [AgentType.SOER]: {
    name: '索儿',
    avatar: 'leaf', // 使用图标名称而不是图片路径
    description: '养生智能体，根据体质和环境因素，为您提供个性化健康计划和养生建议。',
    abilities: [
      '个性化健康计划',
      '传感器数据分析',
      '生活方式建议',
      '健康趋势预测',
      '情绪与睡眠管理'
    ],
    color: '#96CEB4',
    specialties: ['健康计划', '生活方式', '数据分析', '趋势预测'],
    greeting: '您好！我是索儿，您的个人健康管家。让我根据您的体质和生活环境，为您制定专属的养生方案。'
  }
}; 
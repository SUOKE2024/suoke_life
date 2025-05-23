import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { STORAGE_KEYS } from './constants';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { NativeModules, Platform } from 'react-native';

// 获取设备的语言设置
const getDeviceLanguage = () => {
  const deviceLanguage =
    Platform.OS === 'ios'
      ? NativeModules.SettingsManager.settings.AppleLocale ||
        NativeModules.SettingsManager.settings.AppleLanguages[0] // iOS 13+
      : NativeModules.I18nManager.localeIdentifier;

  return deviceLanguage.split('_')[0]; // 只取语言代码，例如"zh_CN"取"zh"
};

// 本地化资源
const resources = {
  en: {
    translation: {
      common: {
        confirm: 'Confirm',
        cancel: 'Cancel',
        save: 'Save',
        delete: 'Delete',
        edit: 'Edit',
        back: 'Back',
        next: 'Next',
        done: 'Done',
        loading: 'Loading...',
        error: 'An error occurred',
        search: 'Search',
        seeMore: 'See More',
        noData: 'No data available',
      },
      auth: {
        login: 'Login',
        register: 'Register',
        forgotPassword: 'Forgot Password',
        password: 'Password',
        confirmPassword: 'Confirm Password',
        username: 'Username',
        mobile: 'Mobile Number',
        email: 'Email',
        verificationCode: 'Verification Code',
        getCode: 'Get Code',
        loginSuccess: 'Login successful',
        registerSuccess: 'Registration successful',
        passwordReset: 'Password has been reset',
        logout: 'Logout',
        logoutConfirm: 'Are you sure you want to logout?',
        alreadyHaveAccount: 'Already have an account? Login',
        noAccount: 'Don\'t have an account? Register',
      },
      home: {
        title: 'Home',
        explore: 'Explore',
        life: 'Life',
        suoke: 'Suoke',
        profile: 'Profile',
        welcome: 'Welcome to Suoke Life',
        todayHealth: 'Today\'s Health',
        dailyTask: 'Daily Tasks',
        recommendation: 'Recommendations',
      },
      explore: {
        title: 'Explore',
        categories: 'Categories',
        recommended: 'Recommended',
        popular: 'Popular',
        latest: 'Latest',
        tcmBasics: 'TCM Basics',
        healthGuides: 'Health Guides',
        foodTherapy: 'Food Therapy',
        acupressure: 'Acupressure',
        seasonalHealth: 'Seasonal Health',
        meridians: 'Meridians',
        emotionalHealth: 'Emotional Health',
      },
      agents: {
        xiaoai: 'Xiaoai',
        xiaoke: 'Xiaoke',
        laoke: 'Laoke',
        soer: 'Soer',
        chat: 'Chat',
        history: 'History',
        consultation: 'Consultation',
      },
      health: {
        report: 'Health Report',
        plan: 'Health Plan',
        data: 'Health Data',
        constitution: 'Constitution',
        score: 'Health Score',
        trends: 'Health Trends',
        sleep: 'Sleep',
        steps: 'Steps',
        activity: 'Activity',
        weight: 'Weight',
        bloodPressure: 'Blood Pressure',
        heartRate: 'Heart Rate',
        bloodSugar: 'Blood Sugar',
        mood: 'Mood',
      },
      diagnostic: {
        title: 'Diagnostic',
        observation: 'Observation',
        auscultation: 'Auscultation',
        interview: 'Interview',
        palpation: 'Palpation',
        result: 'Diagnostic Result',
        recommendation: 'Recommendations',
      },
      profile: {
        title: 'Profile',
        personal: 'Personal Info',
        settings: 'Settings',
        language: 'Language',
        theme: 'Theme',
        privacy: 'Privacy',
        help: 'Help',
        about: 'About',
        feedback: 'Feedback',
      },
    },
  },
  zh: {
    translation: {
      common: {
        confirm: '确认',
        cancel: '取消',
        save: '保存',
        delete: '删除',
        edit: '编辑',
        back: '返回',
        next: '下一步',
        done: '完成',
        loading: '加载中...',
        error: '发生错误',
        search: '搜索',
        seeMore: '查看更多',
        noData: '暂无数据',
        welcome: '欢迎',
        view_all: '查看全部',
      },
      auth: {
        login: '登录',
        register: '注册',
        forgotPassword: '忘记密码',
        password: '密码',
        confirmPassword: '确认密码',
        username: '用户名',
        mobile: '手机号',
        email: '邮箱',
        verificationCode: '验证码',
        getCode: '获取验证码',
        loginSuccess: '登录成功',
        registerSuccess: '注册成功',
        passwordReset: '密码已重置',
        logout: '退出登录',
        logoutConfirm: '确定要退出登录吗？',
        alreadyHaveAccount: '已有账号？去登录',
        noAccount: '没有账号？去注册',
      },
      home: {
        title: '首页',
        explore: '探索',
        life: '生活',
        suoke: '索克',
        profile: '我的',
        welcome: '欢迎来到索克生活',
        todayHealth: '今日健康',
        dailyTask: '日常任务',
        recommendation: '推荐',
        quick_access: '快速访问',
        health_data: '健康数据',
        health_plan: '健康计划',
        knowledge: '健康知识',
      },
      explore: {
        title: '探索',
        categories: '分类',
        recommended: '推荐',
        popular: '热门',
        latest: '最新',
        tcmBasics: '中医基础',
        healthGuides: '健康指南',
        foodTherapy: '食疗食补',
        acupressure: '穴位按摩',
        seasonalHealth: '四季养生',
        meridians: '经络养护',
        emotionalHealth: '情志调养',
      },
      agents: {
        title: '智能体',
        xiaoai: '小艾',
        xiaoke: '小克',
        laoke: '老克',
        soer: '索儿',
        xiaoai_desc: '中医诊断智能体，专业四诊合参',
        xiaoke_desc: '服务调度智能体，医疗资源与食农结合',
        laoke_desc: '知识传授智能体，中医养生教育专家',
        soer_desc: '生活养生智能体，个性化健康管理',
        chat: '对话',
        history: '历史记录',
        consultation: '问诊',
        collaboration: '智能体协同',
        collaboration_desc: '四大智能体协同工作，为您提供全方位健康管理服务',
      },
      health: {
        report: '健康报告',
        plan: '健康计划',
        data: '健康数据',
        constitution: '体质',
        score: '健康评分',
        trends: '健康趋势',
        sleep: '睡眠',
        steps: '步数',
        activity: '活动',
        weight: '体重',
        bloodPressure: '血压',
        heartRate: '心率',
        bloodSugar: '血糖',
        mood: '情绪',
      },
      diagnostic: {
        title: '诊断',
        observation: '望诊',
        auscultation: '闻诊',
        interview: '问诊',
        palpation: '切诊',
        result: '诊断结果',
        recommendation: '建议',
      },
      diagnosis: {
        title: '四诊合参',
      },
      profile: {
        title: '个人中心',
        personal: '个人信息',
        settings: '设置',
        language: '语言',
        theme: '主题',
        privacy: '隐私',
        help: '帮助',
        about: '关于',
        feedback: '反馈',
      },
    },
  },
};

// 初始化i18next（同步版本）
i18n.use(initReactI18next).init({
  resources,
  lng: 'zh', // 默认使用中文
  fallbackLng: 'zh',
  compatibilityJSON: 'v3',
  interpolation: {
    escapeValue: false,
  },
  react: {
    useSuspense: false,
  },
});

// 异步设置用户语言偏好
const setupI18n = async () => {
  try {
    const userLanguage = await AsyncStorage.getItem(STORAGE_KEYS.LOCALE);
    if (userLanguage && userLanguage !== i18n.language) {
      await i18n.changeLanguage(userLanguage);
    } else if (!userLanguage) {
      // 如果没有保存的语言设置，使用设备语言
      const deviceLanguage = getDeviceLanguage();
      if (deviceLanguage !== 'zh') {
        await i18n.changeLanguage(deviceLanguage);
      }
    }
  } catch (error) {
    console.error('Error setting up language:', error);
  }
  
  return i18n;
};

// 改变语言
export const changeLanguage = async (language: string) => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.LOCALE, language);
    await i18n.changeLanguage(language);
  } catch (error) {
    console.error('Error changing language:', error);
  }
};

export { setupI18n };
export default i18n; 
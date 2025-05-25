/**
 * 国际化Hook
 */

import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setLanguage } from '../store/slices/uiSlice';
import { t, changeLanguage, getCurrentLanguage } from '../i18n';
import { RootState } from '../types';

export const useI18n = () => {
  const dispatch = useDispatch();
  const language = useSelector((state: RootState) => state.ui.language);
  const [isChanging, setIsChanging] = useState(false);

  /**
   * 切换语言
   */
  const switchLanguage = async (newLanguage: 'zh' | 'en') => {
    if (newLanguage === language || isChanging) {
      return;
    }

    setIsChanging(true);
    try {
      await changeLanguage(newLanguage);
      dispatch(setLanguage(newLanguage));
    } catch (error) {
      console.warn('切换语言失败:', error);
    } finally {
      setIsChanging(false);
    }
  };

  /**
   * 翻译函数
   */
  const translate = (key: string, options?: object): string => {
    return t(key, options);
  };

  /**
   * 获取当前语言
   */
  const currentLanguage = getCurrentLanguage();

  return {
    language: currentLanguage,
    switchLanguage,
    translate,
    t: translate,
    isChanging,
  };
};

export default useI18n;

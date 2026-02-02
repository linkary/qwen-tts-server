import { en } from './locales/en/common';
import { zhCN } from './locales/zh-cn/common';

export const translations = {
  en,
  'zh-cn': zhCN
};

export type TranslationKey = keyof typeof translations.en;

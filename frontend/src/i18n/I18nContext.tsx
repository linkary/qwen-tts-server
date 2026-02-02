import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { translations, TranslationKey } from './translations';
import type { Language } from '../types';

interface I18nContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: TranslationKey) => string;
}

const I18nContext = createContext<I18nContextType | null>(null);

interface I18nProviderProps {
  children: ReactNode;
}

export function I18nProvider({ children }: I18nProviderProps) {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('qwen-tts-lang');
    if (saved) return saved as Language;

    const browserLang = navigator.language.toLowerCase();
    if (browserLang.startsWith('zh')) return 'zh-cn';
    
    return 'en';
  });

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('qwen-tts-lang', lang);
  }, []);

  const t = useCallback((key: TranslationKey): string => {
    return translations[language]?.[key] || translations.en[key] || key;
  }, [language]);

  return (
    <I18nContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return context;
}

export function useTranslation() {
  const { t } = useI18n();
  return t;
}

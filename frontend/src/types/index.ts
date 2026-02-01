export * from './api';
export * from './audio';
export * from './speaker';

export type Language = 'en' | 'zh-cn';

export interface VoicePrompt {
  id: string;
  createdAt: string;
}

export interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

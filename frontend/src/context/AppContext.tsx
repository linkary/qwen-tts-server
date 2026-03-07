import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { DEFAULT_API_KEY } from '../config/constants';
import type { VoicePrompt } from '../types';
import type { AudioMetrics } from '../types/audio';

export interface TabAudioState {
  url: string | null;
  metrics: AudioMetrics;
  isLoading: boolean;
}

const emptyAudio: TabAudioState = { url: null, metrics: {}, isLoading: false };

export type TabId = 'custom-voice' | 'voice-design' | 'voice-clone' | 'settings';

interface AppState {
  apiKey: string;
  selectedSpeaker: string;
  savedPrompts: VoicePrompt[];
  uploadedFileBase64: string | null;
  recordedAudioBase64: string | null;
  selectedPromptId: string | null;
  apiDocsOpen: boolean;
  activeTab: TabId;
  customVoiceAudio: TabAudioState;
  voiceDesignAudio: TabAudioState;
  voiceCloneAudio: TabAudioState;
}

interface AppContextType extends AppState {
  setApiKey: (key: string) => void;
  setSelectedSpeaker: (speaker: string) => void;
  addSavedPrompt: (prompt: VoicePrompt) => void;
  removeSavedPrompt: (id: string) => void;
  setUploadedFileBase64: (base64: string | null) => void;
  setRecordedAudioBase64: (base64: string | null) => void;
  setSelectedPromptId: (id: string | null) => void;
  setApiDocsOpen: (open: boolean) => void;
  toggleApiDocs: () => void;
  setActiveTab: (tab: TabId) => void;
  setCustomVoiceAudio: (audio: TabAudioState) => void;
  setVoiceDesignAudio: (audio: TabAudioState) => void;
  setVoiceCloneAudio: (audio: TabAudioState) => void;
}

const AppContext = createContext<AppContextType | null>(null);

interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const [apiKey, setApiKeyState] = useState<string>(() => {
    return localStorage.getItem('qwen-tts-api-key') || DEFAULT_API_KEY;
  });

  const [selectedSpeaker, setSelectedSpeaker] = useState<string>('Ryan');

  const [savedPrompts, setSavedPrompts] = useState<VoicePrompt[]>(() => {
    const saved = localStorage.getItem('qwen-tts-prompts');
    return saved ? JSON.parse(saved) : [];
  });

  const [uploadedFileBase64, setUploadedFileBase64] = useState<string | null>(null);
  const [recordedAudioBase64, setRecordedAudioBase64] = useState<string | null>(null);
  const [selectedPromptId, setSelectedPromptId] = useState<string | null>(null);
  
  const [apiDocsOpen, setApiDocsOpenState] = useState<boolean>(() => {
    return localStorage.getItem('qwen-tts-api-docs-open') === 'true';
  });
  
  const [activeTab, setActiveTab] = useState<TabId>('custom-voice');
  const [customVoiceAudio, setCustomVoiceAudio] = useState<TabAudioState>(emptyAudio);
  const [voiceDesignAudio, setVoiceDesignAudio] = useState<TabAudioState>(emptyAudio);
  const [voiceCloneAudio, setVoiceCloneAudio] = useState<TabAudioState>(emptyAudio);

  // Persist API key
  useEffect(() => {
    localStorage.setItem('qwen-tts-api-key', apiKey);
  }, [apiKey]);

  // Persist saved prompts
  useEffect(() => {
    localStorage.setItem('qwen-tts-prompts', JSON.stringify(savedPrompts));
  }, [savedPrompts]);
  
  // Persist API docs open state
  useEffect(() => {
    localStorage.setItem('qwen-tts-api-docs-open', apiDocsOpen.toString());
  }, [apiDocsOpen]);

  const setApiKey = useCallback((key: string) => {
    setApiKeyState(key);
  }, []);

  const addSavedPrompt = useCallback((prompt: VoicePrompt) => {
    setSavedPrompts(prev => [...prev, prompt]);
  }, []);

  const removeSavedPrompt = useCallback((id: string) => {
    setSavedPrompts(prev => prev.filter(p => p.id !== id));
    setSelectedPromptId(prev => prev === id ? null : prev);
  }, []);
  
  const setApiDocsOpen = useCallback((open: boolean) => {
    setApiDocsOpenState(open);
  }, []);
  
  const toggleApiDocs = useCallback(() => {
    setApiDocsOpenState(prev => !prev);
  }, []);

  return (
    <AppContext.Provider
      value={{
        apiKey,
        selectedSpeaker,
        savedPrompts,
        uploadedFileBase64,
        recordedAudioBase64,
        selectedPromptId,
        apiDocsOpen,
        activeTab,
        customVoiceAudio,
        voiceDesignAudio,
        voiceCloneAudio,
        setApiKey,
        setSelectedSpeaker,
        addSavedPrompt,
        removeSavedPrompt,
        setUploadedFileBase64,
        setRecordedAudioBase64,
        setSelectedPromptId,
        setApiDocsOpen,
        toggleApiDocs,
        setActiveTab,
        setCustomVoiceAudio,
        setVoiceDesignAudio,
        setVoiceCloneAudio,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
}

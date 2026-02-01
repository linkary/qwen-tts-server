import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { DEFAULT_API_KEY } from '../config/constants';
import type { VoicePrompt } from '../types';

interface AppState {
  apiKey: string;
  selectedSpeaker: string;
  savedPrompts: VoicePrompt[];
  uploadedFileBase64: string | null;
  recordedAudioBase64: string | null;
  selectedPromptId: string | null;
}

interface AppContextType extends AppState {
  setApiKey: (key: string) => void;
  setSelectedSpeaker: (speaker: string) => void;
  addSavedPrompt: (prompt: VoicePrompt) => void;
  removeSavedPrompt: (id: string) => void;
  setUploadedFileBase64: (base64: string | null) => void;
  setRecordedAudioBase64: (base64: string | null) => void;
  setSelectedPromptId: (id: string | null) => void;
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

  // Persist API key
  useEffect(() => {
    localStorage.setItem('qwen-tts-api-key', apiKey);
  }, [apiKey]);

  // Persist saved prompts
  useEffect(() => {
    localStorage.setItem('qwen-tts-prompts', JSON.stringify(savedPrompts));
  }, [savedPrompts]);

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

  return (
    <AppContext.Provider
      value={{
        apiKey,
        selectedSpeaker,
        savedPrompts,
        uploadedFileBase64,
        recordedAudioBase64,
        selectedPromptId,
        setApiKey,
        setSelectedSpeaker,
        addSavedPrompt,
        removeSavedPrompt,
        setUploadedFileBase64,
        setRecordedAudioBase64,
        setSelectedPromptId,
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

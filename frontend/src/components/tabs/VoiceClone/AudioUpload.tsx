import React, { useRef, useState } from 'react';
import { UploadCloud } from 'lucide-react';
import { useTranslation } from '../../../i18n/I18nContext';
import { useToast } from '../../../context/ToastContext';
import { fileToBase64 } from '../../../utils/audio';
import { formatFileSize } from '../../../utils/format';

interface AudioUploadProps {
  onAudioUploaded: (base64: string, file: File) => void;
}

export function AudioUpload({ onAudioUploaded }: AudioUploadProps) {
  const t = useTranslation();
  const { showToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    // Validate file type
    if (!file.type.startsWith('audio/')) {
      showToast('Please upload an audio file', 'error');
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      showToast('File too large (max 5MB)', 'error');
      return;
    }

    try {
      const base64 = await fileToBase64(file);
      setUploadedFile(file);
      setAudioUrl(URL.createObjectURL(file));
      onAudioUploaded(base64, file);
      showToast('Audio uploaded successfully', 'success');
    } catch (error) {
      showToast('Failed to process audio file', 'error');
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div>
      {!uploadedFile ? (
        <div
          onClick={handleClick}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className="border-2 border-dashed border-border-subtle rounded-lg p-2xl text-center cursor-pointer transition-all hover:border-accent-cyan hover:bg-[rgba(0,245,212,0.05)]"
        >
          <div className="flex justify-center mb-md opacity-50">
            <UploadCloud className="w-12 h-12" />
          </div>
          <div className="text-base text-text-secondary mb-sm">{t('uploadZoneText')}</div>
          <div className="text-xs text-text-muted">{t('uploadZoneHint')}</div>
          <input
            ref={fileInputRef}
            type="file"
            accept="audio/*"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            className="hidden"
          />
        </div>
      ) : (
        <div className="p-lg bg-bg-surface border border-border-subtle rounded-md">
          <div className="flex items-center justify-between mb-md">
            <span className="font-display text-sm text-text-primary">{uploadedFile.name}</span>
            <span className="text-xs text-text-muted">{formatFileSize(uploadedFile.size)}</span>
          </div>
          {audioUrl && <audio controls src={audioUrl} className="w-full" />}
        </div>
      )}
    </div>
  );
}

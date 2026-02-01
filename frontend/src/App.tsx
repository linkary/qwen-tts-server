import React, { useEffect } from 'react';
import { Header } from './components/layout/Header';
import { TabNavigation, TabId } from './components/layout/TabNavigation';
import { ToastContainer } from './components/ui/ToastContainer';
import { ApiDocsPanel } from './components/ui/ApiDocsPanel';
import { ApiDocsToggle } from './components/ui/ApiDocsToggle';
import { CustomVoiceTab } from './components/tabs/CustomVoice';
import { VoiceDesignTab } from './components/tabs/VoiceDesign';
import { VoiceCloneTab } from './components/tabs/VoiceClone';
import { SettingsTab } from './components/tabs/Settings';
import { I18nProvider } from './i18n/I18nContext';
import { AppProvider, useAppContext } from './context/AppContext';
import { ToastProvider } from './context/ToastContext';

function AppContent() {
  const { activeTab, setActiveTab, apiDocsOpen, toggleApiDocs } = useAppContext();

  const renderTabContent = () => {
    switch (activeTab) {
      case 'custom-voice':
        return <CustomVoiceTab />;
      case 'voice-design':
        return <VoiceDesignTab />;
      case 'voice-clone':
        return <VoiceCloneTab />;
      case 'settings':
        return <SettingsTab />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen">
      <Header />
      <main className="py-xl pb-3xl">
        <div className="max-w-[1200px] mx-auto px-lg">
          <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
          <div role="tabpanel" className="animate-fadeIn">
            {renderTabContent()}
          </div>
        </div>
      </main>
      <ToastContainer />
      <ApiDocsToggle isOpen={apiDocsOpen} onClick={toggleApiDocs} />
      <ApiDocsPanel 
        isOpen={apiDocsOpen} 
        onClose={toggleApiDocs}
        activeTab={activeTab}
      />
    </div>
  );
}

function App() {
  return (
    <I18nProvider>
      <AppProvider>
        <ToastProvider>
          <AppContent />
        </ToastProvider>
      </AppProvider>
    </I18nProvider>
  );
}

export default App;

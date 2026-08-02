import { Header } from './components/layout/Header';
import { TabNavigation, type TabId } from './components/layout/TabNavigation';
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
import { useCrossfade } from './hooks/useCrossfade';
import { cn } from './utils/cn';

function renderTab(tab: TabId) {
  switch (tab) {
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
}

function AppContent() {
  const { activeTab, setActiveTab, apiDocsOpen, toggleApiDocs } = useAppContext();

  // The nav follows `activeTab` immediately so the click is acknowledged at once,
  // while the panel renders `rendered` — one exit animation behind — so the outgoing
  // tab gets to leave before the incoming one arrives.
  const { rendered, phase, onAnimationEnd } = useCrossfade(activeTab);

  return (
    <div className="min-h-screen">
      <Header />
      <main className="py-xl pb-3xl">
        <div className="max-w-[1200px] mx-auto px-lg">
          <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
          <div
            // Remounting on every swap is what makes the CSS animation replay at
            // all — without a key React reuses this node and nothing animates.
            key={rendered}
            role="tabpanel"
            onAnimationEnd={onAnimationEnd}
            className={cn(
              // Absorbs most of the height difference between tabs, so the
              // scrollbar does not jump when moving to a short tab like Settings.
              'min-h-[60vh]',
              phase === 'leaving' ? 'animate-tabOut' : 'animate-tabIn'
            )}
          >
            {renderTab(rendered)}
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

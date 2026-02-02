import React, { useState, useEffect } from 'react';
import { BookOpen, X, ExternalLink } from 'lucide-react';
import { API_DOCS, type ApiDocConfig, type ApiSubTab, type ApiParam, type ApiHeader, type ApiEndpoint, type ApiAdditionalEndpoint } from '../../config/apiDocs';
import { syntaxHighlightJSON } from '../../utils/syntaxHighlight';
import { useCopyToClipboard } from '../../hooks/useCopyToClipboard';

interface ApiDocsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab: 'custom-voice' | 'voice-design' | 'voice-clone' | 'settings';
}

export function ApiDocsPanel({ isOpen, onClose, activeTab }: ApiDocsPanelProps) {
  const [activeSubTab, setActiveSubTab] = useState<string>('');
  const { copy, copiedText } = useCopyToClipboard();
  const baseUrl = window.location.origin;

  const docs = API_DOCS[activeTab];

  // Reset sub-tab when main tab changes
  useEffect(() => {
    if (docs?.subTabs && docs.subTabs.length > 0) {
      setActiveSubTab(docs.subTabs[0].id);
    }
  }, [activeTab, docs]);

  if (!docs) return null;

  const renderEndpointBadge = (endpoint: ApiEndpoint, docsAnchor?: string) => (
    <div className="flex items-center gap-sm mb-md px-sm py-sm bg-bg-card rounded-md border border-border-subtle">
      <span className={`text-[0.625rem] font-display font-bold px-sm py-xs rounded-sm uppercase ${
        endpoint.method === 'POST' ? 'bg-accent-cyan/20 text-accent-cyan' : 'bg-accent-amber/20 text-accent-amber'
      }`}>
        {endpoint.method}
      </span>
      <span className="text-[0.75rem] font-display text-text-primary">{endpoint.path}</span>
      {docsAnchor && (
        <a
          href={`/docs${docsAnchor}`}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-auto text-accent-cyan hover:text-accent-cyan-dim transition-colors"
          title="Open in Swagger UI"
        >
          ↗️
        </a>
      )}
    </div>
  );

  const renderHeaders = (headers: ApiHeader[]) => (
    <div className="mb-md">
      <div className="text-[0.625rem] font-display font-semibold text-text-muted uppercase tracking-wider mb-xs">
        Request Headers
      </div>
      <div className="space-y-xs">
        {headers.map((h, i) => (
          <div key={i} className="flex justify-between text-[0.75rem] py-xs border-b border-border-subtle">
            <span className="font-display text-accent-coral">{h.name}</span>
            <span className="text-text-secondary">
              {h.value} <span className="text-text-muted italic">// {h.description}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );

  const renderParamsTable = (params: ApiParam[]) => (
    <div className="mb-md">
      <div className="text-[0.625rem] font-display font-semibold text-text-muted uppercase tracking-wider mb-xs">
        Request Parameters
      </div>
      <div className="border border-border-subtle rounded-md overflow-x-auto">
        <table className="w-full text-[0.75rem] text-left">
          <thead>
            <tr className="bg-bg-elevated/50">
              <th className="font-display text-text-secondary font-semibold uppercase tracking-wider p-sm border-b border-border-subtle">Name</th>
              <th className="font-display text-text-secondary font-semibold uppercase tracking-wider p-sm border-b border-border-subtle">Type</th>
              <th className="font-display text-text-secondary font-semibold uppercase tracking-wider p-sm border-b border-border-subtle">Required</th>
              <th className="font-display text-text-secondary font-semibold uppercase tracking-wider p-sm border-b border-border-subtle">Description</th>
            </tr>
          </thead>
          <tbody>
            {params.map((p, i) => (
              <tr key={i} className="border-b border-border-subtle last:border-0">
                <td className="p-sm font-display text-accent-cyan font-semibold">{p.name}</td>
                <td className="p-sm font-display text-accent-amber text-[0.7rem]">{p.type}</td>
                <td className="p-sm">
                  <span className={`inline-block px-[6px] py-[2px] rounded text-[0.625rem] font-bold uppercase ${
                    p.required ? 'bg-accent-coral/20 text-accent-coral' : 'bg-text-muted/20 text-text-muted'
                  }`}>
                    {p.required ? 'YES' : 'NO'}
                  </span>
                </td>
                <td className="p-sm text-text-secondary">{p.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderCodeBlock = (label: string, content: string | object, showCopy: boolean = true) => {
    const jsonString = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
    const highlighted = typeof content === 'string' ? content : syntaxHighlightJSON(content);
    const isCopied = copiedText === jsonString;

    return (
      <div className="mb-md relative">
        <div className="text-[0.625rem] font-display font-semibold text-text-muted uppercase tracking-wider mb-xs">
          {label}
        </div>
        {showCopy && (
          <button
            onClick={() => copy(jsonString)}
            className="absolute top-lg right-sm bg-bg-surface border border-border-subtle rounded-sm px-sm py-xs text-[0.625rem] font-display text-text-muted hover:border-accent-cyan hover:text-accent-cyan transition-all"
          >
            {isCopied ? 'Copied!' : 'Copy'}
          </button>
        )}
        <pre className="bg-bg-deep border border-border-subtle rounded-md p-md text-[0.75rem] font-display leading-relaxed text-text-primary overflow-x-auto max-h-[300px] overflow-y-auto">
          <code dangerouslySetInnerHTML={{ __html: highlighted }} />
        </pre>
      </div>
    );
  };

  const renderResponseHeaders = (headers: ApiHeader[]) => (
    <div className="mb-md">
      <h3 className="text-[0.75rem] font-display font-semibold text-text-secondary uppercase tracking-wider mb-md flex items-center gap-sm before:content-[''] before:inline-block before:w-2 before:h-2 before:bg-accent-cyan before:rounded-sm">
        Response Headers
      </h3>
      <div className="space-y-xs">
        {headers.map((h, i) => (
          <div key={i} className="flex justify-between text-[0.75rem] py-xs border-b border-border-subtle last:border-0">
            <span className="font-display text-accent-coral">{h.name}</span>
            <span className="text-text-secondary">{h.description}</span>
          </div>
        ))}
      </div>
    </div>
  );

  const renderSubTabContent = (subTab: ApiSubTab) => (
    <div className="space-y-md">
      <div className="p-md bg-accent-cyan/5 border-l-[3px] border-accent-cyan rounded-r-md">
        <p className="text-[0.8rem] text-text-secondary leading-relaxed">{subTab.description}</p>
      </div>
      {renderEndpointBadge(subTab.endpoint, subTab.docsAnchor)}
      {subTab.requestHeaders && renderHeaders(subTab.requestHeaders)}
      {subTab.requestParams && renderParamsTable(subTab.requestParams)}
      {subTab.requestExample && renderCodeBlock('Request Body Example', subTab.requestExample)}
      {subTab.responseExample && renderCodeBlock('Response Example', subTab.responseExample, false)}
      {subTab.responseHeaders && renderResponseHeaders(subTab.responseHeaders)}
      {subTab.curlExample && renderCodeBlock('cURL Example', subTab.curlExample.replace(/\{\{baseUrl\}\}/g, baseUrl))}
    </div>
  );

  const renderMainContent = () => {
    if (docs.subTabs) {
      const currentSubTab = docs.subTabs.find(st => st.id === activeSubTab);
      return (
        <>
          <div className="p-md bg-accent-cyan/5 border-l-[3px] border-accent-cyan rounded-r-md mb-md">
            <p className="text-[0.8rem] text-text-secondary leading-relaxed">{docs.description}</p>
          </div>
          <div className="flex gap-xs mb-md border-b border-border-subtle">
            {docs.subTabs.map((st) => (
              <button
                key={st.id}
                onClick={() => setActiveSubTab(st.id)}
                className={`px-md py-xs font-display text-[0.8rem] border-b-2 transition-all ${
                  activeSubTab === st.id
                    ? 'text-accent-cyan border-accent-cyan'
                    : 'text-text-secondary border-transparent hover:text-text-primary'
                }`}
              >
                {st.label}
              </button>
            ))}
          </div>
          {currentSubTab && renderSubTabContent(currentSubTab)}
        </>
      );
    }

    return (
      <div className="space-y-md">
        <div className="p-md bg-accent-cyan/5 border-l-[3px] border-accent-cyan rounded-r-md">
          <p className="text-[0.8rem] text-text-secondary leading-relaxed">{docs.description}</p>
        </div>
        {docs.endpoint && renderEndpointBadge(docs.endpoint, docs.docsAnchor)}
        {docs.requestHeaders && renderHeaders(docs.requestHeaders)}
        {docs.requestParams && renderParamsTable(docs.requestParams)}
        {docs.requestExample && renderCodeBlock('Request Body Example', docs.requestExample)}
        {docs.responseExample && renderCodeBlock('Response Example', docs.responseExample, false)}
        {docs.responseHeaders && renderResponseHeaders(docs.responseHeaders)}
        {docs.curlExample && renderCodeBlock('cURL Example', docs.curlExample.replace(/\{\{baseUrl\}\}/g, baseUrl))}
        {docs.additionalEndpoints && docs.additionalEndpoints.map((endpoint: ApiAdditionalEndpoint, i: number) => (
          <div key={i} className="mt-xl">
            <h3 className="text-[0.75rem] font-display font-semibold text-text-secondary uppercase tracking-wider mb-md flex items-center gap-sm before:content-[''] before:inline-block before:w-2 before:h-2 before:bg-accent-cyan before:rounded-sm">
              {endpoint.title}
            </h3>
            {renderEndpointBadge(endpoint.endpoint)}
            {endpoint.description && (
              <div className="p-md bg-accent-cyan/5 border-l-[3px] border-accent-cyan rounded-r-md mb-md">
                <p className="text-[0.8rem] text-text-secondary leading-relaxed">{endpoint.description}</p>
              </div>
            )}
            {endpoint.responseExample && renderCodeBlock('Response Example', endpoint.responseExample, false)}
          </div>
        ))}
      </div>
    );
  };

  return (
    <>
      {/* Backdrop - only on mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-[199] md:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Panel */}
      <div
        className={`fixed top-0 h-screen w-full md:w-[600px] bg-bg-surface border-l border-border-subtle z-[200] flex flex-col shadow-[-8px_0_32px_rgba(0,0,0,0.3)] transition-all duration-300 ${
          isOpen ? 'right-0' : '-right-full md:-right-[600px]'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-lg bg-bg-card border-b border-border-subtle shrink-0">
          <div className="flex items-center gap-sm text-accent-cyan">
            <BookOpen className="w-5 h-5" />
            <span className="font-display text-base font-semibold">API Reference</span>
          </div>
          <button
            onClick={onClose}
            className="text-text-muted hover:text-accent-coral transition-colors p-xs leading-none"
            title="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-lg api-docs-panel">
          {renderMainContent()}
        </div>
      </div>

      {/* Custom scrollbar styles */}
      <style>{`
        .api-docs-panel::-webkit-scrollbar {
          width: 6px;
        }
        .api-docs-panel::-webkit-scrollbar-track {
          background: #15151f;
        }
        .api-docs-panel::-webkit-scrollbar-thumb {
          background: #3a3a48;
          border-radius: 3px;
        }
        .api-docs-panel::-webkit-scrollbar-thumb:hover {
          background: #00c4a9;
        }
        .key { color: #ff6b6b; }
        .string { color: #00f5d4; }
        .number { color: #ffc107; }
        .boolean { color: #c792ea; }
        .null { color: #606070; }
      `}</style>
    </>
  );
}

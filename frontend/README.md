# Qwen3-TTS React Frontend

Modern React + TypeScript frontend for the Qwen3-TTS API Server.

## Features

- 🎨 **Custom Voice**: Generate speech using 9 preset speakers with emotional control
- 🎭 **Voice Design**: Create custom voices using natural language descriptions
- 🎙️ **Voice Clone**: Clone any voice from reference audio (upload or record)
- ⚙️ **Settings**: Configure API access, view server status, and manage cache

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + CSS Modules
- **State Management**: React Context API
- **HTTP Client**: Native Fetch API
- **Audio**: Web Audio API for recording and playback

## Development

### Prerequisites

- Node.js 18+ and npm
- Backend server running at `http://localhost:8000`

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

The dev server runs at `http://localhost:5173` and proxies API requests to the backend.

### Build for Production

```bash
npm run build
```

Outputs to `dist/` directory. The backend server will automatically serve the built app.

## Project Structure

```
src/
├── components/          # React components
│   ├── layout/         # Header, TabNavigation
│   ├── tabs/           # Feature tabs (CustomVoice, VoiceDesign, VoiceClone, Settings)
│   ├── audio/          # AudioPlayer, WaveformVisualizer, PerformanceMetrics
│   ├── forms/          # Form components (Input, Textarea, Select, etc.)
│   └── ui/             # UI primitives (Button, Card, Toast, etc.)
├── hooks/              # Custom React hooks
├── services/           # API service layer
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
├── styles/             # Global styles and animations
├── i18n/               # Internationalization (English/Chinese)
├── context/            # React Context providers
├── config/             # Configuration and constants
├── App.tsx             # Main application
└── main.tsx            # Entry point
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## Environment Variables

No environment variables required. API base URL is automatically detected from `window.location.origin`.

## Language Support

The UI supports:
- English (en)
- Chinese Simplified (zh-cn)

Switch between languages using the language toggle in the header.

## API Integration

All API calls go through `src/services/api.ts`:

- `generateCustomVoice()` - Custom Voice generation
- `generateVoiceDesign()` - Voice Design generation
- `cloneVoice()` - Voice Clone generation
- `createVoicePrompt()` - Create cached prompt
- `generateWithPrompt()` - Generate with saved prompt
- `checkHealth()` - Server health check
- `checkModelsHealth()` - Model status
- `fetchCacheStats()` - Cache statistics
- `clearCache()` - Clear voice prompt cache

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires:
- MediaRecorder API (for voice recording)
- Web Audio API (for audio playback)
- Fetch API (for HTTP requests)

## Design System

### Colors

- **Background**: Deep dark theme (`#0a0a0f`)
- **Accent Cyan**: Primary actions (`#00f5d4`)
- **Accent Coral**: Secondary/danger (`#ff6b6b`)
- **Accent Amber**: Warnings (`#ffc107`)

### Typography

- **Display**: JetBrains Mono (headings, code)
- **Body**: DM Sans (body text)

### Animations

- Pulse glow effects on interactive elements
- Waveform visualization during audio playback
- VU meter loading animation
- Smooth transitions and slide-in animations

## Accessibility

- Semantic HTML elements
- ARIA labels on interactive components
- Keyboard navigation support
- Focus indicators on all interactive elements

## License

Same as parent project

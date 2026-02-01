/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '900px',
      'xl': '1200px',
    },
    extend: {
      colors: {
        bg: {
          deep: '#0a0a0f',
          surface: '#12121a',
          elevated: '#1a1a25',
          card: '#15151f',
        },
        accent: {
          cyan: '#00f5d4',
          'cyan-dim': '#00c4a9',
          coral: '#ff6b6b',
          'coral-dim': '#cc5555',
          amber: '#ffc107',
        },
        text: {
          primary: '#f0f0f5',
          secondary: '#9090a0',
          muted: '#606070',
        },
        border: {
          subtle: '#2a2a35',
          active: '#3a3a48',
        },
      },
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body: ['Space Grotesk', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      boxShadow: {
        'glow-cyan': '0 0 24px rgba(0, 245, 212, 0.4), 0 0 48px rgba(0, 245, 212, 0.2), 0 0 96px rgba(0, 245, 212, 0.1)',
        'glow-cyan-strong': '0 0 32px rgba(0, 245, 212, 0.6), 0 0 64px rgba(0, 245, 212, 0.3), 0 0 128px rgba(0, 245, 212, 0.15)',
        'glow-coral': '0 0 24px rgba(255, 107, 107, 0.4), 0 0 48px rgba(255, 107, 107, 0.2), 0 0 96px rgba(255, 107, 107, 0.1)',
        'card': '0 8px 32px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.05)',
        'brutal': '8px 8px 0px 0px rgba(0, 245, 212, 0.3)',
        'brutal-hover': '12px 12px 0px 0px rgba(0, 245, 212, 0.5)',
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { 
            boxShadow: '0 0 8px var(--tw-shadow-color), 0 0 16px var(--tw-shadow-color)' 
          },
          '50%': { 
            boxShadow: '0 0 16px var(--tw-shadow-color), 0 0 32px var(--tw-shadow-color), 0 0 48px color-mix(in srgb, var(--tw-shadow-color) 30%, transparent)' 
          },
        },
        'vu-bounce': {
          '0%, 100%': { height: '10px' },
          '50%': { height: '35px' },
        },
        'slideInRight': {
          'from': { 
            opacity: '0',
            transform: 'translateX(100%)'
          },
          'to': { 
            opacity: '1',
            transform: 'translateX(0)'
          },
        },
        'slideUp': {
          'from': { 
            opacity: '0',
            transform: 'translateY(16px)'
          },
          'to': { 
            opacity: '1',
            transform: 'translateY(0)'
          },
        },
        'fadeIn': {
          'from': { 
            opacity: '0',
            transform: 'translateY(8px)'
          },
          'to': { 
            opacity: '1',
            transform: 'translateY(0)'
          },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        'glitch': {
          '0%, 100%': { 
            transform: 'translate(0)', 
            opacity: '1' 
          },
          '20%': { 
            transform: 'translate(-2px, 2px)', 
            opacity: '0.8' 
          },
          '40%': { 
            transform: 'translate(2px, -2px)', 
            opacity: '0.8' 
          },
          '60%': { 
            transform: 'translate(-2px, -2px)', 
            opacity: '0.8' 
          },
          '80%': { 
            transform: 'translate(2px, 2px)', 
            opacity: '0.8' 
          },
        },
        'scanline': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'vu-bounce': 'vu-bounce 0.5s ease-in-out infinite',
        'slideInRight': 'slideInRight 0.3s ease-out',
        'slideUp': 'slideUp 0.3s ease-out',
        'fadeIn': 'fadeIn 0.3s ease-out',
        'float': 'float 3s ease-in-out infinite',
        'glitch': 'glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both',
        'scanline': 'scanline 8s linear infinite',
      },
    },
  },
  plugins: [],
}

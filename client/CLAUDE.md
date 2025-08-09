# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **FinDocGPT**, a Next.js 15 application built for a hackathon challenge. It's an AI-powered financial analyst tool that combines document analysis, market forecasting, and investment strategy recommendations. The app features a conversational interface with real-time chart generation, processing both FinanceBench dataset documents and live Yahoo Finance data.

## Key Technologies & Dependencies

- **Next.js 15** with App Router and React Server Components
- **React 19** with concurrent features
- **TypeScript** with strict mode enabled
- **Tailwind CSS v4** with PostCSS configuration
- **shadcn/ui** components library (New York style with CSS variables)
- **Zustand** for state management
- **Motion** (Framer Motion) for animations
- **Recharts** for financial data visualizations
- **react-resizable-panels** for split-screen layout
- **Radix UI** primitives for accessible components
- **Lucide React** for icons

## Architecture & Structure

### Core Application Concept

Split-screen conversational financial analyst interface:

- **Left Panel**: Chat interface for AI financial analyst interactions
- **Right Panel**: Dynamic chart canvas that generates visualizations based on conversation context
- **Real-time streaming**: AI responses and chart configurations stream simultaneously

### File Organization

```
src/
├── app/
│   ├── layout.tsx              # Root layout with theme provider
│   ├── page.tsx               # Main dashboard with SplitLayout
│   └── globals.css            # Tailwind imports and custom styles
├── components/
│   ├── ui/                    # shadcn/ui component library
│   ├── chat/
│   │   ├── chat-interface.tsx # Main chat container with streaming logic
│   │   ├── message-list.tsx   # Animated message display
│   │   └── message-input.tsx  # Auto-resizing input with send functionality
│   ├── charts/
│   │   ├── chart-canvas.tsx   # Chart container with tabs and management
│   │   ├── dynamic-chart.tsx  # Recharts wrapper for different chart types
│   │   └── chart-types/       # Specific financial chart components
│   └── layout/
│       └── split-layout.tsx   # Resizable panels layout
├── stores/
│   ├── chat-store.ts          # Zustand store for chat state and streaming
│   └── chart-store.ts         # Zustand store for chart management
├── types/
│   └── index.ts               # TypeScript definitions for Message, ChartConfig, etc.
├── lib/
│   ├── utils.ts               # shadcn/ui cn() utility
│   └── api.ts                 # Backend API client for streaming communication
└── hooks/
    └── use-auto-resize-textarea.ts # Auto-resizing textarea functionality
```

### Data Sources & Integration

- **FinanceBench Dataset**: 10,231 Q&A pairs from SEC filings, earnings reports
- **Yahoo Finance API**: Real-time stock prices, market data, financial metrics
- **Backend API**: Python FastAPI with RAG system, sentiment analysis, forecasting models

### Key Component Architecture

**SplitLayout Component**: Main container using react-resizable-panels

- Resizable horizontal panels with 50/50 default split
- Left: ChatInterface, Right: ChartCanvas
- Responsive design that stacks vertically on mobile

**ChatInterface Component**:

- Streams responses from financial AI backend
- Auto-scrolling message history with animated transitions
- Real-time typing indicators and message updates
- Context-aware conversation management

**ChartCanvas Component**:

- Tabbed interface for multiple visualizations
- Real-time chart generation based on AI analysis
- Interactive chart controls (zoom, export, fullscreen)
- Supports line, bar, pie, area, and scatter charts

**State Management with Zustand**:

- `chat-store.ts`: Messages, streaming state, conversation context
- `chart-store.ts`: Active charts, selected chart, generation status

### API Integration

**Streaming Architecture**:

- Server-Sent Events for real-time AI responses
- Simultaneous text and chart data streaming
- Progressive chart building based on conversation flow
- Error handling and reconnection logic

**Chart Generation Flow**:

1. User asks financial question
2. Backend analyzes query + conversation context
3. AI streams text response while generating chart config
4. Frontend renders chart alongside streaming text
5. Charts update/transform based on follow-up questions

## Development Guidelines

### Component Patterns

- Use server components by default, "use client" for interactive features
- Zustand stores for global state, useState for local component state
- Custom hooks for reusable logic (textarea resizing, API calls)
- Motion components for smooth animations and transitions

### Financial Data Handling

- All monetary values should be properly formatted with currency symbols
- Support for different time ranges (1Y, 6M, 3M, 1M, 1W)
- Percentage changes should include proper +/- indicators
- Handle market hours and weekend data appropriately

### Chart Configuration

- Consistent color scheme across all visualizations
- Responsive charts that work on different screen sizes
- Accessibility features (alt text, keyboard navigation)
- Export functionality for charts (PNG, SVG, data download)

### Styling Conventions

- Tailwind v4 with CSS variables for theming
- Dark/light mode support throughout
- Financial data styling (green for gains, red for losses)
- Consistent spacing and typography for financial metrics

### Performance Considerations

- Virtual scrolling for long chat histories
- Debounced chart updates to prevent excessive re-renders
- Lazy loading for heavy chart components
- Proper cleanup of streaming connections

## Common Development Commands

```bash
# Development server with Turbopack
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Lint code
npm run lint
```

## Backend Integration

- **API Base URL**: `http://localhost:8000` (configurable via env)
- **Streaming Endpoint**: `/api/analyze/stream`
- **Request Format**: `{ message: string, context: Message[] }`
- **Response Format**: Server-Sent Events with `data:` prefix

## Hackathon Development Phases

1. **Stage 1**: Document Q&A with FinanceBench dataset
2. **Stage 2**: Real-time market data integration with Yahoo Finance
3. **Stage 3**: Investment strategy recommendations and buy/sell signals

## File Path References

- Main layout: `components/layout/split-layout.tsx`
- Chat interface: `components/chat/chat-interface.tsx`
- Chart canvas: `components/charts/chart-canvas.tsx`
- Chat state: `stores/chat-store.ts`
- Chart state: `stores/chart-store.ts`
- API client: `lib/api.ts`
- Type definitions: `types/index.ts`

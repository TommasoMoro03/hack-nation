**Frontend Implementation Instructions for Claude Code:**

## Project Setup and Structure

Create a Next.js 14 application with TypeScript and Tailwind CSS. The main goal is to build a financial AI analyst interface with a split-screen layout where users chat with an AI on the left side and see dynamically generated charts on the right side based on the conversation.

## Core Application Architecture

Build the main layout as a split-screen interface with two equal-width panels. The left panel contains the chat interface where users interact with the AI financial analyst. The right panel contains a dynamic visualization canvas that displays charts and graphs generated in response to the conversation.

Use React hooks for state management to track chat messages, active visualizations, streaming states, and current analysis context. Implement real-time streaming responses where the AI responses appear word-by-word and charts animate in as the AI talks about financial data.

## Chat Interface Component

Create a chat interface component that displays a conversation history with user messages and AI responses. Include an input field at the bottom for typing new messages. Implement auto-scrolling to keep the latest messages visible. Add typing indicators when the AI is responding.

Handle streaming responses by making API calls to the backend and processing the response stream chunk by chunk. As text chunks arrive, append them to the current AI message in real-time. When chart configuration chunks arrive, trigger chart generation in the visualization panel.

Store the complete conversation history and pass it as context with each new message to maintain conversation continuity. Style messages differently for user and AI with appropriate spacing and visual hierarchy.

## Visualization Canvas Component

Build a dynamic chart container that can display multiple types of financial visualizations including line charts for price trends, bar charts for comparisons, and pie charts for portfolio breakdowns. Use Recharts library for all chart implementations.

Implement chart animations and smooth transitions when data updates or when switching between different chart types. Charts should respond to conversation context - for example, when the AI mentions specific metrics, highlight those data points on existing charts.

Create a chart generation system that takes configuration objects from the backend and renders appropriate chart components. Support chart transformations like converting a single company chart to a comparison chart when users ask to compare multiple companies.

## Real-Time Communication

Implement Server-Sent Events or WebSocket connection to handle streaming responses from the backend. Process incoming data streams to separate text content from chart configurations. Update the UI progressively as data arrives rather than waiting for complete responses.

Handle different types of streaming data including partial text updates, complete chart configurations, and metadata about the analysis being performed. Maintain responsive UI during streaming with appropriate loading states.

## State Management Structure

Use React Context or Zustand for global state management. Track current conversation messages, active visualizations, selected companies or stocks, streaming status, and partial message content during streaming responses.

Implement context awareness where charts remember previous conversation topics and can build upon existing visualizations rather than replacing them entirely. Store chart history to allow users to refer back to previous analyses.

## User Interaction Patterns

Support progressive conversation flows where users can ask follow-up questions that modify existing charts. For example, after showing Apple's revenue, allow "compare with Microsoft" to add Microsoft data to the existing chart rather than creating a new one.

Implement voice-like interaction patterns where charts respond to natural language. When the AI says "as you can see in Q3" highlight Q3 data points. When mentioning specific metrics, emphasize those areas of charts.

## Responsive Design and Performance

Make the interface responsive by stacking the chat and visualization panels vertically on mobile devices. Implement virtual scrolling for chat messages to handle long conversations efficiently.

Optimize chart rendering performance by debouncing rapid updates and using React.memo for chart components. Implement proper cleanup for streaming connections and chart animations.

## Integration Points

Create API integration functions to communicate with the Python FastAPI backend. Send user messages along with conversation context to maintain continuity. Handle both regular HTTP requests and streaming responses appropriately.

Implement error handling for network issues, streaming interruptions, and invalid chart configurations. Provide fallback UI states when charts cannot be generated or when the backend is unavailable.

The final result should feel like chatting with a human financial analyst who can instantly generate relevant charts and visualizations as they explain financial concepts and data analysis.

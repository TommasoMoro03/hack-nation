import { create } from "zustand";
import type { Message } from "@/lib/types";

interface ChatState {
	messages: Message[];
	isStreaming: boolean;
	currentStreamingId: string | null;
}

interface ChatActions {
	addMessage: (message: Omit<Message, "id" | "timestamp">) => string;
	updateMessage: (id: string, updates: Partial<Message>) => void;
	setStreaming: (isStreaming: boolean, messageId?: string) => void;
	clearMessages: () => void;
}

export const useChatStore = create<ChatState & ChatActions>((set) => ({
	// State
	messages: [
		{
			id: "welcome",
			role: "assistant",
			content:
				"Hello! I'm your AI financial analyst. I can help you analyze financial documents, market data, and provide investment insights. What would you like to explore today?",
			timestamp: new Date(),
		},
	],
	isStreaming: false,
	currentStreamingId: null,

	// Pure state actions only
	addMessage: (message) => {
		const id = crypto.randomUUID();
		const newMessage: Message = {
			...message,
			id,
			timestamp: new Date(),
		};
		set((state) => ({
			messages: [...state.messages, newMessage],
		}));
		return id;
	},

	updateMessage: (id, updates) => {
		set((state) => ({
			messages: state.messages.map((msg) =>
				msg.id === id ? { ...msg, ...updates } : msg
			),
		}));
	},

	setStreaming: (isStreaming, messageId) => {
		set({
			isStreaming,
			currentStreamingId: messageId || null,
		});
	},

	clearMessages: () => {
		set({
			messages: [],
			isStreaming: false,
			currentStreamingId: null,
		});
	},
}));

import React, { useEffect, useRef } from "react";
import Hero from "../hero";
import Features from "../features";
import AiPrompt from "../ai-prompt";
import { useChatStore } from "@/lib/stores/chat-store";
import { ScrollArea } from "../ui/scroll-area";
import { MessageList } from "./message-list";
import ChatHeader from "./chat-header";
import Footer from "../footer";

interface ChatInterfaceProps {
	centered?: boolean;
}

function ChatInterface({ centered = false }: ChatInterfaceProps) {
	const { messages } = useChatStore();
	const scrollAreaRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (scrollAreaRef.current) {
			// Target the actual viewport inside ScrollArea
			const viewport = scrollAreaRef.current.querySelector(
				"[data-radix-scroll-area-viewport]"
			) as HTMLElement;
			if (viewport) {
				viewport.scrollTop = viewport.scrollHeight;
			}
		}
	}, [messages]);

	if (messages.length <= 1 && centered) {
		return <WelcomeScreen />;
	}

	return (
		<div className="flex flex-col h-screen">
			<ChatHeader />
			<ScrollArea
				ref={scrollAreaRef}
				className="w-full px-4 overflow-y-auto flex-1">
				<div className="mt-4" />
				<MessageList messages={messages} />
			</ScrollArea>
			<div className="sticky bottom-0 w-full pt-4 px-4">
				<AiPrompt />
			</div>
		</div>
	);
}

const WelcomeScreen = () => {
	return (
		<div className="flex flex-col mt-40 w-full max-w-3xl p-4">
			<Hero />
			<Features />
			<AiPrompt />
			{/* <AiResult /> */}
			<div className="p-40" />
			<Footer />
		</div>
	);
};

export { ChatInterface };

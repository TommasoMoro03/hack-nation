"use client";

import {
	ArrowRight,
	ChevronDown,
	StopCircle,
	TrendingUpDown,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useAutoResizeTextarea } from "@/hooks/use-auto-resize-textarea";
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { motion, AnimatePresence } from "motion/react";
import { FileUploadDialog } from "./file-upload-dialog";
import { SelectedFilesDisplay } from "./selected-files-display";
import { useIsMobile } from "@/hooks/use-mobile";
import { useChartStore } from "@/lib/stores/chart-store";
import { useChatStore } from "@/lib/stores/chat-store";
import { experimental_useObject as useObject } from "@ai-sdk/react";
import { handleChartUpdates, responseSchema } from "@/lib/types";
import { toast } from "sonner";
import { useFileStore } from "@/lib/stores/file-store";

export default function AiPrompt() {
	const [prompt, setPrompt] = useState("");
	const [messageId, setMessageId] = useState<string | null>(null);
	const { textareaRef, adjustHeight } = useAutoResizeTextarea({
		minHeight: 72,
		maxHeight: 300,
	});
	const [selectedModel] = useState("GPT-4-1 Mini");
	const isMobile = useIsMobile();
	const { addMessage, messages, updateMessage, isStreaming, setStreaming } =
		useChatStore();
	const { addChart, isGenerating, setGenerating } = useChartStore();
	const { uploadedFiles } = useFileStore();

	const { object, submit, isLoading, stop } = useObject({
		id: "ai-prompt",
		api: "http://localhost:8000/api/chat",
		schema: responseSchema,
		onError: (err) => {
			console.error("Error occurred:", err);
			toast.error("An error occurred while processing your request.");
		},
		onFinish: () => {
			console.log("Message Response finished");
			setGenerating(false);
			setStreaming(false);
			setMessageId(null);
		},
	});

	useEffect(() => {
		if (isLoading) {
			if (!isGenerating) {
				setGenerating(true);
			}
			if (!isStreaming) {
				setStreaming(true);
			}
		}
	}, [isGenerating, isLoading, isStreaming, setGenerating, setStreaming]);

	useEffect(() => {
		if (!object?.content) return;
		console.log(
			"Messages are: ",
			messages.map((msg) => msg.id)
		);

		if (!messageId) {
			// Create assistant message
			const newMessageId = addMessage({
				role: "assistant",
				content: object.content,
			});
			console.log("New message ID:", newMessageId);
			if (newMessageId === "") {
				return;
			}
			setMessageId(newMessageId);
		} else {
			// Update existing assistant message
			updateMessage(messageId, {
				role: "assistant",
				content: object.content,
			});
		}
	}, [addMessage, messageId, object?.content, setMessageId, updateMessage]);

	// Handle chart updates
	useEffect(() => {
		if (object?.charts) {
			handleChartUpdates(object.charts, addChart, (_, updatedChart) => {
				useChartStore.getState().updateChart(updatedChart.id, updatedChart);
			});
		}
	}, [addChart, object?.charts]);

	const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
			e.preventDefault();
			if (prompt.trim() && !isLoading) {
				handleSubmit(e);
			}
			return;
		}
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			setPrompt(prompt + "\n");
			adjustHeight(true);
		}
	};

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (prompt.trim() && !isLoading) {
			addMessage({
				role: "user",
				content: prompt.trim(),
			});
			setPrompt("");
			submit({
				prompt: prompt.trim(),
				files: uploadedFiles.map((file) => file.name),
			});
		} else if (isLoading) {
			stop();
		}
	};

	return (
		<motion.div
			initial={{ opacity: 0, y: 30 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ duration: 0.6 }}
			className="w-full pb-4">
			{/* Outer Shape */}
			<div className="bg-black/5 dark:bg-white/5 rounded-xl p-1.5">
				<div className="flex items-center gap-2 mb-2.5 mx-2 mt-2 ">
					<div className="flex-1 flex items-center gap-2 ">
						<h3 className="text-xs tracking-tighter">
							Forecast your next breakthrough!
						</h3>
						<TrendingUpDown className="w-4 h-4 text-blue-500" />
					</div>
					<div className="ml-auto flex items-center gap-2">
						<p className="text-xs tracking-tighter">Predict and Analyze</p>
					</div>
				</div>
				{/* Inner Textarea */}
				<div className="relative flex flex-col">
					{/* Actual Text Area */}
					<div
						className="overflow-y-auto"
						style={{ maxHeight: "400px" }}>
						<Textarea
							id="ai-input-15"
							value={prompt}
							placeholder={
								!isMobile
									? "Ask about market trends, financial forecasts, stock analysis, or upload financial data for insights..."
									: "Type your message..."
							}
							className={cn(
								"w-full rounded-xl rounded-b-none px-4 py-3 bg-black/5 dark:bg-white/5 border-none dark:text-white placeholder:text-black/70 dark:placeholder:text-white/70 resize-none focus-visible:ring-0 focus-visible:ring-offset-0",
								"min-h-[72px]"
							)}
							ref={textareaRef}
							onKeyDown={handleKeyDown}
							onChange={(e) => {
								setPrompt(e.target.value);
								adjustHeight();
							}}
						/>
					</div>
					<SelectedFilesDisplay className=" bg-black/5 dark:bg-white/5 pl-3" />
					{/* Tool bar */}
					<div className="h-14 bg-black/5 dark:bg-white/5 rounded-b-xl flex items-center">
						<div className="absolute left-3 right-3 bottom-3 flex items-center justify-between w-[calc(100%-24px)]">
							<div className="flex items-center gap-2">
								<DropdownMenu>
									<DropdownMenuTrigger asChild>
										<Button
											variant="ghost"
											className="flex items-center gap-1 h-8 pl-1 pr-2 text-xs rounded-md dark:text-white hover:bg-black/10 dark:hover:bg-white/10 focus-visible:ring-1 focus-visible:ring-offset-0 focus-visible:ring-blue-500">
											<AnimatePresence mode="wait">
												<motion.div
													key={selectedModel}
													initial={{
														opacity: 0,
														y: -5,
													}}
													animate={{
														opacity: 1,
														y: 0,
													}}
													exit={{
														opacity: 0,
														y: 5,
													}}
													transition={{
														duration: 0.15,
													}}
													className="flex items-center gap-1">
													{selectedModel}
													<ChevronDown className="w-3 h-3 opacity-50" />
												</motion.div>
											</AnimatePresence>
										</Button>
									</DropdownMenuTrigger>
									<DropdownMenuContent
										className={cn(
											"min-w-[10rem]",
											"border-black/10 dark:border-white/10",
											"bg-gradient-to-b from-white via-white to-neutral-100 dark:from-neutral-950 dark:via-neutral-900 dark:to-neutral-800"
										)}></DropdownMenuContent>
								</DropdownMenu>
								<div className="h-4 w-px bg-black/10 dark:bg-white/10 mx-0.5" />
								<FileUploadDialog />
							</div>
							<button
								type="button"
								className={cn(
									"rounded-lg p-2 bg-black/5 dark:bg-white/5",
									"hover:bg-black/10 dark:hover:bg-white/10 focus-visible:ring-1 focus-visible:ring-offset-0 focus-visible:ring-blue-500"
								)}
								onClick={handleSubmit}
								aria-label="Send message"
								disabled={!prompt.trim() || isLoading}>
								{isLoading ? (
									<StopCircle className="w-4 h-4 transition-opacity duration-200" />
								) : (
									<ArrowRight
										className={cn(
											"w-4 h-4 dark:text-white transition-opacity duration-200",
											prompt.trim() ? "opacity-100" : "opacity-30"
										)}
									/>
								)}
							</button>
						</div>
					</div>
				</div>
			</div>
		</motion.div>
	);
}

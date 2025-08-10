"use client";

import { type Message } from "@/lib/types";
import { motion, AnimatePresence } from "framer-motion";
import { User, TrendingUp, FileText, Paperclip } from "lucide-react";
import { cn } from "@/lib/utils";
import { MemoizedMarkdown } from "../memoized-markdown";

interface MessageListProps {
	messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
	return (
		<div className="space-y-4">
			<AnimatePresence>
				{messages.map((message, index) => (
					<motion.div
						key={message.id}
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						exit={{ opacity: 0, y: -20 }}
						transition={{ duration: 0.3, delay: index * 0.1 }}
						className={cn(
							"flex gap-3 p-3 rounded-lg",
							message.role === "user"
								? "bg-primary/10 ml-8"
								: "bg-muted/50 mr-8"
						)}>
						<div
							className={cn(
								"w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
								message.role === "user"
									? "bg-primary text-primary-foreground"
									: "bg-secondary text-secondary-foreground"
							)}>
							{message.role === "user" ? (
								<User className="w-4 h-4" />
							) : (
								<TrendingUp className="w-4 h-4" />
							)}
						</div>

						<div className="flex-1 min-w-0">
							<div className="flex items-center gap-2 mb-3">
								<span className="text-sm font-medium">
									{message.role === "user" ? "You" : "FinDocGPT"}
								</span>
								<span className="text-xs text-muted-foreground">
									{message.timestamp.toLocaleTimeString()}
								</span>
							</div>

							<div className="text-sm text-foreground whitespace-pre-wrap prose">
								{message.attachedFiles && message.attachedFiles.length > 0 && (
									<div className="mb-3 p-2 bg-muted/30 rounded border-l-2 border-primary">
										<div className="flex items-center gap-2 mb-2 text-xs text-muted-foreground">
											<Paperclip className="w-3 h-3" />
											<span>Attached Documents:</span>
										</div>
										<div className="space-y-1">
											{message.attachedFiles.map((file) => (
												<div
													key={file.id}
													className="flex items-center gap-2 text-xs">
													<FileText className="w-3 h-3" />
													<span className="truncate">{file.name}</span>
													<span className="text-muted-foreground">
														({(file.size / 1024 / 1024).toFixed(1)} MB)
													</span>
												</div>
											))}
										</div>
									</div>
								)}
								<MemoizedMarkdown
									content={message.content}
									id={message.id}
								/>
								{message.isStreaming && (
									<motion.span
										animate={{ opacity: [1, 0] }}
										transition={{
											duration: 0.8,
											repeat: Number.POSITIVE_INFINITY,
										}}
										className="inline-block w-2 h-4 bg-primary ml-1"
									/>
								)}
							</div>
						</div>
					</motion.div>
				))}
			</AnimatePresence>
		</div>
	);
}

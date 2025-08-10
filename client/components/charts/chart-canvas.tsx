/* eslint-disable react/display-name */
"use client";

import { DynamicChart } from "./dynamic-chart";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
	BarChart3,
	LineChart,
	PieChart,
	TrendingUp,
	Download,
	Sparkles,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useChartStore } from "@/lib/stores/chart-store";
import { ScrollArea } from "../ui/scroll-area";
import React from "react";
import { useChatStore } from "@/lib/stores/chat-store";

export function ChartCanvas() {
	const { charts, isGenerating } = useChartStore();
	const { isStreaming } = useChatStore();

	const getChartIcon = (type: string) => {
		switch (type) {
			case "line":
				return <LineChart className="w-4 h-4" />;
			case "bar":
				return <BarChart3 className="w-4 h-4" />;
			case "pie":
				return <PieChart className="w-4 h-4" />;
			default:
				return <TrendingUp className="w-4 h-4" />;
		}
	};

	const ChartSkeleton = () => (
		<Card>
			<CardHeader className="pb-2">
				<CardTitle className="text-base flex items-center gap-2">
					<Skeleton className="w-4 h-4 rounded" />
					<Skeleton className="h-4 w-32" />
				</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="space-y-3">
					<Skeleton className="h-6 w-full" />
					<Skeleton className="h-64 w-full" />
					<div className="flex gap-2">
						<Skeleton className="h-4 w-16" />
						<Skeleton className="h-4 w-20" />
						<Skeleton className="h-4 w-24" />
					</div>
				</div>
			</CardContent>
		</Card>
	);

	const GeneratingState = React.memo(() => (
		<motion.div
			initial={{ opacity: 0, scale: 0.9 }}
			animate={{ opacity: 1, scale: 1 }}
			exit={{ opacity: 0, scale: 0.9 }}
			className="flex items-center justify-center h-full">
			<div className="text-center space-y-6 max-w-md">
				<motion.div
					animate={{ rotate: 360 }}
					transition={{
						duration: 2,
						repeat: Number.POSITIVE_INFINITY,
						ease: "linear",
					}}
					className="w-16 h-16 rounded-full bg-gradient-to-r from-primary to-primary/60 flex items-center justify-center mx-auto">
					<Sparkles className="w-8 h-8 text-primary-foreground" />
				</motion.div>

				<div>
					<h3 className="text-xl font-semibold mb-2">
						Generating Visualization
					</h3>
					<p className="text-muted-foreground text-sm">
						Analyzing your data and creating interactive charts...
					</p>
				</div>

				<motion.div
					initial={{ width: 0 }}
					animate={{ width: "100%" }}
					transition={{ duration: 3, ease: "easeInOut" }}
					className="h-1 bg-gradient-to-r from-primary to-primary/60 rounded-full mx-auto"
				/>
			</div>
		</motion.div>
	));

	const EmptyState = () => (
		<motion.div
			initial={{ opacity: 0, y: 20 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ duration: 0.6 }}
			className="h-full flex items-center justify-center bg-muted/20 mt-40">
			<div className="text-center space-y-4 max-w-md">
				<motion.div
					initial={{ scale: 0.8 }}
					animate={{ scale: 1 }}
					transition={{ duration: 0.5, delay: 0.2 }}
					className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
					<TrendingUp className="w-8 h-8 text-primary" />
				</motion.div>
				<div>
					<h3 className="text-lg font-semibold mb-2">Chart Canvas</h3>
					<p className="text-muted-foreground text-sm">
						Interactive visualizations will appear here as you chat with the AI
						analyst.
					</p>
				</div>
				<div className="flex flex-wrap gap-2 justify-center">
					<Badge variant="secondary">Real-time Data</Badge>
					<Badge variant="secondary">Interactive Charts</Badge>
					<Badge variant="secondary">Export Ready</Badge>
				</div>
			</div>
		</motion.div>
	);

	return (
		<div className="h-full flex flex-col bg-card">
			{/* Header */}
			<motion.div
				initial={{ opacity: 0, y: -10 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ duration: 0.4, delay: 0.3 }}
				className="p-4 border-b border-border bg-card/50 backdrop-blur">
				<div className="flex items-center justify-between">
					<h2 className="font-semibold text-sm">Financial Charts</h2>
					<div className="flex items-center gap-2">
						{isGenerating && (
							<motion.div
								animate={{ rotate: 360 }}
								transition={{
									duration: 2,
									repeat: Number.POSITIVE_INFINITY,
									ease: "linear",
								}}>
								<Sparkles className="w-4 h-4 text-primary" />
							</motion.div>
						)}
						{charts.some((chart) => !chart) && (
							<Button
								variant="ghost"
								size="sm">
								<Download className="w-4 h-4" />
							</Button>
						)}
					</div>
				</div>
			</motion.div>

			{/* Content */}
			<div className="flex-1 p-4">
				<ScrollArea className="h-screen">
					<AnimatePresence mode="wait">
						{!isGenerating && isStreaming ? (
							<GeneratingState />
						) : charts.length === 0 && !isGenerating ? (
							<EmptyState key="empty" />
						) : (
							<motion.div
								key="charts"
								className="space-y-4 mr-4 mb-20"
								initial={{ opacity: 0, y: 20 }}
								animate={{ opacity: 1, y: 0 }}
								exit={{ opacity: 0, y: -20 }}
								transition={{ duration: 0.4 }}>
								{charts.map((chart) => (
									<motion.div
										key={chart.id}
										initial={{ opacity: 0, y: 20 }}
										animate={{ opacity: 1, y: 0 }}
										transition={{ duration: 0.3 }}>
										{!chart ? (
											<ChartSkeleton />
										) : (
											<Card>
												<CardHeader className="pb-2">
													<CardTitle className="text-base flex items-center gap-2">
														{getChartIcon(chart.type)}
														{chart.title}
													</CardTitle>
												</CardHeader>
												<CardContent>
													<DynamicChart config={chart} />
												</CardContent>
											</Card>
										)}
									</motion.div>
								))}

								{/* Show additional loading skeleton if more charts are being generated */}
								{isGenerating && (
									<motion.div
										initial={{ opacity: 0, y: 20 }}
										animate={{ opacity: 1, y: 0 }}
										transition={{ duration: 0.3 }}>
										<ChartSkeleton />
									</motion.div>
								)}
							</motion.div>
						)}
					</AnimatePresence>
				</ScrollArea>
			</div>
		</div>
	);
}

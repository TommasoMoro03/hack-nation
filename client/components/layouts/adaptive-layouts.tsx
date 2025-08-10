"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { ChatInterface } from "@/components/chat/chat-interface";
import { ChartCanvas } from "@/components/charts/chart-canvas";
import { useLayoutStore } from "@/lib/stores/layout-store";
import { useChartStore } from "@/lib/stores/chart-store";
import { GripVertical } from "lucide-react";

export function AdaptiveLayout() {
	const { isSplitView, setSplitView, setAnimating } = useLayoutStore();
	const { charts, isGenerating } = useChartStore();

	// Trigger split view when chart generation starts or charts exist
	useEffect(() => {
		const shouldSplit = isGenerating || charts.length > 0;

		if (shouldSplit && !isSplitView) {
			setAnimating(true);
			// Small delay to ensure smooth animation
			setTimeout(() => {
				setSplitView(true);
				setTimeout(() => setAnimating(false), 800); // Match animation duration
			}, 100);
		}
	}, [isGenerating, charts.length, isSplitView, setSplitView, setAnimating]);

	if (!isSplitView) {
		return (
			<main>
				<ChatInterface centered />
			</main>
		);
	}

	return (
		<main className="w-full">
			<motion.div
				initial={{ opacity: 0 }}
				animate={{ opacity: 1 }}
				transition={{ duration: 0.4, delay: 0.2 }}
				className="h-screen bg-background">
				<PanelGroup
					direction="horizontal"
					className="h-full">
					<Panel
						defaultSize={50}
						minSize={30}>
						<motion.div
							initial={{ x: "-50%", opacity: 0 }}
							animate={{ x: 0, opacity: 1 }}
							transition={{ duration: 0.6, ease: "easeOut" }}
							className="h-full border-r border-border">
							<ChatInterface />
						</motion.div>
					</Panel>

					<PanelResizeHandle className="w-2 bg-border hover:bg-accent transition-colors relative group">
						<div className="absolute inset-y-0 left-1/2 w-1 -translate-x-1/2 bg-border group-hover:bg-primary transition-colors" />
						<GripVertical className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
					</PanelResizeHandle>

					<Panel
						defaultSize={50}
						minSize={30}>
						<motion.div
							initial={{ x: "50%", opacity: 0 }}
							animate={{ x: 0, opacity: 1 }}
							transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
							className="h-full">
							<ChartCanvas />
						</motion.div>
					</Panel>
				</PanelGroup>
			</motion.div>
		</main>
	);
}

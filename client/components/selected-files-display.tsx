"use client";

import { FileText, X } from "lucide-react";
import { useFileStore } from "@/lib/stores/file-store";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface SelectedFilesDisplayProps {
	className?: string;
}

export function SelectedFilesDisplay({ className }: SelectedFilesDisplayProps) {
	const { uploadedFiles, selectedFiles, deselectFile } = useFileStore();

	// Get the actual file objects for selected files
	const selectedFileObjects = uploadedFiles.filter(
		(file) => selectedFiles.includes(file.id) && file.status === "ready"
	);

	if (selectedFileObjects.length === 0) {
		return null;
	}

	const handleRemoveFile = (fileId: string) => {
		deselectFile(fileId);
	};

	// Show only first 3 files, then show count for the rest
	const maxDisplayFiles = 3;
	const displayFiles = selectedFileObjects.slice(0, maxDisplayFiles);
	const remainingCount = selectedFileObjects.length - maxDisplayFiles;

	return (
		<div className={cn("flex items-center gap-2 flex-wrap", className)}>
			<AnimatePresence>
				{displayFiles.map((file) => (
					<motion.div
						key={file.id}
						initial={{ opacity: 0, scale: 0.95, x: -10 }}
						animate={{ opacity: 1, scale: 1, x: 0 }}
						exit={{ opacity: 0, scale: 0.95, x: -10 }}
						transition={{ duration: 0.15 }}
						className={cn(
							"flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg",
							"bg-blue-50 dark:bg-blue-950/30",
							"border border-blue-200 dark:border-blue-800",
							"text-blue-700 dark:text-blue-300",
							"text-xs font-medium",
							"max-w-[200px]"
						)}>
						<FileText className="w-3.5 h-3.5 flex-shrink-0" />
						<span
							className="truncate"
							title={file.name}>
							{file.name}
						</span>
						<Button
							variant="ghost"
							size="sm"
							className="h-4 w-4 p-0 hover:bg-blue-100 dark:hover:bg-blue-900/50"
							onClick={() => handleRemoveFile(file.id)}
							aria-label={`Remove ${file.name}`}>
							<X className="w-3 h-3" />
						</Button>
					</motion.div>
				))}
			</AnimatePresence>

			{remainingCount > 0 && (
				<motion.div
					initial={{ opacity: 0, scale: 0.95 }}
					animate={{ opacity: 1, scale: 1 }}
					className={cn(
						"px-2.5 py-1.5 rounded-lg",
						"bg-gray-100 dark:bg-gray-800",
						"border border-gray-200 dark:border-gray-700",
						"text-gray-600 dark:text-gray-400",
						"text-xs font-medium"
					)}
					title={`${remainingCount} more file${
						remainingCount === 1 ? "" : "s"
					} selected`}>
					+{remainingCount} more
				</motion.div>
			)}
		</div>
	);
}

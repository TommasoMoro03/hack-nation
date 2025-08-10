"use client";

import type React from "react";

import { useState, useCallback } from "react";
import { useFileStore } from "@/lib/stores/file-store";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import {
	FileText,
	Trash2,
	Check,
	AlertCircle,
	Loader2,
	Download,
	Eye,
	Plus,
	Paperclip,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { UploadedFile } from "@/lib/types";
import FileUpload from "./dnd-file-upload";
import { toast } from "sonner";

interface FileUploadDialogProps {
	children?: React.ReactNode;
}

export function FileUploadDialog({ children }: FileUploadDialogProps) {
	const [open, setOpen] = useState(false);
	const [activeTab, setActiveTab] = useState("upload");

	const {
		uploadedFiles,
		selectedFiles,
		uploadProgress,
		addFile,
		updateFile,
		removeFile,
		selectFile,
		deselectFile,
		clearSelectedFiles,
		setUploadProgress,
		clearUploadProgress,
		setUploading,
	} = useFileStore();

	const handleFiles = async (files: File[]) => {
		setUploading(true);

		for (const file of files) {
			const fileId = Math.random().toString(36).substr(2, 9);

			// Create file record
			const uploadedFile: UploadedFile = {
				id: fileId,
				name: file.name,
				size: file.size,
				type: file.type,
				uploadDate: new Date(),
				status: "uploading",
			};

			addFile(uploadedFile);

			// Simulate upload progress
			setUploadProgress(fileId, {
				fileId,
				progress: 0,
				status: "uploading",
			});

			// Simulate upload process
			for (let progress = 0; progress <= 100; progress += 10) {
				await new Promise((resolve) => setTimeout(resolve, 100));
				setUploadProgress(fileId, {
					fileId,
					progress,
					status: progress === 100 ? "processing" : "uploading",
				});
			}

			// Simulate processing
			updateFile(fileId, { status: "processing" });
			await new Promise((resolve) => setTimeout(resolve, 1500));

			// Complete upload
			updateFile(fileId, {
				status: "ready",
				url: URL.createObjectURL(file),
				extractedText: "Sample extracted text from PDF...",
				summary: "This document contains financial information and analysis.",
			});

			clearUploadProgress(fileId);
		}

		setUploading(false);
		setActiveTab("select");
	};

	const handleFileUploadSuccess = useCallback((file: File) => {
		handleFiles([file]);
		toast.success("File uploaded successfully!");
	}, []);

	const handleFileUploadError = useCallback(
		(error: { message: string; code: string }) => {
			console.error("File upload error:", error);
		},
		[]
	);

	const handleRemoveFile = useCallback(
		(fileId: string) => {
			// Remove file from store
			removeFile(fileId);
			// Clear any remaining upload progress for this file
			clearUploadProgress(fileId);
		},
		[removeFile, clearUploadProgress]
	);

	const handleCloseDialog = useCallback(
		(isOpen: boolean) => {
			setOpen(isOpen);
			if (!isOpen) {
				// Clear all upload progress when closing dialog
				Object.keys(uploadProgress).forEach((fileId) => {
					clearUploadProgress(fileId);
				});
			}
		},
		[uploadProgress, clearUploadProgress]
	);

	const formatFileSize = (bytes: number) => {
		if (bytes === 0) return "0 Bytes";
		const k = 1024;
		const sizes = ["Bytes", "KB", "MB", "GB"];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return (
			Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
		);
	};

	const getStatusIcon = (status: UploadedFile["status"]) => {
		switch (status) {
			case "uploading":
				return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
			case "processing":
				return <Loader2 className="w-4 h-4 animate-spin text-yellow-500" />;
			case "ready":
				return <Check className="w-4 h-4 text-green-500" />;
			case "error":
				return <AlertCircle className="w-4 h-4 text-red-500" />;
			default:
				return <FileText className="w-4 h-4" />;
		}
	};

	const getStatusBadge = (status: UploadedFile["status"]) => {
		const variants = {
			uploading: "default",
			processing: "secondary",
			ready: "default",
			error: "destructive",
		} as const;

		const labels = {
			uploading: "Uploading",
			processing: "Processing",
			ready: "Ready",
			error: "Error",
		};

		return (
			<Badge
				variant={variants[status as keyof typeof variants]}
				className="text-xs">
				{labels[status as keyof typeof labels]}
			</Badge>
		);
	};

	const handleApplySelection = () => {
		// Here you would typically update the chat context with selected files
		console.log("Selected files for chat:", selectedFiles);
		handleCloseDialog(false);
	};

	return (
		<Dialog
			open={open}
			onOpenChange={handleCloseDialog}>
			<DialogTrigger asChild>
				{children || (
					<label
						className={cn(
							"rounded-lg p-2 bg-black/5 dark:bg-white/5 cursor-pointer",
							"hover:bg-black/10 dark:hover:bg-white/10 focus-visible:ring-1 focus-visible:ring-offset-0 focus-visible:ring-blue-500",
							"text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white"
						)}
						aria-label="Attach file">
						<Paperclip className="w-4 h-4 transition-colors" />
					</label>
				)}
			</DialogTrigger>
			<DialogContent className="md:min-w-2xl max-h-[80vh] flex flex-col">
				<DialogHeader>
					<DialogTitle>Document Management</DialogTitle>
					<DialogDescription>
						Upload PDF documents or select from previously uploaded files for
						analysis.
					</DialogDescription>
				</DialogHeader>

				<Tabs
					value={activeTab}
					onValueChange={setActiveTab}
					className="flex-1 flex flex-col">
					<TabsList className="grid w-full grid-cols-2">
						<TabsTrigger
							value="upload"
							className="flex items-center gap-2">
							<Plus className="w-4 h-4" />
							Upload New Files
						</TabsTrigger>
						<TabsTrigger
							value="select"
							className="flex items-center gap-2">
							<FileText className="w-4 h-4" />
							Select Files ({uploadedFiles.length})
						</TabsTrigger>
					</TabsList>

					<TabsContent
						value="upload"
						className="flex-1 flex flex-col">
						<FileUpload
							onUploadSuccess={handleFileUploadSuccess}
							onUploadError={handleFileUploadError}
							acceptedFileTypes={["application/pdf"]}
							maxFileSize={10 * 1024 * 1024} // 10MB
							uploadDelay={2000}
							className="w-full max-w-none"
						/>

						{Object.keys(uploadProgress).length > 0 && (
							<div className="mt-4 space-y-3">
								<h4 className="font-medium">Upload Progress</h4>
								{Object.values(uploadProgress).map((progress) => {
									const file = uploadedFiles.find(
										(f) => f.id === progress.fileId
									);
									return (
										<div
											key={progress.fileId}
											className="space-y-2">
											<div className="flex items-center justify-between text-sm">
												<span className="truncate">{file?.name}</span>
												<span>{progress.progress}%</span>
											</div>
											<Progress
												value={progress.progress}
												className="h-2"
											/>
										</div>
									);
								})}
							</div>
						)}
					</TabsContent>

					<TabsContent
						value="select"
						className="flex-1 flex flex-col">
						<div className="flex items-center justify-between mb-4">
							<div className="flex items-center gap-2">
								<span className="text-sm text-muted-foreground">
									{selectedFiles.length} of {uploadedFiles.length} files
									selected
								</span>
								{selectedFiles.length > 0 && (
									<Button
										variant="ghost"
										size="sm"
										onClick={clearSelectedFiles}
										className="h-6 px-2 text-xs">
										Clear All
									</Button>
								)}
							</div>
							<Badge
								variant="secondary"
								className="text-xs">
								{uploadedFiles.filter((f) => f.status === "ready").length} Ready
							</Badge>
						</div>

						<ScrollArea className="h-[400px] md:h-[600px] pr-3">
							<div className="space-y-3">
								{uploadedFiles.map((file) => (
									<div
										key={file.id}
										onClick={() => {
											if (file.status === "ready") {
												if (selectedFiles.includes(file.id)) {
													deselectFile(file.id);
												} else {
													selectFile(file.id);
												}
											}
										}}
										className={cn(
											"border rounded-lg p-4 transition-colors",
											selectedFiles.includes(file.id)
												? "border-primary bg-primary/5"
												: "border-border hover:border-muted-foreground/50"
										)}>
										<div className="flex items-start gap-3">
											<Checkbox
												checked={selectedFiles.includes(file.id)}
												onCheckedChange={(checked) => {
													if (checked) {
														selectFile(file.id);
													} else {
														deselectFile(file.id);
													}
												}}
												disabled={file.status !== "ready"}
												className="mt-1"
											/>

											<div className="flex-1 min-w-0">
												<div className="flex items-center gap-2 mb-2">
													{getStatusIcon(file.status)}
													<h4 className="font-medium truncate">{file.name}</h4>
													{getStatusBadge(file.status)}
												</div>

												<div className="flex items-center gap-4 text-xs text-muted-foreground mb-2">
													<span>{formatFileSize(file.size)}</span>
													<span>
														{new Date(file.uploadDate).toLocaleDateString()}
													</span>
												</div>

												{file.summary && (
													<p className="text-sm text-muted-foreground line-clamp-2">
														{file.summary}
													</p>
												)}
											</div>

											<div className="flex items-center gap-1">
												{file.status === "ready" && (
													<>
														<Button
															onClick={(e) => {
																e.stopPropagation();
															}}
															variant="ghost"
															size="sm"
															className="h-8 w-8 p-0">
															<Eye className="w-4 h-4" />
														</Button>
														<Button
															onClick={(e) => {
																e.stopPropagation();
															}}
															variant="ghost"
															size="sm"
															className="h-8 w-8 p-0">
															<Download className="w-4 h-4" />
														</Button>
													</>
												)}
												<Button
													variant="ghost"
													size="sm"
													className="h-8 w-8 p-0 text-destructive hover:text-destructive"
													onClick={(e) => {
														e.stopPropagation();
														handleRemoveFile(file.id);
													}}>
													<Trash2 className="w-4 h-4" />
												</Button>
											</div>
										</div>
									</div>
								))}

								{uploadedFiles.length === 0 && (
									<div className="text-center py-8 text-muted-foreground">
										<FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
										<p>No files uploaded yet</p>
										<p className="text-sm">
											Upload some PDF documents to get started
										</p>
									</div>
								)}
							</div>
						</ScrollArea>
					</TabsContent>
				</Tabs>

				<DialogFooter>
					<div className="flex items-center justify-between ">
						<div className="text-sm text-muted-foreground">
							{selectedFiles.length > 0 && (
								<span>{selectedFiles.length} files selected for analysis</span>
							)}
						</div>
						<div className="flex items-center gap-2">
							<Button
								variant="outline"
								onClick={() => handleCloseDialog(false)}>
								Cancel
							</Button>
							<Button
								onClick={handleApplySelection}
								disabled={selectedFiles.length === 0}>
								Apply Selection
							</Button>
						</div>
					</div>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}

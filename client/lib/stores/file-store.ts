import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { UploadedFile, FileUploadProgress } from "../types";

interface FileState {
	uploadedFiles: UploadedFile[];
	selectedFiles: string[];
	uploadProgress: Record<string, FileUploadProgress>;
	isUploading: boolean;
	addFile: (file: UploadedFile) => void;
	updateFile: (id: string, updates: Partial<UploadedFile>) => void;
	removeFile: (id: string) => void;
	selectFile: (id: string) => void;
	deselectFile: (id: string) => void;
	clearSelectedFiles: () => void;
	setUploadProgress: (fileId: string, progress: FileUploadProgress) => void;
	clearUploadProgress: (fileId: string) => void;
	setUploading: (isUploading: boolean) => void;
}

export const useFileStore = create<FileState>()(
	persist(
		(set) => ({
			uploadedFiles: [],
			selectedFiles: [],
			uploadProgress: {},
			isUploading: false,

			addFile: (file) => {
				set((state) => ({
					uploadedFiles: [...state.uploadedFiles, file],
				}));
			},

			updateFile: (id, updates) => {
				set((state) => ({
					uploadedFiles: state.uploadedFiles.map((file) =>
						file.id === id ? { ...file, ...updates } : file
					),
				}));
			},

			removeFile: (id) => {
				set((state) => ({
					uploadedFiles: state.uploadedFiles.filter((file) => file.id !== id),
					selectedFiles: state.selectedFiles.filter((fileId) => fileId !== id),
				}));
			},

			selectFile: (id) => {
				set((state) => ({
					selectedFiles: state.selectedFiles.includes(id)
						? state.selectedFiles
						: [...state.selectedFiles, id],
				}));
			},

			deselectFile: (id) => {
				set((state) => ({
					selectedFiles: state.selectedFiles.filter((fileId) => fileId !== id),
				}));
			},

			clearSelectedFiles: () => {
				set({ selectedFiles: [] });
			},

			setUploadProgress: (fileId, progress) => {
				set((state) => ({
					uploadProgress: {
						...state.uploadProgress,
						[fileId]: progress,
					},
				}));
			},

			clearUploadProgress: (fileId) => {
				set((state) => {
					// eslint-disable-next-line @typescript-eslint/no-unused-vars
					const { [fileId]: _, ...rest } = state.uploadProgress;
					return { uploadProgress: rest };
				});
			},

			setUploading: (isUploading) => {
				set({ isUploading });
			},
		}),
		{
			name: "file-storage",
			partialize: (state) => ({
				uploadedFiles: state.uploadedFiles,
			}),
		}
	)
);

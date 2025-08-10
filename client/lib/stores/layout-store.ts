import { create } from "zustand";

interface LayoutState {
	isSplitView: boolean;
	isAnimating: boolean;
	setSplitView: (split: boolean) => void;
	setAnimating: (animating: boolean) => void;
}

export const useLayoutStore = create<LayoutState>((set) => ({
	isSplitView: false,
	isAnimating: false,
	setSplitView: (split) => set({ isSplitView: split }),
	setAnimating: (animating) => set({ isAnimating: animating }),
}));

import create from 'zustand'

interface AppState {
  project: string | null
  darkMode: boolean
  selectedFile: string | null
  testResults: any
  gitStatus: any
  setProject: (project: string) => void
  setDarkMode: (enabled: boolean) => void
  setSelectedFile: (file: string) => void
  setTestResults: (results: any) => void
  setGitStatus: (status: any) => void
}

export const useStore = create<AppState>((set) => ({
  project: null,
  darkMode: true,
  selectedFile: null,
  testResults: null,
  gitStatus: null,
  setProject: (project) => set({ project }),
  setDarkMode: (enabled) => set({ darkMode: enabled }),
  setSelectedFile: (file) => set({ selectedFile: file }),
  setTestResults: (results) => set({ testResults: results }),
  setGitStatus: (status) => set({ gitStatus: status })
}))

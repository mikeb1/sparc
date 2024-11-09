import { useState } from 'react'
import { Sidebar } from './Sidebar'
import { ThemeProvider } from './ThemeProvider'

export const Layout = ({ children }) => {
  const [darkMode, setDarkMode] = useState(true)
  
  return (
    <ThemeProvider darkMode={darkMode}>
      <div className="flex h-screen">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </ThemeProvider>
  )
}

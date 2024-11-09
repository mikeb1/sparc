import { useState } from 'react'

export const Sidebar = () => {
  const [currentPage, setCurrentPage] = useState('Project')
  
  const pages = ['Project', 'Code', 'Tests', 'Settings']
  
  return (
    <div className="w-64 bg-sidebar">
      <div className="p-4">
        <h1 className="text-xl font-bold">SPARC GUI</h1>
      </div>
      <nav>
        {pages.map(page => (
          <button
            key={page}
            onClick={() => setCurrentPage(page)}
            className={`w-full p-4 text-left ${
              currentPage === page ? 'bg-selected' : ''
            }`}
          >
            {page}
          </button>
        ))}
      </nav>
    </div>
  )
}

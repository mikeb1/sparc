const API_BASE = 'http://localhost:8000/api'

export const api = {
  async getState() {
    const res = await fetch(`${API_BASE}/state`)
    return res.json()
  },
  
  async updateState(key: string, value: any) {
    const res = await fetch(`${API_BASE}/state/${key}`, {
      method: 'POST',
      body: JSON.stringify(value)
    })
    return res.json()
  },
  
  async createProject(name: string) {
    const res = await fetch(`${API_BASE}/project/create`, {
      method: 'POST',
      body: JSON.stringify({ name })
    })
    return res.json()
  },
  
  async getGitStatus() {
    const res = await fetch(`${API_BASE}/git/status`)
    return res.json()
  }
}

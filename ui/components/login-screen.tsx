import { useState, FormEvent } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

interface LoginFormData {
  email: string
  password: string
}

interface LoginScreenProps {
  onSubmit: (data: LoginFormData) => void
  onForgotPassword: () => void
}

export function LoginScreen({ onSubmit, onForgotPassword }: LoginScreenProps) {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: ''
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-8 p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <Input
              id="email"
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="Enter your email"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
              Password
            </label>
            <Input
              id="password"
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Enter your password"
            />
          </div>

          <div className="space-y-4">
            <Button type="submit" className="w-full">
              Sign In
            </Button>
            <Button
              type="button"
              variant="ghost"
              className="w-full"
              onClick={onForgotPassword}
            >
              Forgot Password?
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

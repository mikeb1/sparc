import { Button } from './ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Switch } from './ui/switch'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './ui/tooltip'
import { useToast } from './ui/use-toast'
import { LLMModelConfig } from '@/lib/models'
import { Settings2, Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { OpenRouterModel, fetchAvailableModels, loadSettings, saveSettings, testApiKey } from '@/lib/settingsService'

export function ChatSettings({
  apiKeyConfigurable,
  baseURLConfigurable,
  languageModel,
  onLanguageModelChange,
}: {
  apiKeyConfigurable: boolean
  baseURLConfigurable: boolean
  languageModel: LLMModelConfig
  onLanguageModelChange: (model: LLMModelConfig) => void
}) {
  const [apiKey, setApiKey] = useState<string | undefined>(languageModel.apiKey)
  const [models, setModels] = useState<OpenRouterModel[]>([])
  const [enabledModels, setEnabledModels] = useState<string[]>([])
  const [isLoadingModels, setIsLoadingModels] = useState(false)
  const { toast } = useToast()

  // Load saved settings on mount
  useEffect(() => {
    const settings = loadSettings()
    if (settings) {
      setApiKey(settings.apiKey)
      setEnabledModels(settings.enabledModels)
      onLanguageModelChange({ apiKey: settings.apiKey })
    }
  }, [])

  // Fetch models when API key changes
  useEffect(() => {
    if (apiKey) {
      setIsLoadingModels(true)
      fetchAvailableModels(apiKey)
        .then(fetchedModels => {
          setModels(fetchedModels)
          setIsLoadingModels(false)
        })
        .catch(error => {
          console.error('Failed to fetch models:', error)
          toast({
            title: "Error",
            description: "Failed to fetch available models. Please check your API key.",
            variant: "destructive"
          })
          setIsLoadingModels(false)
        })
    }
  }, [apiKey])

  const handleApiKeyChange = async (newKey: string) => {
    setApiKey(newKey)
    if (newKey) {
      const isValid = await testApiKey(newKey)
      if (isValid) {
        saveSettings({
          apiKey: newKey,
          defaultModel: languageModel.model,
          enabledModels
        })
        onLanguageModelChange({ apiKey: newKey })
        toast({
          title: "Success",
          description: "API key validated and saved",
        })
      } else {
        toast({
          title: "Error",
          description: "Invalid API key",
          variant: "destructive"
        })
      }
    }
  }

  const handleModelToggle = (modelId: string) => {
    const newEnabledModels = enabledModels.includes(modelId)
      ? enabledModels.filter(id => id !== modelId)
      : [...enabledModels, modelId]
    
    setEnabledModels(newEnabledModels)
    saveSettings({
      apiKey: apiKey || '',
      defaultModel: languageModel.model,
      enabledModels: newEnabledModels
    })
  }
  return (
    <DropdownMenu>
      <TooltipProvider>
        <Tooltip delayDuration={0}>
          <TooltipTrigger asChild>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="text-muted-foreground h-6 w-6 rounded-sm">
                <Settings2 className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
          </TooltipTrigger>
          <TooltipContent>LLM settings</TooltipContent>
        </Tooltip>
      </TooltipProvider>
      <DropdownMenuContent align="start">
        {apiKeyConfigurable && (
          <>
            <div className="flex flex-col gap-2 px-2 py-2">
              <Label htmlFor="apiKey">API Key</Label>
              <Input
                name="apiKey"
                type="password"
                placeholder="Auto"
                required={true}
                defaultValue={languageModel.apiKey}
                onChange={(e) =>
                  onLanguageModelChange({
                    apiKey:
                      e.target.value.length > 0 ? e.target.value : undefined,
                  })
                }
                className="text-sm"
              />
            </div>
            <DropdownMenuSeparator />
          </>
        )}
        {baseURLConfigurable && (
          <>
            <div className="flex flex-col gap-2 px-2 py-2">
              <Label htmlFor="baseURL">Base URL</Label>
              <Input
                name="baseURL"
                type="text"
                placeholder="Auto"
                required={true}
                defaultValue={languageModel.baseURL}
                onChange={(e) =>
                  onLanguageModelChange({
                    baseURL:
                      e.target.value.length > 0 ? e.target.value : undefined,
                  })
                }
                className="text-sm"
              />
            </div>
            <DropdownMenuSeparator />
          </>
        )}
        <div className="flex flex-col gap-2 px-2 py-2">
          <Label>OpenRouter Models</Label>
          {isLoadingModels ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading models...
            </div>
          ) : models.length > 0 ? (
            <div className="max-h-48 overflow-y-auto space-y-2">
              {models.map(model => (
                <div key={model.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted">
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{model.name}</span>
                    <span className="text-xs text-muted-foreground">
                      Context: {model.context_length.toLocaleString()} tokens
                    </span>
                    <span className="text-xs text-muted-foreground">
                      ${model.pricing.prompt}/1K prompt, ${model.pricing.completion}/1K completion
                    </span>
                  </div>
                  <Switch
                    checked={enabledModels.includes(model.id)}
                    onCheckedChange={() => handleModelToggle(model.id)}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">
              {apiKey ? 'No models available' : 'Enter API key to view available models'}
            </div>
          )}
        </div>
        <DropdownMenuSeparator />
        <div className="flex flex-col gap-1.5 px-2 py-2">
          <span className="text-sm font-medium">Parameters</span>
          <div className="flex space-x-4 items-center">
            <span className="text-sm flex-1 text-muted-foreground">
              Output tokens
            </span>
            <Input
              type="number"
              defaultValue={languageModel.maxTokens}
              min={50}
              max={10000}
              step={1}
              className="h-6 rounded-sm w-[84px] text-xs text-center tabular-nums"
              placeholder="Auto"
              onChange={(e) =>
                onLanguageModelChange({
                  maxTokens: parseFloat(e.target.value) || undefined,
                })
              }
            />
          </div>
          <div className="flex space-x-4 items-center">
            <span className="text-sm flex-1 text-muted-foreground">
              Temperature
            </span>
            <Input
              type="number"
              defaultValue={languageModel.temperature}
              min={0}
              max={5}
              step={0.01}
              className="h-6 rounded-sm w-[84px] text-xs text-center tabular-nums"
              placeholder="Auto"
              onChange={(e) =>
                onLanguageModelChange({
                  temperature: parseFloat(e.target.value) || undefined,
                })
              }
            />
          </div>
          <div className="flex space-x-4 items-center">
            <span className="text-sm flex-1 text-muted-foreground">Top P</span>
            <Input
              type="number"
              defaultValue={languageModel.topP}
              min={0}
              max={1}
              step={0.01}
              className="h-6 rounded-sm w-[84px] text-xs text-center tabular-nums"
              placeholder="Auto"
              onChange={(e) =>
                onLanguageModelChange({
                  topP: parseFloat(e.target.value) || undefined,
                })
              }
            />
          </div>
          <div className="flex space-x-4 items-center">
            <span className="text-sm flex-1 text-muted-foreground">Top K</span>
            <Input
              type="number"
              defaultValue={languageModel.topK}
              min={0}
              max={500}
              step={1}
              className="h-6 rounded-sm w-[84px] text-xs text-center tabular-nums"
              placeholder="Auto"
              onChange={(e) =>
                onLanguageModelChange({
                  topK: parseFloat(e.target.value) || undefined,
                })
              }
            />
          </div>
          <div className="flex space-x-4 items-center">
            <span className="text-sm flex-1 text-muted-foreground">
              Frequence penalty
            </span>
            <Input
              type="number"
              defaultValue={languageModel.frequencyPenalty}
              min={0}
              max={2}
              step={0.01}
              className="h-6 rounded-sm w-[84px] text-xs text-center tabular-nums"
              placeholder="Auto"
              onChange={(e) =>
                onLanguageModelChange({
                  frequencyPenalty: parseFloat(e.target.value) || undefined,
                })
              }
            />
          </div>
          <div className="flex space-x-4 items-center">
            <span className="text-sm flex-1 text-muted-foreground">
              Presence penalty
            </span>
            <Input
              type="number"
              defaultValue={languageModel.presencePenalty}
              min={0}
              max={2}
              step={0.01}
              className="h-6 rounded-sm w-[84px] text-xs text-center tabular-nums"
              placeholder="Auto"
              onChange={(e) =>
                onLanguageModelChange({
                  presencePenalty: parseFloat(e.target.value) || undefined,
                })
              }
            />
          </div>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

import { sandbox } from '@e2b/code-interpreter'

// Your template ID from the previous step
const templateID = 'zhlsrvvoeuzm9sb9rq8q' // $HighlightLine
// Pass the template ID to the `Sandbox.create` method
const sandbox = await Sandbox.create(templateID) // $HighlightLine

// The template installed cowsay, so we can use it
const execution = await sandbox.runCode(`
import cowsay
cowsay.say('Hello from E2B!')
`)

console.log(execution.stdout)

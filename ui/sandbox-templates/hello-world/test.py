from e2b_code_interpreter import Sandbox

# Your template ID from the previous step
template_id = 'hgqcvfyyr1oynxkopwcv' # $HighlightLine
# Pass the template ID to the `Sandbox.create` method
sandbox = Sandbox(template_id) # $HighlightLine

# The template installed cowsay, so we can use it
execution = sandbox.run_code("""
import cowsay
cowsay.say('Hello from E2B!')
""")

print(execution.stdout)
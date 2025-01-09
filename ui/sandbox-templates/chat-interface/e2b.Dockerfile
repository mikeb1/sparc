FROM e2bdev/base:latest

WORKDIR /home/user

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_21.x | bash - && \
    apt-get install -y nodejs

# Install create-vite globally
RUN npm install -g create-vite

# Create a new Vite + React + TypeScript project
RUN create-vite . --template react-ts

# Install dependencies
RUN npm install && \
    npm install -D @vitejs/plugin-react typescript @types/react @types/react-dom \
    tailwindcss postcss autoprefixer @tailwindcss/forms && \
    npm install @headlessui/react @heroicons/react date-fns

# Initialize Tailwind CSS
RUN npx tailwindcss init -p

# Set the startup command
CMD ["npm", "run", "dev"]

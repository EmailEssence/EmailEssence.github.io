# uses a Node.js image as the base image
FROM node:16

# Sets the working directory inside the container to /frontend
WORKDIR /frontend

# Copy package.json and package-lock.json to the working directory
COPY frontend/package*.json ./
COPY frontend/jsconfig.json ./
COPY frontend/jest.config.cjs ./
COPY frontend/tsconfig.json ./

# Install the project dependencies
RUN npm install

# Copy all project files into the container
COPY . .

# Expose the port Vite uses (by default, it's 5173)
EXPOSE 5173

# Run the app in preview mode (for production)
CMD ["npm", "run", "preview"]

FROM node:lts-alpine as builder

# Copy package.json first to leverage Docker's caching strategy
COPY package.json ./
RUN npm install

# Create a directory for your app
RUN mkdir /app-ui
RUN mv ./node_modules /app-ui
WORKDIR /app-ui

# Copy the rest of your app files
COPY . .

# Build the static React files
RUN npm run build

# Expose the port npx serve will use (usually 80 or 3000)
EXPOSE 80 

# Serve the built static files directly using npx for simplicity
CMD ["npx", "serve", "-s", "build"] 

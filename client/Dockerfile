FROM node:14 as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all client files
COPY . .

# Show directory contents before build
RUN ls -la

# Build the React app
RUN npm run build

# Show directory contents after build to see what was created
RUN ls -la
RUN ls -la dist || echo "dist directory not found!" && find . -type d -maxdepth 2

# Use official Nginx image
FROM nginx:alpine

# Copy the build files to Nginx - try with the correct output directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Run command
CMD ["nginx", "-g", "daemon off;"]
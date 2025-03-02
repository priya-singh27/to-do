FROM node:14 as builder

WORKDIR /app

# Copy package files
COPY client/package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY client/ .

# Build the React app (make sure this matches your package.json script)
RUN npm run build

# Use official Nginx image
FROM nginx:alpine

# Copy the build files to Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Create a basic nginx configuration
COPY client/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Run command
CMD ["nginx", "-g", "daemon off;"]
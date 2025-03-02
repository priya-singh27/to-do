FROM node:14 as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all client files
COPY . .

# Build the React app
RUN npm run build

# Use official Nginx image
FROM nginx:alpine

# Copy the build files to Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Run command
CMD ["nginx", "-g", "daemon off;"]
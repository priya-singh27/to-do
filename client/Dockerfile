FROM node:14 as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all client files
COPY . .

# Show what's in the directory
RUN ls -la

# Build the React app
RUN npm run build

# Debug: Check if build created any output
RUN echo "Build output:"
RUN find . -type d | grep -v node_modules

# Try to find where the build output might be
RUN mkdir -p /usr/share/nginx/html

# Use a wildcard to copy build files - will copy from whatever directory Vite is using
RUN if [ -d "dist" ]; then \
      cp -r dist/* /usr/share/nginx/html/; \
    elif [ -d "build" ]; then \
      cp -r build/* /usr/share/nginx/html/; \
    else \
      echo "Build directory not found!"; \
      exit 1; \
    fi

# Show what was copied
RUN ls -la /usr/share/nginx/html

# Use official Nginx image for the final image
FROM nginx:alpine

# Copy the pre-built files from the builder stage
COPY --from=builder /usr/share/nginx/html /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Run command
CMD ["nginx", "-g", "daemon off;"]
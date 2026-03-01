FROM node:24-slim

WORKDIR /app

# Copy app
COPY poe_profiter/ ./

# Install dependencies
RUN npm install

# Expose Vite port
EXPOSE 5173

# Start dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
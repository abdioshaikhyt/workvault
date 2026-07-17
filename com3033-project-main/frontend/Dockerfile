# Use an official Node runtime as a parent image
FROM node:22.17.1

# Set the working directory to /app
WORKDIR /code/frontend

# Copy the package.json and package-lock.json to the working directory
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY public/ /code/frontend/public
COPY src/ /code/frontend/src
COPY eslint.config.js /code/frontend
COPY index.html /code/frontend/index.html
COPY package*.json /code/frontend
COPY vite.config.js /code/frontend

#ENV NODE_ENV=development

# Install the dependencies
RUN npm install
RUN npm run build
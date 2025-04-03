# Deployment Instructions for Piano Chorus Creator Backend

This document provides detailed instructions for deploying the Piano Chorus Creator backend to different platforms.

## Prerequisites

Before deploying, make sure you have:
1. A GitHub account
2. An account on your preferred deployment platform (Render or Heroku)
3. The complete backend code from this repository

## Option 1: Deploying to Render

### Step 1: Push the code to GitHub
1. Create a new repository on GitHub
2. Initialize git in the backend directory:
   ```bash
   cd piano-chorus-creator-backend
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/piano-chorus-creator-backend.git
   git push -u origin main
   ```

### Step 2: Deploy on Render
1. Log in to your Render account
2. Click on "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - Name: piano-chorus-creator-backend
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
5. Add environment variables if needed
6. Click "Create Web Service"

Render will automatically detect the `render.yaml` file and use its configuration.

## Option 2: Deploying to Heroku

### Step 1: Push the code to GitHub
Follow the same steps as above to push your code to GitHub.

### Step 2: Deploy on Heroku
1. Log in to your Heroku account
2. Create a new app
3. Connect your GitHub repository
4. Add the Python buildpack
5. Add the Apt buildpack for system dependencies:
   ```
   heroku buildpacks:add --index 1 heroku-community/apt
   ```
6. Deploy the application
7. Verify that the application is running

## Updating the Frontend

After deploying the backend, you need to update the frontend to point to your deployed backend URL:

1. Note the URL of your deployed backend (e.g., https://piano-chorus-creator-backend.onrender.com)
2. Update the API endpoint URLs in the frontend code to point to this URL
3. Redeploy the frontend if necessary

## Testing the Deployment

To verify that your deployment is working correctly:

1. Visit the root endpoint of your deployed backend (e.g., https://piano-chorus-creator-backend.onrender.com/)
2. You should see a message: "Piano Chorus Creator API is running"
3. Test the YouTube endpoint by sending a POST request to `/api/youtube` with a valid YouTube URL
4. Check the status of your task using the task ID returned from the previous request
5. Download the generated sheet music when the task is complete

## Troubleshooting

If you encounter issues during deployment:

1. Check the deployment logs for error messages
2. Verify that all system dependencies (LilyPond and FFmpeg) are installed correctly
3. Ensure that all environment variables are set properly
4. Check that the CORS configuration allows requests from your frontend domain

## Getting Help

If you need further assistance with deployment, please contact the developer or refer to the documentation of your deployment platform.

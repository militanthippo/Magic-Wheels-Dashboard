# Deploying to Render.com

## Prerequisites
- A Render.com account (free tier is sufficient)
- Git installed on your computer

## Deployment Steps

1. Create a new Git repository with the contents of this directory:
   ```
   cd magic-wheels-dashboard
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Create a new Web Service on Render:
   - Go to https://dashboard.render.com/
   - Click "New +" and select "Blueprint"
   - Connect your Git repository
   - Render will automatically detect the render.yaml configuration
   - Click "Apply Blueprint"

3. Render will automatically deploy both the web service and the worker:
   - The web service runs the dashboard interface
   - The worker handles the hourly data refresh

4. Once deployment is complete, your dashboard will be available at:
   https://magic-wheels-dashboard.onrender.com

5. The first time you access the dashboard, you'll need to complete the OAuth flow:
   - Click the authorization link
   - Log in to your GoHighLevel account
   - Authorize the application
   - You'll be redirected back to the dashboard

## Updating the Dashboard

To update the dashboard in the future:
1. Make your changes
2. Commit them to Git
3. Push to the repository connected to Render
4. Render will automatically redeploy the updated version

## Monitoring and Logs

- View logs and monitor performance in the Render dashboard
- Set up alerts for any issues

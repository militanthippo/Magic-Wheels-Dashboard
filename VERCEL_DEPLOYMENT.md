# Deploying to Vercel

## Prerequisites
- A Vercel account (free tier is sufficient)
- Vercel CLI installed (`npm install -g vercel`)
- Git installed on your computer

## Deployment Steps

1. Create a new Git repository with the contents of this directory:
   ```
   cd magic-wheels-dashboard
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Login to Vercel CLI:
   ```
   vercel login
   ```

3. Deploy to Vercel:
   ```
   vercel
   ```
   - Follow the prompts to set up your project
   - When asked if you want to override the settings, select "No"

4. Once deployment is complete, your dashboard will be available at the URL provided by Vercel

5. The first time you access the dashboard, you'll need to complete the OAuth flow:
   - Click the authorization link
   - Log in to your GoHighLevel account
   - Authorize the application
   - You'll be redirected back to the dashboard

## Updating the Dashboard

To update the dashboard in the future:
1. Make your changes
2. Commit them to Git
3. Run `vercel --prod`

## Monitoring and Logs

- View logs and monitor performance in the Vercel dashboard
- Set up integrations for notifications

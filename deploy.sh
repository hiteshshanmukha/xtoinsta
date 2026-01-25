#!/bin/bash
# Railway Deployment Script

echo "🚀 Deploying to Railway..."
echo ""
echo "Step 1: Initializing Git repository..."
git init

echo "Step 2: Adding all files..."
git add .

echo "Step 3: Creating commit..."
git commit -m "Deploy X to Instagram Reel Converter"

echo ""
echo "✅ Repository ready!"
echo ""
echo "Next steps:"
echo "1. Create a GitHub repository at https://github.com/new"
echo "2. Run: git remote add origin YOUR_REPO_URL"
echo "3. Run: git push -u origin main"
echo "4. Go to https://railway.app and deploy from GitHub"
echo ""

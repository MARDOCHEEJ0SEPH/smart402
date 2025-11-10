#!/bin/bash

# Smart402 Wiki Upload Script
# Uploads wiki pages to GitHub wiki repository

set -e

echo "🚀 Smart402 Wiki Upload Script"
echo "================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    exit 1
fi

# Configuration
WIKI_REPO="https://github.com/MARDOCHEEJ0SEPH/smart402.wiki.git"
TEMP_DIR="temp-wiki-upload"

echo "📦 Cloning wiki repository..."
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

git clone "$WIKI_REPO" "$TEMP_DIR"

echo "📝 Copying wiki files..."
cp *.md "$TEMP_DIR/" 2>/dev/null || true

cd "$TEMP_DIR"

echo "📊 Files to be uploaded:"
ls -1 *.md

echo ""
read -p "Continue with upload? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "⬆️  Uploading to GitHub wiki..."

    git add .
    git commit -m "Update Smart402 wiki documentation - $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin master

    echo ""
    echo "✅ Wiki uploaded successfully!"
    echo "📖 View at: https://github.com/MARDOCHEEJ0SEPH/smart402/wiki"
else
    echo "❌ Upload canceled"
fi

# Cleanup
cd ..
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Done!"

#!/bin/bash
# Build script for GitHub Pages deployment
# Injects git commit info into index.html

echo "🔨 Building for GitHub Pages..."

# Get git commit info
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_DATE=$(git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M:%S')

echo "📝 Commit: $COMMIT_HASH"
echo "📅 Date: $COMMIT_DATE"

# Create a copy of index.html with injected variables
cp index.html index.html.backup
sed -i.tmp "s/BUILD_TIMESTAMP/$COMMIT_DATE/g" index.html
sed -i.tmp "s/BUILD_COMMIT_HASH/$COMMIT_HASH/g" index.html
rm -f index.html.tmp

echo "✅ Build complete!"
echo ""
echo "To deploy to GitHub Pages:"
echo "  git add index.html"
echo "  git commit -m 'Update GitHub Pages build'"
echo "  git push origin main"
echo ""
echo "To restore original:"
echo "  mv index.html.backup index.html"

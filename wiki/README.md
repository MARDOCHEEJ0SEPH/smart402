# Smart402 Wiki

This directory contains the complete wiki documentation for Smart402.

## Uploading to GitHub Wiki

To upload these pages to your GitHub wiki:

### Method 1: Manual Upload (Web Interface)

1. Go to https://github.com/MARDOCHEEJ0SEPH/smart402/wiki
2. Click "New Page" or edit existing pages
3. Copy content from markdown files in this directory
4. Paste and save

### Method 2: Git Clone (Recommended)

```bash
# Clone the wiki repository
git clone https://github.com/MARDOCHEEJ0SEPH/smart402.wiki.git

# Copy all wiki files
cp wiki/*.md smart402.wiki/

# Commit and push
cd smart402.wiki
git add .
git commit -m "Add comprehensive Smart402 documentation"
git push origin master
```

### Method 3: Using Wiki Script

```bash
# Make the upload script
cat > upload-wiki.sh << 'EOF'
#!/bin/bash

# Clone wiki
git clone https://github.com/MARDOCHEEJ0SEPH/smart402.wiki.git temp-wiki

# Copy files
cp wiki/*.md temp-wiki/

# Push
cd temp-wiki
git add .
git commit -m "Update Smart402 wiki documentation"
git push origin master

# Cleanup
cd ..
rm -rf temp-wiki

echo "✓ Wiki uploaded successfully!"
EOF

chmod +x upload-wiki.sh
./upload-wiki.sh
```

## Wiki Structure

### Core Pages
- `Home.md` - Main landing page
- `Installation.md` - Setup guide
- `Quick-Start.md` - 5-minute tutorial
- `FAQ.md` - Frequently asked questions

### Specifications
- `AEO-Specification.md` - Answer Engine Optimization
- `LLMO-Specification.md` - Large Language Model Optimization (to be created)
- `X402-Specification.md` - HTTP Payment Protocol (to be created)

### SDK Guides
- `JavaScript-SDK.md` - Complete JS/TS reference
- `Python-SDK.md` - Python reference (to be created)
- `Rust-SDK.md` - Rust reference (to be created)

### Examples
- `Example-Book-Seller.md` - Digital product sales
- `Example-SaaS-Subscription.md` - Recurring payments (to be created)
- `Example-Freelancer-Escrow.md` - Milestone-based (to be created)

### Advanced
- `Architecture.md` - System design (to be created)
- `Deployment-Guide.md` - Production deployment (to be created)
- `Testing-Guide.md` - Test suites (to be created)
- `API-Reference.md` - Complete API docs (to be created)

## Customizing

### Navigation Sidebar

GitHub wiki automatically generates sidebar from:
1. File names (alphabetically)
2. Custom `_Sidebar.md` file

Create `_Sidebar.md`:

```markdown
**Getting Started**
* [Home](Home)
* [Installation](Installation)
* [Quick Start](Quick-Start)

**SDK Guides**
* [JavaScript SDK](JavaScript-SDK)
* [Python SDK](Python-SDK)
* [Rust SDK](Rust-SDK)

**Specifications**
* [AEO](AEO-Specification)
* [LLMO](LLMO-Specification)
* [X402](X402-Specification)

**Examples**
* [Book Seller](Example-Book-Seller)
* [SaaS Subscription](Example-SaaS-Subscription)
* [Freelancer Escrow](Example-Freelancer-Escrow)

**Advanced**
* [Architecture](Architecture)
* [API Reference](API-Reference)
* [Testing Guide](Testing-Guide)

**Community**
* [Contributing](Contributing)
* [FAQ](FAQ)
```

### Footer

Create `_Footer.md`:

```markdown
---
Smart402 - Universal Protocol for AI-Native Smart Contracts

[GitHub](https://github.com/MARDOCHEEJ0SEPH/smart402) •
[Discord](https://discord.gg/smart402) •
[Website](https://smart402.io)

© 2024 Smart402 • [MIT License](https://opensource.org/licenses/MIT)
```

## Maintenance

### Updating Documentation

```bash
# Edit files in wiki/ directory
vim wiki/Installation.md

# Push to GitHub wiki
cd smart402.wiki
git add Installation.md
git commit -m "Update installation instructions"
git push
```

### Checking Links

```bash
# Find broken internal links
grep -r "\[.*\](.md)" wiki/

# Find external links
grep -r "https://" wiki/
```

### Spell Check

```bash
# Install aspell
sudo apt install aspell

# Check spelling
find wiki/ -name "*.md" -exec aspell check {} \;
```

## Contributing to Wiki

1. Edit markdown files in `wiki/` directory
2. Test locally with markdown viewer
3. Submit PR with wiki updates
4. After merge, upload to GitHub wiki

## Resources

- [GitHub Wiki Documentation](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
- [Markdown Guide](https://www.markdownguide.org/)
- [Smart402 Main Repo](https://github.com/MARDOCHEEJ0SEPH/smart402)

---

**Questions?** Open an issue or ask in Discord!

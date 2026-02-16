# Documentation Site - All Repositories

This repository automatically aggregates markdown documentation from all your private repositories and deploys it to GitHub Pages as a searchable, organized documentation site.

## 🌟 Features

- **Automatic Aggregation**: Fetches all `.md` files from specified repositories
- **Material Design**: Beautiful, responsive UI with Material for MkDocs theme
- **Smart Navigation**: Automatically organizes documentation by repository
- **Full-Text Search**: Search across all documentation
- **Auto-Updates**: Daily automatic updates to catch changes in source repositories
- **Code Highlighting**: Syntax highlighting for all major programming languages
- **Dark Mode**: Built-in light/dark theme toggle

## 🚀 Setup Instructions

### 1. Create a Personal Access Token (PAT)

You need a GitHub Personal Access Token to access private repositories.

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Docs Site Access")
4. Select the `repo` scope (this gives full access to private repositories)
5. Set an appropriate expiration date
6. Click "Generate token"
7. **Important**: Copy the token immediately - you won't be able to see it again!

### 2. Add the Token as a Repository Secret

1. Go to your `docs-site-all-repos` repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `DOCS_PAT`
5. Value: Paste your Personal Access Token
6. Click "Add secret"

### 3. Enable GitHub Pages

1. Go to your repository Settings → Pages
2. Under "Source", select "Deploy from a branch"
3. Under "Branch", select `gh-pages` and `/ (root)`
4. Click "Save"

**Note**: The `gh-pages` branch will be created automatically on the first successful workflow run.

### 4. Configure Repository List (Optional)

If you want to add or remove repositories from the documentation:

1. Edit `scripts/fetch_repos.py`
2. Modify the `REPOSITORIES` list at the top of the file
3. Add or remove repository paths in the format `"username/repository"`
4. Commit and push your changes

## 🔧 Manual Workflow Trigger

To manually trigger a documentation rebuild:

1. Go to the "Actions" tab in your repository
2. Select "Build and Deploy Documentation" workflow
3. Click "Run workflow"
4. Select the branch (usually `main`)
5. Click "Run workflow"

## 📅 Automatic Updates

The documentation site automatically rebuilds:

- **On Push**: Whenever you push changes to the `main` branch
- **Daily**: Every day at 2 AM UTC to catch updates from source repositories
- **Manual**: Via workflow dispatch (see above)

## 🛠️ Local Development

To build and test the documentation site locally:

### Prerequisites

- Python 3.8 or higher
- Git
- A Personal Access Token with `repo` scope

### Setup

```bash
# Clone the repository
git clone https://github.com/at1337github/docs-site-all-repos.git
cd docs-site-all-repos

# Install dependencies
pip install -r requirements.txt

# Set your Personal Access Token
export DOCS_PAT="your_token_here"

# Fetch markdown files from repositories
python scripts/fetch_repos.py

# Serve the documentation locally
mkdocs serve
```

The documentation will be available at `http://127.0.0.1:8000`

### Build Static Site

```bash
# Build the static site
mkdocs build

# The built site will be in the 'site' directory
```

## 📁 Project Structure

```
docs-site-all-repos/
├── .github/
│   └── workflows/
│       └── build-docs.yml    # GitHub Actions workflow
├── docs/
│   ├── index.md              # Landing page
│   └── [repo-name]/          # Auto-generated: docs from each repo
├── scripts/
│   └── fetch_repos.py        # Script to fetch markdown files
├── mkdocs.yml                # MkDocs configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔍 How It Works

1. **GitHub Actions Workflow** triggers on push, schedule, or manual dispatch
2. **Fetch Script** (`scripts/fetch_repos.py`):
   - Uses GitHub API with your PAT
   - Fetches all `.md` files from each configured repository
   - Preserves the directory structure
   - Organizes files into `docs/{repo-name}/` folders
3. **Navigation Generation**: Automatically creates navigation structure in `mkdocs.yml`
4. **MkDocs Build**: Builds the static documentation site
5. **GitHub Pages Deploy**: Deploys to the `gh-pages` branch

## 🎨 Customization

### Theme Colors

Edit `mkdocs.yml` to change colors:

```yaml
theme:
  palette:
    - scheme: default
      primary: indigo  # Change this
      accent: indigo   # Change this
```

Available colors: red, pink, purple, deep purple, indigo, blue, light blue, cyan, teal, green, light green, lime, yellow, amber, orange, deep orange

### Site Information

Edit `mkdocs.yml` to change site details:

```yaml
site_name: Your Site Name
site_description: Your description
site_author: Your name
```

### Landing Page

Edit `docs/index.md` to customize the homepage content.

## ❗ Troubleshooting

### Workflow Fails with "DOCS_PAT not found"

- Make sure you've added the `DOCS_PAT` secret to your repository (see Setup step 2)
- Check that the secret name is exactly `DOCS_PAT` (case-sensitive)

### Repository Not Found Errors

- Verify your PAT has the `repo` scope
- Ensure the repository names in `scripts/fetch_repos.py` are correct
- Check that your PAT hasn't expired

### GitHub Pages Not Showing

- Make sure the `gh-pages` branch exists (it's created after the first successful run)
- Check that GitHub Pages is enabled and set to deploy from `gh-pages` branch
- It may take a few minutes for changes to appear

### No Documentation Showing Up

- Check the Actions tab for workflow run logs
- Verify that your source repositories actually contain `.md` files
- Look for error messages in the "Fetch markdown files" step

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the documentation site!
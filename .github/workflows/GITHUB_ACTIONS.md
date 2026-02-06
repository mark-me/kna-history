# GitHub Actions Workflows

This directory contains CI/CD workflows for the KNA History application.

## Workflows

### 1. CI - Tests and Validation (`ci-tests.yml`)

**Triggers:**
- Push to `main`, `develop`, `test` branches
- Pull requests to `main`
- Manual trigger

**Jobs:**
- **validate-config**: Validates docker-compose.yml and checks required files
- **lint-python**: Python code linting with flake8, black, and isort
- **test-docker-build**: Builds Docker image and tests basic startup
- **validate-scripts**: Shell script validation with shellcheck
- **security-scan**: Security vulnerability scanning with Trivy

**Purpose:** Ensures code quality and catches issues before deployment.

### 2. Build and Push Test Image (`build-test.yml`)

**Triggers:**
- Push to `test` or `develop` branches
- Pull requests to `main` or `test`
- Manual trigger

**What it does:**
- Builds Docker image with test tag
- Pushes to GitHub Container Registry with tags:
  - `test` (latest test build)
  - `test-{branch}-{sha}` (versioned test build)
  - `pr-{number}` (for pull requests - not pushed)
- Generates deployment instructions
- Comments on pull requests with build info

**Test image tags:**
```
ghcr.io/mark-me/kna-history:test
ghcr.io/mark-me/kna-history:test-develop-abc1234
ghcr.io/mark-me/kna-history:test-sha-abc1234567890
```

**Usage:**
```bash
# Deploy test image
docker pull ghcr.io/mark-me/kna-history:test
docker compose pull kna-historie
docker compose up -d kna-historie
```

### 3. Build and Push Release Image (`build-release.yml`)

**Triggers:**
- Push tags matching `v*.*.*` (e.g., v1.0.0, v2.1.3)
- Manual trigger with version input

**What it does:**
- Builds production Docker image
- Pushes to GitHub Container Registry with tags:
  - `v1.2.3` (full version)
  - `1.2` (major.minor)
  - `1` (major)
  - `latest` (latest release)
- Creates GitHub Release with:
  - Automatically generated release notes
  - Deployment instructions
  - Deployment script files
- Sets proper metadata and labels

**Release image tags:**
```
ghcr.io/mark-me/kna-history:v1.2.3
ghcr.io/mark-me/kna-history:1.2
ghcr.io/mark-me/kna-history:1
ghcr.io/mark-me/kna-history:latest
```

**Usage:**
```bash
# Create a release
git tag v1.2.3
git push origin v1.2.3

# Or use GitHub UI to create release
```

## Setting Up Workflows

### 1. Repository Structure

Ensure your repository has this structure:
```
.
├── .github/
│   └── workflows/
│       ├── ci-tests.yml
│       ├── build-test.yml
│       └── build-release.yml
├── src/
│   ├── kna_data/
│   │   ├── config.py
│   │   ├── loader.py
│   │   ├── reader.py
│   │   └── ...
│   └── app.py
├── Dockerfile
├── docker-compose.yml
├── env.example
├── pyproject.toml
├── uv.lock
└── *.sh (deployment scripts)
```

### 2. GitHub Container Registry Setup

The workflows are configured to use GitHub Container Registry (ghcr.io). No additional setup required - the `GITHUB_TOKEN` is automatically available.

**Make packages public (optional):**
1. Go to your repository on GitHub
2. Navigate to "Packages" (right sidebar)
3. Click on the package name
4. Go to "Package settings"
5. Scroll to "Danger Zone" → "Change visibility" → "Public"

### 3. Branch Protection

Recommended branch protection rules for `main`:

```yaml
Protection rules:
  - Require pull request reviews before merging
  - Require status checks to pass before merging:
    - validate-config
    - lint-python
    - test-docker-build
    - validate-scripts
  - Require branches to be up to date before merging
  - Require conversation resolution before merging
```

## Workflow Usage Examples

### Creating a Test Build

**Push to test branch:**
```bash
git checkout -b test
# Make changes
git add .
git commit -m "Test new feature"
git push origin test
```

This triggers `build-test.yml` which creates `ghcr.io/mark-me/kna-history:test`

**Deploy to test environment:**
```bash
# On your test server
export KNA_IMAGE_TAG=test
docker compose pull kna-historie
docker compose up -d kna-historie
./status.sh
```

### Creating a Release

**Method 1: Git tag (automatic)**
```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create and push tag
git tag v1.2.3
git push origin v1.2.3
```

**Method 2: GitHub Release (manual)**
1. Go to repository → Releases → "Draft a new release"
2. Click "Choose a tag" → Type `v1.2.3` → "Create new tag"
3. Title: `Version 1.2.3`
4. Click "Generate release notes" (optional)
5. Click "Publish release"

Both methods trigger `build-release.yml` which:
- Builds the image
- Publishes to registry with version tags
- Creates/updates GitHub Release

**Deploy to production:**
```bash
# On your production server
cd /path/to/kna-history
./update.sh  # Uses latest tag by default
```

### Manual Workflow Trigger

**Via GitHub UI:**
1. Go to repository → Actions
2. Select workflow (e.g., "Build and Push Release Image")
3. Click "Run workflow"
4. Select branch
5. Enter version (if required)
6. Click "Run workflow"

**Via GitHub CLI:**
```bash
# Install gh CLI: https://cli.github.com/

# Trigger release build
gh workflow run build-release.yml -f version=v1.2.3

# Trigger test build
gh workflow run build-test.yml

# Trigger CI tests
gh workflow run ci-tests.yml
```

## Monitoring Workflows

### View Workflow Runs

**GitHub UI:**
- Repository → Actions tab
- Click on workflow name
- Click on specific run for details

**GitHub CLI:**
```bash
# List recent workflow runs
gh run list

# View specific run
gh run view <run-id>

# Watch a running workflow
gh run watch
```

### Workflow Notifications

**Enable notifications:**
1. Go to repository → Settings → Notifications
2. Configure email notifications for:
   - Workflow failures
   - Workflow successes (optional)

**Status badges:**

Add to your README.md:
```markdown
![CI](https://github.com/mark-me/kna-history/actions/workflows/ci-tests.yml/badge.svg)
![Release](https://github.com/mark-me/kna-history/actions/workflows/build-release.yml/badge.svg)
```

## Troubleshooting Workflows

### Common Issues

#### 1. Docker build fails

**Check:**
- Dockerfile syntax
- All required files are committed
- Build context is correct

**Debug:**
```bash
# Test build locally
docker build -t kna-history:test .

# Check build logs in Actions tab
```

#### 2. Push to registry fails

**Possible causes:**
- Package visibility is private (requires authentication)
- Insufficient permissions

**Fix:**
```bash
# Ensure workflow has correct permissions
# (Already configured in workflows)
permissions:
  contents: read
  packages: write
```

#### 3. Tests fail

**Check:**
- Python syntax errors (flake8 job)
- Code formatting (black job)
- Import ordering (isort job)

**Fix locally before pushing:**
```bash
# Install tools
pip install flake8 black isort

# Check and fix
black src/
isort src/
flake8 src/
```

#### 4. env.example validation fails

**Ensure env.example contains all required variables:**
```bash
# Check locally
grep "^SECRET_KEY=" env.example
grep "^MARIADB_" env.example
grep "^DATABASE_URL=" env.example
```

### Workflow Logs

**View detailed logs:**
1. Actions tab → Select workflow run
2. Click on failed job
3. Expand failing step
4. Review error messages

**Download logs:**
```bash
# Using GitHub CLI
gh run view <run-id> --log
gh run download <run-id>
```

## Best Practices

### 1. Version Naming

Follow semantic versioning:
- **Major** (v2.0.0): Breaking changes
- **Minor** (v1.2.0): New features, backward compatible
- **Patch** (v1.1.1): Bug fixes, backward compatible

### 2. Testing Flow

```
feature branch → PR → CI tests pass → merge to develop
develop → test build → test deployment → verify
develop → merge to main → create release tag → deploy production
```

### 3. Release Process

1. **Development**: Work on feature branches
2. **Testing**: Merge to `develop`, deploy test image
3. **Staging**: Merge to `test` branch, thorough testing
4. **Release**: Merge to `main`, create version tag
5. **Deploy**: Use `./update.sh` script

### 4. Rollback Strategy

If a release has issues:
```bash
# Option 1: Deploy previous version
docker pull ghcr.io/mark-me/kna-history:v1.2.2  # previous version
docker tag ghcr.io/mark-me/kna-history:v1.2.2 ghcr.io/mark-me/kna-history:latest
docker compose up -d kna-historie

# Option 2: Use automatic backup
docker compose down kna-historie
docker tag ghcr.io/mark-me/kna-history:backup-20260206-120000 ghcr.io/mark-me/kna-history:latest
docker compose up -d kna-historie
```

### 5. Security

- Never commit secrets to repository
- Use GitHub Secrets for sensitive data (if needed)
- Regularly update dependencies
- Review security scan results
- Keep base images updated

## Customization

### Change Dockerfile Path

If your Dockerfile is in a different location:

```yaml
# In build-*.yml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    file: ./deploy/app/Dockerfile  # Change this
```

### Add Custom Tests

Add to `ci-tests.yml`:

```yaml
test-custom:
  name: Custom Tests
  runs-on: ubuntu-latest
  steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Run custom tests
      run: |
        # Your test commands here
```

### Change Python Version

```yaml
# In ci-tests.yml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.13'  # Change this
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Semantic Versioning](https://semver.org/)

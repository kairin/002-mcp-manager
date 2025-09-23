# MCP Manager - Automated Workflow Makefile
# Complete local CI/CD before pushing to remote

.PHONY: help
help: ## Show this help message
	@echo "MCP Manager - Local Workflow Automation"
	@echo "========================================"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup: ## Initial project setup (install all dependencies)
	@echo "📦 Setting up MCP Manager..."
	npm install
	pip install -e ".[dev]"
	pre-commit install
	@echo "✅ Setup complete!"

.PHONY: branch
branch: ## Create new branch with proper naming
	@echo "Creating new branch..."
	@DATETIME=$$(date +"%Y%m%d-%H%M%S"); \
	read -p "Enter type (feat/fix/docs/refactor/test/chore): " TYPE; \
	read -p "Enter short description (lowercase, hyphens): " DESC; \
	BRANCH="$$DATETIME-$$TYPE-$$DESC"; \
	git checkout -b "$$BRANCH"; \
	echo "✅ Created branch: $$BRANCH"

.PHONY: check
check: ## Run all quality checks (Python)
	@echo "🔍 Running Python quality checks..."
	black src/ tests/ --check
	ruff check src/ tests/
	mypy src/
	@echo "✅ Quality checks passed!"

.PHONY: format
format: ## Auto-format Python code
	@echo "🎨 Formatting code..."
	black src/ tests/
	ruff check src/ tests/ --fix
	@echo "✅ Code formatted!"

.PHONY: test
test: ## Run Python tests with coverage
	@echo "🧪 Running tests..."
	pytest tests/ --cov=mcp_manager --cov-fail-under=80
	@echo "✅ Tests passed!"

.PHONY: astro-check
astro-check: ## Check Astro/TypeScript types
	@echo "📘 Checking TypeScript..."
	npm run check
	@echo "✅ TypeScript valid!"

.PHONY: build
build: ## Build Astro website to docs/
	@echo "🏗️ Building website..."
	npm run build
	@echo "✅ Website built to ./docs"

.PHONY: verify
verify: ## Verify build outputs
	@echo "🔍 Verifying build..."
	@test -d ./docs || (echo "❌ docs/ not found" && exit 1)
	@test -f ./docs/.nojekyll || (echo "❌ .nojekyll not found" && exit 1)
	@test -d ./docs/_astro || (echo "❌ _astro/ not found" && exit 1)
	@FILE_COUNT=$$(find ./docs -type f | wc -l); \
	echo "✅ Verified: $$FILE_COUNT files in docs/"

.PHONY: ci
ci: check test astro-check build verify ## Run complete local CI pipeline
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✨ Local CI passed! Ready to commit."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

.PHONY: push-ready
push-ready: format ci ## Format code and run full CI (use before push)
	@echo ""
	@echo "🚀 All checks passed! Ready to push:"
	@echo "  1. git add -A"
	@echo "  2. git commit -m 'Your message'"
	@echo "  3. git push origin $$(git branch --show-current)"
	@echo ""
	@echo "GitHub Actions will deploy to: https://kairin.github.io/mcp-manager"

.PHONY: commit
commit: push-ready ## Complete workflow and commit changes
	@echo ""
	@read -p "Enter commit message: " MSG; \
	git add -A; \
	git commit -m "$$MSG"; \
	echo "✅ Changes committed! Run 'make push' to push to remote."

.PHONY: push
push: ## Push current branch to remote
	@BRANCH=$$(git branch --show-current); \
	echo "🚀 Pushing $$BRANCH to remote..."; \
	git push origin "$$BRANCH"; \
	echo "✅ Pushed! Create PR if needed."

.PHONY: workflow
workflow: branch push-ready commit push ## Complete workflow: branch, build, commit, push
	@echo ""
	@echo "✅ Complete workflow executed!"
	@echo "📌 Next: Create PR on GitHub if needed"

.PHONY: clean
clean: ## Clean build artifacts and caches
	@echo "🧹 Cleaning..."
	rm -rf ./docs/* ./build ./dist .pytest_cache .coverage .mypy_cache
	@echo "✅ Cleaned!"

.PHONY: dev
dev: ## Start Astro dev server
	npm run dev

.PHONY: preview
preview: ## Preview built site
	npm run preview

.PHONY: mcp-verify
mcp-verify: ## Verify MCP server configuration
	python verify_mcp_servers.py

.PHONY: mcp-test
mcp-test: ## Test MCP server connectivity
	./test_claude_fix.sh

# Default target
.DEFAULT_GOAL := help
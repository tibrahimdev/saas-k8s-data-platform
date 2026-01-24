# Makefile for Crossplane SaaS project

# -------- CONFIG --------
REGISTRY ?= ghcr.io/tibrahimdev
PACKAGE_NAME ?= saas
VERSION ?= v0.0.1

# Full image reference
IMAGE := $(REGISTRY)/$(PACKAGE_NAME):$(VERSION)

# -------- COMMANDS --------
.PHONY: all build push install clean

all: build

# Build the Crossplane package locally
build:
	@echo "==> Building package $(IMAGE)"
	rm -f *.xpkg
	crossplane xpkg build

# Push the package to remote OCI registry
push: build
	@echo "==> Pushing package $(IMAGE)"
	crossplane xpkg push $(IMAGE)

# # Placeholder for future steps
# install:
# 	@echo "==> Installing package $(IMAGE)"
# 	kubectl apply -f <path-to-generated-install-yaml>

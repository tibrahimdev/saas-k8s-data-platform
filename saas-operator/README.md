# SaaS Operator

## Appendix

### How this operator created
Initialize new project using `kubebuilder`.
```bash
mkdir saas-operator && cd saas-operator

# 1. Initialize with a generic domain
kubebuilder init --domain yourorg.io --repo github.com/yourorg/saas-operator

# 2. Switch to multi-group layout (essential for different product lines)
kubebuilder edit --multigroup=true
```

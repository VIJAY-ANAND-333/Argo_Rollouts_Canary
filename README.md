# Argo Rollouts: Canary Deployment on EKS

[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Argo](https://img.shields.io/badge/Argo-EF7B4D?style=flat&logo=argo&logoColor=white)](https://argoproj.github.io/)
[![AWS EKS](https://img.shields.io/badge/AWS_EKS-FF9900?style=flat&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/eks/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

A production-ready Progressive Delivery pipeline demonstrating Canary deployments using Argo Rollouts on Amazon EKS. This implementation provides incremental traffic shifting with manual validation gates to ensure high availability and minimize the blast radius of new releases.

---

##  Table of Contents

- [Overview](#overview)
- [Deployment Strategy](#deployment-strategy)
- [Technical Architecture](#technical-architecture)
- [Configuration](#configuration)
- [Operations Guide](#operations-guide)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

This repository demonstrates a production-grade Canary deployment strategy that:

-  Gradually shifts traffic from stable to canary versions
-  Implements automated observation windows
-  Provides manual promotion gates for validation
-  Enables instant rollback capabilities
-  Integrates with AWS ECR for container registry
-  Automates CI/CD through GitHub Actions

---

## 🚀 Deployment Strategy

The Canary strategy progressively moves traffic from a stable version to a new release through three distinct phases:

| Phase | Traffic Weight | Duration/Action | Description |
|:------|:---------------|:----------------|:------------|
| **Phase 1** | 25% |  2 minutes (Automatic) | Initial canary deployment with automated monitoring window |
| **Phase 2** | 50% |  Indefinite (Manual Gate) | Requires manual validation before proceeding |
| **Phase 3** | 100% | Full Promotion | Complete traffic shift after approval |

### Traffic Flow Diagram

```
Stable (100%) ──┐
                │ Phase 1 (2m auto)
                ├─► Stable (75%) + Canary (25%)
                │
                │ Phase 2 (manual gate)
                ├─► Stable (50%) + Canary (50%)
                │
                │ Phase 3 (after promotion)
                └─► Canary (100%) [now Stable]
```

---

##  Technical Architecture

### 1. **CI Pipeline** (GitHub Actions)

The automated build pipeline triggers on every code push

**Key Features:**
- **Immutable versioning** using Git SHA for traceability
- **Latest tag** for easy reference to current version
- **Secure authentication** with AWS ECR

### 2. **CD Implementation** (Argo Rollouts)

Unlike standard Kubernetes Deployments, the `Rollout` resource provides:

- **Dual ReplicaSet Management**: Maintains both Stable and Canary ReplicaSets
- **Intelligent Traffic Splitting**: Dynamically adjusts traffic weights
- **Automatic Reconciliation**: Ensures desired state matches actual state
- **Health Checks**: Monitors application health during rollout

**Architecture Benefits:**
- Zero-downtime deployments
- Reduced blast radius
- Easy rollback mechanism
- Observable deployment progress

---

##  Configuration

### Core Rollout Specification

The traffic management logic is defined in `rollout.yaml`

### Service Configuration (Traffic Splitting)


> **Note**: Argo Rollouts automatically manages traffic distribution between stable and canary pods through label manipulation.

---

##  Operations Guide

### Monitoring the Rollout

Visualize the rollout progress in real-time:

```bash
# Watch rollout status
kubectl argo rollouts get rollout vj-app-rollout --watch

# Alternative: Dashboard view
kubectl argo rollouts dashboard


### Manual Promotion

After validating the canary at 50% traffic:

```bash
# Promote to next phase
kubectl argo rollouts promote vj-app-rollout

# Check promotion status
kubectl argo rollouts status vj-app-rollout
```

### Emergency Rollback

Instantly revert 100% of traffic to the stable version:

```bash
# Abort the rollout
kubectl argo rollouts abort vj-app-rollout

# Verify rollback
kubectl argo rollouts get rollout vj-app-rollout
```

### Rollout History

View and manage rollout revisions:

```bash
# List all revisions
kubectl argo rollouts history vj-app-rollout

# Rollback to specific revision
kubectl argo rollouts undo vj-app-rollout --to-revision=3
```

---

##  Prerequisites

Before deploying this solution, ensure you have:

### Infrastructure
-  **Amazon EKS Cluster** (v1.24+)
-  **Amazon ECR Repository** configured
-  **IAM Roles** with ECR pull permissions for EKS nodes

### Tools & CLI
-  **kubectl** (v1.24+)
  ```bash
  kubectl version --client
  ```
-  **Argo Rollouts Controller** installed in cluster
  ```bash
  kubectl create namespace argo-rollouts
  kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
  ```
-  **kubectl-argo-rollouts plugin**
  ```bash
  # macOS
  brew install argoproj/tap/kubectl-argo-rollouts
  
  # Linux
  curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
  chmod +x kubectl-argo-rollouts-linux-amd64
  sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts
  ```
-  **AWS CLI** configured with appropriate credentials
  ```bash
  aws configure
  ```

### Permissions
- ECR read/write access for CI pipeline
- EKS cluster admin access for deployments
- GitHub repository with Actions enabled

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/argo-rollouts-canary-eks.git
cd argo-rollouts-canary-eks
```

### 2. Configure AWS ECR

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123256816654.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository (if not exists)
aws ecr create-repository --repository-name vj-app --region us-east-1
```

### 3. Set Up GitHub Secrets

Add the following secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (e.g., `us-east-1`)

### 4. Deploy the Rollout

```bash
# Apply the rollout configuration
kubectl apply -f rollout.yaml

# Apply service (if using traffic management)
kubectl apply -f service.yaml

# Verify deployment
kubectl argo rollouts get rollout vj-app-rollout
```

### 5. Trigger a Deployment

Push code changes to trigger the GitHub Actions workflow:

```bash
git add .
git commit -m "feat: add new feature"
git push origin main
```

---

##  Troubleshooting

### Common Issues

#### Rollout Stuck in Progressing State

```bash
# Check pod status
kubectl get pods -l app=vj-app

# Check rollout events
kubectl describe rollout vj-app-rollout

# Check controller logs
kubectl logs -n argo-rollouts -l app.kubernetes.io/name=argo-rollouts
```

#### Image Pull Errors

```bash
# Verify ECR authentication
aws ecr describe-repositories --repository-names vj-app

# Check node IAM role permissions
kubectl describe pod <pod-name> | grep -A 10 Events
```

#### Traffic Not Shifting

```bash
# Verify service selector matches rollout labels
kubectl get svc vj-app-service -o yaml

# Check rollout strategy
kubectl argo rollouts get rollout vj-app-rollout -o yaml
```

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for Progressive Delivery**
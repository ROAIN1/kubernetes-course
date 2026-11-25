# Kubernetes Course: Beginner to Production

A hands-on course. The goal is to **build and operate** Kubernetes in production, not only to know the theory.

## Who this is for

Beginners who know basic Linux and want to run Kubernetes in production. You need a laptop (macOS, Linux or Windows with WSL2) and Docker; everything runs locally on a free `kind` cluster.

## Learning plan (8–10 weeks, about 1 hour a day)

| Weeks | Notebooks | Milestone |
|---|---|---|
| 1 | 00–02 | Local cluster running; you can explain the control plane |
| 2–3 | 03–05 | Deploy a stateful app with Services, Ingress and storage |
| 4 | 06–07 | Config, secrets, resources and autoscaling |
| 5 | 08–09 | Secure the cluster; package your app as a Helm chart |
| 6 | 10–11 | Operators, GitOps with Argo CD |
| 7 | 12–13 | Monitoring, logging and solving incident tickets |
| 8–10 | 14–16 | Production architecture, managed Kubernetes, capstone projects |

## How to start

1. Open **[00-Start-Here-Lab-Setup.pdf](00-Start-Here-Lab-Setup.pdf)**. It installs Docker, kind and Helm, and creates your practice cluster, `kind-learn`.
2. Do the self-assessment in notebook 00. It tells you which notebook to start at.
3. Read each PDF top to bottom. Open Terminal in the cloned repo folder (`git clone` it, then `cd kubernetes-course`) and paste the commands as you reach them:
   - grey **Terminal** boxes are commands;
   - blue **Create file** boxes are also commands: pasting one creates that YAML file under `labs/`;
   - green **Answer** boxes hold the quiz answers. Try first, then read.

## Notebooks

| # | Notebook | What you learn |
|---|---|---|
| 00 | [Start Here – Lab Setup](00-Start-Here-Lab-Setup.pdf) | Tools, local cluster, self-assessment, learning plan |
| 01 | [Prerequisites](01-Prerequisites.pdf) | Linux internals, networking, Docker, multi-stage builds |
| 02 | [Kubernetes Fundamentals](02-Kubernetes-Fundamentals.pdf) | Architecture, control plane, kubelet, kubectl, labels |
| 03 | [Workloads](03-Workloads.pdf) | Pods, Deployments, StatefulSets, DaemonSets, Jobs, probes |
| 04 | [Networking](04-Networking.pdf) | Services, CoreDNS, Ingress, Gateway API, NetworkPolicy, CNI |
| 05 | [Storage](05-Storage.pdf) | PV/PVC, StorageClass, CSI, snapshots, backup and restore |
| 06 | [Config and Secrets](06-Config-and-Secrets.pdf) | ConfigMaps, Secrets, External Secrets, encryption at rest |
| 07 | [Scheduling and Resources](07-Scheduling-and-Resources.pdf) | Requests and limits, QoS, affinity, taints, PDB, HPA |
| 08 | [Security](08-Security.pdf) | RBAC, Pod Security, admission, image scanning, cert-manager |
| 09 | [Helm](09-Helm.pdf) | Charts and templates; build a reusable production chart |
| 10 | [Advanced Kubernetes](10-Advanced-Kubernetes.pdf) | CRDs, controllers, operators, finalizers, API internals |
| 11 | [CI/CD and GitOps](11-CICD-and-GitOps.pdf) | Pipelines, Argo CD, blue-green, canary, rollbacks |
| 12 | [Observability](12-Observability.pdf) | Prometheus, Grafana, Alertmanager, Loki, OpenTelemetry |
| 13 | [Troubleshooting and Incidents](13-Troubleshooting-and-Incidents.pdf) | Real incident tickets to investigate, plus an RCA template |
| 14 | [Production Architecture](14-Production-Architecture.pdf) | HA, DR, upgrades, multi-tenancy, readiness checklist |
| 15 | [Cloud Kubernetes](15-Cloud-Kubernetes.pdf) | EKS, AKS, GKE and OKE |
| 16 | [Capstone Projects](16-Capstone-Projects.pdf) | 13 projects, plus a portfolio on GitHub |

## Every topic follows the same steps

What it is → why we need it → how it works inside → a real production scenario → a hands-on lab → troubleshooting → lab vs production → a short quiz with answers.

Each notebook ends with interview questions, a practical assignment, and a "break it" challenge.

## Safety rules

- Every lab first checks that your kubectl context is `kind-learn`. If it isn't, the lab stops. That way you can never run a lab against a real cluster by mistake.
- Commands that create paid cloud resources (in notebooks 15 and 16) only run if you set `CONFIRM_CLOUD=yes` yourself.
- To reset everything: `kind delete cluster --name learn`, then run notebook 00 again.

## Study tips

1. **Understand:** read the "how it works inside" part twice.
2. **Implement:** type the YAML yourself before you paste the given box.
3. **Break it:** do every "break it" challenge before you open the answer.
4. **Production:** for every feature, read the "lab vs production" table and think about how you would do it on OKE.

## Files

- `labs/` holds the YAML and config files that the notebooks create when you run them.
- `_src/` holds the plain-text sources and `_notebooks/` the Jupyter versions. Rebuild:
  `python3 _tools/mknb.py _src/03-workloads.txt _notebooks/03-Workloads.ipynb` then `python3 _tools/mkpdf.py _notebooks/*.ipynb --out .`

# ScaleTrail
An opinionated boilerplate and infrastructure toolkit designed for solo developers and small teams to launch SaaS products faster.

ScaleTrail is a collection of templates — including Terraform, GitHub Actions, CI/CD scripts, Django, and Next.js — for quickly creating the infrastructure and boilerplate code needed for new projects.

**Tech Stack:** 
Terraform · GitHub Actions · Docker · Django · Next.js · NGINX · PostgreSQL · Linode · Cloudflare

## Motivation
I have a lot of project ideas (particularly SaaS project ideas). I want to deploy those project ideas quickly in the real world without needing to fight with infrastructure configuration. I also want to do so with predictable pricing.

## Core Principles
ScaleTrail should make projects:
- Simple
    - It should be easy to get started and deploy something that works.
    - It should be easy to understand the code and make modifications if needed.
    - Infrastructure costs should be predictable and easy to understand.
- Scalable
    - As a project grows, it should be easy to manage the operations side (i.e. managing users and related tasks).
    - Infrastructure resources should be easy to scale if needed.
    - n+1-able: Multiple projects should be able to be spun up quickly.
- Secure
    - It should implement security best practices (loaded term, I know).
    - It should only allow trusted traffic.
    - Packages should be updated frequently without introducing breaking changes.

## Prerequisites
ScaleTrail assumes you have a Linode account, a Cloudflare account, and a few existing configurations in each.
**Linode**
1. Create a new SSH key pair. ScaleTrail assumes your public key is at the following location `~/.ssh/scaletrail_project.pub`.
2. Log in to Linode and add your SSH key: https://cloud.linode.com/profile/keys

**Cloudflare**
1. Create a Cloudflare account if you don't already have one.
2. Add a new domain within Cloudflare, and configure Cloudflare DNS for the new domain.

## New project workflow
**Install scaletrail CLI**
1. `cd` into the `cli` directory
2. Create the CLI virtual environment: `python -m venv cli_venv`
3. Activate the CLI virtual environment: `source cli_venv/bin/activate`
4. Upgrade pip: `pip install --upgrade pip`
5. Install CLI dependencies: `pip install .`

**Initialize a new project**
1. Run `scaletrail init`
2. Complete the initialization steps.

## Making changes
**Terraform**
1. Navigate to the project folder for the project that you want to make changes for.
2. Make changes to main.tf, terraform.tfvars, etc.
3. Run `terraform plan -var-file=terraform.tfvars` to preview what infrastructure changes will be made.
4. Run `terraform apply -var-file=terraform.tfvars` to apply changes.

## Roadmap
- [ ] Build out scaletrail cli
- [ ] README updates to better explain prerequisites
- [ ] Django setup automation
- [ ] Next.js setup automation
- [ ] AWS support
- [ ] GCP support
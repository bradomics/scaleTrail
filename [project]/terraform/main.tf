terraform {
  required_providers {
    linode = {
      source  = "linode/linode"
      version = "3.0.0"
    }
  }
}

provider "linode" {
  # Get this from Linode Cloud Manager > API Tokens > 'Create a Personal Access Token': https://cloud.linode.com/profile/tokens
  token = var.linode_token
}

resource "linode_instance" "scaletrail_project" {
  label     = "scaletrail-project"
  region    = "us-central"
  type      = "g6-standard-2"
  image     = "linode/ubuntu24.04"
  tags      = ["django", "nextjs", "nginx", "scaletrail-project", "api.scaletrail-project.net"]
  root_pass = var.root_pass
  backups_enabled = true

  authorized_keys = [
    trimspace(replace(file("~/.ssh/scaletrail_project.pub"), "\n", ""))
  ]
}

# Chunk GitHub's IPs (needed for GitHub Actions) into rules of 255 IPs each
# as Linode firewall rules have a max of 255 IPs per rule.
locals {
  gh_actions_ipv4_chunks = [
    for i in range(0, length(var.gh_actions_ipv4), 255) :
    slice(var.gh_actions_ipv4, i, min(i + 255, length(var.gh_actions_ipv4)))
  ]

  gh_actions_ipv6_chunks = [
    for i in range(0, length(var.gh_actions_ipv6), 255) :
    slice(var.gh_actions_ipv6, i, min(i + 255, length(var.gh_actions_ipv6)))
  ]

  gh_actions_ipv4_inbound_rules = [
    for pair in local.gh_actions_ipv4_chunks : {
      label    = "gh-actions-ipv4-${index(local.gh_actions_ipv4_chunks, pair)}"
      action   = "ACCEPT"
      protocol = "TCP"
      ports    = "22"
      ipv4     = pair
      ipv6     = null
    }
  ]

  gh_actions_ipv6_inbound_rules = [
    for pair in local.gh_actions_ipv6_chunks : {
      label    = "gh-actions-ipv6-${index(local.gh_actions_ipv6_chunks, pair)}"
      action   = "ACCEPT"
      protocol = "TCP"
      ports    = "22"
      ipv4     = null
      ipv6     = pair
    }
  ]

  gh_actions_inbound_rules = concat(
    local.gh_actions_ipv4_inbound_rules,
    local.gh_actions_ipv6_inbound_rules
  )
}


resource "linode_firewall" "scaletrail_project_firewall" {
  label = "scaletrail-project-firewall"

  # Allow GitHub Actions, Cloudflare, developer IPs, and project-specific inbound rules
  dynamic "inbound" {
    for_each = concat(var.developer_inbound_ips,
      var.cloudflare_inbound_rules,
      var.project_inbound_rules,
      local.gh_actions_inbound_rules # 'local' is required here
    )
    content {
      label    = inbound.value.label
      action   = inbound.value.action
      protocol = inbound.value.protocol
      ports    = inbound.value.ports
      ipv4     = inbound.value.ipv4
      ipv6     = inbound.value.ipv6
    }
  }

  inbound_policy = "DROP"

  outbound_policy = "ACCEPT"

  linodes = [linode_instance.scaletrail_project.id]
}

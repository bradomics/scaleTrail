output "project_image" { 
    value = linode_instance.scaletrail_project.image
}
output "project_tags" {
    value = linode_instance.scaletrail_project.tags
}

# Flat list of all inbound rule labels (developer + project + Cloudflare + GH Actions)
output "firewall_inbound_labels" {
  description = "Labels for all inbound firewall rules"
  value = [
    for r in concat(
      var.developer_inbound_ips,
      var.project_inbound_rules,
      var.cloudflare_inbound_rules,
      local.gh_actions_inbound_rules
    ) : r.label
  ]
}
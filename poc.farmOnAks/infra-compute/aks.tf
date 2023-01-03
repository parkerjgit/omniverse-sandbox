locals {
  aks_namespace = "aks"
  aks_cluster_name = "${local.prefix}-${local.aks_namespace}-cluster"
  aks_cluster_dns_prefix = "${local.prefix}-${local.aks_namespace}-dnsprefix"
  aks_cluster_node_pool_name = "${local.prefix}-${local.aks_namespace}-nodepool"
}

# see https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = local.aks_cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = local.aks_cluster_dns_prefix

  linux_profile {
    admin_username = "azureuser"

    ssh_key {
      key_data = file(var.ssh_public_key)
    }
  }

  default_node_pool {
    name       = "nodepool"
    node_count = 2

    # see https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-gpu
    vm_size    = "Standard_NV6" 
    # vm_size    = "Standard_NV12s_v3" # exceeds approved Total Regional Cores quota

    node_labels = {vm_type: "GPU"}
    os_sku = "Ubuntu"
  }

  network_profile {
    load_balancer_sku = "standard"
    network_plugin = "kubenet"
  }

  identity {
    type = "SystemAssigned"
  }
}

output "client_key" {
    value = azurerm_kubernetes_cluster.aks.kube_config.0.client_key
    sensitive = true
}

output "client_certificate" {
    value = azurerm_kubernetes_cluster.aks.kube_config.0.client_certificate
    sensitive = true
}

output "cluster_ca_certificate" {
    value = azurerm_kubernetes_cluster.aks.kube_config.0.cluster_ca_certificate
    sensitive = true
}

output "cluster_username" {
    value = azurerm_kubernetes_cluster.aks.kube_config.0.username
    sensitive = true
}

output "cluster_password" {
    value = azurerm_kubernetes_cluster.aks.kube_config.0.password
    sensitive = true
}

output "kube_config" {
    value = azurerm_kubernetes_cluster.aks.kube_config_raw
    sensitive = true
}

output "host" {
    value = azurerm_kubernetes_cluster.aks.kube_config.0.host
    sensitive = true
}
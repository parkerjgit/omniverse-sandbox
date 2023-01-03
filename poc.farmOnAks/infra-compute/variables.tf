variable "resource_group_name" {
  description = "Name of resource group"
  type        = string
}

variable "env" {
  description = "Name of environment"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "AWS region"
  type        = string
  default     = "eastus"
}

variable "namespace" {
  description = "Resource namespace (prefix)"
  type        = string
  default     = "faks"
}

variable "project" {
  description = "Project name (no spaces)"
  type        = string
  default     = "omniverse-farm-on-aks"
}

variable "ssh_public_key" {
  description = "File path to public SSH key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}
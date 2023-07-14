variable "key_path" {
  type = string
}

variable "gcp_project" {
  type = string
}

// k8s
variable "cluster_name" {
  type = string
}

variable "cluster_location" {
  type = object({
    cluster = string
  })
}

variable "cluster_autoscaler" {
  type = object({
    enabled = bool,
    max_cpu = number,
    min_cpu = number,
    min_mem = number,
    max_mem = number,

  })
}

variable "node_pool_name" {
  type = string
}

variable "node_autoscaler" {
  type = object({
    enabled = bool,
    max_count = number,
    min_count = number
  })
}

variable "node_config" {
  type = object({
    machine_type = string,
    image_type = string,
    disk_size_gb = number,
    disk_type = string
  })
}

variable "max_unavailable" {
  type = number
}

variable "max_surge" {
  type = number
}
variable "auto_repair" {
  type = bool
}

variable "auto_upgrade" {
  type = bool
}

// static ip
variable "static_ip_name" {
  type = string
}

// cloud dns
variable "domain_name" {
  type = string
}

variable "domain_host" {
  type = string
}

variable "subdomain_host" {
  type = string
}

variable "cname_subdomain" {
  type = string
}
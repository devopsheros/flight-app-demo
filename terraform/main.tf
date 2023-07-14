//k8s cluster
resource "google_container_cluster" "primary" {
  name = var.cluster_name
  location = var.cluster_location["cluster"]

  remove_default_node_pool = true
  initial_node_count = 1

  cluster_autoscaling {
    enabled = var.cluster_autoscaler["enabled"]
    resource_limits {
      resource_type = "cpu"
      maximum = var.cluster_autoscaler["max_cpu"]
      minimum = var.cluster_autoscaler["min_cpu"]
    }
    resource_limits {
      resource_type = "memory"
      maximum = var.cluster_autoscaler["max_mem"]
      minimum = var.cluster_autoscaler["min_mem"]
    }
  }
  maintenance_policy {
    recurring_window {
      end_time = "2023-07-13T06:00:00Z"
      recurrence = "FREQ=DAILY"
      start_time = "2023-07-13T02:00:00Z"
    }
  }
}

//k8s node pool

resource "google_container_node_pool" "node_pool" {
  name = var.node_pool_name
  cluster = google_container_cluster.primary.name
  location = var.cluster_location["cluster"]
  autoscaling {
    max_node_count = var.node_autoscaler["enabled"] == true ? var.node_autoscaler["max_count"] : null
    min_node_count = var.node_autoscaler["enabled"] == true ? var.node_autoscaler["min_count"] : null
  }
  management {
    auto_repair = var.auto_repair
    auto_upgrade = var.auto_upgrade
  }
  node_config {
    machine_type = var.node_config["machine_type"]
    image_type = var.node_config["image_type"]
    disk_size_gb = var.node_config["disk_size_gb"]
    disk_type = var.node_config["disk_type"]
  }
  upgrade_settings {
    max_surge = var.max_surge
    max_unavailable = var.max_unavailable
  }
}

// static ip
resource "google_compute_address" "static-ip" {
  name          = var.static_ip_name
  address_type  = "EXTERNAL"
  region        = "us-central1"
}

// cloud dns
resource "google_dns_managed_zone" "my_dns_zone" {
  name        = var.domain_name
  description = "Flight App DNS Zone"
  dns_name    = var.domain_host
}

resource "google_dns_record_set" "a_record_subdomain" {
  name    = var.subdomain_host
  type    = "A"
  ttl     = 300
  managed_zone = google_dns_managed_zone.my_dns_zone.name
  rrdatas = [
    google_compute_address.static-ip.address
  ]
}

resource "google_dns_record_set" "cname_record_subdomain" {
  name    = var.cname_subdomain
  type    = "CNAME"
  ttl     = 300
  managed_zone = google_dns_managed_zone.my_dns_zone.name
  rrdatas = [
    var.subdomain_host
  ]
}
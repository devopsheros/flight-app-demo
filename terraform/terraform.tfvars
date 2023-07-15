//key_path = "C:\\Users\\Alon\\PycharmProjects\\project1\\venv\\flight-app-demo\\key.json"
gcp_project = "devops-project-387209"

// k8s
cluster_name = "flight-app-demo-cluster"
cluster_location = {
  cluster = "us-central1-a"
}

cluster_autoscaler = {
  enabled = true,
  max_cpu = 16,
  min_cpu = 1,
  max_mem = 20,
  min_mem = 1
}


node_pool_name ="flight-app-demo-node"

node_config = {
  machine_type = "e2-medium"
  image_type = "cos_containerd"
  disk_size_gb = 100
  disk_type = "pd-standard"
}

node_autoscaler = {
  enabled = true,
  max_count = 3,
  min_count = 0
}

auto_repair = true
auto_upgrade = true

max_surge = 1
max_unavailable = 1

// static ip
static_ip_name = "app-lb"

// cloud dns

domain_name       = "flight-app-demo-zone"
domain_host       = "devopsheros.com."
subdomain_host    = "flight-app.devopsheros.com."
cname_subdomain   = "www.flight-app.devopsheros.com."
provider "google" {
  project     = "gcp-terraform-test-444406"
  credentials = "gcp_key.json"
}

# resource "google_storage_bucket" "tftest" {
#   name          = "bucket_tftest_001"
#   location      = "US"
  
# }

resource "google_compute_instance" "tf_instance" {

  name         = "my-instance"
  machine_type = "n2-standard-2"
  zone         = "us-central1-a"


  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      labels = {
        my_label = "value"
      }
    }
  }
network_interface {
    network = "default"
}
  metadata_startup_script = "echo hi > /test.txt"
}
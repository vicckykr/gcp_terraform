from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI


resource_reader_agent = Agent(
    role="Azure Resource Reader",
    goal="Analyze Azure Terraform configurations and extract resource details.",
    backstory="Specialized in reading and understanding Azure Terraform resources.",
    verbose=True,
    allow_delegation=True,
)

converter_agent = Agent(
    role="Azure-to-GCP Converter",
    goal="Convert Azure Terraform resource definitions to equivalent GCP Terraform configurations.",
    backstory="Expert in mapping Azure resources to equivalent GCP resources.",
    verbose=True,
    allow_delegation=True,
)

validator_agent = Agent(
    role="Terraform Validator",
    goal="Validate the generated GCP Terraform configuration for correctness and completeness.",
    backstory="Ensures that the GCP Terraform file meets syntax and semantic standards.",
    verbose=True,
    allow_delegation=True,
)


read_azure_task = Task(
    description=(
        "Read and analyze the provided Azure Terraform file `azure.tf` to extract details about resources, "
        "their configurations, and relationships."
    ),
    expected_output="A structured summary of all Azure resources in the Terraform file.",
    agent=resource_reader_agent,
)

convert_to_gcp_task = Task(
    description=(
        "Using the resource summary from the Azure Reader Agent, generate an equivalent GCP Terraform configuration. "
        "Include all Azure resources, such as storage accounts, virtual networks, subnets, and VMs. Do not miss any azure resources"
    ),
    expected_output="A Terraform file defining equivalent GCP resources.",
    agent=converter_agent,
)

validate_gcp_task = Task(
    description=(
        "Validate the GCP Terraform file generated by the Converter Agent. Check for syntax errors, "
        "resource compatibility, and completeness.Also make sure all azure resources are converted in gcp resources"
    ),
    expected_output="A validation report confirming correctness and readiness for deployment.",
    agent=validator_agent,
)


terraform_conversion_crew = Crew(
    agents=[resource_reader_agent, converter_agent, validator_agent],
    tasks=[read_azure_task, convert_to_gcp_task, validate_gcp_task],
    manager_llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
    verbose=True,
)

azure_terraform_file = """
provider "azurerm" {
  features {}
}

resource "azurerm_storage_account" "example" {
  name                     = "examplestorageacct"
  resource_group_name      = "example-resource-group"
  location                 = "East US"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    environment = "Production"
  }
}

resource "azurerm_virtual_machine" "example" {
  name                  = "example-vm"
  location              = "East US"
  resource_group_name   = "example-resource-group"
  network_interface_ids = [azurerm_network_interface.example.id]
  vm_size               = "Standard_DS1_v2"

  storage_os_disk {
    name              = "example-os-disk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  os_profile {
    computer_name  = "hostname"
    admin_username = "adminuser"
    admin_password = "Password1234!"
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }

  tags = {
    environment = "Production"
  }
}
"""

crew_inputs = {
    "azure_terraform_file": azure_terraform_file,
    "project_id": "your-gcp-project-id",
    "region": "us-central1",
}

result = terraform_conversion_crew.kickoff(inputs=crew_inputs)


output_file = "gcp_resources_complete.tf"
#Logger.info(f"Writing the GCP Terraform configuration to {output_file}...")
with open(output_file, "w") as file:
    file.write(result)

print("\nGCP Terraform Configuration:")
print(result)

Brings up a Rocky Linux 9 environment on Azure.


## Usage:

* Modify `001-variable.tf` and change/update the following values....

```
variable "resource_group_name_prefix" {
  default     = "test2024"
  description = "Prefix of the resource group name that's combined with a random ID so name is unique in your Azure subscription."
}

  default = {
    Owner   = "",
    Team    = "Horizon",
    Project = "test2024"
}
```

* (Optional) modify the username in `002-main.tf`

```
resource "azurerm_linux_virtual_machine" "..." {
...
  admin_username      = "pentest"
...
}
admin_ssh_key {
  username   = "pentest"
  ...
}
```

* Initialize Terraform

`terraform init`

* Create Terraform plan

`terraform plan -out "tfplan.plan"`

* Apply Terraform plan

`terraform apply tfplan.plan`

* Retrieve ssh key

```
terraform output -raw tls_private_key > "../id_rsa"
chmod 600 ../id_rsa
```

* Connect to the system, copy and run `install.sh`

```
ssh -i ../id_rsa <admin_username>@<Machine IP Address>
chmod +x install.sh
./install.sh

# Retrive the login password
cat /home/$(whoami)/.login_cred
```

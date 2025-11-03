resource "azurerm_linux_virtual_machine" "CoreVM" {
  name                = "opennms-pt-corevm"
  resource_group_name = azurerm_resource_group.CoreVM.name
  location            = azurerm_resource_group.CoreVM.location
  size                = var.vm_size
  admin_username      = "pentest"
  network_interface_ids = [
    azurerm_network_interface.CoreVM.id,
  ]

  admin_ssh_key {
    username   = "pentest"
    public_key = tls_private_key.connection_key.public_key_openssh
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "erockyenterprisesoftwarefoundationinc1653071250513"
    offer     = "rockylinux-9"
    sku       = "rockylinux-9"
    version   = "9.0.0"
  }
  plan {
    name      = "rockylinux-9"
    product   = "rockylinux-9"
    publisher = "erockyenterprisesoftwarefoundationinc1653071250513"
  }

  tags = var.tags
}

### resource "azurerm_virtual_machine_extension" "CoreVM" {
###   name                 = "install_OpenNMS_Core"
###   virtual_machine_id   = azurerm_linux_virtual_machine.CoreVM.id
###   publisher            = "Microsoft.Azure.Extensions"
###   type                 = "CustomScript"
###   type_handler_version = "2.0"
### 
###     protected_settings = <<PROT
###     {
###         "script": "${base64encode(file(var.installationFile))}"
###     }
###     PROT
### 
###   tags = var.tags
### }


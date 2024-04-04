resource "azurerm_linux_virtual_machine" "MinionVM" {
  count               = var.minion_node_numbers
  name                = "opennms-bm-mvm-${count.index}"
  resource_group_name = azurerm_resource_group.CoreVM.name
  location            = azurerm_resource_group.CoreVM.location
  size                = var.vm_size
  admin_username      = "opennms"
  network_interface_ids = [
    azurerm_network_interface.MinionVMinternalIP[count.index].id,
  ]

  #admin_ssh_key {
  #  username   = "opennms"
  #  public_key = file("~/.ssh/id_rsa.pub")
  #}
  admin_ssh_key {
    username   = "opennms"
    public_key = tls_private_key.connection_key.public_key_openssh
  }


  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18_04-lts-gen2"
    version   = "latest"
  }

  depends_on = [
    azurerm_linux_virtual_machine.CoreVM
  ]

  tags = var.tags
}

resource "azurerm_network_interface" "MinionVMinternalIP" {
  count               = var.minion_node_numbers
  name                = "opennms-bm-mvm-nic${count.index}"
  location            = azurerm_resource_group.CoreVM.location
  resource_group_name = azurerm_resource_group.CoreVM.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.CoreVM.id
    private_ip_address_allocation = "Dynamic"
  }

  tags = var.tags

}


resource "azurerm_virtual_machine_extension" "MinionVM" {
  count                = var.minion_node_numbers
  name                 = "install_OpenNMS_Minion"
  virtual_machine_id   = azurerm_linux_virtual_machine.MinionVM[count.index].id
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.0"

  settings = <<SETTINGS
    {
        "commandToExecute": "wget -O /tmp/autoinstall.sh https://raw.githubusercontent.com/mershad-manesh/test/main/autoinstallminion.sh  && chmod +x /tmp/autoinstall.sh && /tmp/autoinstall.sh > /home/opennms/log.txt 2>&1"
    }
SETTINGS


  tags = var.tags
}
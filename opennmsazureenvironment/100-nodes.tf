resource "azurerm_linux_virtual_machine" "NodeVM" {
  count               = var.child_node_numbers
  name                = "opennms-bm-nvm-${count.index}"
  resource_group_name = azurerm_resource_group.CoreVM.name
  location            = azurerm_resource_group.CoreVM.location
  size                = var.vm_size
  admin_username      = "opennms"
  network_interface_ids = [
    azurerm_network_interface.NodeVMinternalIP[count.index].id,
  ]

  admin_ssh_key {
    username   = "opennms"
    public_key = file("~/.ssh/id_rsa.pub")
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

resource "azurerm_network_interface" "NodeVMinternalIP" {
  count               = var.child_node_numbers
  name                = "opennms-bm-nvm-nic${count.index}"
  location            = azurerm_resource_group.CoreVM.location
  resource_group_name = azurerm_resource_group.CoreVM.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.CoreVM.id
    private_ip_address_allocation = "Dynamic"
  }


  tags = var.tags

}

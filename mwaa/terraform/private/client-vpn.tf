# AWS client VPN (for the private Airflow web server)

resource "aws_security_group" "client_vpn" {
  name        = "${var.mwaa_name}-mwaa-client-vpn"
  description = "Security Group for the ${var.mwaa_name} MWAA Environment Client VPN"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "UDP"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All ingress VPN traffic."
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
    description = "All egress traffic."
  }

  tags = merge(local.tags, {
    Name = "${var.mwaa_name}-mwaa-client-vpn"
  })
}

#############################################################
# Client VPN (for Airflow web server inside private subnet) #
#############################################################
resource "aws_ec2_client_vpn_endpoint" "ec2_client_vpn_endpoint" {
  description            = "Client VPN for MWAA"
  server_certificate_arn = aws_acm_certificate.server.arn
  client_cidr_block      = var.client_vpn_cidr_block
  split_tunnel           = true

  authentication_options {
    type                       = "certificate-authentication"
    root_certificate_chain_arn = aws_acm_certificate.client.arn
  }

  connection_log_options {
    enabled = false
  }

  tags = merge(local.tags, {
    Name = "${var.mwaa_name}-mwaa"
  })
}

resource "aws_ec2_client_vpn_network_association" "ec2_client_vpn_network_associations" {
  count                  = length(aws_subnet.private_subnets)
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.ec2_client_vpn_endpoint.id
  subnet_id              = aws_subnet.private_subnets[count.index].id
  security_groups = [
    aws_security_group.mwaa.id,
    aws_security_group.client_vpn.id
  ]
}

resource "aws_ec2_client_vpn_authorization_rule" "ec2_client_vpn_authorization_rule" {
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.ec2_client_vpn_endpoint.id
  target_network_cidr    = aws_vpc.vpc.cidr_block
  authorize_all_groups   = true
}

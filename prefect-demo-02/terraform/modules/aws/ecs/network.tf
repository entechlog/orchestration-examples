resource "aws_security_group" "prefect_worker" {
  name        = "prefect-worker-sg-${var.name}"
  description = "ECS Prefect worker"
  vpc_id      = var.vpc_id
}

resource "aws_security_group_rule" "prefect_worker_inbound" {

  description       = "Prefect Worker Inbound"
  type              = "ingress"
  security_group_id = aws_security_group.prefect_worker.id
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  self              = true

}

resource "aws_security_group_rule" "prefect_worker_outbound" {

  description       = "Prefect Worker Outbound"
  type              = "egress"
  security_group_id = aws_security_group.prefect_worker.id
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]

}
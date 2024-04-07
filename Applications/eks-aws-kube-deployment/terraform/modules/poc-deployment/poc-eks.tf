locals {
  map_accounts = [
    "153932877404"
  ]

  map_users = [
    {
      userarn  = "arn:aws:iam::153932877404:user/cicd-workflow"
      username = "cicd-workflow"
    },
    {
      userarn  = "arn:aws:iam::153932877404:user/root"
      username = "root"
    }
  ]

}

resource "aws_eks_cluster" "poc_eks_cluster" {
  name     = "${var.environment}-${var.project_name}-${var.application}"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.29"

  enabled_cluster_log_types = ["api", "audit"]

  vpc_config {
    subnet_ids = concat(aws_subnet.public_subnets[*].id, aws_subnet.private_subnets[*].id)
    security_group_ids = [aws_security_group.control_plane_sg.id]

    endpoint_public_access  = true
    endpoint_private_access = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }

  # kubernetes_network_config {
  #   service_ipv4_cidr = "10.100.0.0/16"
  # } # TODO: to check it

  depends_on = [
    aws_security_group.control_plane_sg
  ]
}

# Auth user: https://github.com/terraform-aws-modules/terraform-aws-eks/blob/v17.24.0/aws_auth.tf
resource "kubernetes_config_map" "aws_auth" {

  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
    labels = merge(
      {
        "app.kubernetes.io/managed-by" = "Terraform"
        "terraform.io/module" = "terraform-aws-modules.eks.aws"
      },
    )
  }

  data = {
    mapUsers    = yamlencode(local.map_users)
    mapAccounts = yamlencode(local.map_accounts)
  }

  depends_on = [
    aws_eks_cluster.poc_eks_cluster
  ]
}

resource "aws_cloudwatch_log_group" "poc_eks_cluster_logs" {
  name              = "/aws/eks/${aws_eks_cluster.poc_eks_cluster.name}/cluster"
  retention_in_days = var.log_retention_in_days

  depends_on = [
    aws_eks_cluster.poc_eks_cluster
  ]
}

resource "aws_eks_node_group" "poc_eks_node_group" {
  cluster_name    = aws_eks_cluster.poc_eks_cluster.name
  node_group_name = "${var.environment}-${var.project_name}-${var.application}-worker-node"
  node_role_arn   = aws_iam_role.eks_worker_node_role.arn

  subnet_ids = concat(aws_subnet.public_subnets[*].id, aws_subnet.private_subnets[*].id)

  scaling_config {
    desired_size = 2
    min_size     = 2
    max_size     = 2
  }

  instance_types = ["t2.medium"]
  disk_size      = 20
  version        = "1.29"
  ami_type       = "AL2_x86_64"
}


# resource "kubernetes_config_map_v1" "knitneo4jconfigmap" {
#   metadata {
#     name      = "${var.environment}${var.project}knitneo4j-configmap"
#     namespace = data.kubernetes_namespace_v1.knitneo4jnamespace.metadata[0].name
#   }

#   data = {
#     NEO4J_AUTH = data.aws_secretsmanager_secret_version.knitneo4j_credentials.secret_string
#   }
#   lifecycle {
#     ignore_changes = [
#       data
#     ]
#   }
# }



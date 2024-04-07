data "aws_iam_policy_document" "eks_worker_node_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "eks_cluster_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eks_worker_node_role" {
  name               = "${var.environment}-${var.project_name}-${var.application}-worker-node-role"
  assume_role_policy = data.aws_iam_policy_document.eks_worker_node_assume_role_policy.json

  description = "Allows EKS EC2 instances to call AWS services on behalf of the user."
}

resource "aws_iam_role" "eks_cluster_role" {
  name               = "${var.environment}-${var.project_name}-${var.application}-cluster-role"
  assume_role_policy = data.aws_iam_policy_document.eks_cluster_assume_role_policy.json

  description = "Allows EKS to manage clusters and resources."
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy_attachment" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
  ])

  role       = aws_iam_role.eks_worker_node_role.name
  policy_arn = each.value
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

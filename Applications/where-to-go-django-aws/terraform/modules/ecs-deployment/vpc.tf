locals {
  len_public_subnets  = max(length(var.public_subnets))
  len_private_subnets = max(length(var.private_subnets))

  create_public_subnets  = var.create_vpc && local.len_public_subnets > 0
  create_private_subnets = var.create_vpc && local.len_private_subnets > 0

  nat_gateway_count = var.single_nat_gateway ? 1 : var.one_nat_gateway_per_az ? length(var.availability_zone) : 0 #TODO: add max subnet length
}

resource "aws_vpc" "backend_project_vpc" {
  count = var.create_vpc ? 1 : 0

  cidr_block = var.cidr

  tags = {
    "Name" = local.full_name_env_app
  }
}

resource "aws_subnet" "public_subnets" {
  count = local.create_public_subnets && local.len_public_subnets >= length(var.availability_zone) ? local.len_public_subnets : 0

  vpc_id = aws_vpc.backend_project_vpc[0].id

  cidr_block        = element(concat(var.public_subnets, [""]), count.index)
  availability_zone = length(regexall("^[a-z]{2}-", element(var.availability_zone, count.index))) > 0 ? element(var.availability_zone, count.index) : null
  map_public_ip_on_launch = var.map_public_ip

  tags = {
    Name = "public-subnet-${var.subnet_names[count.index]}"
  }
}

resource "aws_subnet" "private_subnets" {
  count = local.create_private_subnets && local.len_private_subnets >= length(var.availability_zone) ? local.len_public_subnets : 0

  vpc_id = aws_vpc.backend_project_vpc[0].id

  cidr_block        = element(concat(var.private_subnets, [""]), count.index)
  availability_zone = length(regexall("^[a-z]{2}-", element(var.availability_zone, count.index))) > 0 ? element(var.availability_zone, count.index) : null

  tags = {
    Name = "private-subnet-${var.subnet_names[count.index]}"
  }
}

# Route table
resource "aws_route_table" "public_route_table" {
  count = local.create_public_subnets ? 1 : 0

  vpc_id = aws_vpc.backend_project_vpc[0].id

  tags = merge(
    { "Name" = "${local.full_name_env_app}-RT-public" },
  )
}

resource "aws_route_table_association" "public_route_table_association" {
  count = local.create_public_subnets ? local.len_public_subnets : 0

  subnet_id      = element(aws_subnet.public_subnets[*].id, count.index)
  route_table_id = aws_route_table.public_route_table[0].id
}

resource "aws_route_table" "private_route_table" {
  count = local.create_private_subnets && local.len_private_subnets > 0 ? local.nat_gateway_count : 0

  vpc_id = aws_vpc.backend_project_vpc[0].id

  tags = merge(
    {
      "Name" = var.single_nat_gateway ? "${local.full_name_env_app}-RT-private-one-AZ" : "${local.full_name_env_app}-RT-${var.subnet_names[count.index]}-private"
    },
  )
}

resource "aws_route_table_association" "private_route_table_association" {
  count = local.create_private_subnets && length(aws_route_table.private_route_table) > 0 ? local.len_private_subnets : 0

  subnet_id      = element(aws_subnet.private_subnets[*].id, count.index)

  route_table_id = element(
    aws_route_table.private_route_table[*].id,
    var.single_nat_gateway ? 0 : count.index,
  )
}

# Internet Gateway
resource "aws_internet_gateway" "vpc_internet_gateway" {
  count = local.create_public_subnets && var.create_igw ? 1 : 0

  vpc_id = aws_vpc.backend_project_vpc[0].id

  tags = merge(
    { "Name" = "${local.full_name_env_app}-IGW" },
  )
}

# Route IGW for public subnets
resource "aws_route" "public_internet_gateway_route" {
  count = local.create_public_subnets && var.create_igw ? 1 : 0

  route_table_id         = aws_route_table.public_route_table[0].id
  gateway_id             = aws_internet_gateway.vpc_internet_gateway[0].id
  destination_cidr_block = "0.0.0.0/0"
}

# Elastic IP
resource "aws_eip" "elastic_ip_for_nat_gw" {
  count = var.create_vpc && var.create_nat_gw ? local.nat_gateway_count : 0

  # associate_with_private_ip = "10.0.0.5" #TODO

  tags = merge(
    {
      "Name" = format(
        "${local.full_name_env_app}-EIP-%s",
        element(var.availability_zone, var.single_nat_gateway ? 0 : count.index),
      )
    }
  )

  depends_on = [
    aws_internet_gateway.vpc_internet_gateway[0]
  ]
}

# NAT gateway
resource "aws_nat_gateway" "nat_gw" {
  count = var.create_vpc && var.create_nat_gw && local.create_public_subnets ? local.len_public_subnets : 0

  allocation_id = element(
    aws_eip.elastic_ip_for_nat_gw[*].id,
    var.single_nat_gateway ? 0 : count.index,
  )

  subnet_id = element(
    aws_subnet.public_subnets[*].id,
    var.single_nat_gateway ? 0 : count.index,
  )

  tags = merge(
    {
      "Name" = format(
        "${local.full_name_env_app}-NAT-%s",
        element(var.availability_zone, var.single_nat_gateway ? 0 : count.index),
      )
    }
  )

  depends_on = [
    aws_internet_gateway.vpc_internet_gateway[0]
  ]
}

resource "aws_route" "nat_gw_route" {
  count = var.create_vpc && var.create_nat_gw ? local.nat_gateway_count : 0

  route_table_id         = element(aws_route_table.private_route_table[*].id, count.index)
  nat_gateway_id         = element(aws_nat_gateway.nat_gw[*].id, count.index)
  destination_cidr_block = "0.0.0.0/0"

  timeouts {
    create = "5m"
  }
}

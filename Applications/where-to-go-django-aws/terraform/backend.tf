terraform {
  backend "s3" {
    key    = "terraform/terraform.tfstate"
    bucket = "terraform-backend-lock-where-to-go-bucket"
    # dynamodb_table = "terraform-backend-lock-table"
    region = "eu-west-1"
  }
}


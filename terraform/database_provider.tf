provider "aws" {
  region = "sa-east-1"
}

# Creating DynamoDB tables
resource "aws_dynamodb_table" "products_table" {
  name           = "Products"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "name"
    type = "S"
  }

  attribute {
    name = "image_url"
    type = "S"
  }

  attribute {
    name = "description"
    type = "S"
  }

  tags = {
    Environment = "tester"
  }
}

# Criando a tabela no dynamodb
resource "aws_dynamodb_table" "access_logs_table" {
  name           = "AccessLogs"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "type"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = {
    Environment = "tester"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "product_images" {
  bucket = var.s3_bucket_name
}

# Setando as politicas no bucket
resource "aws_s3_bucket_public_access_block" "product_images" {
  bucket = aws_s3_bucket.product_images.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# RDS Instance
resource "aws_db_instance" "postgres" {
  identifier          = "tester_db"
  engine              = "postgres"
  engine_version      = "13.7"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  storage_type        = "gp2"
  
  db_name             = var.rds_database
  username            = var.rds_username
  password            = var.rds_password

  skip_final_snapshot = true

  tags = {
    Environment = "tester"
  }
}
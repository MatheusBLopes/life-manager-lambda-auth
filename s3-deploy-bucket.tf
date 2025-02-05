resource "aws_s3_bucket" "terraform_state_bucket" {
  bucket = "life-manager-lambdas-deploy"
}
resource "aws_lambda_function" "life_manager_lambda_auth" {
  filename         = "dummy_lambda_package.zip"
  function_name    = "LifeManagerLambdaAuth"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.12"
  source_code_hash = filebase64sha256("dummy_lambda_package.zip")

  environment {
    variables = {
      CLIENT_ID    =  "1234" # aws_cognito_user_pool_client.user_pool_client.id
      STAGE = "prod"
    }
  }
}

resource "aws_cloudwatch_log_group" "life_manager_lambda_auth_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.life_manager_lambda_auth.function_name}"
  retention_in_days = 1
}

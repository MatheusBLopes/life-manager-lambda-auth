output "lambda_invoke_arn" {
    value = aws_lambda_function.life_manager_lambda_auth.invoke_arn
}
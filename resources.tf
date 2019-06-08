# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# API GATEWAY
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

resource "aws_api_gateway_rest_api" "dyndns_api" {
  name = "dyndns-api"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "dyndns_api_deployment" {
  depends_on = [
    "aws_api_gateway_integration.duckdns_update_integration",
    "aws_api_gateway_integration.dyndns_v3_update_integration",
    "aws_api_gateway_integration.dyndns_nic_update_integration",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.dyndns_api.id}"
  stage_name  = "prod"
}

resource "aws_api_gateway_base_path_mapping" "dyndns_mapping_prod" {
  api_id      = "${aws_api_gateway_rest_api.dyndns_api.id}"
  stage_name  = "${aws_api_gateway_deployment.dyndns_api_deployment.stage_name}"
  domain_name = "${aws_api_gateway_domain_name.dyndns_api_domain.domain_name}"
}

resource "aws_api_gateway_domain_name" "dyndns_api_domain" {
  regional_certificate_arn = "${aws_acm_certificate.dyndns_api_cert.arn}"
  domain_name     = "${var.api_host}.${var.api_domain}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_route53_record" "dyndns_api_alias_record" {
  name    = "${aws_api_gateway_domain_name.dyndns_api_domain.domain_name}"
  type    = "A"
  zone_id = "${data.aws_route53_zone.api_zone.zone_id}"

  alias {
    evaluate_target_health = true
    name                   = "${aws_api_gateway_domain_name.dyndns_api_domain.regional_domain_name}"
    zone_id                = "${aws_api_gateway_domain_name.dyndns_api_domain.regional_zone_id}"
  }
}

resource "aws_acm_certificate" "dyndns_api_cert" {
  domain_name       = "${var.api_host}.${var.api_domain}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "dyndns_api_cert_validation_record" {
  name    = "${aws_acm_certificate.dyndns_api_cert.domain_validation_options.0.resource_record_name}"
  type    = "${aws_acm_certificate.dyndns_api_cert.domain_validation_options.0.resource_record_type}"
  zone_id = "${data.aws_route53_zone.api_zone.zone_id}"
  ttl     = 60

  records = [
    "${aws_acm_certificate.dyndns_api_cert.domain_validation_options.0.resource_record_value}",
  ]
}

resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = "${aws_acm_certificate.dyndns_api_cert.arn}"
  validation_record_fqdns = ["${aws_route53_record.dyndns_api_cert_validation_record.fqdn}"]
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# DUCK DNS UPDATE ENDPOINT
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# /update
resource "aws_api_gateway_resource" "duckdns_update_resource" {
  path_part   = "update"
  parent_id   = "${aws_api_gateway_rest_api.dyndns_api.root_resource_id}"
  rest_api_id = "${aws_api_gateway_rest_api.dyndns_api.id}"
}

# /update GET
resource "aws_api_gateway_method" "duckdns_update_method" {
  rest_api_id   = "${aws_api_gateway_rest_api.dyndns_api.id}"
  resource_id   = "${aws_api_gateway_resource.duckdns_update_resource.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "duckdns_update_integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.dyndns_api.id}"
  resource_id             = "${aws_api_gateway_resource.duckdns_update_resource.id}"
  http_method             = "${aws_api_gateway_method.duckdns_update_method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.dyndns_lambda.invoke_arn}"
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# DYNDNS V3 UPDATE ENDPOINT
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# /v3
resource "aws_api_gateway_resource" "dyndns_v3_resource" {
  path_part   = "v3"
  parent_id   = "${aws_api_gateway_rest_api.dyndns_api.root_resource_id}"
  rest_api_id = "${aws_api_gateway_rest_api.dyndns_api.id}"
}

# /v3/update
resource "aws_api_gateway_resource" "dyndns_v3_update_resource" {
  path_part   = "update"
  parent_id   = "${aws_api_gateway_resource.dyndns_v3_resource.id}"
  rest_api_id = "${aws_api_gateway_rest_api.dyndns_api.id}"
}

# /v3/update GET
resource "aws_api_gateway_method" "dyndns_v3_update_method" {
  rest_api_id   = "${aws_api_gateway_rest_api.dyndns_api.id}"
  resource_id   = "${aws_api_gateway_resource.dyndns_v3_update_resource.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "dyndns_v3_update_integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.dyndns_api.id}"
  resource_id             = "${aws_api_gateway_resource.dyndns_v3_update_resource.id}"
  http_method             = "${aws_api_gateway_method.dyndns_v3_update_method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.dyndns_lambda.invoke_arn}"
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# DYNDNS NIC UPDATE ENDPOINT
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# /nic
resource "aws_api_gateway_resource" "dyndns_nic_resource" {
  path_part   = "nic"
  parent_id   = "${aws_api_gateway_rest_api.dyndns_api.root_resource_id}"
  rest_api_id = "${aws_api_gateway_rest_api.dyndns_api.id}"
}

# /nic/update
resource "aws_api_gateway_resource" "dyndns_nic_update_resource" {
  path_part   = "update"
  parent_id   = "${aws_api_gateway_resource.dyndns_nic_resource.id}"
  rest_api_id = "${aws_api_gateway_rest_api.dyndns_api.id}"
}

# /nic/update GET
resource "aws_api_gateway_method" "dyndns_nic_update_method" {
  rest_api_id   = "${aws_api_gateway_rest_api.dyndns_api.id}"
  resource_id   = "${aws_api_gateway_resource.dyndns_nic_update_resource.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "dyndns_nic_update_integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.dyndns_api.id}"
  resource_id             = "${aws_api_gateway_resource.dyndns_nic_update_resource.id}"
  http_method             = "${aws_api_gateway_method.dyndns_nic_update_method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.dyndns_lambda.invoke_arn}"
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# LAMBDA FUNCTION
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

data "archive_file" "dyndns_lambda_zip" {
  type        = "zip"
  source_dir  = "dyndns"
  output_path = "dyndns_lambda.zip"
}

resource "aws_lambda_function" "dyndns_lambda" {
  function_name    = "dyndns"
  filename         = "dyndns_lambda.zip"
  source_code_hash = "${data.archive_file.dyndns_lambda_zip.output_base64sha256}"
  role             = "${aws_iam_role.dyndns_lambda_role.arn}"
  description      = "Lambda function that acts a dynamic DNS service"
  handler          = "main.request_handler"
  runtime          = "python3.7"
  publish          = true

  environment {
    variables = {
      "DYNAMODB_TABLE_NAME" = "${aws_dynamodb_table.dyndns_config_table.id}"
    }
  }
}

resource "aws_lambda_permission" "dyndns_lambda_api_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.dyndns_lambda.arn}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.dyndns_api.execution_arn}/*/GET/*"
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# IAM
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

resource "aws_iam_role" "dyndns_lambda_role" {
  name               = "dyndns-lambda-role"
  assume_role_policy = "${file("assume_role_policy.json")}"
}

resource "aws_cloudwatch_log_group" "dyndns_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.dyndns_lambda.function_name}"
  retention_in_days = 14
}

resource "aws_iam_policy" "dyndns_lambda_policy" {
  name        = "dyndns-lambda-policy"
  description = "policy providing needed permissions to dyndns lambda function"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem"
      ],
      "Resource": "${aws_dynamodb_table.dyndns_config_table.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "route53:ChangeResourceRecordSets"
      ],
      "Resource": "*"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = "${aws_iam_role.dyndns_lambda_role.name}"
  policy_arn = "${aws_iam_policy.dyndns_lambda_policy.arn}"
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# DYNAMODB
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

resource "aws_dynamodb_table" "dyndns_config_table" {
  name         = "DynDNSConfig"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "Token"

  attribute {
    name = "Token"
    type = "S"
  }
}

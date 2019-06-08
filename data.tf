data "aws_route53_zone" "api_zone" {
  name = "${var.api_domain}."
}

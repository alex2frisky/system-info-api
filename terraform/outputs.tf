output "website_url" {
  description = "URL to access the API"
  value       = "http://${aws_eip.web.public_ip}"
}

output "public_ip" {
  description = "EC2 public IP address"
  value       = aws_eip.web.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.web.id
}

output "test_commands" {
  description = "Commands to test the API"
  value = <<-EOT

    ✅ Deployed successfully!

    API URL: http://${aws_eip.web.public_ip}

    Wait 3-5 minutes for EC2 to boot and start Docker.

    Test commands:
      curl http://${aws_eip.web.public_ip}/
      curl http://${aws_eip.web.public_ip}/health
      curl http://${aws_eip.web.public_ip}/info
      curl http://${aws_eip.web.public_ip}/metrics

    ⚠️  DESTROY WHEN DONE:
      terraform destroy

    Cost: ~$0.017/hour
  EOT
}

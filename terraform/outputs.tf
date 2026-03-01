output "public_ip" {
  description = "EC2 public IP"
  value       = aws_eip.web.public_ip
}

output "website_url" {
  description = "URL to access the API"
  value       = "http://${aws_eip.web.public_ip}"
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.web.id
}

# reminder to test and destroy
output "next_steps" {
  value = <<-EOT
    Wait ~3-5 minutes for EC2 to boot and pull the Docker image.

    Test it:
      curl http://${aws_eip.web.public_ip}/health
      curl http://${aws_eip.web.public_ip}/info

    SSH in to debug:
      ssh ec2-user@${aws_eip.web.public_ip}

    Check the bootstrap log on the instance:
      sudo cat /var/log/user-data.log

    Remember to destroy when done (this costs money):
      terraform destroy
  EOT
}

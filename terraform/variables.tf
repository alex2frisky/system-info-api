variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "system-info-api"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "docker_image" {
  description = "Docker image to deploy (e.g., username/system-info-api:latest)"
  type        = string
}

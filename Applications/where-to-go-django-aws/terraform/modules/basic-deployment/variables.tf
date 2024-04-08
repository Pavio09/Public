variable "environment" {
  type        = string
  description = "(Optional)"
}

variable "project_name" {
  type        = string
  description = "(Required) - {project_name}/{environment}/{name}."
}

variable "application" {
  type = string
}

locals {
  full_name_env_app = "${var.environment}-${var.project_name}"
}

variable "image_name" {
  type        = string
  description = "(Required)"
}

variable "image_tag_mutability" {
  type        = string
  description = "(Optional)"
  default     = "MUTABLE"
}

variable "scan_on_push" {
  type        = bool
  description = "(Required)"
  default     = true
}

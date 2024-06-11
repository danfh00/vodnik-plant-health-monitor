variable "ACCESS_KEY" {
    type = string
  
}
variable "SECRET_ACCESS_KEY" {
    type = string
  
}
variable "AWS_REGION" {
    type = string
    default = "eu-west-2"
  
}

variable "HISTORICAL_BUCKET_NAME" {
    type = string
    default = "vodnik-historical-readings"
}
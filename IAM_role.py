"""
    In the IAM console, create a role with the following policies

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "redshift-serverless:GetCredentials",
        "redshift-serverless:ListWorkgroups",
        "redshift-serverless:ListNamespaces"
      ],
      "Resource": "*"
    }
  ]
}

"""


"""
    Associate the IAM role with Redshift Serverless
    
{
  "Effect": "Allow",
  "Action": [
    "redshift-serverless:AssociateIamRole",
    "redshift-serverless:DisassociateIamRole"
  ],
  "Resource": "arn:aws:redshift-serverless:region:account-id:namespace/namespace-id"
}

"""
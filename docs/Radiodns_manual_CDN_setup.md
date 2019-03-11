# Setting up the XML publishing feature

This document covers the AWS setup required to publish your SI/PI files to AWS CloudFront.

At the end of this document, you'll be able to enable SI/PI delivery through CDN.

## Prerequisites
You'll need an AWS account with the sufficient rights to create and administrate S3 buckets and CloudFront distributions.

## Setup
### Edit the environment file
By default the CDN serving is disabled and unconfigured. You'll need to edit the correct .env file corresponding
to your deployment method (.env.example for EBU.io and .env.standalone.example to standalone) and fill the CDN part
of the file. 

### Create an S3 Bucket
Create an S3 bucket with the name you choosed in the previous step. To do this [go to your S3 console](https://s3.console.aws.amazon.com/s3/home)
and click on the "CREATE BUCKET" button. 

Choose a name, a region and you are good to go to the next step.

You don't need to configure anything in steps 2 and 3 and can press next twice and then "create bucket".

Click on your newly created bucket.

Select the "Management" tab. Click on the "ADD LIFECYCLE RULE" button.

Enter a rule name, and as prefix type "schedule/". The type of the filter must be a "prefix/tag".

You don't need to configure anything in step 2 and can press next.

You can tick in this step 3 the "Current version" checkbox as well as "Expire current version of object". 
Then set the expiry 28 days after creation.

Review and create the rule.

### Create a CloudFront distribution
To create a CloudFront distribution [go to your CloudFront console](https://console.aws.amazon.com/cloudfront/home) and
click on the "CREATE DISTRIBUTION" button.

Click on the "GET STARTED" button that is in the "Web" section.

As "Origin Domain Name" choose the bucket you created earlier.

Leave "Origin Path" empty.

You can choose to Restrict Bucket Access so that your user can only get your SPI files through CloudFront. You can choose 
either one.

"Viewer Protocol Policy" must be set to HTTP / HTTPS.

"Allowed HTTP Methods" must be set to GET/HEAD.

"Cache Based on Selected Request Headers" must be set on None.

"Object Caching" can be set on custom to fit your needs. In doubt, leave this value as "Use Origin Cache Headers".

"Forward Cookies" must be set to None.

"Query String Forwarding and Caching" must be set to None.

"Smooth Streaming" must be set to No.

"Restrict Viewer Access" must be set to unless you implemented this feature (RadioDNS does not support it).

"Compress Objects Automatically" must be set to Yes.

"Price Class" can be chosen to fit your needs.

Use "Alternate Domain Names" and "SSL Certificate" to setup a custom serving domain with or without https support.
If you request a Certificate with ACM make sure you request it in the US East (N. Virginia) region.

The rest of the options can stay with their default value.

Finally hit the "CREATE DISTRIBUTION" button.

Now you can fill the SPI_CLOUDFRONT_DOMAIN key of your .env file with your CloudFront domain name.

### Generate all SI/PI files at once
**THIS STEP IS A  MANDATORY PART OF THE SETUP**

In the RadioDNS manager, click in the left pane the "Generate all spi files" button. In a short time, your SI/PI
files will be generated and uploaded to AWS S3 and CloudFront services.

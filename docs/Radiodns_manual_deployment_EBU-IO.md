**Notes**

This documents covers the deployment of the application on an EC2 amazon ubuntu instance.

**THIS DOCUMENT ONLY COVERS DEPLOYMENT IN AN EBU.IO ENVIRONMENT!**

## Installation
### AWS Setup
First, go to ec2 and select “launch a new instance”. Be sure to follow every one of the seven steps of the instance creation.

1.  Select ubuntu 18 as AMI.
2. Select as machine a medium.t2.
3. You can leave the details as default.
4. Use the default storage provided.
5.  Leave tag as they are.
-  Create or use a security group called "RadioDns-sg" that enables communication with ports 22, 80, 443 from anywhere.
Then create a security group called "RadioVis-sg" that enables communication with ports 22 and 61613 from anywhere. Then allow
all traffic from "RadioDns-sg" security group. Also allow all traffic from "RadioVis-sg" in the RadioDns security group.
-  Launch the instance. Attach the "RadioDns-sg" to the instance.
-  Redo steps 1 to 5 then attach to this new second instance the "RadioVis-sg" security group.
-  Next, we need to create an IAM user. Go to https://console.aws.amazon.com/iam/home. Choose as Access type “Programmatic access”. 
Once created save its access key and secret key. **This is your only change to save them somewhere**. ![image10](/docs/images/image10.png)
-  Add this user to a group that have full permissions (`AmazonS3FullAccess` and `AmazonRoute53FullAccess`) on route 53 and s3. 
- (Optional) Register a domain in route 53.
- Go to https://console.aws.amazon.com/route53/. Create or use the hosted zone for your domain. We will call this zone
the root hosted zone. In this example our domain will be staging-radiodns.com.
- Add also another hosted zone (we’ll call it the second hosted zone) but this time it will be a subdomain of the root 
hosted zone (RadioDns-PlugIt server will do the NS configuration for you). For this example, one created staging-radiodns.com
in step 13 as a root hosted zone and dev.staging-radiodns.com as the second hosted zone.
- Add to the second hosted zone 4 CNAME entry:

a. epg.<second_hosted_zone> -> <second_hosted_zone>

a. api.<second_hosted_zone> -> <second_hosted_zone>

b. tag.<second_hosted_zone> -> <second_hosted_zone>

c. vis.<second_hosted_zone> -> <second_hosted_zone>

For example:

a. epg.dev.staging-radiodns.com -> dev.staging-radiodns.com

a. spi.dev.staging-radiodns.com -> dev.staging-radiodns.com

b. tag.dev.staging-radiodns.com -> dev.staging-radiodns.com

c. vis.dev.staging-radiodns.com -> dev.staging-radiodns.com

- Add to the second hosted zone an A record pointing on your instance of RadioDns.

## RDS setup
- Go to the rds service and hit the "create a database" button.
- As an engine choose MySQL. Hit the "next" button.
- As a use case choose "production - MySQL". Hit the "next" button.
- As a DB engine version choose 8 or higher.
- You can choose the DB instance class, A-Z deployment options, allocated storage to your liking.
- As a DB instance identifier enter radiodns.
- Choose a master username/password. Hit the "next" button.
- Public accessibility must be set to "No".
- As a database name choose radiodns.
- Set up the rest of the options to your liking then hit the "create database" button.
After a while you database will be available at its entrypoint:port.

**Note** We configured the database such as it cannot be accessed outside the Virtual Private Network (VPC) where is belongs.
This guide assumes that you are using the default VPC of your AWS account.

## Instance setup
Ssh to he ubuntu RadioDns instance:

    ssh -i <PATH TO KEY> ubuntu@<INSTANCE_IP>
    
Copy and rename the file `docker-compose-ebu-io.yml` to `docker-compose.yml`

    cp docker-compose-ebu-io.yml docker-compose.yml

Create a file in the containing you AWS credentials named `credentials` placed under the `/home/<username>/.aws` folder.

    cd $HOME
    mkdir .aws
    nano .aws/credentials

Clone the project (With git. You may have to install this tool using
`sudo apt update && sudo apt install git -y`) and set your working directory in the root folder of the project.

    git clone <project url>
    cd radiodns-plugit

### Docker setup
- Run the `./scripts/docker-setup.sh` script to install docker. The script is located in the root folder of the project.
- Disconnect and reconnect to the instance or reload your shell and test that docker is running by writing theses
commands:
```
docker --version
docker-compose -v
docker run
docker run hello-world
```
    
Every commands should complete without error.

### (optional) Certbot setup
Run the `./scripts/certbot-setup`.
This scripts installs automatically the letsencrypt client with its route53 plugin.

## Instance configuration
Copy .env.example to .env (`cp .env.example .env`). Edit this file until you are satisfied with the configuration
(every configuration key is faithfully described in it).

For `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` you will use the one from the IAM user you created earlier.

For `API_URL` you must use the url that was given to you during the configuration of ebu.io. You can always get this value
by going in the config menu of your project.
![image4](/docs/images/image4.png)

Repeat this process for the two instances. You only need to configure the `MYSQL SERVER`, `NGINX` and `RADIODNS` section of
the .env for the RadioDns instance. You only need to configure the `RADIO VIS` section for the RadioVis instance.

## HTTPS Setup
- First you need to register some wildcard certificates:
    - `<second hosted zone>`
    - `*.<second hosted zone>`
    - `*.spi.<second hosted zone>`
    - `*.epg.<second hosted zone>`

- For example, with the domain used in this document it would be:
    - `dev.staging-radiodns.com`
    - `*.dev.staging-radiodns.com`
    - `*.spi.dev.staging-radiodns.com`
    - `*.epg.dev.staging-radiodns.com`

Once you have retrieved those certificates place them in `<PROJECT_ROOT_FOLDER>/Ngnix/certificates.`
The server expects to find here two files: `fullchain.pem` and `privkey.pem`.

### letsencrypt.org support
There is a support for cerbot if you were to use letsencrypt.org certificates (only in a ubuntu instance!).
You must have certbot installed with its route53 plugin installed. Next you'll have to create an aws credentials file containing the
`AWS_ACCESS_KEY` and `AWS_SECRET_KEY` with this format:

    [default]
    aws_access_key_id=AWS_ACCESS_KEY
    aws_secret_access_key=AWS_SECRET_KEY

then you can call the `setup_cron_job_for_certificate_renewal.sh` script located in the scripts directory. You'll have to 
specify the full path to the aws credentials file and the second hosted zone.
For example if one were to register
the domain `dev.staging-radiodns.com` one would set the script's parameters as follow:

- `/home/ubuntu/.aws/credentials` as the full path to the aws credentials file.
- `dev.staging-radiodns.com` as the second hosted zone.

Example:

    sudo ./scripts/setup_cron_job_for_certificate_renewal.sh /home/ubuntu/.aws/credentials dev.staging-radiodns.com

Next you will call with the same parameters the `renew_certificates.sh` script located in the scripts directory to renew
now the certificate (basically get it for the first time).

Example:

    sudo ./scripts/renew_certificate.sh /home/ubuntu/.aws/credentials dev.staging-radiodns.com

**NOW REDO THE Instance setup SECTION BUT THIS TIME WITH THE VIS INSTANCE AND CONFIGURING IT FOR THE VIS SERVICE.**

## EBU.io
In this section, we will configure ebu.io. Go to your project and hit the “config” button. You’ll have to fill the following inputs:
-  Name: The name of the project.
-  Is public: If the project can be accessed by anyone.
-  PlugIt URI: This must be a uri compiling the following scheme:  http://<instance_hostname>/<api_secret>.
The api_secret can be any string but it has to match the API_SECRET option of the .env file of the project.
That string should be a randomly generated string.
-  PlugItOrgaMode: This checkbox must be ticked.

Next go to the Services tab
![image5](/docs/images/image5.png)
Here you have to tick the “Run” service otherwise you won’t be able to use the project.

## Run
### RadioDns instance
To build and deploy the containers

    docker-compose up --build -d
    
To stop the containers

    docker-compose down
    
### RadioVis instance
To build and deploy the containers

    docker-compose -f docker-compose-radiovis-prod.yml up --build -d
    
To stop the containers

    docker-compose -f docker-compose-radiovis-prod.yml down
    
 
## Backup and restore database
### Backup
    docker exec <name_of_docker_container> /usr/bin/mysqldump -u root --password=<database_passowrd> <database_name> > backup.sql

### Restore
    cat backup.sql | docker exec -i <name_of_docker_container> /usr/bin/mysql -u root --password=<database_passowrd> <database_name>

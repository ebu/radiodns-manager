**Note**

This documents covers the deployment of the application on an EC2 amazon ubuntu instance in AWS.

# AWS Configuration 
Running on an AWS EC2 instance is mandatory.

You MUST have a domain with a hosted zone setup in your AWS account.

## Instance setup
- Go to the [EC2 panel](https://eu-west-1.console.aws.amazon.com/ec2) and click on "Launch Instance".
- Select as AMI type `Ubuntu Server 18.04 LTS (HVM)`
- As Instance type you should at least choose a t2.medium.
- You don't have to modify anything here unless you don't want to use the default VPC. Then you can hit the "Next: Add Storage" button.
- At least 8 GB of disk space is required. You can hit the "Next: Add Tags" button.
- You can add tags on your instance for better AWS account organisation but you can also ignore this step. You can hit the
"Next: Configure Security Group"
- You will need a security group with the following inbound rules: 
    - SSH: 22
    - HTTP: 80
    - HTTPS: 443
    - STOMP: 61613
with as source 0.0.0.0/0. Then you can hit the like "Review and launch" button.
    - **Note** it is a good idea to restrict the ip addresses that can connect to the port 22 to your ip address.
![alt text](docs/images/security_group.png "RadioDns security group")
- Verify that your instance settings are correct and launch the instance.

## Route 53 setup
IF YOU HAVE ALREADY A HOSTED ZONE CONFIGURED WITH A DOMAIN IN AWS SKIPS THE TWO NEXT STEPS.

IF YOU DONT HAVE BUT WANT TO BUY A DOMAIN IN AWS FOLLOW THE STEP BELLOW AND SKIP THE NEXT ONE.

IF YOU HAVE ALREADY A DOMAIN ON AN OTHER DNS SERVICE PROVIDER SKIP THE FIRST NEXT STEP BUT FOLLOW THE SECOND.

### (Optional) Register a domain
- Go to the [route 53 domain registration panel](https://console.aws.amazon.com/route53/home#DomainRegistration:)
- Choose a domain name. Click the "Check" button. If the domain name is available, click "add to cart" then click "continue".
- Enter your Registrant Contact then click "continue".
- Review and agree to the therms of service and complete your purchase.

### (Optional) Link the hosted zone to a third party registrar as a subdomain.
- Create a hosted zone with as Domain Name the subdomain of your domain.
- In your third party dns records manager, add four NS records pointing to the four Name Server that your AWS hosted zone has
in its NS record for as Domain Name the choosen subdomain.

You can use the tool called `nslookup` included on Windows and macOS to check if your DNS records are properly configured.

    nslookup <domain>

### Hosted zone setup
Go to the [route 53 hosted zone panel](https://console.aws.amazon.com/route53/home#hosted-zones:) and
click on the hosted zone with as name the name of your domain.

Add an A record  pointing to your EC2 instance. To do so click on the blue "Create Record Set" button. You'll be prompted 
on the right side of the screen to fill the information about the new record.

You also need to create 6 CNAMEs pointing to this A record:
- `tag.<domain>` -> `<domain>`
- `spi.<domain>` -> `<domain>`
- `epg.<domain>` -> `<domain>`
- `vis.<domain>` -> `<domain>`
- `visadmin.<domain>` -> `<domain>`
- `manager.<domain>` -> `<domain>`

## IAM setup - Group
- Go to the [IAM group panel](https://console.aws.amazon.com/iam/home#/groups) and hit the "Create New Group" button.
- Choose the group's name and hit the "Next Step" button.
- You will need route 53 full access (AmazonRoute53FullAccess) and S3 full access (AmazonS3FullAccess). Then click on
the "Next Step" button.
- Verify that the group has the two permissions and create the group.

## IAM setup - User
- Go to the [IAM user panel](https://console.aws.amazon.com/iam/home#/users) and hit the "Add user" button.
- Add a name and choose as access type "Programmatic access". Then hit the "Next" button.
- Add this user to the group you created in the `IAM setup - Group` step. Then hit the "Next" button.
- You can make/choose tags if you want. Then hit the "Next: Review" button.
- Verify the user details and then create the user.
- Either download the .csv or note the `Access key ID` and the `Secret access key` somewhere.
**THIS IS YOUR ONLY CHANCE TO SAVE THESE CREDENTIALS!**

## Instance configuration
## Connection and AWS configuration
Now ssh to your instance:

    ssh -i <PATH TO KEY> ubuntu@<INSTANCE_IP>
    
Copy and rename the file `docker-compose-standalone.yml` to `docker-compose.yml`

    cp docker-compose-standalone.yml docker-compose.yml

Create a file in the containing you AWS credentials named `credentials` placed under the `/home/<username>/.aws` folder.

    cd $HOME
    mkdir .aws
    nano .aws/credentials
    
(To close the nano editor: CTRL + x then press y then enter)

its contents must be:

    [default]
    aws_access_key_id=<AWS_ACCESS_KEY>
    aws_secret_access_key=<AWS_SECRET_KEY>
    
Clone this repository and cd into it:

    git clone https://github.com/ioannisNoukakis/radiodns-docker
    cd radiodns-docker

### Installing dependencies

IF YOU FOLLOWED THESES INSTRUCTION WITH THE RECOMMENDED AMI (`Ubuntu Server 18.04 LTS AMI`) FOLLOW THE NEXT STEP 
BUT SKIP THE NEXT ONE.

IF YOU DECIDED TO USE AND OTHER AMI SKIP THE NEXT STEP BUT FOLLOW THE NEXT ONE. 

#### (Optional) If you running this on the instance you started Ubuntu Server 18.04 LTS AMI
There is support out of the box for docker and Letsencrypt.org certificates with Ubuntu Server 18.04 LTS AMI.

Run the `./scripts/docker-setup.sh` script to automatically install docker.

You **MUST** reload your shell or logout/login to access it with the ubuntu user.

Test your docker installation by running those two commands:

    docker run hello-world
    docker-compose -version

Run the `./scripts/certbot-setup.sh` script to install automatically certbot.

#### (Optional) If you choosed an another AMI  
You need to install docker 18.06.1 or higher (install docker [here](https://docs.docker.com/install/)).

You also need certbot with route53 plugin installed in order to use the HTTPS features.

## RadioDns Manager Configuration 
For your convenience a `.env.standalone.example` containing the various configurations for the docker images has been provided.
You must copy it or rename it to `.env` (`cp .env.standalone.example .env`). The project wont be able to work if the file named
`.env` is missing.

You must edit the `.env` and fill the fields that have as value <CHANGE_ME>.

If you use the Ubuntu Server 18.04 LTS AMI use the `./scripts/renew_certificate.sh` script.

This script takes two parameters. The first MUST be the full path to the aws credentials file. The seconds is the domain
to register.

For automatic renewal, use the `./scripts/setup_cron_job_for_certificate_renewal.sh` script with the same parameters.
(You still need to run the `./scripts/renew_certificate.sh` script before this one).

Example:

    sudo ./scripts/renew_certificate.sh /home/ubuntu/.aws/credentials example.org
    
If you dont use the recommended AMI or want to use your own certificates instead, you'll have to provide the keys as you
would normally do for an nginx server under the Nginx/certificates folder. The ssl_certificate shall be named
`fullchain.pem` and the private key shall be named `privkey.pem`.

You will need a certificate for `<domain>`, `*.<domain>`, `*.spi.<domain>` and `*.epg.<domain>`.

# Commands

If you ran the `./scripts/renew_certificate.sh` script successfully the service is already running!

**NOTE** The commands should be run in the application's folder.

To check the service status:

    docker ps
    
To access applications logs:

    docker logs <name_of_docker_container>

To start up:

    docker-compose up --build -d

To shut down:

    docker-compose down

To remove the database and start afresh

    docker-compose down
    docker volume rm radiodns-manager_db_data
    docker volume rm radiodns-manager_pgdata
    docker-compose up --build -d
    
## Backup and restore database
### Backup
    docker exec <name_of_docker_container> /usr/bin/mysqldump -u root --password=<database_passowrd> <database_name> > backup.sql

### Restore
    cat backup.sql | docker exec -i <name_of_docker_container> /usr/bin/mysql -u root --password=<database_passowrd> <database_name>

# Services
## RadioDns Manager
Once the service is running you can access the RadioDns manager at `https://manager.<domain>`. By default, an admin account
has been created with the credentials you provided.

By default you will be working the "default" organization. To fill you organization parameters you'll have to access
the `Administration panel`.
Here you will be able to create your organization and assign the admin account to this newly created organization.

## SPI/EPG services
Once you created a station and filled your service provider information,
you can get the SPI file at `https://<codops>.spi.<domain>/radiodns/spi/3.1/SI.xml` (codops can be found on the sevice provider page.).

To test the client identifier feature, you'll need to add a client (under the "my client" tab), add some overrides to a station
or some more channels for this client and send your request with this specific header: `{Authorization: ClientIdentifier <identifier>}`.

You can get the EPG file at `http://<codops>.epg.<domain>/radiodns/epg/XSI.xml`

## VIS service
You can listen to the STOMP VIS server by ` telnet <codops>.vis.<domain> 61613`.
Once the connection has been established you need to connect first using the following command:

    CONNECT
    ^@
    
You can then subscribe to a topic. For example:

    SUBSCRIBE
    destination:/topic/dab/4e1/4fff/4001/0/text
    ^@

NOTE: ^@ is the null character. On macOS this is done with an american keyboard layout by pressing 
`CTRL + SHIFT + 2`.

You can connect to the rabbitmq control panel at `https://visadmin.<domain>` with the credentials you provided.

## Contact

Contact the EBU (Ben Poor poor@ebu.ch) if you need more information about RadioDNS and its associated developments.
Contact Ioannis Noukakis (inoukakis@gmail.com) if you need any help with this demo. You can also submit an issue at
[the demo github repository](https://github.com/ioannisNoukakis/radiodns-docker-demo).

# Copyright & License

Copyright (c) 2013-2015, EBU-UER Technology & Innovation

The code is under BSD (3-Clause) License. (see LICENSE.txt)

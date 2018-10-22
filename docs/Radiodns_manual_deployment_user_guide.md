**Note**

This method of deployment is only temporary as we will automate the process “soonish”. 

## AWS Setup
First, go to ec2 and select “launch a new instance”. Be sure to follow every one of the seven steps of the instance creation.

1.  Select ubuntu 18 as AMI![image3](/docs/images/image3.png)
2.  Select as machine a micro.t2![image2](/docs/images/image2.png)
3.  You can leave the details as default.
4.  Use the default storage provided.
5.  Leave tag as they are.
6.  Create or use a security group that enables at least communication with port 80 and port 61613 (for radio vis).![image8](/docs/images/image8.png)
7.  Launch the instance.
8.  Next, we need to create an IAM user. Go to https://console.aws.amazon.com/iam/home. Choose as Access type “Programmatic access”. Once created save its access key and secret key. This is your only change to save them somewhere. ![image10](/docs/images/image10.png)
9.  Add this user to a group that have full permissions (AmazonS3FullAccess and AmazonRoute53FullAccess) on route 53 and s3. 
10. (Optional) Register a domain.
11. Next, we need to configure route 53. First, go to https://console.aws.amazon.com/route53/. Create a root hosted zone that is a subdomain of your domain. ![image1](/docs/images/image1.png)
In this example, I created radio-staging.ebu.io that is a subdomain of ebu.io.
12. In the domain you registered in step 10 or in your existing domain or in ebu.io domain records, add a new NS record for with as name the name the root hosted zone as value the 4 NS servers of the root hosted zone.
13. Add also another hosted zone (we’ll call it the second hosted zone) but this time it will be a subdomain of the root hosted zone (RadioDns-PlugIt server will do the NS configuration for you). For this example, I created radio-staging.ebu in step 12 as a root hosted zone and the hosted zone of this step as the second hosted zone will be radio.radio-staging.ebu.io.
14. Add to the second hosted zone 3 CNAME entry:
  a. epg.<second_hosted_zone> -> <second_hosted_zone>
  b. tag.<second_hosted_zone> -> <second_hosted_zone>
  c. vis.<second_hosted_zone> -> <second_hosted_zone>

For example:
  a. epg.radio.radio-staging.ebu.io. -> radio.radio-staging.ebu.io.
  b. tag.radio.radio-staging.ebu.io. -> radio.radio-staging.ebu.io.
  c. vis.radio.radio-staging.ebu.io. -> radio.radio-staging.ebu.io.
15. Add to the second hosted zone an A record pointing on your instance of RadioDns.

## EBU.io
In this section, we will configure ebu.io. Go to your project and hit the “config” button. You’ll have to fill the following inputs:
1.  Name: The name of the project.
2.  Is public: If the project can be accessed by anyone.
3.  PlugIt URI: This must be a uri compling the following scheme:  http://<instance_hostname>/<api_secret>. The api_secret can be any string but it has to match the API_SECRET option of the .env file of the project. The author of the project recommends that this string should be a randomly generated string. *Also save the api Url url for later.*
4.  PlugItOrgaMode: This checkbox must be ticked.

Next go to the Services tab
![image5](/docs/images/image5.png)
Here you have to tick the “Run” service otherwise you won’t be able to use the project.

## Instance configuration
Connect to our instance, clone the project and copy .env.example to .env (cp .env.example .env). Edit this file until you are satisfied with the configuration (every configuration key is faithfully described in it).

For AWS_ACCESS_KEY and  AWS_SECRET_KEY you will use the one from the IAM user you created earlier.

For API_URL you must use the url that was given to you during the configuration of ebu.io. You can always get this value by going in the config menu of your project.
![image4](/docs/images/image4.png)

Once the configuration is complete. Run the `docker-setup.sh` script if docker is not installed (this will install docker and docker-compose) then run `docker-compose build` and `docker-compose up -d`.
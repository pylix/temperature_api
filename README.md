## Temperature Converter API Project

### Rationale 

For this API I decided to use Python. Because of the short timeline I wanted to use something I was more familiar with. Python is a mostly interpreted language that has support for practically all forms of computing and is very popular for science, machine learning and scripting due to it’s easy to understand code and high levels of dynamism and abstraction. 

In terms of libraries, I decided to use a library called fastAPI. This library claims to be as fast as NodeJS and makes it very easy to quickly write an API with features like built in input validation and self-documentation, and automatic handling of certain header and file formats. 
For the overall API design, because the requirement was to use HTTP, I decided to follow the REST API standard. This REST framework is also well supported by fastAPI. 
For the task of having a single endpoint that does both Celsius to Fahrenheit conversion and vice versa, I decided on the endpoint http://alixetienne.com/convert

The convert endpoint url is constructed as shown below:

http://alixetienne.com/convert/{temperature}/{unit}/{convertTo}

- http://alixetienne.com is the address of the host also at ip 
- convert/ is the endpoint topic
- {temperature} is the temperature that’s being converted is a numerical amount like 32
- {unit} is the source temperature unit that’s being converted like Celsius or Fahrenheit
- {convertTo} is the destination unit or the unit that you want the result of the computation to be in.

I thought about just having two parameters like temperature and unit because you can only convert from one to the other in a binary way, but by choosing the three-tiered API call structure, it leaves room for easy extension if we were to add kelvin or some other temperature scale. It also makes it more clear to see what kind of conversion is going on. I decided on JSON output because it makes it easy to parse and program with, and it has good readability for smaller responses.

Moving on to the overall architecture behind my solution, fastAPI uses the unicorn webserver which is popularly used in Ruby on Rails. FastAPI also implements the python’s asynchronous server gateway specification (ASGI) https://asgi.readthedocs.io/en/latest/ 
Because the task didn’t specify how many users that API would have, I was challenged to come up with a scalable solution. I had two main options 
1. Use a load balanced solution using an out of the box reverse proxy like nginx
2. Use a library called Ray to handle the scalability and load balancing


In the end, I decided to use Ray because with nginx I would have to work on a custom solution and try to manually calculate when I should scale and how to handle adding and removing logical workers to the cluster.

Ray(https://github.com/ray-project/ray) is a library the allows for remote processing of distributed computing and machine learning algorithms on cloud providers like AWS, AZURE and GCP. While Ray specializes in compute heavy tasks such as executing machine learning algorithms, its focus on parallelism and distributed computing make it suitable for scalable API use cases and it has a built-in integration with fastAPI.
Ray is a processing engine similar to spark, but with a greater focus on utilizing the raw compute power of a cluster or system. It uses a worker slave system where the head node pushes tasks to all the worker nodes. It uses the actor model and futures for concurrency. One of the biggest selling points of ray is its ability to manage and auto scale a cluster in a cloud agnostic way working on AWS/AZURE/CPG with similar configuration. 

### Build and deployment

#### Docker based version
In terms of building, python is primarily a dynamically typed and interpreted programming and so in most cases there’s nothing to build. Even though some dependencies controlled from python may be built from source these are not part of the overall package. 
I did include a docker file for a simplified version of the application that doesn’t use ray. This simplified version can be quickly built and deployed with docker but would not be immediately deployable to a multi node environment. 
To use build and deploy this version. You must first download and install docker https://docs.docker.com/get-docker/.  At the time of writing docker desktop on windows and mac have ready-made binaries that can be taken advantage of. For Linux, if you use a RHEL based OS you can use.. 
```
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager \
    --add-repo \
    https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
```

For other Linux distributions please see the docker website https://docs.docker.com/engine/install/
After downloading docker unzip the API application code which can be found here (https://github.com/pylix/temperature_api and go into the top-level directory. From there there should be a file called Dockerfile which you can build via the command
docker build -t <image_name>:<image_tag>
after running the command, you can upload this image to a repository or move it to the production server. 
Then we would need to install the docker engine on the production server. On RHEL based Linux servers we can run the commands below to do this

```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo systemctl restart docker -f
```

Ubuntu
```
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg 
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

Once the docker engine is set up we can simply run the image with the exposed port and add a ip route from 8080 to 80 on the host

```
sudo docker run -d -p 8080:8080 --name app1 <image_name>
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
```

### Building and deploying with Ray

To build the application as it exists in production, we need to use Ray and Amazon web services. The way my build works is that I launch the ray cluster creation service on my home/dev machine using my AWS application admin credentials. IAM specific permissions for Ray are a bit more complicated, but as a start you can view the incomplete page https://github.com/ray-project/ray/issues/9327. Using the root account is not advised, but a set of keys with admin credentials will make things easy to start up.  If you don’t have an AWS account, you can create one at https://aws.amazon.com/
Once you have an AWS account and keys with all the necessary permissions, you need to install ray a machine. It doesn’t need to be a local machine but unless your keys expire it’s best not to put admin keys on servers that don’t have the proper level of security. 

Currently ray is supported on Mac OS and Linux and is in beta for windows. I used my mac book pro for this installation. There are many ways to install ray for remote cluster creation including downloading the binaries, using package managers, and building from source see: https://docs.ray.io/en/latest/ray-overview/installation.html 
After installing Ray, you need to extract the zip of API code (https://github.com/pylix/temperature_api) to a directory on the machine with user read and write permission.
 The next step in to enter the directory where this code is using the command line. Upon entering you should run modify the temperature_api yaml file to remove my specific folder path “/Users/alix/PycharmProjects/temperature_api/” and replace it with the code directory extracted earlier this is on line 75 https://github.com/pylix/temperature_api/blob/master/temperature_api.yaml. 
Finally run the following from the AWS server with admin keys to start the cluster. Ensure that you’re in the API code directory
```
ray up -y temperature_api.yaml
```
Then when the cluster is ready run
```
ray attach temperature_api.yaml
```
This will connect you to the cluster in a docker container
From this container run 
```
python /home/ubuntu/temperature_api/main.py
```
This will start the API
You can then run the tests in the docker container via 
```
pytest --no-header -v /home/ubuntu/temperature_api/
```
### Testing

As mentioned, automated test can be run from within the cluster docker container with the command 
You must be attached to the cluster docker container via ray attach temperature_api.yaml
Before running the command below
```
pytest --no-header -v /home/ubuntu/temperature_api/
```
I implemented these tests following the conventions of the test module pytest.
A pytest file is a python file that has one or more test functions in file starting with “test_” and the inside of those functions should have assert statements to test different conditions. My approach to testing was to compare my results to a source of truth and sol I loaded a temperature table which has values from Celsius to Fahrenheit and Fahrenheit to Celsius. Because this tables had close to 100 rows each, and I wanted my tests to run quickly, I choose random elements of the table which has the correct calculations and compared them with my API results. I needed to do some rounding because the table that I used was less precise than my API. I also tested to make sure that different areas of the API were reachable and tested for invalid cases like the wrong type of parameter, extra arguments and for values below absolute zero. Pytest treats every function that starts with test_ as a test case and shows you the number of test cases passed or failed accompanied by the percentages. 
In addition to this automated testing, you can test via curl commands such as 
```
curl -X GET http://alixetienne.com/convert/30/fahrenheit/C -H accept: application/json
```
You can also use the graphical web interface found http://alixetienne.com/documentation query the API; this is a convenience dev function, but I exposed it for this demo. 
Lastly, please note that if you launched your own AWS version of the API, when you’re done you should shutdown the API to save costs. To shutdown the API you should exit the remote docker container and then run
```
ray down temperature_api.yaml
```
This stops all AWS instances, but it doesn’t remove the EBS volumes which can still incur costs. Please terminate them as well to avoid paying unnecessary costs. You should be able to do this via AWS CLI / the Console
These are the basics are the deployment and testing of this application for more information oh the configuration file that deploys the cluster and sets up all the dependencies see https://docs.ray.io/en/latest/cluster/config.html

### Thank you!
